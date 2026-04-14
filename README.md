# mahkrab

`mahkrab` is a lightweight CLI that installs as `mk`.

It is a cross-language source runner and compile-and-run helper for small files and small projects.

## Why

`mk` gives you one command shape for many languages:

- `mk <file>` to run/interpret or compile a source file by extension
- `mk run` to run the configured entry from `.mkconfig.toml` or `.mkconfig`

The goal is reducing friction when switching between languages.

## Installation

Install from PyPI:

```bash
pip install mahkrab
```

Or with `pipx` (isolated CLI install):

```bash
pipx install mahkrab
```

### 1) Run a file directly

```bash
mk hello.py
mk main.c -r
mk src/app.js
```

`-r/--run-on-compile` matters for compiled languages.  
For interpreted files, it has no practical effect.

### 2) Use a config entry

Create `.mkconfig.toml` in your project:

```toml
entry = "src/main.c"
build_dir = "build"
run_on_compile = true
```

Then run:

```bash
mk run
```

You can also point to a specific config file:

```bash
mk run --config /path/to/.mkconfig.toml
```

## Usage

Basic forms:

```bash
mk <file>
mk run
```

Useful options:

- `--config <file>`: use a specific config file
- `--cwd <dir>`: run as if started from a different directory
- `-o, --output <file>`: output path/name for compiled targets
- `--build-dir <dir>`: build output directory (default: `build`)
- `--python <python>`: override Python interpreter for `.py`
- `--program-args ...`: extra compiler/interpreter args
- `-r, --run-on-compile`: compile then run (compiled languages)
- `-c, --clear`: clear terminal before action
- `-v, --version`: show version
- `-h, --help`: show help

Example commands:

```bash
mk main.cpp --build-dir out -o out/main -r
mk script.py --python python3
mk run --cwd ./examples
mk app.go --program-args "-trimpath" -r
```

## Config (`.mkconfig.toml` / `.mkconfig`)

`mk run` reads TOML config and resolves an entry file.

Auto-discovery checks current directory and parent directories for:

- `.mkconfig/.mkconfig.toml`
- `.mkconfig.toml`
- `.mkconfig`

Supported keys currently used by runtime:

```toml
entry = "src/main.py"
cwd = "."
build_dir = "build"
output = "build/main"
python = "python3"
python_cmd = "python3"
run_on_compile = true
clear = false
program_args = ["-O2"]

[env]
MY_VAR = "value"
```

Notes:

- `entry` is required for `mk run`.
- Relative paths in config are resolved from the config location.
- `mk run` currently forces compile-and-run behavior (`run_on_compile = true` at runtime).
- `.mkconfig` is also parsed as TOML.
- `lang` and `tool` values can be parsed from config/CLI, but are not currently applied by executors.

## Tool detection and external dependencies

`mk` calls external compilers/interpreters. They are not bundled.

If a required tool is missing, execution fails with a runtime error for that tool.

By default, command names come from `PATH` (for example `gcc`, `node`, `javac`).  
You can override tool paths/commands with environment variables, for example:

```bash
export MAHKRAB_GCC=/usr/bin/gcc-14
export MAHKRAB_PYTHON=/usr/bin/python3.12
export MAHKRAB_JAVA=/usr/lib/jvm/default/bin/java
```

Common overrides include:

- `MAHKRAB_GCC`, `MAHKRAB_GPP`, `MAHKRAB_RUSTC`, `MAHKRAB_GO`
- `MAHKRAB_JAVAC`, `MAHKRAB_JAVA`
- `MAHKRAB_PYTHON`, `MAHKRAB_NODE`, `MAHKRAB_TS`
- `MAHKRAB_SQLITE3`, `MAHKRAB_NASM`
- plus other `MAHKRAB_*` tool variables defined in `src/mahkrab/constants.py`

## Supported language note

Language support is extension-driven and depends on your installed toolchain.

Current extension handlers include:

- Interpreted: 

   - `.py`, `.js`, `.ts`, `.rb`, `.php`, `.lua`, `.sh`, `.ps1`, `.pl`, `.r`, `.m`, `.pro`, `.prolog`, `.plg`, `.dart`, `.sql`, `.sb3`
- Compiled via dedicated executors: 

   - `.c`, `.cpp`, `.cc`, `.cxx`, `.rs`, `.go`, `.java`, `.asm`

- Compiled via command mapping: 
   - `.cs`, `.vb`, `.pas`, `.f`, `.for`, `.f77`, `.f90`, `.f95`, `.f03`, `.f08`, `.adb`, `.ada`, `.swift`, `.kt`, `.bas`, `.cob`, `.cbl`

There is also a binary run path for targets with no extension (or `.exe`).

## Current limitations

- Focus is convenience for small projects and standalone files, not full project orchestration.
- Behavior depends on external tools being installed and available.
- Assembly flow is currently Unix-like only (`.asm` is not supported on Windows in current code).
- C/C++ dependency flags are limited, no current auto-discovery system

## Development

From this repository:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
mk -h
```

## Contributing

Issues and pull requests are welcome.