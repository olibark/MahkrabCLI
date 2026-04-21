# mahkrab

`mahkrab` is a lightweight CLI that installs as `mk`.

It is a cross-language source runner and compile-and-run helper for small files and small projects.

## Why

`mk` gives you one command shape for many languages:

- `mk <file>` to run/interpret or compile a source file by extension
- `mk run` to run the configured entry from `.mkconfig.toml` or `.mkconfig`
- `mk build` to compile the configured entry without running it
- `mk doctor` to diagnose external compiler/interpreter availability

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

Or compile the configured entry without running it:

```bash
mk build
```

You can also point to a specific config file:

```bash
mk run --config /path/to/.mkconfig.toml
mk build --config /path/to/.mkconfig.toml
```

## Usage

Basic forms:

```bash
mk <file>
mk run
mk build
mk doctor
```

Useful options:

- `--config <file>`: use a specific config file
- `--cwd <dir>`: run as if started from a different directory
- `-o, --output <file>`: output path/name for compiled targets
- `--build-dir <dir>`: build output directory (default: `build`)
- `--python <python>`: override Python interpreter for `.py`
- `--lang <language>`: force a language handler instead of using file extension
- `--tool <tool>`: override the compiler/interpreter executable
- `--compile-args ...`: extra compiler/interpreter args
- `--program-args ...`: args passed to the compiled program or script
- `-q, --quiet`: only print the `mk doctor` summary
- `--verbose`: print extra `mk doctor` diagnostics, including generated command plans
- `-e, --explain`: print the resolved execution plan before running
- `-r, --run-on-compile`: compile then run (compiled languages)
- `-c, --clear`: clear terminal before action
- `-v, --version`: show version
- `-h, --help`: show help

Example commands:

```bash
mk main.cpp --build-dir out -o out/main -r
mk script.py --python python3
mk README.md --lang python --tool python3.12 --explain
mk run --cwd ./examples
mk build --cwd ./examples
mk doctor
mk doctor --quiet
mk doctor --verbose
mk app.go --compile-args "-trimpath" -r
mk main.c -r --program-args -- hello world
mk hello.asm -r
mk hello.S -r
mk hello.asm --lang gas --explain
```

## Config (`.mkconfig.toml` / `.mkconfig`)

`mk run` and `mk build` read TOML config and resolve an entry file.

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
lang = "python"
tool = "python3.12"
run_on_compile = true
clear = false
compile_args = ["-O2"]
program_args = ["hello", "world"]

[doctor]
quiet = false
verbose = false

[env]
MY_VAR = "value"
```

Notes:

- `entry` is required for `mk run` and `mk build`.
- Relative paths in config are resolved from the config location.
- `mk run` currently forces compile-and-run behavior (`run_on_compile = true` at runtime).
- `mk build` forces compile-only behavior and exits with the compiler/build exit code.
- `.mkconfig` is also parsed as TOML.
- CLI values win over config values for `lang`, `tool`, and other runtime settings.
- `compile_args` are passed to the compiler or interpreter command.
- `program_args` are passed to the compiled program or script.
- `tool` replaces the executable used to invoke the selected compiler/interpreter. For Java this affects the compile step (`javac`-side), not the `java` runtime command.
- `doctor.quiet` and `doctor.verbose` configure `mk doctor` output. You can also use top-level `doctor_quiet` and `doctor_verbose`; CLI flags win over config.

## `--lang`, `--tool`, and `--explain`

- `--lang` lets you force a handler even when the file extension would normally map somewhere else. Example: `mk README.md --lang python`.
- `--tool` replaces the underlying executable token for the selected handler. Example: `mk main.cpp --tool clang++`.
- `--explain` prints the resolved target, cwd, config path, chosen language source (`extension` or `override`), output path, tool override, and the concrete command(s) that will be executed, then continues with the normal run.

## Tool detection and external dependencies

`mk` calls external compilers/interpreters. They are not bundled.

Use `mk doctor` to check the configured compiler/interpreter commands before running code. It reports each supported language, the required command values, whether each command resolves, the resolved executable path, and whether the language is runnable/buildable on the current machine.

Use `mk doctor --quiet` when you only need the final status. Use `mk doctor --verbose` to include the generated compile/link/run command plans used for the checks.

`mk doctor` exits with status `0` only when every supported language toolchain is available. If any language is unavailable, it exits non-zero and prints an `Unavailable languages:` line.

If a required tool is missing during normal execution, execution fails with a runtime error for that tool.

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
- `MAHKRAB_SQLITE3`, `MAHKRAB_NASM`, `MAHKRAB_AS`, `MAHKRAB_LD`
- plus other `MAHKRAB_*` tool variables defined in `src/mahkrab/constants.py`

## Supported language note

Language support is extension-driven and depends on your installed toolchain.

Current extension handlers include:

- Interpreted: 

   - `.py`, `.js`, `.ts`, `.rb`, `.php`, `.lua`, `.sh`, `.ps1`, `.pl`, `.r`, `.m`, `.pro`, `.prolog`, `.plg`, `.dart`, `.sql`, `.sb3`
- Compiled via dedicated executors: 

   - `.c`, `.cpp`, `.cc`, `.cxx`, `.rs`, `.go`, `.java`, `.asm`, `.nasm`, `.s`, `.S`

- Compiled via command mapping: 
   - `.cs`, `.vb`, `.pas`, `.f`, `.for`, `.f77`, `.f90`, `.f95`, `.f03`, `.f08`, `.adb`, `.ada`, `.swift`, `.kt`, `.bas`, `.cob`, `.cbl`

There is also a binary run path for targets with no extension (or `.exe`).

## Assembly support

Supported assembly extensions:

- NASM / Intel syntax: `.asm`, `.nasm`
- GNU assembler / GAS: `.s`, `.S`

Supported `--lang` overrides:

- generic assembly: `assembly`, `asm`
- NASM-specific: `nasm`
- GAS-specific: `gas`, `gnu-asm`

Default behavior:

- `.asm` and `.nasm` resolve to NASM
- `.s` and `.S` resolve to GAS
- `--lang assembly` / `--lang asm` keeps assembly handling generic and then resolves the concrete backend from the file extension
- `--lang nasm` or `--lang gas` forces a backend when you need to override the extension-based choice

External tools used by assembly handlers:

- NASM: `nasm`
- GAS: `as` for `.s`, `gcc -c` for `.S`
- Linker: `ld` on Unix-like systems

Examples:

```bash
mk hello.asm -r
mk hello.nasm --compile-args "-g" -r
mk hello.s -r
mk hello.S --compile-args "-Iinclude" -r
mk hello.asm --lang gas --explain
```

Current platform notes:

- NASM currently supports Unix-like systems only.
- GAS currently supports Unix-like systems only.
- MASM is not implemented yet, but the assembly executor is now variant-based so another backend can be added without rewriting the executor.

## Current limitations

- Focus is convenience for small projects and standalone files, not full project orchestration.
- Behavior depends on external tools being installed and available.
- C/C++ dependency flags are limited, no current auto-discovery system

## Development

From this repository:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
mk -h
pytest tests
```

### Internal layout

The CLI entry point stays in `src/mahkrab/cli.py`. Runtime settings and config parsing live in `src/mahkrab/tools/config.py` and command-line parsing lives in `src/mahkrab/tools/parser.py`.

Execution code is split by responsibility:

- `src/mahkrab/func/workflow.py`: top-level run and build workflow.
- `src/mahkrab/func/plans.py`: execution-plan creation and `--explain` output.
- `src/mahkrab/func/commands.py`: compiler, interpreter, and run command construction.
- `src/mahkrab/func/languages.py`: language aliases, labels, and extension mapping.

The old internal `run.py` module has been renamed to the clearer workflow module. The command-line interface remains unchanged.

## Contributing

Issues and pull requests are welcome.
