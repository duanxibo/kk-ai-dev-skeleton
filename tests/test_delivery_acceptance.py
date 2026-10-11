"""Recorded completion must not masquerade as verified task delivery."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.gstack/scripts'))
import gstack_dashboard as dashboard
import nontechnical_continue as continuation
import nontechnical_delivery_summary as delivery
import qa_verify
import target_verification
import test_target_adoption


class DeliveryAcceptanceTest(unittest.TestCase):
    def setUp(self):
        test_target_adoption.TargetAdoptionTest.setUp(self)
        self.report = self.root / '.gstack/qa-reports/task.md'
        self.report.parent.mkdir()
        self.report.write_text('QA claimed done\n')
        flow = '\n## GStack Required Flow\n' + ''.join(
            '- ' + stage + ':\n  status: done\n' + ('  evidence: .gstack/qa-reports/task.md\n' if stage == 'qa' else '')
            for stage in dashboard.FLOW_SEQUENCE)
        self.boundary.write_text(self.boundary.read_text() + flow)
        for module in (dashboard, continuation, delivery):
            mock = patch.object(module, 'REPO_ROOT', self.root)
            mock.start()
            self.addCleanup(mock.stop)

    def summarize(self, active=True):
        return dashboard.summarize_boundary(self.boundary, self.boundary if active else None)

    def delivery(self, summary):
        with patch.object(delivery, 'dashboard_for', return_value={'tasks': [asdict(summary)]}):
            return delivery.build_delivery_summary(argparse.Namespace(raw='完成说明', query=''))

    def continuation(self, summary):
        with patch.object(continuation, 'active_boundary', return_value=self.boundary), patch.object(
                continuation, 'summarize_boundary', return_value=summary):
            return continuation.build_continue_plan(argparse.Namespace(raw='继续'))

    def test_forged_done_record_recovers_same_authorized_task(self):
        summary = self.summarize()
        self.assertEqual(summary.current_step_key, 'qa')
        self.assertEqual(summary.acceptance_status, 'needs-verification')
        self.assertEqual(summary.progress, '6/7')
        self.assertEqual(self.delivery(summary).status, 'progress-summary')
        plan = self.continuation(summary)
        self.assertEqual(plan.status, 'continue-current-task')
        self.assertEqual(plan.auto_chain_status, 'continue-current-boundary')

    def test_historical_done_is_labeled_and_not_final_delivery(self):
        summary = self.summarize(active=False)
        self.assertEqual(summary.acceptance_status, 'historical-record')
        self.assertIn('历史记录', summary.current_step_label)
        result = self.delivery(summary)
        self.assertFalse(result.task_done)
        self.assertEqual(result.progress, '6/7')

    def test_valid_receipt_delivers_then_source_change_reopens_qa(self):
        target_verification.configure(self.root, [sys.executable, '-B', 'product/test_product.py'])
        (self.product / 'app.py').write_text('def add(a, b):\n    return a + b\n')
        receipt, result = qa_verify.verify(self.root, ['qa_verify'], boundary=self.boundary)
        self.assertEqual(result['status'], 'passed')
        self.report.write_text('- Execution Receipt: ' + receipt.relative_to(self.root).as_posix() + '\n')
        summary = self.summarize()
        self.assertEqual(summary.acceptance_status, 'verified')
        self.assertEqual(self.delivery(summary).status, 'ready-to-share')
        self.assertEqual(self.continuation(summary).auto_chain_status, 'needs-next-task-authorization')
        (self.product / 'app.py').write_text('def add(a, b):\n    return a - b\n')
        reopened = self.summarize()
        self.assertEqual(reopened.current_step_key, 'qa')
        self.assertFalse(self.delivery(reopened).task_done)
        # Even a cached summary cannot produce a final statement after code changes.
        self.assertFalse(self.delivery(summary).task_done)
        self.assertFalse(self.continuation(summary).task_done)


if __name__ == '__main__':
    unittest.main()
