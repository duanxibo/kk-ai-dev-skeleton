import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / '.gstack/scripts'
sys.path.insert(0, str(SCRIPTS))
from source_coverage import load_coverage_runtime, uncovered_sources


class SourceCoverageTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write_adapter('default', ['src/'])

    def write_adapter(self, name, prefixes):
        folder = self.root / 'adapters' / name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'runtime.json').write_text(json.dumps({'version':1, 'name':name, 'paths':{'implementation_prefixes':prefixes}, 'commands':{}, 'gates':{}}))

    def source_marker(self):
        self.write_adapter('skeleton', ['scripts/', 'tests/', '.gstack/scripts/'])
        for name in ['scripts/init_project.py', 'plugins/kk-dev-skeleton-adoption/.codex-plugin/plugin.json']:
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('{}')

    def test_monorepo_partial_mapping_is_reported(self):
        runtime = load_coverage_runtime(self.root)
        missing = uncovered_sources(self.root, runtime, ['src/index.ts', 'services/payments/main.go', 'packages/web/src/index.tsx'])
        self.assertEqual(missing, ['services/payments/main.go', 'packages/web/src/index.tsx'])

    def test_source_repository_covers_real_framework_files(self):
        self.source_marker()
        with patch.dict(os.environ, {}, clear=True):
            runtime = load_coverage_runtime(self.root)
        self.assertEqual(runtime.adapter_name, 'skeleton')
        self.assertEqual(uncovered_sources(self.root, runtime, ['scripts/init_project.py', 'tests/test_adapter_runtime.py', '.gstack/scripts/gstack_loop.py']), [])

    def test_installed_project_keeps_business_adapter(self):
        self.write_adapter('skeleton', ['scripts/'])
        runtime = load_coverage_runtime(self.root)
        self.assertEqual(runtime.adapter_name, 'default')
        self.assertEqual(uncovered_sources(self.root, runtime, ['app/page.tsx']), ['app/page.tsx'])

    def test_explicit_adapter_overrides_source_identity(self):
        self.source_marker()
        with patch.dict(os.environ, {'KK_ADAPTER':'default'}, clear=True):
            self.assertEqual(load_coverage_runtime(self.root).adapter_name, 'default')

    def test_scan_finds_unknown_root_without_git(self):
        p = self.root / 'unusual/module/main.rs'
        p.parent.mkdir(parents=True)
        p.write_text('fn main() {}')
        ignored = self.root / 'node_modules/pkg/index.js'
        ignored.parent.mkdir(parents=True)
        ignored.write_text('')
        self.assertEqual(uncovered_sources(self.root, load_coverage_runtime(self.root)), ['unusual/module/main.rs'])

    def test_spec_guard_fails_before_no_implementation_shortcut(self):
        scripts = self.root / '.gstack/scripts'
        scripts.mkdir(parents=True)
        for name in ['adapter_runtime.py', 'source_coverage.py', 'spec_sync_guard.py', 'evidence_contract.py']:
            shutil.copy2(SCRIPTS / name, scripts / name)
        source = self.root / 'services/payment/main.go'
        source.parent.mkdir(parents=True)
        source.write_text('package main')
        env = os.environ.copy()
        env.pop('KK_ADAPTER', None)
        env.pop('KK_ADAPTER_RUNTIME', None)
        result = subprocess.run([sys.executable, str(scripts / 'spec_sync_guard.py')], cwd=self.root, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('services/payment/main.go', result.stdout)
        self.assertNotIn('no implementation changes', result.stdout)

    def test_declared_archive_and_example_are_classified(self):
        runtime = load_coverage_runtime(self.root)
        runtime.data['paths'].update({'archive_prefixes':['archive/'], 'demo_prefixes':['examples/']})
        self.assertEqual(uncovered_sources(self.root, runtime, ['archive/old.py', 'examples/demo.ts', '.gstack/scripts/guard.py', 'scripts/init_project.py']), [])

if __name__ == '__main__':
    unittest.main()
