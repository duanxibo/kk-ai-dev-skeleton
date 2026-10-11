import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / '.gstack/scripts'
sys.path.insert(0, str(SCRIPTS))
import nontechnical_continue as continuation
import team_flow_guard as guard
import gstack_loop as loop
import qa_verify
import required_gates_audit as gate_audit


class ScopedContinuationTest(unittest.TestCase):
    def test_completed_task_does_not_authorize_a_recommendation(self):
        summary = SimpleNamespace(current_step_key='complete', current_step_label='完成',
                                  task='demo', progress='7/7', blocked=False)
        with patch.object(continuation, 'active_boundary', return_value=Path('demo.md')), \
             patch.object(continuation, 'read_text', return_value=''), \
             patch.object(continuation, 'summarize_boundary', return_value=summary), \
             patch('acceptance_contract.task_completion_check', return_value=(True, 'verified')):
            plan = continuation.build_continue_plan(argparse.Namespace(raw='继续做'))
        self.assertEqual(plan.auto_chain_status, 'needs-next-task-authorization')
        self.assertTrue(any('授权' in s for s in plan.needs_user_confirmation))

    def test_unfinished_task_can_continue_inside_its_boundary(self):
        self.assertEqual(continuation.auto_chain_status_for('continue-current-task'),
                         'continue-current-boundary')
        self.assertTrue(any('当前任务范围' in s for s in continuation.confirmation_for('continue-current-task', False)))


class CompactEvidenceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        target = self.root / '.gstack/scripts'
        target.mkdir(parents=True)
        for name in ('autopilot_bootstrap.py', 'codex_mode.py', 'acceptance_contract.py', 'evidence_contract.py', 'adapter_runtime.py'):
            shutil.copy2(SCRIPTS / name, target / name)
        result = subprocess.run([
            sys.executable, str(target / 'autopilot_bootstrap.py'),
            '--topic', 'small-fix', '--goal', 'Fix one local behavior',
            '--allowed', 'src/demo.py', '--must', 'Verified behavior',
            '--verification', 'python3 -m unittest', '--compact-evidence',
            '--ai-reviewed', '--format', 'json',
        ], capture_output=True, text=True, check=True)
        files = json.loads(result.stdout)['files']
        self.assertEqual(len(set(files.values())), 1)
        self.path = files['boundary']
        self.file = self.root / self.path
        self.config = tomllib.loads((ROOT / '.gstack/workflows/team-development-flow.toml').read_text())

    def check_evidence(self, command):
        with patch.object(guard, 'REPO_ROOT', self.root):
            return guard.evidence_ok(command, {'evidence': self.path}, self.config)[0]

    def test_only_one_file_is_created_and_reviews_are_usable(self):
        self.assertEqual(len(list((self.root / '.gstack/task-boundaries').glob('*.md'))), 1)
        self.assertFalse((self.root / '.gstack/requirements').exists())
        for stage in ('requirement-brief', 'requirement-freeze', 'plan-ceo-review', 'plan-eng-review'):
            self.assertTrue(self.check_evidence(stage), stage)

    def test_qa_requires_execution_receipt(self):
        self.assertFalse(self.check_evidence('qa'))
        text = self.file.read_text().replace('- Status: pending', '- Status: done')
        self.file.write_text(text.replace('- Command: 待运行', '- Command: never-executed')
                            .replace('- Result: 待记录实际结果；不能把生成 scaffold 视为 QA 通过。', '- Result: claimed success'))
        self.assertFalse(self.check_evidence('qa'))
        adapter = self.root / 'adapters/default'
        adapter.mkdir(parents=True)
        (adapter / 'runtime.json').write_text(json.dumps({
            'version': 1, 'name': 'default', 'paths': {'implementation_prefixes': ['src/']},
            'commands': {'qa_verify': [sys.executable, '-c', 'assert 2 + 3 == 5']}, 'gates': {},
        }))
        self.file.write_text(self.file.read_text().replace('\"command_keys\": []', '\"command_keys\": [\"qa_verify\"]'))
        path, receipt = qa_verify.verify(self.root, ['qa_verify'], boundary=self.path)
        self.file.write_text(self.file.read_text().replace('- Execution Receipt: 待生成',
            '- Execution Receipt: ' + path.relative_to(self.root).as_posix()))
        self.assertTrue(self.check_evidence('qa'))

    def test_default_four_file_scaffold_can_complete_bound_acceptance(self):
        result = subprocess.run([
            sys.executable, str(self.root / '.gstack/scripts/autopilot_bootstrap.py'),
            '--topic', 'full-fix', '--goal', 'Correct addition', '--allowed', 'src/app.py',
            '--must', 'Adding two and three yields five', '--verification', 'product tests',
            '--ai-reviewed', '--format', 'json',
        ], capture_output=True, text=True, check=True)
        files = json.loads(result.stdout)['files']
        self.assertGreater(len(set(files.values())), 1)
        boundary = self.root / files['boundary']
        boundary.write_text(boundary.read_text().replace('"command_keys": []', '"command_keys": ["qa_verify"]'))
        adapter = self.root / 'adapters/default'
        adapter.mkdir(parents=True)
        (adapter / 'runtime.json').write_text(json.dumps({
            'version': 1, 'name': 'default', 'paths': {'implementation_prefixes': []},
            'commands': {'qa_verify': [sys.executable, '-c', 'assert 2 + 3 == 5']},
        }))
        receipt_path, receipt = qa_verify.verify(self.root, [], boundary=boundary)
        self.assertEqual(receipt['status'], 'passed')
        from acceptance_contract import qa_completion_check
        self.assertTrue(qa_completion_check(self.root,
            '- Execution Receipt: ' + receipt_path.relative_to(self.root).as_posix(),
            boundary=boundary)[0])

    def test_loop_and_team_guard_share_compact_review_contract(self):
        with patch.object(loop, 'REPO_ROOT', self.root):
            self.assertEqual(loop.eng_review_evidence_check_for(self.path).status, 'pass')
        self.assertTrue(self.check_evidence('plan-eng-review'))
        self.file.write_text(self.file.read_text().replace('- Result: pass', '- Result: pending'))
        with patch.object(loop, 'REPO_ROOT', self.root):
            self.assertNotEqual(loop.eng_review_evidence_check_for(self.path).status, 'pass')
        self.assertFalse(self.check_evidence('plan-eng-review'))

    def test_compact_gate_records_are_all_parsed(self):
        gates = gate_audit.parse_required_gates(self.file.read_text())
        self.assertEqual(len(gates), 6)
        self.assertEqual({g['gate_id'] for g in gates}, {'data-access', 'data-query',
                         'prototype-logic-extraction', 'subagent-plan', 'doc-backfill', 'data-knowledge-sync'})
        self.assertTrue(all(g.get('done_criteria') for g in gates))

    def test_full_compact_lifecycle_completes_with_actual_qa(self):
        self.test_qa_requires_execution_receipt()
        text = self.file.read_text().replace('  status: pending', '  status: done')
        self.file.write_text(text)
        records = guard.parse_required_flow(text)
        with patch.object(guard, 'REPO_ROOT', self.root):
            failures = guard.validate_commands(records, self.config['pre_push_requires'], self.config, allow_qa_only=True)
        self.assertEqual(failures, [])
        self.file.write_text(text.replace('- Spec Impact: `not-required`', '- Spec Impact: `pending`'))
        with patch.object(guard, 'REPO_ROOT', self.root):
            failures = guard.validate_commands(records, self.config['pre_push_requires'], self.config, allow_qa_only=True)
        self.assertTrue(any('domain-spec-readiness' in failure for failure in failures))

    def test_compact_implementation_record_is_accepted(self):
        self.assertTrue(self.check_evidence('implement'))

    def test_standard_lane_cannot_use_compact_exception(self):
        self.file.write_text(self.file.read_text().replace('- Lane: `fast-lane`', '- Lane: `standard`'))
        self.assertFalse(self.check_evidence('plan-eng-review'))

    def test_empty_review_field_does_not_consume_the_next_line(self):
        self.file.write_text(self.file.read_text().replace('- Scope: src/demo.py', '- Scope:'))
        self.assertFalse(self.check_evidence('plan-eng-review'))
        with patch.object(loop, 'REPO_ROOT', self.root):
            self.assertNotEqual(loop.eng_review_evidence_check_for(self.path).status, 'pass')

    def test_missing_review_section_is_rejected(self):
        self.file.write_text(self.file.read_text().replace('## Compact Review', '## Missing Review'))
        self.assertFalse(self.check_evidence('plan-eng-review'))


if __name__ == '__main__':
    unittest.main()
