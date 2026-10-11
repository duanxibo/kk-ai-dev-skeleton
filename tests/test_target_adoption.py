"""Product assertions survive adoption and do not turn smoke checks into acceptance."""
import json
import os
from pathlib import Path
import shutil
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / '.gstack/scripts'
sys.path.insert(0, str(SCRIPTS))
import qa_verify
import target_verification


class TargetAdoptionTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        scripts = self.root / '.gstack/scripts'
        scripts.mkdir(parents=True)
        shutil.copy2(SCRIPTS / 'target_verification.py', scripts)
        adapter = self.root / 'adapters/default'
        adapter.mkdir(parents=True)
        runtime = {'version': 1, 'name': 'default', 'paths': {'implementation_prefixes': ['product/']},
                   'commands': {'qa_verify': [sys.executable, '.gstack/scripts/target_verification.py']},
                   'qa_policy': {'acceptance_command_keys': ['qa_verify']}}
        (adapter / 'runtime.json').write_text(json.dumps(runtime))
        self.product = self.root / 'product'
        self.product.mkdir()
        (self.product / 'app.py').write_text('def add(a, b):\n    return a - b\n')
        (self.product / 'test_product.py').write_text('from app import add\nassert add(2, 3) == 5, "sum must equal five"\n')
        self.boundary = self.root / '.gstack/task-boundaries/task.md'
        self.boundary.parent.mkdir()
        self.boundary.write_text('## User-visible Acceptance\n- AC-1: Adding two and three yields five.\n\n'
                                 '## Acceptance Verification\n```json\n' + json.dumps({'version': 1, 'criteria': [
                                     {'id': 'AC-1', 'description': 'Adding two and three yields five.',
                                      'command_keys': ['qa_verify']}]}) + '\n```\n')
        self.env = patch.dict(os.environ, {'KK_ADAPTER': 'default', 'KK_ADAPTER_RUNTIME': 'adapters/default/runtime.json'})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_missing_product_configuration_cannot_pass(self):
        with self.assertRaisesRegex(ValueError, 'not configured'):
            target_verification.run(self.root)

    def test_real_product_assertion_fails_then_passes_bound_verification(self):
        target_verification.configure(self.root, [sys.executable, '-B', 'product/test_product.py'])
        _, failed = qa_verify.verify(self.root, ['qa_verify'], boundary=self.boundary)
        self.assertEqual(failed['status'], 'failed')
        self.assertNotEqual(failed['runs'][0]['exit_code'], 0)
        (self.product / 'app.py').write_text('def add(a, b):\n    return a + b\n')
        _, passed = qa_verify.verify(self.root, ['qa_verify'], boundary=self.boundary)
        self.assertEqual(passed['status'], 'passed')
        self.assertEqual(passed['schema_version'], 2)

    def test_configuration_does_not_execute_or_overwrite(self):
        argv = [sys.executable, '-c', 'raise AssertionError("must not execute during configuration")']
        path = target_verification.configure(self.root, argv)
        original = path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'already exists'):
            target_verification.configure(self.root, ['different'])
        self.assertEqual(path.read_bytes(), original)

    def test_product_argv_is_passed_without_shell_interpretation(self):
        sentinel = self.root / 'shell-must-not-run'
        target_verification.configure(self.root, [sys.executable, '-c',
            'import sys; assert sys.argv[1] == "$(touch shell-must-not-run)"',
            '$(touch shell-must-not-run)'])
        self.assertEqual(target_verification.run(self.root), 0)
        self.assertFalse(sentinel.exists())

    def test_ci_is_opt_in_separate_and_does_not_overwrite(self):
        existing = self.root / '.github/workflows/existing.yml'
        existing.parent.mkdir(parents=True)
        existing.write_text('existing workflow\n')
        output = target_verification.install_target_ci(self.root, self.boundary.relative_to(self.root).as_posix())
        text = output.read_text()
        self.assertIn('--boundary', text)
        self.assertNotIn('--command-key', text)  # Execute all contract keys, including project-specific checks.
        self.assertIn('contents: read', text)
        self.assertEqual(existing.read_text(), 'existing workflow\n')
        with self.assertRaisesRegex(ValueError, 'refusing to overwrite'):
            target_verification.install_target_ci(self.root, self.boundary.relative_to(self.root).as_posix())

    def test_installed_target_and_fresh_checkout_require_real_acceptance(self):
        installer = SCRIPTS.parents[1] / 'scripts/init_project.py'
        result = subprocess.run([sys.executable, str(installer), '--repo-root', str(self.root),
            '--project-name', 'Assertion product', '--apply-runtime', '--rewrite-adapter'],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        runtime = json.loads((self.root / 'adapters/default/runtime.json').read_text())
        self.assertEqual(runtime['commands']['qa_verify'], ['python3', '.gstack/scripts/target_verification.py'])
        self.assertEqual(runtime['qa_policy']['acceptance_command_keys'], ['qa_verify'])
        target_verification.configure(self.root, [sys.executable, '-B', 'product/test_product.py'])
        command = [sys.executable, '.gstack/scripts/qa_verify.py', '--boundary',
                   self.boundary.relative_to(self.root).as_posix()]
        failed = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)
        (self.product / 'app.py').write_text('def add(a, b):\n    return a + b\n')
        passed = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
        receipt = json.loads(passed.stdout)['execution_receipt']
        import acceptance_contract
        qa_text = '- Execution Receipt: ' + receipt + '\n'
        self.assertEqual(acceptance_contract.qa_completion_check(self.root, qa_text, boundary=self.boundary), (True, ''))
        fresh = self.root.parent / (self.root.name + '-fresh')
        self.addCleanup(shutil.rmtree, fresh, True)
        shutil.copytree(self.root, fresh, ignore=shutil.ignore_patterns('output', '__pycache__'))
        valid, _ = acceptance_contract.qa_completion_check(fresh, qa_text,
            boundary=self.boundary.relative_to(self.root))
        self.assertFalse(valid, 'receipts must not be assumed present in a fresh checkout')
        regenerated = subprocess.run(command, cwd=fresh, capture_output=True, text=True)
        self.assertEqual(regenerated.returncode, 0, regenerated.stdout + regenerated.stderr)
        fresh_receipt = json.loads(regenerated.stdout)['execution_receipt']
        self.assertNotEqual(receipt, fresh_receipt)
        self.assertEqual(acceptance_contract.qa_completion_check(fresh,
            '- Execution Receipt: ' + fresh_receipt + '\n',
            boundary=self.boundary.relative_to(self.root)), (True, ''))

    def test_core_only_installer_detects_without_runtime_dependencies(self):
        installer = SCRIPTS.parents[1] / 'scripts/init_project.py'
        result = subprocess.run([sys.executable, str(installer), '--repo-root', str(self.root),
            '--apply-core'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        # Fixture initially provided only target helper; core install must not need runtime imports.
        self.assertFalse((self.root / '.gstack/scripts/acceptance_contract.py').exists())
        detected = subprocess.run([sys.executable, 'scripts/init_project.py', '--detect'],
            cwd=self.root, capture_output=True, text=True)
        self.assertEqual(detected.returncode, 0, detected.stdout + detected.stderr)

    def test_unsafe_command_and_ci_paths_fail_before_write(self):
        for argv in ([], 'python test.py', [''], ['bad\x00command']):
            with self.assertRaises(ValueError):
                target_verification.configure(self.root, argv)
        for boundary in ('../outside.md', '/tmp/task.md', 'missing.md', 'product/app.py'):
            with self.assertRaises(ValueError):
                target_verification.install_target_ci(self.root, boundary)
        self.assertFalse((self.root / target_verification.CONFIG).exists())
        self.assertFalse((self.root / target_verification.WORKFLOW).exists())


if __name__ == '__main__':
    unittest.main()
