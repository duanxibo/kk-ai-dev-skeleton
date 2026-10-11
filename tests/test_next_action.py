"""Next-step guidance preserves task evidence and authorization boundaries."""
import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.gstack/scripts'))
import next_action
import nontechnical_intent_router as router
import nontechnical_next_step as entry
import qa_verify
import target_verification
import test_target_adoption as adoption
SCRIPTS = adoption.SCRIPTS


def route(raw):
    return router.build_route(argparse.Namespace(raw=raw, audience='', success='', non_goal='', risk_confirmation=''))


class NextActionSafetyTest(unittest.TestCase):
    def test_completed_unverified_and_blocked_work_never_recommend_new_execution(self):
        completed = {'current_step_key': 'complete', 'acceptance_status': 'verified'}
        action = next_action.next_action_for(completed)
        self.assertEqual(action.status, 'accept-result')
        self.assertTrue(action.reply_required)
        self.assertIn('不要开启新任务', action.suggested_user_input)
        self.assertEqual(route(action.suggested_user_input).intent, 'completion_verify')
        for status in ('needs-verification', 'historical-record', 'not-checked'):
            action = next_action.next_action_for({**completed, 'acceptance_status': status})
            self.assertEqual(action.status, 'needs-verification')
            self.assertNotIn('新任务', action.suggested_user_input)
        self.assertEqual(next_action.next_action_for({**completed, 'blocked': True}).status, 'blocked')

    def test_pause_failure_manual_and_risk_supersede_generic_continue(self):
        task = {'current_step_key': 'implement'}
        for kwargs, expected in (({'intent': 'pause_current_task'}, 'paused'),
                                 ({'helper_status': 'failed'}, 'inspect-first'),
                                 ({'needs_confirmation': True}, 'clarify-scope'),
                                 ({'intent': 'undo_request'}, 'inspect-first')):
            with self.subTest(kwargs=kwargs):
                action = next_action.next_action_for(task, **kwargs)
                self.assertEqual(action.status, expected)
                self.assertNotIn('请继续', action.suggested_user_input)
        self.assertEqual(next_action.next_action_for({**task, 'mode': 'manual'}).status, 'manual-review')
        self.assertEqual(next_action.next_action_for({**task, 'mode': '手动控制'}).status, 'manual-review')
        manual_block = next_action.next_action_for({**task, 'mode': 'manual', 'blocked': True})
        self.assertTrue(manual_block.reply_required)
        self.assertIn('不要修改文件', manual_block.suggested_user_input)

    def test_unfinished_authorized_work_does_not_require_another_reply(self):
        action = next_action.next_action_for({'current_step_key': 'implement', 'mode': 'autonomous'})
        self.assertFalse(action.reply_required)
        self.assertIn('可选', next_action.render_reminder(action))
        self.assertEqual(route(action.suggested_user_input).intent, 'continue_current_task')
        for raw in ('下一步干啥', '下一句怎么说', '我不知道下一步要干啥'):
            self.assertEqual(route(raw).intent, 'nontechnical_home')

    def test_every_copyable_input_routes_to_its_intended_flow(self):
        cases = [
            (None, {}, {'clarification', 'task_kickoff'}),
            (None, {'intent': 'task_kickoff'}, {'clarification', 'task_kickoff'}),
            ({'current_step_key': 'implement'}, {}, {'continue_current_task'}),
            ({'current_step_key': 'qa', 'acceptance_status': 'needs-verification'}, {}, {'continue_current_task'}),
            ({'current_step_key': 'implement', 'blocked': True}, {}, {'progress_status'}),
            ({'current_step_key': 'complete', 'acceptance_status': 'verified'}, {}, {'completion_verify'}),
            ({'current_step_key': 'implement', 'mode': 'manual'}, {}, {'mode_control'}),
            (None, {'intent': 'pause_current_task'}, {'pause_current_task'}),
            (None, {'helper_status': 'failed'}, {'error_recovery'}),
            (None, {'needs_confirmation': True}, {'confirmation_brief'}),
        ]
        for task, kwargs, expected in cases:
            action = next_action.next_action_for(task, **kwargs)
            with self.subTest(status=action.status):
                self.assertIn(route(action.suggested_user_input).intent, expected)

    def test_entry_replaces_unsafe_helper_footer_after_failure(self):
        args = argparse.Namespace(raw='下一步干啥', audience='', success='', non_goal='', risk_confirmation='', topic='', ai_reviewed=False)
        old = next_action.render_reminder(next_action.next_action_for({'current_step_key': 'implement'}))
        with patch.object(entry, 'helper_for_route', return_value=('helper', 'failed', '检查失败\n'+old)), \
             patch('gstack_dashboard.active_boundary', return_value=None):
            result = entry.build_next_step(args)
        self.assertEqual(result.next_action['status'], 'inspect-first')
        self.assertEqual(result.user_response.count('你下一句可以直接复制：'), 1)
        self.assertNotIn('请继续当前', result.user_response)


class InstalledNextActionTest(unittest.TestCase):
    def setUp(self):
        adoption.TargetAdoptionTest.setUp(self)
        installer = SCRIPTS.parents[1] / 'scripts/init_project.py'
        installed = subprocess.run([sys.executable, str(installer), '--repo-root', str(self.root),
                                   '--project-name', 'Reminder example', '--apply-runtime', '--rewrite-adapter'],
                                  capture_output=True, text=True)
        self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
        self.env_vars = {**os.environ, 'KK_ACTIVE_BOUNDARY': str(self.boundary), 'KK_ADAPTER': 'default',
                         'KK_ADAPTER_RUNTIME': 'adapters/default/runtime.json'}

    def cli(self, helper, *args, active=True):
        env = dict(self.env_vars)
        if not active:
            env.pop('KK_ACTIVE_BOUNDARY', None)
        result = subprocess.run([sys.executable, '.gstack/scripts/'+helper+'.py', *args, '--format', 'json'],
                                cwd=self.root, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_fresh_install_and_actual_receipt_lifecycle_produce_truthful_copyable_guidance(self):
        agents = (self.root / 'AGENTS.md').read_text()
        self.assertIn('copyable user input', agents)
        no_task = self.cli('nontechnical_home', active=False)
        self.assertEqual(no_task['next_action']['status'], 'no-active-task')
        self.assertIn('【谁】', no_task['next_action']['suggested_user_input'])
        pending = self.cli('nontechnical_next_step', '--raw', '下一步干啥')
        self.assertIn('你下一句可以直接复制：', pending['user_response'])
        self.assertFalse(pending['next_action']['reply_required'])
        import gstack_dashboard
        flow = '\n## GStack Required Flow\n'+''.join('- '+key+':\n  status: done\n'+
                ('  evidence: .gstack/qa-reports/task.md\n' if key == 'qa' else '') for key in gstack_dashboard.FLOW_SEQUENCE)
        self.boundary.write_text(self.boundary.read_text()+flow)
        report = self.root / '.gstack/qa-reports/task.md'
        report.parent.mkdir(exist_ok=True)
        report.write_text('No executed acceptance\n')
        stale = self.cli('next_action')
        self.assertEqual(stale['status'], 'needs-verification')
        target_verification.configure(self.root, [sys.executable, '-B', 'product/test_product.py'])
        (self.product / 'app.py').write_text('def add(a, b):\n    return a + b\n')
        receipt, data = qa_verify.verify(self.root, [], boundary=self.boundary)
        self.assertEqual(data['status'], 'passed')
        report.write_text('- Execution Receipt: '+receipt.relative_to(self.root).as_posix()+'\n')
        completed = self.cli('nontechnical_delivery_summary', '--raw', '完成说明')
        self.assertTrue(completed['task_done'])
        self.assertEqual(completed['next_action']['status'], 'accept-result')
        self.assertEqual(completed['next_user_message'], completed['next_action']['suggested_user_input'])
        paused = self.cli('nontechnical_next_step', '--raw', '先停一下，暂停这个任务')
        self.assertEqual(paused['next_action']['status'], 'paused')
        self.assertNotIn('请继续当前', paused['user_response'])
        (self.product / 'app.py').write_text('def add(a, b):\n    return a - b\n')
        reopened = self.cli('nontechnical_delivery_summary', '--raw', '完成说明')
        self.assertFalse(reopened['task_done'])
        self.assertEqual(reopened['next_action']['status'], 'needs-verification')
        self.assertEqual(self.cli('next_action')['status'], 'needs-verification')
        self.boundary.write_text(self.boundary.read_text() + '\n## Decision Mode\n- Mode: manual\n')
        manual = self.cli('nontechnical_continue', '--raw', '继续做')
        self.assertEqual(manual['next_action']['status'], 'manual-review')
        self.assertEqual(manual['auto_chain_status'], 'needs-execution-authorization')
        self.assertNotIn('自主决定', ' '.join(manual['codex_next_actions']))
        self.assertIn('不自主修改文件', manual['status_reason'])


if __name__ == '__main__':
    unittest.main()
