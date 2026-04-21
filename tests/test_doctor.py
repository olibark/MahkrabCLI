from __future__ import annotations

import re
from types import SimpleNamespace

from mahkrab.func import doctor

ANSI_PATTERN = re.compile(r'\x1b\[[0-9;]*m')


def make_args(**overrides):
    defaults = {
        'lang': None,
        'tool': None,
        'compileArgs': [],
        'programArgs': [],
        'buildDir': 'build',
        'pythonCmd': 'python3',
        'runOnCompile': False,
        'configPath': None,
        'explain': False,
        'sources': {'pythonCmd': 'default'},
        'doctorQuiet': False,
        'doctorVerbose': False,
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


def test_doctor_verbose_prints_generated_commands(monkeypatch, capsys) -> None:
    monkeypatch.setattr(doctor, 'LANGUAGE_TARGETS', (doctor.DiagnosticTarget('c', 'doctor.c'),))
    monkeypatch.setattr(doctor.shutil, 'which', lambda command: f'/usr/bin/{command}')

    assert doctor.run(make_args(doctorVerbose=True, sources={'doctorMode': 'CLI option --verbose'})) == 0

    output = clean_output(capsys.readouterr().out)
    assert 'doctor mode: verbose (CLI option --verbose)' in output
    assert 'mode: compile+run' in output
    assert 'compile command: gcc ' in output
    assert 'run command: ./build/doctor' in output
