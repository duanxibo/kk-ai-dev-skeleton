"""Exercise source installer against a complete portable target runtime."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RuntimeUpgradeIntegrationTest(unittest.TestCase):
    def installer(self, target, *flags):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/init_project.py'),
                               '--repo-root', str(target), '--project-name', 'Upgrade sample',
                               '--format', 'json', *flags], capture_output=True, text=True)

    def test_full_pristine_upgrade_and_customized_conflict_preserve_target(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            installed = self.installer(target, '--apply-runtime', '--rewrite-adapter')
            self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
            manifest = target / '.gstack/runtime-install.json'
            baseline = json.loads(manifest.read_text())
            loop = target / '.gstack/scripts/gstack_loop.py'
            previous = b'# Previous installed release\n' + loop.read_bytes()
            loop.write_bytes(previous)
            baseline['files']['.gstack/scripts/gstack_loop.py'] = hashlib.sha256(previous).hexdigest()
            manifest.write_text(json.dumps(baseline))
            before_manifest = manifest.read_bytes()
            preview = self.installer(target, '--apply-runtime', '--upgrade-runtime', '--dry-run')
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            self.assertEqual(loop.read_bytes(), previous)
            self.assertEqual(manifest.read_bytes(), before_manifest)
            upgraded = self.installer(target, '--apply-runtime', '--upgrade-runtime')
            self.assertEqual(upgraded.returncode, 0, upgraded.stdout + upgraded.stderr)
            result = json.loads(upgraded.stdout)['runtime_apply']
            self.assertTrue(result['upgrade_complete'])
            self.assertEqual(loop.read_bytes(), (ROOT / '.gstack/scripts/gstack_loop.py').read_bytes())
            # A later user customization must block every bundle change, not only that file.
            baseline = json.loads(manifest.read_text())
            loop.write_bytes(previous)
            baseline['files']['.gstack/scripts/gstack_loop.py'] = hashlib.sha256(previous).hexdigest()
            manifest.write_text(json.dumps(baseline))
            qa = target / '.gstack/scripts/qa_verify.py'
            qa.write_bytes(qa.read_bytes() + b'\n# User-owned customization\n')
            snapshot = {path: (target / path).read_bytes() for path in baseline['files']}
            before_manifest = manifest.read_bytes()
            blocked = self.installer(target, '--apply-runtime', '--upgrade-runtime')
            self.assertEqual(blocked.returncode, 1, blocked.stdout + blocked.stderr)
            self.assertEqual(json.loads(blocked.stdout)['runtime_apply']['upgrade_status'], 'conflicts-preserved')
            self.assertEqual(manifest.read_bytes(), before_manifest)
            for path, content in snapshot.items():
                self.assertEqual((target / path).read_bytes(), content, path)


if __name__ == '__main__':
    unittest.main()
