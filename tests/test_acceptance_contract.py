"""Acceptance completion requires the intended task tests, not merely a green command."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.gstack/scripts'))
from acceptance_contract import load_acceptance, qa_completion_check
from evidence_contract import qa_check
from qa_verify import verify


class AcceptanceContractTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        env = patch.dict(os.environ, {'KK_ADAPTER': 'default', 'KK_ADAPTER_RUNTIME': 'adapters/default/runtime.json'})
        env.start()
        self.addCleanup(env.stop)
        adapter = self.root / 'adapters/default'
        adapter.mkdir(parents=True)
        self.runtime = {'version': 1, 'name': 'default', 'paths': {'implementation_prefixes': ['product/']},
                        'commands': {'qa_verify': [sys.executable, '-B', 'product/test.py'],
                                     'other_product_test': [sys.executable, '-c', 'assert 4 * 2 == 8'],
                                     'message': [sys.executable, '-c', 'print("no product tests")']},
                        'qa_policy': {'acceptance_command_keys': ['qa_verify', 'other_product_test']}}
        (adapter / 'runtime.json').write_text(json.dumps(self.runtime))
        (self.root / 'product').mkdir()
        (self.root / 'product/app.py').write_text('def add(a, b):\n return a + b\n')
        (self.root / 'product/test.py').write_text('from app import add\nassert add(2, 3) == 5\n')
        self.boundary = self.root / '.gstack/task-boundaries/task.md'
        self.boundary.parent.mkdir(parents=True)
        self.criteria = [{'id': 'AC-1', 'description': 'Adding two and three yields five', 'command_keys': ['qa_verify']}]
        self.write_boundary()

    def write_boundary(self):
        self.boundary.write_text('# Task\n## Goal\n- Correct addition\n## User-visible Acceptance\n' + ''.join('- ' + c['description'] + '\n' for c in self.criteria if isinstance(c, dict) and isinstance(c.get('description'), str)) +
                                 '## Acceptance Verification\n```json\n' + json.dumps({'version': 1, 'criteria': self.criteria}) + '\n```\n'
                                 '## GStack Required Flow\n- qa:\n  status: pending\n')

    def run_bound(self):
        path, receipt = verify(self.root, [], boundary=self.boundary)
        text = '- Execution Receipt: ' + path.relative_to(self.root).as_posix() + '\n'
        return receipt, text

    def test_message_success_does_not_complete_product_acceptance(self):
        (self.root / 'product/app.py').write_text('raise RuntimeError("broken product")\n')
        path, receipt = verify(self.root, ['message'])
        text = '- Execution Receipt: ' + path.relative_to(self.root).as_posix()
        self.assertEqual(receipt['status'], 'passed')
        self.assertTrue(qa_check(self.root, text)[0])  # Backward-compatible execution evidence.
        self.assertFalse(qa_completion_check(self.root, text, boundary=self.boundary)[0])
        with self.assertRaisesRegex(ValueError, 'every mapped'):
            verify(self.root, ['message'], boundary=self.boundary)
        receipt, text = self.run_bound()
        self.assertEqual(receipt['status'], 'failed')
        self.assertFalse(qa_completion_check(self.root, text, boundary=self.boundary)[0])

    def test_real_assertion_completes_the_current_task(self):
        receipt, text = self.run_bound()
        self.assertEqual(receipt['status'], 'passed')
        self.assertTrue(qa_completion_check(self.root, text, boundary=self.boundary)[0])

    def test_edited_acceptance_invalidates_receipt_even_without_source_change(self):
        receipt, text = self.run_bound()
        self.criteria[0]['description'] = 'Adding two and three yields six'
        self.write_boundary()
        self.assertTrue(qa_check(self.root, text)[0])
        self.assertFalse(qa_completion_check(self.root, text, boundary=self.boundary)[0])

    def test_changed_visible_acceptance_is_not_hidden_by_unchanged_mapping(self):
        receipt, text = self.run_bound()
        self.boundary.write_text(self.boundary.read_text().replace('- Adding two and three yields five', '- Product now must support decimals'))
        self.assertFalse(qa_completion_check(self.root, text, boundary=self.boundary)[0])

    def test_flow_status_and_report_writes_do_not_stale_acceptance(self):
        receipt, text = self.run_bound()
        self.boundary.write_text(self.boundary.read_text().replace('status: pending', 'status: done'))
        self.assertTrue(qa_completion_check(self.root, text, boundary=self.boundary)[0])

    def test_unmapped_criteria_and_smoke_mapping_fail_before_execution(self):
        for keys in ([], ['message'], ['missing']):
            self.criteria[0]['command_keys'] = keys
            self.write_boundary()
            with self.subTest(keys=keys), self.assertRaises(ValueError):
                verify(self.root, [], boundary=self.boundary)
        self.assertFalse((self.root / 'output').exists())

    def test_partial_acceptance_execution_is_refused(self):
        self.criteria.append({'id': 'AC-2', 'description': 'Multiplication works', 'command_keys': ['other_product_test']})
        self.write_boundary()
        with self.assertRaisesRegex(ValueError, 'every mapped'):
            verify(self.root, ['qa_verify'], boundary=self.boundary)
        receipt, text = self.run_bound()
        self.assertEqual(len(receipt['runs']), 2)
        self.assertTrue(qa_completion_check(self.root, text, boundary=self.boundary)[0])

    def test_receipt_cannot_be_reused_for_another_task(self):
        receipt, text = self.run_bound()
        other = self.boundary.with_name('other.md')
        other.write_text(self.boundary.read_text())
        self.assertFalse(qa_completion_check(self.root, text, boundary=other)[0])

    def test_unmapped_visible_behavior_cannot_complete(self):
        self.boundary.write_text(self.boundary.read_text().replace('## Acceptance Verification', '- Decimal arithmetic also works\n## Acceptance Verification'))
        with self.assertRaisesRegex(ValueError, 'omits'):
            self.run_bound()

    def test_legacy_boundary_has_clear_migration_error(self):
        self.boundary.write_text('# Legacy boundary without acceptance mapping\n')
        with self.assertRaisesRegex(ValueError, 'migrate legacy'):
            load_acceptance(self.root, self.boundary)

    def test_duplicate_ids_and_invalid_contract_shapes_are_rejected(self):
        for criteria in ([], [None], self.criteria * 2, [{'id': 'AC-1', 'description': ' ', 'command_keys': ['qa_verify']}]):
            self.criteria = criteria
            self.write_boundary()
            with self.assertRaises(ValueError):
                load_acceptance(self.root, self.boundary)


if __name__ == '__main__':
    unittest.main()
