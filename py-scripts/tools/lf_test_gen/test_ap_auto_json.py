"""Headless regression checks for AP Auto output; no LANforge connection required."""
import argparse
import ast
import inspect
import json
from pathlib import Path
import shlex
import tempfile
import unittest

from lf_create_ap_auto_json import lf_create_ap_auto_json


class Var:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class ApAutoJsonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.kwargs = {}
        for key in inspect.signature(lf_create_ap_auto_json).parameters:
            if 'dict' in key:
                value = {0: Var('Use'), 1: Var('Use')}
            elif key.startswith('_file_'):
                value = key + '.json'
            elif key.startswith('_dir_'):
                value = str(self.directory)
            elif key.startswith('_suite_radios_'):
                value = '_W7_W9'
            elif key.startswith('_lf_radio_'):
                value = 'Radio-4'
            elif key == '_ap_auto_duration':
                value = '15000 (15 sec)'
            elif key == '_radio_count':
                value = 2
            elif key == '_upstream_port':
                value = '1.3.eth2'
            else:
                value = Var('Use')
            self.kwargs[key] = value
        self.kwargs['_radio_dict'] = {0: Var('1.2.wiphy7'), 1: Var('1.3.wiphy9')}
        self.kwargs['_radio_batch_dict'] = {0: Var('1,4,2'), 1: Var('1,2')}
        self.kwargs['_lf_ap_auto_number_dut_indexes_combobox'] = Var('4')
        self.kwargs['_use_idx_entry_var_dict'] = {i: Var('Use') for i in range(4)}
        for band in ('2g', '5g', '6g'):
            self.kwargs[f'_suite_test_name_{band}_dict'] = {0: Var('BE200'), 1: Var('BE200')}
        self.kwargs['_lf_ap_auto_capacity'] = Var('Do Not Use')

    def generate(self, band='6g'):
        generator = lf_create_ap_auto_json(**self.kwargs)
        generator.test_suite_band = band
        generator.create_suite()
        path = Path(getattr(generator, f'dir_file_{band}'))
        self.assertEqual(path.parent, self.directory)
        return next(iter(json.loads(path.read_text())['test_suites'].values()))

    def runner_parser(self):
        # Extract the real parser without importing the runner's hardware dependencies.
        root = Path(__file__).resolve().parents[3]
        base = ast.parse((root / 'py-json/cv_test_manager.py').read_text())
        function = next(n for n in base.body if isinstance(n, ast.FunctionDef) and n.name == 'cv_add_base_parser')
        namespace = {'argparse': argparse}
        exec(compile(ast.Module(body=[function], type_ignores=[]), '<base parser>', 'exec'), namespace)
        parser = argparse.ArgumentParser()
        namespace['cv_add_base_parser'](parser)
        tree = ast.parse((root / 'py-scripts/lf_ap_auto_test.py').read_text())
        main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
        statements = [n for n in main.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                      and isinstance(n.value.func, ast.Attribute) and isinstance(n.value.func.value, ast.Name)
                      and n.value.func.value.id == 'parser' and n.value.func.attr == 'add_argument']
        exec(compile(ast.Module(body=statements, type_ignores=[]), '<AP Auto parser>', 'exec'), {'parser': parser})
        return parser

    def test_combined_bands_and_runner_compatibility(self):
        for band in ('2g', '5g', '6g'):
            with self.subTest(band=band):
                suite = self.generate(band)
                runs = [v for v in suite.values() if v['command'] == 'lf_ap_auto_test.py']
                self.assertEqual(len(runs), 1)
                arguments = ' '.join(runs[0]['args_list'])
                arguments = arguments.replace('LF_MGR_PORT', '8080').replace('DUT_SET_NAME', "'DUT_NAME' 'test'")
                arguments = arguments.replace('use_ssid_idx=3', '')
                parsed = self.runner_parser().parse_args(shlex.split(arguments))
                self.assertEqual(getattr(parsed, f'radio{band[0]}'), [['1.2.wiphy7'], ['1.3.wiphy9']])
                self.assertEqual(getattr(parsed, f'max_stations_{band[0]}'), 6)
                self.assertIn('SSID_USED BSSID_TO_USE (4)', getattr(parsed, f'dut{band[0]}_0'))
                self.assertIn(['basic_cx', '1'], parsed.set)
                self.assertIn(['capacity', '0'], parsed.set)
                self.assertIn(['channel_switch', '1'], parsed.set)
                self.assertIn(['dur20: 15'], parsed.raw_line)
                scenario = next(v for v in suite.values() if v['command'] == 'create_chamberview.py')
                self.assertIn('profile_link 1.2 STA-AUTO 4', ' '.join(scenario['args_list']))
                self.assertIn('wiphy7,AUTO', ' '.join(scenario['args_list']))
                self.assertIn('profile_link 1.3 upstream', ' '.join(scenario['args_list']))
                dut = next(v for v in suite.values() if v['command'] == 'create_chamberview_dut.py')
                self.assertEqual(sum('--ssid ' in arg for arg in dut['args_list']), 4)

    def test_individual_and_report_controls(self):
        self.kwargs['_lf_ap_auto_use_combined_var'] = Var('Do Not Use')
        self.kwargs['_lf_ap_auto_use_inspect_var'] = Var('Do Not Use')
        suite = self.generate()
        self.assertEqual(sum(v['command'] == 'lf_ap_auto_test.py' for v in suite.values()), 2)
        self.assertNotIn('lf_inspect', suite)
        self.assertIn('lf_qa', suite)

    def test_no_tests_or_disabled_dut_index_are_rejected(self):
        self.kwargs['_use_idx_entry_var_dict'][3] = Var('Do Not Use')
        with self.assertRaisesRegex(ValueError, "Enable DUT index 3"):
            self.generate()
        self.kwargs['_use_idx_entry_var_dict'][3] = Var('Use')
        generator = lf_create_ap_auto_json(**self.kwargs)
        for var in generator._test_options().values():
            var.value = 'Do Not Use'
        with self.assertRaisesRegex(ValueError, "Select at least one"):
            generator.validate_settings()
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_invalid_settings_do_not_write_files(self):
        for key, value in [('_ap_auto_duration', '<Custom>'),
                           ('_lf_ap_auto_number_dut_indexes_combobox', Var('1')),
                           ('_lf_radio_6g', '<Custom>')]:
            with self.subTest(key=key):
                previous = self.kwargs[key]
                self.kwargs[key] = value
                with self.assertRaises(ValueError):
                    self.generate()
                self.assertEqual(list(self.directory.iterdir()), [])
                self.kwargs[key] = previous


if __name__ == '__main__':
    unittest.main()
