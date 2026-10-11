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


class ScopedContinuationTest(unittest.TestCase):
    def test_completed_task_does_not_authorize_a_recommendation(self):
        summary = SimpleNamespace(current_step_key='complete', current_step_label='完成',
                                  task='demo', progress='7/7', blocked=False)
        with patch.object(continuation, 'active_boundary', return_value=Path('demo.md')), \
             patch.object(continuation, 'read_text', return_value=''), \
             patch.object(continuation, 'summarize_boundary', return_value=summary):
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
        for name in ('autopilot_bootstrap.py', 'codex_mode.py'):
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

    def test_qa_requires_actual_command_and_result(self):
        self.assertFalse(self.check_evidence('qa'))
        text = self.file.read_text().replace('- Status: pending', '- Status: done')
        self.file.write_text(text)
        self.assertFalse(self.check_evidence('qa'))
        self.file.write_text(text.replace('- Command: 待运行', '- Command: python3 -m unittest')
                            .replace('- Result: 待记录实际结果；不能把生成 scaffold 视为 QA 通过。',
                                     '- Result: 7 tests passed'))
        self.assertTrue(self.check_evidence('qa'))

    def test_standard_lane_cannot_use_compact_exception(self):
        self.file.write_text(self.file.read_text().replace('- Lane: `fast-lane`', '- Lane: `standard`'))
        self.assertFalse(self.check_evidence('plan-eng-review'))

    def test_missing_review_section_is_rejected(self):
        self.file.write_text(self.file.read_text().replace('## Compact Review', '## Missing Review'))
        self.assertFalse(self.check_evidence('plan-eng-review'))


if __name__ == '__main__':
    unittest.main()
