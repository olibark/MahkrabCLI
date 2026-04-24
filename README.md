# MahkrabCLI

MahkrabCLI installs the `mk` command: a lightweight source-file runner and
compile-and-run helper for small files and small projects.

It gives you one command shape across many languages:

```bash
mk hello.py
mk main.c -r
mk src/app.js
mk init main.py
mk run
mk build
mk config
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

```bash
mk init src/main.c --lang c --run-on-compile
```

This creates `.mkconfig/mkconfig.toml`:

```toml
entry = "src/main.c"
lang = "c"
os = "linux"
build_dir = "build"
run_on_compile = true
```

Then run:

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
| `mk init [file]` | Create `.mkconfig/mkconfig.toml` for project commands. |
| `mk run` | Run the configured `entry` from a Mahkrab config file. |
| `mk build` | Compile the configured `entry` without running it. |
| `mk config` | Show the resolved config file and read or update supported config keys. |
| `mk doctor` | Diagnose compiler and interpreter availability. |

The bare names `init`, `run`, `build`, `config`, and `doctor` are reserved subcommands. If you
have files with those exact names, use an explicit path:

```bash
mk ./init
mk ./run
mk ./build
mk ./config
mk ./doctor
```

## Common Options

| Option | Purpose |
| --- | --- |
| `--config <file>` | Use a specific config file. If a directory is given, `mk` looks for supported config names inside it. |
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

## Init

Use `mk init` to create a project config at `.mkconfig/mkconfig.toml`.
The generated file is TOML and uses the same keys that `mk run` and `mk build`
read at runtime.

```bash
mk init
mk init main.py
mk init --entry src/main.c --lang c --run-on-compile
mk init --os windows
mk init --build-dir out --output out/app
mk init --force
```

Options:

| Option | Purpose |
| --- | --- |
| `--entry <file>` | Set the configured `entry`. A positional file, such as `mk init main.py`, does the same thing. |
| `--lang <language>` | Write a `lang` override. |
| `--os <os>` | Write `os` for doctor install hints. Supported values: `linux`, `macos`, `windows`. |
| `--build-dir <dir>` | Write `build_dir`. Defaults to `build`. |
| `-o`, `--output <file>` | Write `output`. |
| `-r`, `--run-on-compile` | Write `run_on_compile = true`. |
| `--force` | Overwrite an existing generated config. |

If you do not provide an entry, `mk init` looks for common files such as
`src/main.py`, `main.py`, `src/main.c`, or `main.c`. When it cannot infer one,
it writes a short commented placeholder instead. By default it refuses to
overwrite any discovered Mahkrab config and exits with status `2`.

## Config Files

`mk run`, `mk build`, and `mk doctor` can read TOML config from:

- `.mkconfig/mkconfig.toml`
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
os = "linux"
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

## Config Command

Use `mk config` to inspect the config file Mahkrab resolved and to read or
update supported config keys without opening the TOML file manually. The output
uses the normal coloured Mahkrab conventions.

```bash
mk config
mk config --entry
mk config --entry src/main.c
mk config --run-on-compile true
mk config --compile-args "-O2 -Wall"
mk config --env FOO=bar
```

Getter flags print the current configured value. The same flag becomes a setter
when you pass a value:

- `--entry`
- `--cwd`
- `--build-dir`
- `-o`, `--output`
- `--python`
- `--lang`
- `--tool`
- `-r`, `--run-on-compile`
- `-c`, `--clear`
- `--compile-args`
- `--program-args`

Boolean setters accept `true`, `false`, `1`, or `0`. `--compile-args` and
`--program-args` accept a quoted shell-style string and store the parsed result
as a TOML string array. `--env KEY=VALUE` adds or replaces entries in the
`[env]` table.

If no config exists, `mk config` exits with status `2` and tells you to create
one with `mk init`. Config updates preserve existing keys and rewrite the TOML
file deterministically, but comments and original formatting may be normalized.

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

## Assembly Support

Assembly targets on Unix-like systems now get the same kind of lightweight
dependency help that C already has. Mahkrab scans supported assembly sources
for obvious `extern`, `call`, `include`, and entry-point markers, then adds
common compile or link flags automatically when it can.

This applies to:

- NASM: `.asm`, `.nasm`
- GNU assembler: `.s`, `.S`

Common cases now work without manually remembering linker flags for things such
as C-runtime style `main` entry points, `pthread`, `libm`, SDL2, `curl`,
`sqlite3`, OpenSSL, `libpng`, `uuid`, and X11 symbol usage. Preprocessed GNU
assembler sources (`.S`) also reuse the existing C header-based mapping for
common `#include` cases where that helps.

Examples:

```bash
mk hello.asm -r
mk hello.S --explain
mk math_demo.s -r
```

Manual `--compile-args` still work for custom assembler options or more
advanced toolchain cases:

```bash
mk hello.S --compile-args "-Iinclude -g" -r
```

## Doctor

`mk doctor` checks whether external tools are available on `PATH` or through
configured overrides. It needs a configured `entry`, a direct target, `--lang`,
or `--all`. When something is missing, doctor now prints a short OS-aware
install hint so onboarding is more actionable. Doctor resolves the hint OS in
this order: `--os`, then mkconfig `os`, then the current machine OS.

```bash
mk doctor
mk doctor src/main.py
mk doctor --lang python,c,cpp
mk doctor --all
mk doctor --os windows
mk doctor --quiet
mk doctor --json
mk doctor --verbose
mk doctor --languages
```

Doctor exits with:

- `0` when all checked toolchains are available.
- `1` when one or more checked toolchains are missing.
- `2` for usage or configuration errors.

Normal terminal output keeps the coloured Mahkrab summary and adds a compact
missing-tools section:

```text
[MAHKRAB-CLI] Doctor
  config: /project/.mkconfig/mkconfig.toml
  cwd: /project
  doctor mode: default (default)
  hint os: linux (config file)
  C: missing
    - gcc: value=gcc source=default available=no path=-
  Missing tools:
    - gcc: languages=C install (linux)=sudo apt install build-essential
[MAHKRAB-CLI] - Unavailable checked languages: C
```

Use `mk doctor --json` for scripting, CI, or editor integrations. It prints
JSON only, with no ANSI colour codes or extra text:

```json
{
  "checked_languages": ["python", "c"],
  "checked_tools": [
    {
      "command": "gcc",
      "install_hints": {
        "windows": ["Install MSYS2 or Visual Studio Build Tools and add the compiler bin directory to PATH"]
      },
      "languages": ["c"],
      "recommended_hint": "Install MSYS2 or Visual Studio Build Tools and add the compiler bin directory to PATH",
      "resolved_path": null,
      "source": "default",
      "status": "missing",
      "tool": "gcc",
      "value": "gcc"
    }
  ],
  "detected_os": "linux",
  "ok": false,
  "os": "windows",
  "os_source": "config file"
}
```

`--json` composes with the normal doctor selectors such as `--all`, `--lang`,
and `--os`. If `--json` is combined with human-oriented output flags like
`--quiet`, JSON still wins so the output stays machine-readable.

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
