# MahkrabCLI

MahkrabCLI installs the `mk` command: a lightweight source-file runner and
compile-and-run helper for small files and small projects.

It gives you one command shape across many languages:

```bash
mk hello.py
mk main.c -r
mk src/app.js
mk run
mk build
mk doctor
```

The goal is to reduce friction when switching between languages without turning
the tool into a full build system.

## Documentation

- [CLI reference](https://github.com/olibark/MahkrabCLI/blob/main/docs/cli-reference.md)
- [Configuration guide](https://github.com/olibark/MahkrabCLI/blob/main/docs/configuration.md)

These links use GitHub URLs so they remain useful when this README is rendered
on PyPI.

## Installation

Install from PyPI:

```bash
pip install mahkrab
```

Or install as an isolated CLI with `pipx`:

```bash
pipx install mahkrab
```

Check the installation:

```bash
mk --version
mk --help
```

## Quick Start

Run a source file directly:

```bash
mk hello.py
mk src/app.js
mk main.c -r
mk hello
```

For compiled languages, `-r` / `--run-on-compile` compiles and then runs the
result. Interpreted files run directly, so this option has no practical effect
there. Targets with no extension, such as `hello`, are treated as runnable
binaries.

Create a project config when you want repeatable commands:

```toml
entry = "src/main.c"
build_dir = "build"
run_on_compile = true
```

Save that as `.mkconfig.toml`, then run:

```bash
mk run
mk build
```

`mk run` reads the configured `entry` and runs it. `mk build` reads the same
entry and compiles it without running the output.

## Command Forms

| Command | Purpose |
| --- | --- |
| `mk <file>` | Run, interpret, compile, or execute a direct target. |
| `mk run` | Run the configured `entry` from `.mkconfig.toml` or `.mkconfig`. |
| `mk build` | Compile the configured `entry` without running it. |
| `mk doctor` | Diagnose compiler and interpreter availability. |

The bare names `run`, `build`, and `doctor` are reserved subcommands. If you
have files with those exact names, use an explicit path:

```bash
mk ./run
mk ./build
mk ./doctor
```

## Common Options

| Option | Purpose |
| --- | --- |
| `--config <file>` | Use a specific config file. If a directory is given, `mk` looks for `.mkconfig.toml` inside it. |
| `--cwd <dir>` | Run as if `mk` started from another working directory. |
| `-o`, `--output <file>` | Set the compiled output path or name. |
| `--build-dir <dir>` | Set the build output directory. Defaults to `build`. |
| `--python <python>` | Override the Python interpreter for Python files. |
| `--lang <language>` | Force a language handler instead of using the file extension. |
| `--tool <tool>` | Override the compiler or interpreter executable for the selected handler. |
| `--compile-args ...` | Pass extra arguments to the compiler or interpreter. |
| `--tool-args ...` | Alias for `--compile-args`. |
| `--program-args ...` | Pass arguments to the script or compiled program. |
| `-e`, `--explain` | Print the resolved execution plan before running. |
| `-r`, `--run-on-compile` | Compile then run compiled languages. |
| `-c`, `--clear` | Clear the terminal before running the action. |
| `-h`, `--help` | Show command help. |
| `-v`, `--version` | Show the installed version. |

Examples:

```bash
mk main.cpp --build-dir out -o out/main -r
mk script.py --python python3.12
mk README.md --lang python --tool python3.12 --explain
mk app.go --compile-args "-trimpath" -r
mk main.c -r --program-args -- hello world
mk run --cwd ./examples
mk build --config ./examples/.mkconfig.toml
```

See the [CLI reference](https://github.com/olibark/MahkrabCLI/blob/main/docs/cli-reference.md)
for the full command and option reference.

## Config Files

`mk run`, `mk build`, and `mk doctor` can read TOML config from:

- `.mkconfig/.mkconfig.toml`
- `.mkconfig.toml`
- `.mkconfig`

Example:

```toml
entry = "src/main.py"
cwd = "."
build_dir = "build"
output = "build/main"
python = "python3"
lang = "python"
tool = "python3.12"
run_on_compile = true
clear = false
compile_args = ["-O"]
program_args = ["hello", "world"]

[doctor]
quiet = false
verbose = false

[env]
MY_VAR = "value"
```

Important rules:

- `entry` is required for `mk run` and `mk build`.
- Config files are TOML, including `.mkconfig`.
- Relative config paths are resolved from the config file location.
- CLI options take precedence over config values where both are available.
- `mk run` always runs after compilation.
- `mk build` always compiles only.

See the [configuration guide](https://github.com/olibark/MahkrabCLI/blob/main/docs/configuration.md)
for discovery rules, key-by-key reference, and precedence details.

## Passing Arguments

Use `--compile-args` for flags that belong to the compiler or interpreter:

```bash
mk main.c -r --compile-args "-O2 -Wall"
mk script.py --compile-args "-X utf8"
```

Use `--program-args` for values that belong to your program:

```bash
mk main.c -r --program-args -- hello world
mk script.py --program-args -- --name Ada
```

A bare `--` also forwards the rest of the command line as program arguments:

```bash
mk main.c -r -- hello world
```

## Doctor

`mk doctor` checks whether external tools are available on `PATH` or through
configured overrides. It needs a configured `entry`, a direct target, `--lang`,
or `--all`.

```bash
mk doctor
mk doctor src/main.py
mk doctor --lang python,c,cpp
mk doctor --all
mk doctor --quiet
mk doctor --verbose
mk doctor --languages
```

Doctor exits with:

- `0` when all checked toolchains are available.
- `1` when one or more checked toolchains are missing.
- `2` for usage or configuration errors.

## Supported Languages

Language support is extension-driven and depends on the relevant external
compiler or interpreter being installed.

Current handlers include Python, C, C++, Java, C#, JavaScript, TypeScript,
Visual Basic, SQL, R, Pascal, Perl, Scratch, Fortran, Rust, MATLAB, Go,
Assembly, PHP, Ada, Swift, Prolog, Kotlin, Classic Visual Basic, COBOL, Dart,
Ruby, Lua, Bash, PowerShell, and extensionless binaries.

Use `mk doctor --languages` to list the language names and aliases accepted by
doctor checks. The full extension and alias reference is in the
[CLI reference](https://github.com/olibark/MahkrabCLI/blob/main/docs/cli-reference.md).

## External Tools

MahkrabCLI does not bundle compilers or interpreters. By default, command names
come from `PATH`, such as `gcc`, `python`, `node`, or `javac`.

Tool commands can also be overridden with environment variables:

```bash
export MAHKRAB_GCC=/usr/bin/gcc-14
export MAHKRAB_PYTHON=/usr/bin/python3.12
export MAHKRAB_NODE=/usr/bin/node
```

Common overrides include:

- `MAHKRAB_GCC`, `MAHKRAB_GPP`, `MAHKRAB_RUSTC`, `MAHKRAB_GO`
- `MAHKRAB_JAVAC`, `MAHKRAB_JAVA`
- `MAHKRAB_PYTHON`, `MAHKRAB_NODE`, `MAHKRAB_TS`
- `MAHKRAB_SQLITE3`, `MAHKRAB_NASM`, `MAHKRAB_AS`, `MAHKRAB_LD`

## Current Limitations

- MahkrabCLI is focused on convenience for standalone files and small projects.
- Behavior depends on external tools being installed and available.
- C/C++ dependency flag support is limited.
- Assembly support currently targets Unix-like systems for NASM and GAS.

## Development

Use the `dev` virtual environment in this repository:

```bash
python3 -m venv dev
. dev/bin/activate
python -m pip install -U pip
python -m pip install -e '.[dev]'
mk -h
pytest tests
```

### Internal Layout

- `src/mahkrab/cli.py`: CLI entry point.
- `src/mahkrab/tools/parser.py`: command-line parsing.
- `src/mahkrab/tools/config.py`: config parsing and runtime settings.
- `src/mahkrab/func/workflow.py`: top-level run and build workflow.
- `src/mahkrab/func/plans.py`: execution-plan creation and `--explain` output.
- `src/mahkrab/func/commands.py`: command construction.
- `src/mahkrab/func/languages.py`: language aliases, labels, and extension mapping.

## Contributing

Issues and pull requests are welcome.
