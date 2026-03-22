import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from mahkrab import constants as c
from mahkrab.func import run

class LanguageSupportTests(unittest.TestCase):
    def test_supported_languages_match_top_25_target(self) -> None:
        expected = {
            'Ada',
            'Assembly',
            'C',
            'C#',
            'C++',
            'COBOL',
            'Classic Visual Basic',
            'Dart',
            'Delphi/Object Pascal',
            'Fortran',
            'Go',
            'Java',
            'JavaScript',
            'Kotlin',
            'MATLAB',
            'Perl',
            'PHP',
            'Prolog',
            'Python',
            'R',
            'Rust',
            'SQL',
            'Scratch',
            'Swift',
            'Visual Basic',
        }

        self.assertEqual(set(run.SUPPORTED_LANGUAGES), expected)
        self.assertEqual(len(run.SUPPORTED_LANGUAGES), 25)

    def test_interpreted_map_contains_new_languages(self) -> None:
        full_path = '/tmp/example'
        interpret_map = run.get_interpret_map(full_path)

        self.assertEqual(interpret_map['.r'], ([c.RSCRIPT_PATH, full_path], 'Rscript'))
        self.assertEqual(interpret_map['.sb3'], ([c.TURBOWARP_PATH, 'run', full_path], 'twcli'))
        self.assertEqual(interpret_map['.dart'], ([c.DART_PATH, full_path], 'dart'))
        self.assertEqual(interpret_map['.pro'], ([c.SWIPL_PATH, '-q', '-s', full_path, '-t', 'halt'], 'swipl'))
        self.assertEqual(interpret_map['.m'], (run.matlab_run_cmd(full_path), 'matlab'))

    def test_command_compile_map_contains_new_languages(self) -> None:
        full_path = '/tmp/example.kt'
        outputfile = 'build/example'
        command_compile_map = run.get_command_compile_map(full_path, outputfile)

        self.assertEqual(
            command_compile_map['.cs'],
            ([c.CSC_PATH, '-nologo', '-out:build/example.exe', full_path], run.mono_run_cmd('build/example.exe'), 'C#')
        )
        self.assertEqual(
            command_compile_map['.vb'],
            ([c.VBC_PATH, '-nologo', '-out:build/example.exe', full_path], run.mono_run_cmd('build/example.exe'), 'Visual Basic')
        )
        self.assertEqual(
            command_compile_map['.kt'],
            ([c.KOTLINC_PATH, full_path, '-include-runtime', '-d', 'build/example.jar'], [c.JAVA_PATH, '-jar', 'build/example.jar'], 'kotlinc')
        )
        self.assertEqual(
            command_compile_map['.cob'],
            ([c.COBC_PATH, '-x', '-o', outputfile, full_path], run.native_run_cmd(outputfile), 'cobc')
        )
        self.assertIn('.pas', command_compile_map)
        self.assertIn('.f90', command_compile_map)
        self.assertIn('.adb', command_compile_map)
        self.assertIn('.swift', command_compile_map)
        self.assertIn('.bas', command_compile_map)

    def test_python_dispatch_uses_python_executor(self) -> None:
        args = SimpleNamespace()

        with patch('mahkrab.func.run.pyexec.Executor.exec') as exec_mock:
            run.run('example.py', 'build/example', args, False)

        exec_mock.assert_called_once_with('example.py', 'build/example', args)

    def test_compiled_dispatch_uses_compiled_executor(self) -> None:
        args = SimpleNamespace()

        with patch('mahkrab.func.run.cexec.Executor.exec') as exec_mock:
            run.run('example.c', 'build/example', args, True)

        exec_mock.assert_called_once()
        call_args = exec_mock.call_args[0]
        self.assertTrue(call_args[0].endswith('/example.c'))
        self.assertEqual(call_args[1:], ('build/example', args, True))

    def test_command_compiled_dispatch_uses_command_executor(self) -> None:
        args = SimpleNamespace()

        with patch('mahkrab.func.run.cmdexec.Executor.exec') as exec_mock:
            run.run('example.kt', 'build/example', args, True)

        exec_mock.assert_called_once()
        cmd, run_cmd, tool_name, run_on_compile = exec_mock.call_args[0]
        self.assertEqual(cmd, [c.KOTLINC_PATH, str(Path.cwd() / 'example.kt'), '-include-runtime', '-d', 'build/example.jar'])
        self.assertEqual(run_cmd, [c.JAVA_PATH, '-jar', 'build/example.jar'])
        self.assertEqual(tool_name, 'kotlinc')
        self.assertTrue(run_on_compile)

    def test_sql_dispatch_uses_sql_executor(self) -> None:
        args = SimpleNamespace()

        with patch('mahkrab.func.run.sqlexec.Executor.exec') as exec_mock:
            run.run('example.sql', 'build/example', args, False)

        exec_mock.assert_called_once()
        call_args = exec_mock.call_args[0]
        self.assertTrue(call_args[0].endswith('/example.sql'))
        self.assertEqual(call_args[1:], ('build/example', args))

    def test_interpreted_dispatch_uses_interpreter_executor(self) -> None:
        args = SimpleNamespace()

        with patch('mahkrab.func.run.interpexec.Executor.exec') as exec_mock:
            run.run('example.r', 'build/example', args, False)

        exec_mock.assert_called_once()
        run_cmd, tool_name, passed_args = exec_mock.call_args[0]
        self.assertEqual(run_cmd, [c.RSCRIPT_PATH, str(Path.cwd() / 'example.r')])
        self.assertEqual(tool_name, 'Rscript')
        self.assertIs(passed_args, args)

if __name__ == '__main__':
    unittest.main()
