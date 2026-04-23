from __future__ import annotations

import json
import re
from types import SimpleNamespace

from mahkrab.func import doctor

ANSI_PATTERN = re.compile(r'\x1b\[[0-9;]*m')


def make_args(**overrides):
    defaults = {
        'lang': None,
        'targetOs': 'linux',
        'tool': None,
        'compileArgs': [],
        'programArgs': [],
        'buildDir': 'build',
        'targetfile': None,
        'pythonCmd': 'python3',
        'runOnCompile': False,
        'configPath': None,
        'explain': False,
        'sources': {'pythonCmd': 'default', 'targetOs': 'detected host OS'},
        'doctorQuiet': False,
        'doctorVerbose': False,
        'doctorJson': False,
        'doctorAll': True,
        'doctorLanguages': False,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def clean_output(output: str) -> str:
    return ANSI_PATTERN.sub('', output)


def test_doctor_returns_success_when_all_checked_languages_are_available(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        doctor,
        'LANGUAGE_TARGETS',
        (
            doctor.DiagnosticTarget('python', 'doctor.py'),
            doctor.DiagnosticTarget('c', 'doctor.c'),
        ),
    )
    monkeypatch.setattr(doctor.shutil, 'which', lambda command: f'/usr/bin/{command}')

    assert doctor.run(make_args()) == 0

    raw_output = capsys.readouterr().out
    output = clean_output(raw_output)
    assert doctor.c.Colours.MAGENTA in raw_output
    assert doctor.c.Colours.GREEN in raw_output
    assert '[MAHKRAB-CLI] Doctor' in output
    assert 'doctor mode: default (default)' in output
    assert 'hint os: linux (detected host OS)' in output
    assert 'Python: ok' in output
    assert 'C: ok' in output
    assert 'available=yes' in output
    assert 'All supported languages are runnable.' in output


def test_doctor_returns_failure_and_lists_missing_languages(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        doctor,
        'LANGUAGE_TARGETS',
        (
            doctor.DiagnosticTarget('python', 'doctor.py'),
            doctor.DiagnosticTarget('c', 'doctor.c'),
        ),
    )

    def which(command: str) -> str | None:
        if command == 'gcc':
            return None

        return f'/usr/bin/{command}'

    monkeypatch.setattr(doctor.shutil, 'which', which)

    assert doctor.run(make_args()) == 1

    raw_output = capsys.readouterr().out
    output = clean_output(raw_output)
    assert doctor.c.Colours.RED in raw_output
    assert 'C: missing' in output
    assert 'gcc: value=gcc source=default available=no path=-' in output
    assert 'Missing tools:' in output
    assert 'install (linux)=sudo apt install build-essential' in output
    assert 'Unavailable languages: C' in output


def test_doctor_reports_cli_python_override_source(monkeypatch, capsys) -> None:
    monkeypatch.setattr(doctor, 'LANGUAGE_TARGETS', (doctor.DiagnosticTarget('python', 'doctor.py'),))
    monkeypatch.setattr(doctor.shutil, 'which', lambda command: f'/usr/bin/{command}')

    args = make_args(
        pythonCmd='python3.13',
        sources={'pythonCmd': 'CLI option --python'},
    )

    assert doctor.run(args) == 0

    output = clean_output(capsys.readouterr().out)
    assert 'python: value=python3.13 source=CLI option --python available=yes path=/usr/bin/python3.13' in output


def test_doctor_reports_config_tool_override_source(monkeypatch, capsys) -> None:
    monkeypatch.setattr(doctor, 'LANGUAGE_TARGETS', (doctor.DiagnosticTarget('c', 'doctor.c'),))
    monkeypatch.setattr(doctor.shutil, 'which', lambda command: f'/usr/bin/{command}')

    args = make_args(
        tool='clang -Weverything',
        sources={'tool': 'config file', 'pythonCmd': 'default'},
    )

    assert doctor.run(args) == 0

    output = clean_output(capsys.readouterr().out)
    assert 'gcc: value=clang -Weverything source=config file available=yes path=/usr/bin/clang' in output


def test_doctor_reports_environment_override_source(monkeypatch, capsys) -> None:
    monkeypatch.setattr(doctor, 'LANGUAGE_TARGETS', (doctor.DiagnosticTarget('c', 'doctor.c'),))
    monkeypatch.setattr(doctor.c, 'GCC_PATH', '/opt/toolchains/gcc-14')
    monkeypatch.setenv('MAHKRAB_GCC', '/opt/toolchains/gcc-14')
    monkeypatch.setattr(doctor.shutil, 'which', lambda command: command)

    assert doctor.run(make_args()) == 0

    output = clean_output(capsys.readouterr().out)
    assert (
        'gcc: value=/opt/toolchains/gcc-14 '
        'source=environment variable MAHKRAB_GCC available=yes path=/opt/toolchains/gcc-14'
    ) in output


def test_doctor_reports_assembly_variant_commands(monkeypatch, capsys) -> None:
    monkeypatch.setattr(doctor, 'LANGUAGE_TARGETS', (doctor.DiagnosticTarget('assembly_nasm', 'doctor.asm'),))
    monkeypatch.setattr(doctor.c, 'osName', 'unixlike')
    monkeypatch.setattr(doctor.c, 'NASM_PATH', 'nasm')
    monkeypatch.setattr(doctor.c, 'LD_PATH', 'ld')
    monkeypatch.setattr(doctor.shutil, 'which', lambda command: f'/usr/bin/{command}')

    assert doctor.run(make_args()) == 0

    output = clean_output(capsys.readouterr().out)
    assert 'Assembly (NASM): ok' in output
    assert 'nasm: value=nasm source=default available=yes path=/usr/bin/nasm' in output
    assert 'ld: value=ld source=default available=yes path=/usr/bin/ld' in output


def test_doctor_quiet_only_prints_summary(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        doctor,
        'LANGUAGE_TARGETS',
        (
            doctor.DiagnosticTarget('python', 'doctor.py'),
            doctor.DiagnosticTarget('c', 'doctor.c'),
        ),
    )
    monkeypatch.setattr(doctor.shutil, 'which', lambda command: None if command == 'gcc' else f'/usr/bin/{command}')

    assert doctor.run(make_args(doctorQuiet=True, sources={'doctorMode': 'CLI option --quiet'})) == 1

    output = clean_output(capsys.readouterr().out)
    assert 'Unavailable languages: C' in output
    assert '[MAHKRAB-CLI] Doctor' not in output
    assert 'Python: ok' not in output
    assert 'gcc: value=' not in output
    assert 'Missing tools:' in output
    assert 'install (linux)=sudo apt install build-essential' in output


def test_doctor_verbose_prints_generated_commands(monkeypatch, capsys) -> None:
    monkeypatch.setattr(doctor, 'LANGUAGE_TARGETS', (doctor.DiagnosticTarget('c', 'doctor.c'),))
    monkeypatch.setattr(doctor.shutil, 'which', lambda command: f'/usr/bin/{command}')

    assert doctor.run(make_args(doctorVerbose=True, sources={'doctorMode': 'CLI option --verbose'})) == 0

    output = clean_output(capsys.readouterr().out)
    assert 'doctor mode: verbose (CLI option --verbose)' in output
    assert 'mode: compile+run' in output
    assert 'compile command: gcc ' in output
    assert 'run command: ./build/doctor' in output


def test_doctor_defaults_to_target_language(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        doctor,
        'LANGUAGE_TARGETS',
        (
            doctor.DiagnosticTarget('python', 'doctor.py'),
            doctor.DiagnosticTarget('c', 'doctor.c'),
        ),
    )

    monkeypatch.setattr(doctor.shutil, 'which', lambda command: None if command == 'gcc' else f'/usr/bin/{command}')

    args = make_args(doctorAll=False, targetfile='/tmp/project/main.py')

    assert doctor.run(args) == 0

    output = clean_output(capsys.readouterr().out)
    assert 'Python: ok' in output
    assert 'C: missing' not in output
    assert 'All checked languages are runnable.' in output


def test_doctor_quiet_defaults_to_target_language(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        doctor,
        'LANGUAGE_TARGETS',
        (
            doctor.DiagnosticTarget('python', 'doctor.py'),
            doctor.DiagnosticTarget('c', 'doctor.c'),
        ),
    )

    monkeypatch.setattr(doctor.shutil, 'which', lambda command: None if command == 'gcc' else f'/usr/bin/{command}')

    args = make_args(doctorAll=False, doctorQuiet=True, targetfile='/tmp/project/main.py')

    assert doctor.run(args) == 0

    output = clean_output(capsys.readouterr().out)
    assert 'All checked languages are runnable.' in output
    assert 'Unavailable' not in output


def test_doctor_lang_checks_selected_languages(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        doctor,
        'LANGUAGE_TARGETS',
        (
            doctor.DiagnosticTarget('python', 'doctor.py'),
            doctor.DiagnosticTarget('c', 'doctor.c'),
            doctor.DiagnosticTarget('cpp', 'doctor.cpp'),
        ),
    )
    monkeypatch.setattr(doctor.shutil, 'which', lambda command: f'/usr/bin/{command}')

    args = make_args(doctorAll=False, lang='py,c++')

    assert doctor.run(args) == 0

    output = clean_output(capsys.readouterr().out)
    assert 'Python: ok' in output
    assert 'C++: ok' in output
    assert 'C: ok' not in output


def test_doctor_generic_assembly_lang_uses_target_extension(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        doctor,
        'LANGUAGE_TARGETS',
        (
            doctor.DiagnosticTarget('assembly_nasm', 'doctor.asm'),
            doctor.DiagnosticTarget('assembly_gas', 'doctor.s'),
        ),
    )
    monkeypatch.setattr(doctor.c, 'osName', 'unixlike')
    monkeypatch.setattr(doctor.shutil, 'which', lambda command: f'/usr/bin/{command}')

    args = make_args(doctorAll=False, lang='asm', targetfile='/tmp/project/hello.s')

    assert doctor.run(args) == 0

    output = clean_output(capsys.readouterr().out)
    assert 'Assembly (GNU assembler): ok' in output
    assert 'Assembly (NASM): ok' not in output


def test_doctor_lang_rejects_unsupported_language(capsys) -> None:
    args = make_args(doctorAll=False, lang='python,brainfuck')

    assert doctor.run(args) == 2

    raw_output = capsys.readouterr().out
    output = clean_output(raw_output)
    assert doctor.c.Colours.RED in raw_output
    assert 'Unsupported doctor language: brainfuck' in output


def test_doctor_without_target_lang_or_all_returns_usage_error(capsys) -> None:
    args = make_args(doctorAll=False)

    assert doctor.run(args) == 2

    output = clean_output(capsys.readouterr().out)
    assert 'Doctor needs a target, --lang, or --all.' in output


def test_doctor_languages_lists_supported_aliases(capsys) -> None:
    args = make_args(doctorAll=False, doctorLanguages=True)

    assert doctor.run(args) == 0

    raw_output = capsys.readouterr().out
    output = clean_output(raw_output)
    assert doctor.c.Colours.MAGENTA in raw_output
    assert '[MAHKRAB-CLI] Doctor languages' in output
    assert 'Python: python, py' in output
    assert 'C++: cpp, c++, cxx, cc' in output
    assert 'Assembly (NASM): nasm, assembly, asm' in output


def test_doctor_json_emits_valid_json_without_ansi(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        doctor,
        'LANGUAGE_TARGETS',
        (
            doctor.DiagnosticTarget('python', 'doctor.py'),
            doctor.DiagnosticTarget('c', 'doctor.c'),
        ),
    )
    monkeypatch.setattr(doctor.shutil, 'which', lambda command: None if command == 'gcc' else f'/usr/bin/{command}')

    assert doctor.run(make_args(doctorJson=True)) == 1

    raw_output = capsys.readouterr().out
    assert ANSI_PATTERN.search(raw_output) is None
    payload = json.loads(raw_output)
    assert payload['ok'] is False
    assert payload['os'] == 'linux'
    assert payload['detected_os'] == 'linux'
    assert payload['os_source'] == 'detected host OS'
    assert payload['checked_languages'] == ['python', 'c']

    tools = {tool['tool']: tool for tool in payload['checked_tools']}
    assert tools['python']['status'] == 'installed'
    assert tools['python']['resolved_path'] == '/usr/bin/python3'
    assert tools['gcc']['status'] == 'missing'
    assert tools['gcc']['languages'] == ['c']
    assert tools['gcc']['recommended_hint'] == 'sudo apt install build-essential'
    assert tools['gcc']['install_hints'] == {'linux': ['sudo apt install build-essential']}


def test_doctor_json_reports_installed_tool_state(monkeypatch, capsys) -> None:
    monkeypatch.setattr(doctor, 'LANGUAGE_TARGETS', (doctor.DiagnosticTarget('python', 'doctor.py'),))
    monkeypatch.setattr(doctor.shutil, 'which', lambda command: f'/usr/bin/{command}')

    assert doctor.run(make_args(doctorJson=True)) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload['ok'] is True
    assert payload['checked_tools'] == [
        {
            'command': 'python3',
            'install_hints': {
                'linux': ['sudo apt install python3'],
            },
            'languages': ['python'],
            'recommended_hint': None,
            'resolved_path': '/usr/bin/python3',
            'source': 'default',
            'status': 'installed',
            'tool': 'python',
            'value': 'python3',
        }
    ]


def test_doctor_json_uses_os_specific_recommended_hint(monkeypatch, capsys) -> None:
    monkeypatch.setattr(doctor, 'LANGUAGE_TARGETS', (doctor.DiagnosticTarget('c', 'doctor.c'),))
    monkeypatch.setattr(doctor.shutil, 'which', lambda command: None)

    assert doctor.run(make_args(doctorJson=True, targetOs='macos', sources={'pythonCmd': 'default', 'targetOs': 'CLI option --os'})) == 1

    payload = json.loads(capsys.readouterr().out)
    assert payload['os'] == 'macos'
    assert payload['os_source'] == 'CLI option --os'
    assert payload['checked_tools'][0]['recommended_hint'] == 'xcode-select --install'
    assert payload['checked_tools'][0]['install_hints'] == {'macos': ['xcode-select --install']}


def test_doctor_json_usage_error_stays_json(monkeypatch, capsys) -> None:
    assert doctor.run(make_args(doctorAll=False, doctorJson=True)) == 2

    raw_output = capsys.readouterr().out
    assert ANSI_PATTERN.search(raw_output) is None
    payload = json.loads(raw_output)
    assert payload['ok'] is False
    assert payload['error'] == 'Doctor needs a target, --lang, or --all.'
    assert payload['checked_tools'] == []


def test_doctor_json_wins_over_quiet_and_lang_selection(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        doctor,
        'LANGUAGE_TARGETS',
        (
            doctor.DiagnosticTarget('python', 'doctor.py'),
            doctor.DiagnosticTarget('c', 'doctor.c'),
        ),
    )
    monkeypatch.setattr(doctor.shutil, 'which', lambda command: f'/usr/bin/{command}')

    args = make_args(doctorAll=False, doctorJson=True, doctorQuiet=True, lang='py')

    assert doctor.run(args) == 0

    raw_output = capsys.readouterr().out
    payload = json.loads(raw_output)
    assert payload['checked_languages'] == ['python']
    assert 'All checked languages are runnable.' not in raw_output
    assert '[MAHKRAB-CLI]' not in raw_output


def test_doctor_uses_detected_host_os_when_no_config_or_override(monkeypatch, capsys) -> None:
    monkeypatch.setattr(doctor, 'LANGUAGE_TARGETS', (doctor.DiagnosticTarget('c', 'doctor.c'),))
    monkeypatch.setattr(doctor, 'detectHostOs', lambda: 'windows')
    monkeypatch.setattr(doctor.shutil, 'which', lambda command: None)

    assert doctor.run(make_args(targetOs=None, doctorJson=True, sources={'pythonCmd': 'default'})) == 1

    payload = json.loads(capsys.readouterr().out)
    assert payload['os'] == 'windows'
    assert payload['detected_os'] == 'windows'
    assert payload['os_source'] == 'detected host OS'
    assert payload['checked_tools'][0]['recommended_hint'].startswith('Install MSYS2')
