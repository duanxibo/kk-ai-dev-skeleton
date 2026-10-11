import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / '.gstack/scripts'
sys.path.insert(0, str(SCRIPTS))
import evidence_contract as contract
import qa_verify
import team_flow_guard as guard
import gstack_loop as loop


class ReceiptTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        adapter = self.root / 'adapters/default'
        adapter.mkdir(parents=True)
        (adapter / 'runtime.json').write_text(json.dumps({
            'version': 1, 'name': 'default', 'paths': {'implementation_prefixes': ['src/']},
            'commands': {'pass': [sys.executable, '-c', 'print("verified")'],
                         'fail': [sys.executable, '-c', 'raise SystemExit(3)'],
                         'timeout': [sys.executable, '-c', 'import time; time.sleep(3)'],
                         'mutate': [sys.executable, '-c', 'from pathlib import Path; Path("src/demo.py").write_text("changed")']},
            'gates': {},
        }))
        (self.root / 'src').mkdir()
        (self.root / 'src/demo.py').write_text('initial')
        self.config = {'commands': {'qa': {'evidence_prefixes': ['.gstack/qa-reports/']}}}

    def execute(self, key='pass', timeout=10):
        path, receipt = qa_verify.verify(self.root, [key], timeout)
        text = '- Status: done\n- Execution Receipt: ' + path.relative_to(self.root).as_posix() + '\n'
        return path, receipt, text

    def test_actual_execution_passes_both_checker_consumers(self):
        path, receipt, text = self.execute()
        self.assertEqual(receipt['status'], 'passed')
        self.assertTrue(contract.qa_check(self.root, text)[0])
        report = self.root / '.gstack/qa-reports/result.md'
        report.parent.mkdir(parents=True)
        report.write_text(text)
        with patch.object(guard, 'REPO_ROOT', self.root):
            self.assertTrue(guard.evidence_ok('qa', {'evidence': '.gstack/qa-reports/result.md'}, self.config)[0])
        self.assertIs(loop.qa_check, guard.qa_check)

    def test_handwritten_pass_is_rejected(self):
        self.assertFalse(contract.qa_check(self.root, '- Command: never-executed\n- Result: pass')[0])

    def test_failed_and_timed_out_execution_cannot_pass(self):
        for key, timeout in [('fail', 10), ('timeout', 1)]:
            with self.subTest(key=key):
                path, receipt, text = self.execute(key, timeout)
                self.assertEqual(receipt['status'], 'failed')
                self.assertFalse(contract.qa_check(self.root, text)[0])

    def test_code_change_and_new_source_make_receipts_stale(self):
        for name in ('src/demo.py', 'src/new.py'):
            with self.subTest(name=name):
                path, receipt, text = self.execute()
                (self.root / name).write_text('new behavior')
                self.assertFalse(contract.qa_check(self.root, text)[0])

    def test_log_modification_is_rejected(self):
        path, receipt, text = self.execute()
        (self.root / receipt['runs'][0]['stdout_path']).write_text('forged log')
        self.assertFalse(contract.qa_check(self.root, text)[0])

    def test_verification_that_changes_code_is_failed(self):
        path, receipt, text = self.execute('mutate')
        self.assertEqual(receipt['status'], 'failed')
        self.assertFalse(contract.qa_check(self.root, text)[0])

    def test_malformed_receipt_shapes_fail_cleanly(self):
        for payload in ([], None, {"schema_version": 1, "status": "passed", "runs": ["bad"]}):
            path, receipt, text = self.execute()
            if isinstance(payload, dict):
                payload.update(source_before=receipt['source_before'], source_after=receipt['source_after'])
            path.write_text(json.dumps(payload))
            self.assertFalse(contract.qa_check(self.root, text)[0])

    def test_unknown_key_never_executes(self):
        with self.assertRaises(ValueError):
            qa_verify.verify(self.root, ['pass', 'missing'])
        self.assertFalse((self.root / 'output').exists())

    def test_outside_repo_receipt_rejected(self):
        self.assertFalse(contract.qa_check(self.root, '- Execution Receipt: ../receipt.json')[0])

    def test_evidence_write_does_not_make_receipt_stale(self):
        path, receipt, text = self.execute()
        evidence = self.root / '.gstack/task-boundaries/task.md'
        evidence.parent.mkdir(parents=True)
        evidence.write_text('status: done')
        self.assertTrue(contract.qa_check(self.root, text)[0])


if __name__ == '__main__':
    unittest.main()
