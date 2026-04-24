import os
import tempfile
import textwrap
import unittest
from pathlib import Path

from mahkrab.tools import config, parser


class Chdir:
    def __init__(self, target: str) -> None:
        self.target = target
        self.original = os.getcwd()

    def __enter__(self) -> None:
        os.chdir(self.target)

    def __exit__(self, exc_type, exc, tb) -> None:
        os.chdir(self.original)


class TestParserAndConfig(unittest.TestCase):
    def test_parser_supports_run_command_and_quoted_program_args(self) -> None:
        args = parser.parse_args(['run', '--program-args', '-O3 -Wall'])

        self.assertEqual(args.command, 'run')
        self.assertIsNone(args.targetfile)
        self.assertEqual(args.programArgs, ['-O3', '-Wall'])

    def test_parser_target_and_run_on_compile_flag(self) -> None:
        args = parser.parse_args(['hello.c', '-r'])

        self.assertEqual(args.targetfile, 'hello.c')
        self.assertIsNone(args.command)
        self.assertTrue(args.runOnCompile)

    def test_build_settings_uses_mkconfig_directory_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tempDir:
            projectDir = Path(tempDir) / 'project'
            configDir = projectDir / '.mkconfig'
            sourceDir = projectDir / 'src'
            configDir.mkdir(parents=True)
            sourceDir.mkdir(parents=True)
            (sourceDir / 'main.c').write_text('int main(){return 0;}\n', encoding='utf-8')

            (configDir / '.mkconfig.toml').write_text(
                textwrap.dedent(
                    """
                    entry = "src/main.c"
                    python = "python3.12"
                    clear = true
                    run_on_compile = false
                    program_args = ["-O3"]
                    """
                ).strip()
                + '\n',
                encoding='utf-8',
            )

            with Chdir(str(projectDir)):
                args = parser.parse_args(['run'])
                settings = config.buildSettings(args)

            self.assertTrue(settings.runOnCompile)
            self.assertTrue(settings.clear)
            self.assertEqual(settings.pythonCmd, 'python3.12')
            self.assertTrue(settings.targetfile.endswith('/src/main.c'))
            self.assertEqual(settings.programArgs, ['-O3'])

    def test_build_command_uses_entry_without_run_on_compile(self) -> None:
        with tempfile.TemporaryDirectory() as tempDir:
            projectDir = Path(tempDir) / 'project'
            configDir = projectDir / '.mkconfig'
            sourceDir = projectDir / 'src'
            configDir.mkdir(parents=True)
            sourceDir.mkdir(parents=True)
            (sourceDir / 'main.c').write_text('int main(){return 0;}\n', encoding='utf-8')

            (configDir / '.mkconfig.toml').write_text(
                'entry = "src/main.c"\nrun_on_compile = true\n',
                encoding='utf-8',
            )

            with Chdir(str(projectDir)):
                args = parser.parse_args(['build'])
                settings = config.buildSettings(args)

            self.assertEqual(settings.command, 'build')
            self.assertFalse(settings.runOnCompile)
            self.assertTrue(settings.targetfile.endswith('/src/main.c'))

    def test_cli_python_override_wins_over_config(self) -> None:
        with tempfile.TemporaryDirectory() as tempDir:
            projectDir = Path(tempDir) / 'project'
            configDir = projectDir / '.mkconfig'
            sourceDir = projectDir / 'src'
            configDir.mkdir(parents=True)
            sourceDir.mkdir(parents=True)
            (sourceDir / 'main.py').write_text('print("ok")\n', encoding='utf-8')

            (configDir / '.mkconfig.toml').write_text(
                'entry = "src/main.py"\npython = "python3.11"\n',
                encoding='utf-8',
            )

            with Chdir(str(projectDir)):
                args = parser.parse_args(['run', '--python', 'python3.13'])
                settings = config.buildSettings(args)

            self.assertEqual(settings.pythonCmd, 'python3.13')

    def test_explicit_target_uses_invocation_directory_when_parent_config_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tempDir:
            projectDir = Path(tempDir) / 'project'
            nestedDir = projectDir / 'tests' / 'cli_cases'
            configDir = projectDir / '.mkconfig'
            configDir.mkdir(parents=True)
            nestedDir.mkdir(parents=True)

            (configDir / '.mkconfig.toml').write_text(
                'entry = "project_entry.py"\n',
                encoding='utf-8',
            )
            (nestedDir / 'hello.py').write_text('print("ok")\n', encoding='utf-8')

            with Chdir(str(nestedDir)):
                args = parser.parse_args(['hello.py'])
                settings = config.buildSettings(args)

            self.assertEqual(settings.cwd, str(nestedDir.resolve()))
            self.assertEqual(settings.targetfile, str((nestedDir / 'hello.py').resolve()))

    def test_direct_target_with_cwd_resolves_target_from_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tempDir:
            projectDir = Path(tempDir) / 'project'
            caseDir = projectDir / 'tests' / 'cli_cases'
            caseDir.mkdir(parents=True)
            (caseDir / 'hello.py').write_text('print("ok")\n', encoding='utf-8')

            with Chdir(str(projectDir)):
                args = parser.parse_args(['--cwd', 'tests/cli_cases', 'hello.py'])
                settings = config.buildSettings(args)

            self.assertEqual(settings.cwd, str(caseDir.resolve()))
            self.assertEqual(settings.targetfile, str((caseDir / 'hello.py').resolve()))

    def test_doctor_options_load_from_config_table(self) -> None:
        with tempfile.TemporaryDirectory() as tempDir:
            projectDir = Path(tempDir) / 'project'
            configDir = projectDir / '.mkconfig'
            configDir.mkdir(parents=True)

            (configDir / '.mkconfig.toml').write_text(
                '[doctor]\nverbose = true\n',
                encoding='utf-8',
            )

            with Chdir(str(projectDir)):
                args = parser.parse_args(['doctor'])
                settings = config.buildSettings(args)

            self.assertFalse(settings.doctorQuiet)
            self.assertTrue(settings.doctorVerbose)
            self.assertEqual(settings.sources['doctorMode'], 'config file')

    def test_doctor_target_os_loads_from_config(self) -> None:
        with tempfile.TemporaryDirectory() as tempDir:
            projectDir = Path(tempDir) / 'project'
            configDir = projectDir / '.mkconfig'
            configDir.mkdir(parents=True)

            (configDir / '.mkconfig.toml').write_text(
                'os = "windows"\n',
                encoding='utf-8',
            )

            with Chdir(str(projectDir)):
                args = parser.parse_args(['doctor', '--all'])
                settings = config.buildSettings(args)

            self.assertEqual(settings.targetOs, 'windows')
            self.assertEqual(settings.sources['targetOs'], 'config file')

    def test_doctor_cli_options_win_over_config(self) -> None:
        with tempfile.TemporaryDirectory() as tempDir:
            projectDir = Path(tempDir) / 'project'
            configDir = projectDir / '.mkconfig'
            configDir.mkdir(parents=True)

            (configDir / '.mkconfig.toml').write_text(
                'doctor_verbose = true\n',
                encoding='utf-8',
            )

            with Chdir(str(projectDir)):
                args = parser.parse_args(['doctor', '--quiet'])
                settings = config.buildSettings(args)

            self.assertTrue(settings.doctorQuiet)
            self.assertFalse(settings.doctorVerbose)
            self.assertEqual(settings.sources['doctorMode'], 'CLI option --quiet')

    def test_doctor_cli_os_wins_over_config(self) -> None:
        with tempfile.TemporaryDirectory() as tempDir:
            projectDir = Path(tempDir) / 'project'
            configDir = projectDir / '.mkconfig'
            configDir.mkdir(parents=True)

            (configDir / '.mkconfig.toml').write_text(
                'os = "linux"\n',
                encoding='utf-8',
            )

            with Chdir(str(projectDir)):
                args = parser.parse_args(['doctor', '--all', '--os', 'macos'])
                settings = config.buildSettings(args)

            self.assertEqual(settings.targetOs, 'macos')
            self.assertEqual(settings.sources['targetOs'], 'CLI option --os')

    def test_doctor_uses_configured_entry_as_target_context(self) -> None:
        with tempfile.TemporaryDirectory() as tempDir:
            projectDir = Path(tempDir) / 'project'
            configDir = projectDir / '.mkconfig'
            sourceDir = projectDir / 'src'
            configDir.mkdir(parents=True)
            sourceDir.mkdir(parents=True)

            (configDir / '.mkconfig.toml').write_text(
                'entry = "src/main.py"\n',
                encoding='utf-8',
            )

            with Chdir(str(projectDir)):
                args = parser.parse_args(['doctor'])
                settings = config.buildSettings(args)

            self.assertEqual(settings.command, 'doctor')
            self.assertTrue(settings.targetfile.endswith('/src/main.py'))

    def test_doctor_direct_target_uses_invocation_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tempDir:
            projectDir = Path(tempDir) / 'project'
            configDir = projectDir / '.mkconfig'
            configDir.mkdir(parents=True)

            (configDir / '.mkconfig.toml').write_text(
                'entry = "src/main.c"\n',
                encoding='utf-8',
            )

            with Chdir(str(projectDir)):
                args = parser.parse_args(['doctor', 'script.py'])
                settings = config.buildSettings(args)

            self.assertEqual(settings.targetfile, str((projectDir / 'script.py').resolve()))


if __name__ == '__main__':
    unittest.main()
