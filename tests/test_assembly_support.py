from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

from mahkrab.func import languages, plans
from mahkrab.func.executors.compiled import asmexec


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
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest.fixture
def assembly_tools(monkeypatch):
    monkeypatch.setattr(asmexec.c, 'NASM_PATH', 'nasm')
    monkeypatch.setattr(asmexec.c, 'AS_PATH', 'as')
    monkeypatch.setattr(asmexec.c, 'GCC_PATH', 'gcc')
    monkeypatch.setattr(asmexec.c, 'LD_PATH', 'ld')
    monkeypatch.setattr(asmexec.c, 'osName', 'unixlike')


@pytest.mark.parametrize(
    ('filename', 'expected'),
    [
        ('hello.asm', 'assembly_nasm'),
        ('hello.nasm', 'assembly_nasm'),
        ('hello.s', 'assembly_gas'),
        ('hello.S', 'assembly_gas'),
    ],
)
def test_assembly_extensions_resolve_to_expected_variant(
    assembly_tools,
    filename: str,
    expected: str,
) -> None:
    args = make_args()
    plan = plans.build_execution_plan(filename, None, args, False)

    assert plan is not None
    assert plan['language_key'] == expected


@pytest.mark.parametrize(
    ('alias', 'expected'),
    [
        ('assembly', 'assembly'),
        ('asm', 'assembly'),
        ('nasm', 'assembly_nasm'),
        ('gas', 'assembly_gas'),
        ('gnu-asm', 'assembly_gas'),
    ],
)
def test_assembly_language_aliases_normalize(alias: str, expected: str) -> None:
    assert languages.normalize_language(alias) == expected


def test_nasm_plan_includes_compile_link_and_run_commands(assembly_tools, capsys) -> None:
    args = make_args(compileArgs=['-g'], programArgs=['hello'], runOnCompile=True)
    plan = plans.build_execution_plan('hello.asm', None, args, True)

    assert plan is not None
    assert plan['language_key'] == 'assembly_nasm'
    assert plan['compile_cmd'] == [
        'nasm',
        '-g',
        '-f',
        'elf64',
        os.path.abspath('hello.asm'),
        '-o',
        'build/hello.o',
    ]
    assert plan['link_cmd'] == ['ld', '-o', 'build/hello', 'build/hello.o']
    assert plan['run_cmd'] == ['./build/hello', 'hello']

    plans.print_explain(args, plan)
    output = capsys.readouterr().out

    assert 'language: Assembly (NASM) (extension)' in output
    assert 'compile command: nasm -g -f elf64' in output
    assert 'link command: ld -o build/hello build/hello.o' in output
    assert "run command: ./build/hello hello" in output


def test_gas_plan_uses_gcc_driver_for_preprocessed_sources(assembly_tools, capsys) -> None:
    args = make_args(compileArgs=['-Iinclude'], programArgs=['arg1'], runOnCompile=True)
    plan = plans.build_execution_plan('hello.S', None, args, True)

    assert plan is not None
    assert plan['language_key'] == 'assembly_gas'
    assert plan['compile_cmd'] == [
        'gcc',
        '-Iinclude',
        '-c',
        os.path.abspath('hello.S'),
        '-o',
        'build/hello.o',
    ]
    assert plan['link_cmd'] == ['ld', '-o', 'build/hello', 'build/hello.o']
    assert plan['run_cmd'] == ['./build/hello', 'arg1']

    plans.print_explain(args, plan)
    output = capsys.readouterr().out

    assert 'language: Assembly (GNU assembler) (extension)' in output
    assert 'compile command: gcc -Iinclude -c' in output
    assert 'link command: ld -o build/hello build/hello.o' in output


def test_gas_language_override_forces_gas_plan_on_asm_file(assembly_tools) -> None:
    args = make_args(lang='gas')
    plan = plans.build_execution_plan('hello.asm', None, args, False)

    assert plan is not None
    assert plan['language_key'] == 'assembly_gas'
    assert plan['language_source'] == 'override'
    assert plan['compile_cmd'] == [
        'as',
        '--64',
        os.path.abspath('hello.asm'),
        '-o',
        'build/hello.o',
    ]


def test_gas_plan_reports_platform_restriction(monkeypatch, capsys) -> None:
    monkeypatch.setattr(asmexec.c, 'osName', 'windows')

    args = make_args()
    plan = plans.build_execution_plan('hello.s', None, args, False)

    assert plan is None
    assert 'Assembly (GNU assembler) is not supported on windows.' in capsys.readouterr().out


def test_nasm_plan_reports_platform_restriction(monkeypatch, capsys) -> None:
    monkeypatch.setattr(asmexec.c, 'osName', 'windows')

    args = make_args()
    plan = plans.build_execution_plan('hello.asm', None, args, False)

    assert plan is None
    assert 'Assembly (NASM) is not supported on windows.' in capsys.readouterr().out


def test_nasm_executor_builds_compile_link_and_run_commands(assembly_tools, monkeypatch) -> None:
    calls = {}

    def fake_run_on_compile(compile_cmd: list[str], link_cmd: list[str], run_cmd: list[str]) -> None:
        calls['compile_cmd'] = compile_cmd
        calls['link_cmd'] = link_cmd
        calls['run_cmd'] = run_cmd

    monkeypatch.setattr(asmexec.Executor, 'runOnCompile', staticmethod(fake_run_on_compile))

    args = make_args(
        lang='nasm',
        resolvedLanguage='assembly_nasm',
        compileArgs=['-g'],
        programArgs=['hello'],
    )
    asmexec.Executor.exec('/tmp/hello.asm', 'build/hello', args, True)

    assert calls == {
        'compile_cmd': ['nasm', '-g', '-f', 'elf64', '/tmp/hello.asm', '-o', 'build/hello.o'],
        'link_cmd': ['ld', '-o', 'build/hello', 'build/hello.o'],
        'run_cmd': ['./build/hello', 'hello'],
    }


def test_gas_executor_builds_compile_and_link_commands(assembly_tools, monkeypatch) -> None:
    calls = {}

    def fake_compile(compile_cmd: list[str], link_cmd: list[str]) -> None:
        calls['compile_cmd'] = compile_cmd
        calls['link_cmd'] = link_cmd

    monkeypatch.setattr(asmexec.Executor, 'compile', staticmethod(fake_compile))

    args = make_args(
        lang='gas',
        resolvedLanguage='assembly_gas',
        compileArgs=['-Iinclude'],
    )
    asmexec.Executor.exec('/tmp/hello.S', 'build/hello', args, False)

    assert calls == {
        'compile_cmd': ['gcc', '-Iinclude', '-c', '/tmp/hello.S', '-o', 'build/hello.o'],
        'link_cmd': ['ld', '-o', 'build/hello', 'build/hello.o'],
    }
