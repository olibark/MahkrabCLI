# MahkrabCLI CLI Reference

This page documents the `mk` command, its arguments, and the behavior of each
flag. For config-file usage, see the
[configuration guide](https://github.com/olibark/MahkrabCLI/blob/main/docs/configuration.md).

## Command Forms

```bash
mk <target> [options]
mk init [target] [options]
mk config [options]
mk run [options]
mk build [options]
mk doctor [target] [options]
```

| Form | Description |
| --- | --- |
| `mk <target>` | Runs a direct file target. The language is inferred from the extension unless `--lang` is supplied. |
| `mk init [target]` | Creates `.mkconfig/mkconfig.toml` for project commands. |
| `mk config` | Shows the resolved config file and reads or updates supported config keys. |
| `mk run` | Loads the configured `entry` and runs it. Compiled languages are compiled and then run. |
| `mk build` | Loads the configured `entry` and compiles it without running it. |
| `mk doctor` | Checks whether required external compiler and interpreter commands are available. |

`init`, `config`, `run`, `build`, and `doctor` are reserved subcommand names.
To run a file with one of those names, provide an explicit path:

```bash
mk ./init
mk ./run
```

Targets without an extension, and targets ending in `.exe`, are treated as
runnable binaries.

## Shared Options

These options are accepted by direct targets, `run`, `build`, and `doctor`.

| Option | Value | Description |
| --- | --- | --- |
| `-o`, `--output` | `<file>` | Sets the output path/name for compiled targets. |
| `--build-dir` | `<dir>` | Sets the directory used for compiled outputs. Defaults to `build`. |
| `--cwd` | `<dir>` | Runs as if the command started in another directory. |
| `--config` | `<file>` | Uses a specific config file. If a directory is given, supported config names are checked inside it. |
| `--python` | `<python>` | Overrides the Python interpreter for Python files. |
| `--lang` | `<language>` | Forces a language handler instead of resolving by extension. |
| `--tool` | `<tool>` | Overrides the compiler or interpreter executable for the selected handler. |
| `-r`, `--run-on-compile` | none | Runs the compiled output after compilation for compiled languages. |
| `--compile-args`, `--tool-args` | `<args>` | Adds arguments to the compiler or interpreter command. `--tool-args` is an alias. |
| `--program-args` | `<args>` | Adds arguments to the script or compiled program. |
| `-c`, `--clear` | none | Clears the terminal before running the selected action. |
| `-og`, `--ogs` | none | Runs the built-in `ogs` helper. |
| `-t`, `--terry` | none | Runs the built-in Terry helper. |
| `-e`, `--explain` | none | Prints the resolved execution plan before running. |
| `-v`, `--version` | none | Prints the installed version and exits. |
| `-h`, `--help` | none | Prints help and exits. |

## Direct Target Examples

```bash
mk hello.py
mk src/app.js
mk main.c -r
mk main.cpp --build-dir out -o out/main -r
mk script.py --python python3.12
mk README.md --lang python --tool python3.12 --explain
mk hello
```

## `init`

`mk init` creates `.mkconfig/mkconfig.toml`. That file provides the `entry` and
other defaults used by `mk run`, `mk build`, and `mk doctor`.

```bash
mk init
mk init main.py
mk init --entry src/main.c --lang c --run-on-compile
mk init --build-dir out --output out/app
mk init --force
```

Init options:

| Option | Description |
| --- | --- |
| `--entry <file>` | Writes the `entry` key. A positional target, such as `mk init main.py`, is also accepted. |
| `--lang <language>` | Writes the `lang` key. |
| `--build-dir <dir>` | Writes the `build_dir` key. Defaults to `build`. |
| `-o`, `--output <file>` | Writes the `output` key. |
| `-r`, `--run-on-compile` | Writes `run_on_compile = true`. |
| `--force` | Overwrites an existing generated config. |

If no entry is provided, `mk init` tries common source names such as
`src/main.py` or `main.c`. If none is found, it writes a commented placeholder.
By default, it refuses to overwrite an existing Mahkrab config and exits with
status `2`.

## `run`

`mk run` loads the configured `entry` from a discovered Mahkrab config or a file
passed with `--config`.

```bash
mk run
mk run --config ./examples/.mkconfig.toml
mk run --cwd ./examples
```

For compiled languages, `mk run` always runs after compilation. This is true
even when `run_on_compile = false` appears in the config file.

## `build`

`mk build` loads the configured `entry` and compiles it without running the
output.

```bash
mk build
mk build --config ./examples/.mkconfig.toml
mk build --build-dir out
```

`mk build` always compiles only. This is true even when `run_on_compile = true`
appears in the config file.

## `config`

`mk config` inspects the Mahkrab config resolved from the current directory, or
from an explicit `--config` path. It can print a summary, get one or more
supported keys, or update supported keys without opening the TOML file manually.

```bash
mk config
mk config --config ./examples/.mkconfig.toml
mk config --entry
mk config --entry src/main.c
mk config --run-on-compile true
mk config --compile-args "-O2 -Wall"
mk config --env FOO=bar
```

With no getter or setter flags, `mk config` prints the resolved config path and
the current values for supported keys. A key flag without a value is a getter:

```bash
mk config --entry
mk config --entry --tool
```

A key flag with a value is a setter:

```bash
mk config --entry src/main.c
mk config --clear false
```

Getters and setters cannot be mixed in the same command. A getter for an unset
key exits with status `2`. Boolean setters accept `true`, `false`, `1`, or `0`;
other boolean values exit with status `2` and leave the config unchanged.

Config command options:

| Option | Behavior |
| --- | --- |
| `--config <file>` | Uses a specific config file. If a directory is given, supported config names are checked inside it. |
| `--entry [file]` | Gets or sets `entry`. |
| `--cwd [dir]` | Gets or sets `cwd`. |
| `--build-dir [dir]` | Gets or sets `build_dir`. |
| `-o`, `--output [file]` | Gets or sets `output`. |
| `--python [python]` | Gets or sets `python`. If `python_cmd` exists, getters read it as an alias and setters replace it with `python`. |
| `--lang [language]` | Gets or sets `lang`. |
| `--tool [tool]` | Gets or sets `tool`. |
| `-r`, `--run-on-compile [bool]` | Gets or sets `run_on_compile`. |
| `-c`, `--clear [bool]` | Gets or sets `clear`. |
| `--compile-args [args]` | Gets or sets `compile_args` from a quoted shell-style string. If `tool_args` exists, getters read it as an alias and setters replace it with `compile_args`. |
| `--program-args [args]` | Gets or sets `program_args` from a quoted shell-style string. |
| `--env KEY=VALUE` | Adds or replaces one value in the `[env]` table. May be repeated. |

`--env` is setter-only. Values must use `KEY=VALUE`; invalid values exit with
status `2` and leave the config unchanged.

If no config exists, `mk config` exits with status `2` and tells you to create
one with `mk init`. If `--config` points to a missing file or directory without
a supported config file, it exits with status `2` and prints the resolved path.

## `doctor`

`mk doctor` checks for the external commands needed by one or more language
handlers.

```bash
mk doctor
mk doctor src/main.py
mk doctor --lang python,c,cpp
mk doctor --all
mk doctor --languages
mk doctor --os windows
mk doctor --json
mk doctor --quiet
mk doctor --verbose
```

Doctor target selection:

| Form | Selection |
| --- | --- |
| `mk doctor` | Uses the configured `entry` when one exists. |
| `mk doctor <target>` | Checks the language inferred from that target. |
| `mk doctor --lang python,c` | Checks the selected language handlers. |
| `mk doctor --all` | Checks every supported doctor target. |
| `mk doctor --languages` or `mk doctor languages` | Lists supported doctor language aliases. |

If no configured entry, direct target, `--lang`, or `--all` is available,
doctor exits with a usage error.

Doctor output flags:

| Option | Description |
| --- | --- |
| `-q`, `--quiet` | Prints only the summary. |
| `--verbose` | Prints extra diagnostics, including generated command plans. |
| `--json` | Prints machine-readable JSON. |
| `--os <os>` | Uses install hints for `linux`, `macos`, or `windows`. |

`--quiet` and `--verbose` are mutually exclusive.

Doctor exit codes:

| Exit code | Meaning |
| --- | --- |
| `0` | All checked toolchains are available. |
| `1` | One or more checked toolchains are missing. |
| `2` | Usage error, unsupported doctor language, missing target context, or config error. |

## Passing Compiler and Program Arguments

Use `--compile-args` for values that belong to the compiler or interpreter:

```bash
mk main.c -r --compile-args "-O2 -Wall"
mk app.go --compile-args "-trimpath" -r
mk script.py --compile-args "-X utf8"
```

Use `--program-args` for values passed to your program after compilation or to
your interpreted script:

```bash
mk main.c -r --program-args -- hello world
mk script.py --program-args -- --name Ada
```

You can also use a bare `--` to forward the rest of the command line as program
arguments:

```bash
mk main.c -r -- hello world
```

Config-file arguments are prepended before CLI arguments. For example, if
`program_args = ["from-config"]` is configured, then this command:

```bash
mk run --program-args -- from-cli
```

runs with both `from-config` and `from-cli`.

## Language and Tool Overrides

`--lang` selects a language handler explicitly:

```bash
mk README.md --lang python
mk hello.asm --lang gas
```

`--tool` replaces the executable token used by the selected handler:

```bash
mk main.cpp --tool clang++
mk script.py --tool python3.12
```

For Java, `--tool` affects the compile step (`javac` side), not the `java`
runtime command. Use environment variables for separate compile and runtime
tool overrides when a language has multiple external tools.

`--explain` prints the resolved target, working directory, config path, selected
language, output path, tool override, and generated command plan before running.

## Config Option

`--config <file>` points `mk` to a specific TOML config file:

```bash
mk run --config ./examples/.mkconfig.toml
```

If the value is a directory, `mk` checks the supported config names inside that
directory and uses the first one it finds:

```bash
mk run --config ./examples
```

Relative `--config` paths are resolved from the directory where you invoked
`mk`.

## Supported Extensions

| Language | Extensions |
| --- | --- |
| Python | `.py` |
| C | `.c` |
| C++ | `.cpp`, `.cc`, `.cxx` |
| Java | `.java` |
| C# | `.cs` |
| JavaScript | `.js` |
| TypeScript | `.ts` |
| Visual Basic | `.vb` |
| SQL | `.sql` |
| R | `.r` |
| Pascal | `.pas` |
| Perl | `.pl` |
| Scratch | `.sb3` |
| Fortran | `.f`, `.for`, `.f77`, `.f90`, `.f95`, `.f03`, `.f08` |
| Rust | `.rs` |
| MATLAB | `.m` |
| Go | `.go` |
| NASM assembly | `.asm`, `.nasm` |
| GAS assembly | `.s`, `.S` |
| PHP | `.php` |
| Ada | `.adb`, `.ada` |
| Swift | `.swift` |
| Prolog | `.pro`, `.prolog`, `.plg` |
| Kotlin | `.kt` |
| Classic Visual Basic | `.bas` |
| COBOL | `.cob`, `.cbl` |
| Dart | `.dart` |
| Ruby | `.rb` |
| Lua | `.lua` |
| Bash | `.sh` |
| PowerShell | `.ps1` |
| Binary | no extension, `.exe` |

## Common Language Aliases

Aliases are accepted by `--lang` and doctor language selection.

| Handler | Common aliases |
| --- | --- |
| Python | `python`, `py` |
| C++ | `cpp`, `c++`, `cxx`, `cc` |
| C# | `c#`, `csharp`, `cs` |
| JavaScript | `javascript`, `js`, `node`, `nodejs` |
| TypeScript | `typescript`, `ts` |
| Visual Basic | `visual basic`, `visualbasic`, `vb` |
| Pascal | `delphi`, `object pascal`, `pascal` |
| Rust | `rust`, `rs` |
| Go | `go`, `golang` |
| Assembly | `assembly`, `asm` |
| NASM assembly | `nasm` |
| GAS assembly | `gas`, `gnu asm`, `gnu assembler` |
| Binary | `binary`, `bin`, `executable` |

Use `mk doctor --languages` for the exact alias list recognized by the
installed version.

## Assembly Notes

Supported assembly extensions:

- NASM / Intel syntax: `.asm`, `.nasm`
- GNU assembler / GAS: `.s`, `.S`

Supported overrides:

- Generic assembly: `--lang assembly` or `--lang asm`
- NASM: `--lang nasm`
- GAS: `--lang gas` or `--lang gnu-asm`

Default behavior:

- `.asm` and `.nasm` use NASM.
- `.s` and `.S` use GAS.
- `--lang assembly` keeps handling generic and resolves the concrete backend
  from the file extension.
- `--lang nasm` or `--lang gas` forces a backend.

Current platform notes:

- NASM currently supports Unix-like systems only.
- GAS currently supports Unix-like systems only.
- MASM is not implemented.
