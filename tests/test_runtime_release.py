from dataclasses import replace
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.gstack/scripts'))
import autopilot_bootstrap as bootstrap
import nontechnical_formal_kickoff as kickoff
from codex_mode import current_mode


class RuntimeReleaseTest(unittest.TestCase):
    def test_compact_record_has_bounded_size_and_pending_qa(self):
        args = bootstrap.build_parser().parse_args(['--topic', 'fix', '--goal', 'Fix behavior', '--allowed', 'src/a.py', '--must', 'Regression passes', '--verification', 'python3 -m unittest', '--ai-reviewed'])
        args.title = 'Fix'
        paths = bootstrap.EvidencePaths(*(ROOT / '.gstack/task-boundaries/fix.md',) * 3)
        text = bootstrap.compact_boundary_text(args, paths, current_mode())
        self.assertLessEqual(len(text.splitlines()), 100)
        self.assertIn('- Status: pending', text)
        self.assertIn('- Execution Receipt: 待生成', text)
        self.assertIn('- Engineering decisions:', text)

    def test_automatic_compact_requires_review_and_excludes_ui_and_data(self):
        for raw, reviewed, expected in (("修复脚本重复输出", True, True), ("修复脚本重复输出", False, False), ("修复页面重复输出", True, False), ("修复 API 重复输出", True, False)):
            argv = ['--raw', raw, '--success', '输出一次', '--non-goal', '不扩大范围', '--allowed', 'scripts/demo.py']
            if reviewed:
                argv.append('--ai-reviewed')
            args = kickoff.build_parser().parse_args(argv)
            with patch.object(kickoff, 'normalize_lane', return_value='fast-lane'):
                package = kickoff.build_formal_package(args)
            self.assertEqual(package.paths['requirement'] == package.paths['boundary'], expected, raw)

    def test_formal_compact_write_preserves_explicit_scope_and_requires_scope(self):
        argv = ['--raw', '修复脚本重复输出', '--success', '输出一次', '--non-goal', '不扩大范围', '--ai-reviewed', '--write']
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            patches = dict(REPO_ROOT=root, REQUIREMENTS_DIR=root / '.gstack/requirements', REVIEWS_DIR=root / '.gstack/reviews', BOUNDARIES_DIR=root / '.gstack/task-boundaries', QA_DIR=root / '.gstack/qa-reports')
            summary = kickoff.build_summary(kickoff.build_parser().parse_args(argv))
            summary = replace(summary, can_continue=True)
            with patch.multiple(kickoff, **patches), patch.object(kickoff, 'normalize_lane', return_value='fast-lane'), patch.object(kickoff, 'build_summary', return_value=summary):
                args = kickoff.build_parser().parse_args(argv + ['--topic', 'unknown'])
                full = kickoff.build_formal_package(args)
                self.assertNotEqual(full.paths['requirement'], full.paths['boundary'])
                args = kickoff.build_parser().parse_args(argv + ['--topic', 'explicit', '--allowed', 'scripts/demo.py'])
                compact = kickoff.build_formal_package(args)
                text = (root / compact.paths['boundary']).read_text()
                scope = text.split('## Allowed Files')[1].split('## Forbidden Files')[0]
                self.assertIn('- scripts/demo.py', scope)
                self.assertNotIn('stack/**', scope)
                self.assertNotIn('src/**', scope)
                self.assertEqual(compact.paths['requirement'], compact.paths['boundary'])
                args = kickoff.build_parser().parse_args(argv + ['--allowed', '../outside.py'])
                with self.assertRaises(SystemExit):
                    kickoff.build_formal_package(args)

    def test_explicit_upgrade_changes_pristine_files_and_preserves_custom_files(self):
        spec = importlib.util.spec_from_file_location('release_init', ROOT / 'scripts/init_project.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as source_tmp, tempfile.TemporaryDirectory() as target_tmp:
            source, target = Path(source_tmp), Path(target_tmp)
            (source / 'plain.py').write_text('original')
            (source / 'custom.py').write_text('original')
            with patch.object(module, 'SOURCE_REPO_ROOT', source), patch.object(module, 'REPO_ROOT', target), patch.object(module, 'RUNTIME_BUNDLE_FILES', ('plain.py', 'custom.py')):
                module.copy_runtime_bundle(dry_run=False)
                (target / 'custom.py').write_text('customized')
                (source / 'plain.py').write_text('updated')
                (source / 'custom.py').write_text('updated')
                preview = module.copy_runtime_bundle(dry_run=True, upgrade=True)
                self.assertEqual((target / 'plain.py').read_text(), 'original')
                self.assertIn('plain.py', preview['would_create'])
                result = module.copy_runtime_bundle(dry_run=False, upgrade=True)
                self.assertEqual(result['updated_paths'], ['plain.py'])
                self.assertFalse(result['upgrade_complete'])
                self.assertEqual(result['upgrade_status'], 'conflicts-preserved')
                self.assertEqual((target / 'plain.py').read_text(), 'updated')
                self.assertEqual((target / 'custom.py').read_text(), 'customized')
                self.assertEqual(result['preserved_differences'][0]['path'], 'custom.py')
                self.assertEqual(json.loads((target / '.gstack/runtime-install.json').read_text())['release_version'], '0.2.0')


if __name__ == '__main__':
    unittest.main()
