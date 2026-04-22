# MahkrabCLI Configuration Guide

MahkrabCLI uses TOML config files to make `mk run`, `mk build`, and `mk doctor`
repeatable inside a project.

## Config File Names

`mk` discovers config files by searching from the current directory up through
parent directories. In each directory, it checks these paths in order:

1. `.mkconfig/.mkconfig.toml`
2. `.mkconfig.toml`
3. `.mkconfig`

All supported config files are parsed as TOML, including `.mkconfig`.

You can also pass a config explicitly:

```bash
mk run --config ./path/to/.mkconfig.toml
mk build --config ./path/to/project
```

When `--config` points to a directory, `mk` reads `.mkconfig.toml` inside that
directory.

## Minimal Config

```toml
entry = "src/main.py"
```

With that file in place:

```bash
mk run
mk build
mk doctor
```

`entry` is required for `mk run` and `mk build`. `mk doctor` can also use it as
the target context when no explicit doctor target, `--lang`, or `--all` is
provided.

## Full Example

```toml
entry = "src/main.c"
cwd = "."
build_dir = "build"
output = "build/main"
lang = "c"
tool = "gcc"
run_on_compile = true
clear = false
compile_args = ["-O2", "-Wall"]
program_args = ["hello", "world"]

[doctor]
quiet = false
verbose = false

[env]
APP_ENV = "development"
```

## Key Reference

| Key | Type | Description |
| --- | --- | --- |
| `entry` | string | Project entry file used by `mk run`, `mk build`, and default `mk doctor` target selection. |
| `cwd` | string | Working directory used while running commands. Relative paths are resolved from the config root. |
| `build_dir` | string | Directory used for compiled outputs. Defaults to `build`. |
| `output` | string | Output path/name for compiled targets. If omitted, `mk` derives one from the target name and `build_dir`. |
| `python` | string | Python interpreter command for Python files. |
| `python_cmd` | string | Alias for `python`. |
| `lang` | string | Language handler override, equivalent to `--lang`. |
| `tool` | string | Compiler or interpreter executable override, equivalent to `--tool`. |
| `run_on_compile` | boolean | Compiles and runs direct compiled targets when true. `mk run` always runs; `mk build` never runs. |
| `clear` | boolean | Clears the terminal before running the selected action. |
| `compile_args` | string or list | Extra arguments passed to the compiler or interpreter. |
| `tool_args` | string or list | Alias for `compile_args`; values are appended after `compile_args`. |
| `program_args` | string or list | Arguments passed to the script or compiled program. |
| `[doctor].quiet` | boolean | Makes `mk doctor` print only its summary. |
| `[doctor].verbose` | boolean | Makes `mk doctor` include generated command plans and extra detail. |
| `[env]` | table | Environment variables added to the process before execution. Values are converted to strings. |

Legacy top-level `doctor_quiet` and `doctor_verbose` keys are also accepted.
Prefer the `[doctor]` table for new config files.

## Config Root and Relative Paths

The config root is the directory that owns the config:

- For `.mkconfig.toml`, the config root is its parent directory.
- For `.mkconfig`, the config root is its parent directory.
- For `.mkconfig/.mkconfig.toml`, the config root is the directory containing
  `.mkconfig`.

Relative config values are resolved from that root where applicable. This keeps
config behavior stable even when you run `mk` from a subdirectory.

Example layout:

```text
project/
  .mkconfig/
    .mkconfig.toml
  src/
    main.c
```

Config:

```toml
entry = "src/main.c"
build_dir = "build"
```

From anywhere inside `project`, `entry` resolves to `project/src/main.c`.

## Working Directory Rules

`cwd` controls where commands run:

```toml
cwd = "examples"
entry = "hello.py"
```

CLI behavior:

- `--cwd <dir>` wins over config `cwd`.
- Relative `--cwd` paths are resolved from the directory where you invoked `mk`.
- Relative config `cwd` paths are resolved from the config root.
- For `mk run` and `mk build`, when no `cwd` is configured, the working
  directory defaults to the config root.
- For direct file targets, when no `cwd` is configured, the working directory
  defaults to the invocation directory.

## Precedence Rules

When the same setting exists in more than one place, `mk` uses this order:

| Setting | Precedence |
| --- | --- |
| `--config` | CLI path only. If omitted, auto-discovery is used. |
| `entry` | Config file only for `run`, `build`, and default `doctor` target context. |
| `cwd` | CLI `--cwd`, then config `cwd`, then config root or invocation directory depending on command. |
| `output` | CLI `--output`, then config `output`, then derived output path. |
| `build_dir` | CLI `--build-dir`, then config `build_dir`, then `build`. |
| `python` | CLI `--python`, then config `python` / `python_cmd`, then `MAHKRAB_PYTHON`, then the running Python executable. |
| `lang` | CLI `--lang`, then config `lang`, then extension detection. |
| `tool` | CLI `--tool`, then config `tool`, then language default or `MAHKRAB_*` environment override. |
| `run_on_compile` | CLI `--run-on-compile` or config `run_on_compile`; forced true by `mk run`; forced false by `mk build`. |
| `clear` | CLI `--clear` or config `clear`. |
| `compile_args` | Config `compile_args`, then config `tool_args`, then CLI `--compile-args` / `--tool-args`. |
| `program_args` | Config `program_args`, then CLI `--program-args` or bare `--` arguments. |
| Doctor output | CLI `--quiet` / `--verbose`, then `[doctor]` config, then default output. |

## Argument Values

`compile_args`, `tool_args`, and `program_args` can be strings or lists.

List form:

```toml
compile_args = ["-O2", "-Wall"]
program_args = ["hello", "world"]
```

String form is split like a shell command line:

```toml
compile_args = "-O2 -Wall"
program_args = "--name Ada"
```

Use list form when an argument contains spaces and should remain one value:

```toml
program_args = ["--message", "hello world"]
```

## Environment Variables

Use `[env]` to define environment variables for commands launched by `mk`:

```toml
[env]
APP_ENV = "development"
DATABASE_URL = "sqlite:///dev.db"
```

These values are added to the process environment before execution.

## Doctor Configuration

Use `[doctor]` to control default doctor output:

```toml
[doctor]
quiet = true
verbose = false
```

CLI flags win over config:

```bash
mk doctor --verbose
mk doctor --quiet
```

`quiet` and `verbose` are mutually exclusive at the CLI level. If both are set
in config, quiet mode wins because it is evaluated first.

## Tool Overrides

Config `tool` overrides the executable for the selected language handler:

```toml
entry = "src/main.cpp"
tool = "clang++"
```

You can also set environment variables for persistent tool paths:

```bash
export MAHKRAB_GCC=/usr/bin/gcc-14
export MAHKRAB_GPP=/usr/bin/g++-14
export MAHKRAB_PYTHON=/usr/bin/python3.12
```

Common environment overrides:

| Variable | Tool |
| --- | --- |
| `MAHKRAB_GCC` | C compiler |
| `MAHKRAB_GPP` | C++ compiler |
| `MAHKRAB_RUSTC` | Rust compiler |
| `MAHKRAB_GO` | Go compiler |
| `MAHKRAB_JAVAC` | Java compiler |
| `MAHKRAB_JAVA` | Java runtime |
| `MAHKRAB_PYTHON` | Python interpreter |
| `MAHKRAB_NODE` | Node.js |
| `MAHKRAB_TS` | TypeScript runner |
| `MAHKRAB_SQLITE3` | SQLite CLI |
| `MAHKRAB_NASM` | NASM assembler |
| `MAHKRAB_AS` | GNU assembler |
| `MAHKRAB_LD` | Linker |

## Recommended Project Layout

For small projects, keep config at the project root:

```text
project/
  .mkconfig.toml
  src/
    main.py
```

For projects where you prefer a config directory:

```text
project/
  .mkconfig/
    .mkconfig.toml
  src/
    main.c
```

Both layouts work. The directory form keeps the root cleaner if more MahkrabCLI
configuration files are added later.
