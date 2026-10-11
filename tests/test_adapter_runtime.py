import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / '.gstack/scripts/adapter_runtime.py'
spec = importlib.util.spec_from_file_location('review_adapter_runtime', SCRIPT)
runtime = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runtime
spec.loader.exec_module(runtime)


class AdapterRuntimeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.env = patch.dict(os.environ, {'KK_ADAPTER': 'default', 'KK_ADAPTER_RUNTIME': ''})
        self.env.start()
        self.addCleanup(self.env.stop)

    def write(self, payload):
        p = self.root / 'adapters/default/runtime.json'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(payload), encoding='utf-8')
        return p

    def test_missing_adapter_fails_by_default(self):
        with self.assertRaisesRegex(RuntimeError, 'runtime missing'):
            runtime.load_adapter_runtime(self.root)

    def test_explicit_compatibility_mode_has_no_project_paths(self):
        result = runtime.load_adapter_runtime(self.root, strict=False)
        self.assertTrue(result.warnings)
        self.assertEqual(result.paths(), {})
        self.assertEqual(result.gates(), {})

    def test_valid_adapter_preserves_only_its_paths(self):
        self.write({'paths': {'implementation_prefixes': ['src/'], 'spec_prefixes': ['docs/']}})
        result = runtime.load_adapter_runtime(self.root)
        self.assertEqual(result.path_tuple('implementation_prefixes'), ('src/',))
        self.assertNotIn('backend_implementation_prefixes', result.paths())

    def test_wrong_types_report_field_path(self):
        cases = [
            ({'paths': []}, 'paths'),
            ({'paths': {'implementation_prefixes': 'src/'}}, 'paths.implementation_prefixes'),
            ({'commands': {'doctor': [1]}}, 'commands.doctor'),
            ({'gates': {'data_access_status_requirements': 1}}, 'gates.data_access_status_requirements'),
            ({'gates': {'data_access_status_requirements': [{}]}}, 'requirements\\[0\\].prefixes'),
        ]
        for payload, field in cases:
            with self.subTest(payload=payload):
                self.write(payload)
                with self.assertRaisesRegex(RuntimeError, field):
                    runtime.load_adapter_runtime(self.root)

    def test_unsafe_paths_are_rejected(self):
        for value in ('../src/', '/src/', 'https://example.com/', 'C:\\src', ''):
            with self.subTest(value=value):
                self.write({'paths': {'implementation_prefixes': [value]}})
                with self.assertRaisesRegex(RuntimeError, 'repository-relative'):
                    runtime.load_adapter_runtime(self.root)

    def test_incomplete_adapter_cannot_be_treated_as_ready(self):
        self.write({"name": "demo"})
        with self.assertRaisesRegex(RuntimeError, "paths.implementation_prefixes"):
            runtime.load_adapter_runtime(self.root)

    def test_malformed_json_has_actionable_error(self):
        self.write({}).write_text('{', encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, 'runtime invalid'):
            runtime.load_adapter_runtime(self.root)

    def test_invalid_compatibility_config_cannot_disable_a_gate_silently(self):
        self.write({'gates': {'data_access_status_requirements': 1}})
        result = runtime.load_adapter_runtime(self.root, strict=False)
        self.assertTrue(result.warnings)
        self.assertEqual(result.gates(), {})


if __name__ == '__main__':
    unittest.main()
