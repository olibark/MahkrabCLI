#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CASE_DIR="$ROOT/tests/cli_cases"
RESULTS="$CASE_DIR/results.txt"
: > "$RESULTS"

pass=0
fail=0
skip=0

if command -v mk >/dev/null 2>&1; then
  RUNNER=(mk)
else
  RUNNER=(python3 -m mahkrab.cli)
fi

run_mk() {
  if [[ "${RUNNER[0]}" == "mk" ]]; then
    mk "$@"
  else
    PYTHONPATH="$ROOT/src" python3 -m mahkrab.cli "$@"
  fi
}

record() {
  local status="$1"
  local name="$2"
  echo "[$status] $name" | tee -a "$RESULTS"
}

expect_ok() {
  local name="$1"
  shift
  if run_mk "$@" >/dev/null 2>&1; then
    record PASS "$name"
    pass=$((pass + 1))
  else
    record FAIL "$name"
    fail=$((fail + 1))
  fi
}

expect_fail() {
  local name="$1"
  shift
  if run_mk "$@" >/dev/null 2>&1; then
    record FAIL "$name"
    fail=$((fail + 1))
  else
    record PASS "$name"
    pass=$((pass + 1))
  fi
}

ensure_tool() {
  local tool="$1"
  if command -v "$tool" >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

lang_case() {
  local name="$1"
  local tool="$2"
  local file="$3"
  local kind="$4"

  if ! ensure_tool "$tool"; then
    record SKIP "$name (missing $tool)"
    skip=$((skip + 1))
    return
  fi

  if [[ "$kind" == "interpreted" ]]; then
    expect_ok "$name: mk <file>" "$file"
    expect_ok "$name: mk <file> -r" "$file" -r
  else
    expect_ok "$name: mk <file>" "$file"
    expect_ok "$name: mk <file> -r" "$file" -r
  fi
}

# Core flag behavior
expect_ok "version flag" -v
expect_ok "help flag" -h
expect_fail "no args should error"
expect_ok "clear flag with interpreted file" "$CASE_DIR/hello.py" -c
expect_ok "explain flag with file" "$CASE_DIR/hello.py" -e
expect_ok "python override" "$CASE_DIR/hello.py" --python python3
expect_ok "program args quoted compile" "$CASE_DIR/hello.c" -r --program-args "-O3"
expect_ok "tool args alias compile" "$CASE_DIR/hello.c" -r --tool-args "-O2"
expect_ok "lang flag parses" "$CASE_DIR/hello.py" --lang python
expect_ok "tool flag parses" "$CASE_DIR/hello.py" --tool python3
expect_ok "output flag compile" "$CASE_DIR/hello.c" -o "$CASE_DIR/build/custom_hello"
expect_ok "cwd flag" --cwd "$CASE_DIR" hello.py
expect_ok "ogs flag" -og
expect_ok "terry flag" -t

# mk run with .mkconfig/.mkconfig.toml
PROJECT_DIR="$CASE_DIR/project_run"
mkdir -p "$PROJECT_DIR/.mkconfig"
cat > "$PROJECT_DIR/entry.py" << 'PYEOF'
print('hello from mk run config')
PYEOF
cat > "$PROJECT_DIR/.mkconfig/.mkconfig.toml" << 'TMLEOF'
entry = "entry.py"
python = "python3"
program_args = []
TMLEOF

if (cd "$PROJECT_DIR" && run_mk run >/dev/null 2>&1); then
  record PASS "mk run reads .mkconfig/.mkconfig.toml"
  pass=$((pass + 1))
else
  record FAIL "mk run reads .mkconfig/.mkconfig.toml"
  fail=$((fail + 1))
fi

if run_mk run --config "$PROJECT_DIR/.mkconfig/.mkconfig.toml" >/dev/null 2>&1; then
  record PASS "--config with mk run"
  pass=$((pass + 1))
else
  record FAIL "--config with mk run"
  fail=$((fail + 1))
fi

if ensure_tool gcc; then
  BUILD_PROJECT_DIR="$CASE_DIR/project_build"
  mkdir -p "$BUILD_PROJECT_DIR/.mkconfig" "$BUILD_PROJECT_DIR/src"
  cat > "$BUILD_PROJECT_DIR/src/main.c" << 'CEOF'
#include <stdio.h>

int main(void) {
  FILE *file = fopen("ran.txt", "w");
  if (file) {
    fputs("ran", file);
    fclose(file);
  }
  puts("ran");
  return 0;
}
CEOF
  cat > "$BUILD_PROJECT_DIR/.mkconfig/.mkconfig.toml" << 'TMLEOF'
entry = "src/main.c"
build_dir = "build"
run_on_compile = true
TMLEOF

  rm -f "$BUILD_PROJECT_DIR/ran.txt"
  if (cd "$BUILD_PROJECT_DIR" && run_mk build >/dev/null 2>&1) \
    && [[ -x "$BUILD_PROJECT_DIR/build/main" ]] \
    && [[ ! -e "$BUILD_PROJECT_DIR/ran.txt" ]]; then
    record PASS "mk build compiles configured entry only"
    pass=$((pass + 1))
  else
    record FAIL "mk build compiles configured entry only"
    fail=$((fail + 1))
  fi

  if (cd "$BUILD_PROJECT_DIR" && run_mk run >/dev/null 2>&1) \
    && [[ -e "$BUILD_PROJECT_DIR/ran.txt" ]]; then
    record PASS "mk run still compiles and runs configured entry"
    pass=$((pass + 1))
  else
    record FAIL "mk run still compiles and runs configured entry"
    fail=$((fail + 1))
  fi
else
  record SKIP "mk build configured entry (missing gcc)"
  skip=$((skip + 1))
fi

# Language matrix (one file per supported extension mapping)
lang_case "Python" python3 "$CASE_DIR/hello.py" interpreted
lang_case "C" gcc "$CASE_DIR/hello.c" compiled
lang_case "C++" g++ "$CASE_DIR/hello.cpp" compiled
lang_case "Java" javac "$CASE_DIR/HelloJava.java" compiled
lang_case "C#" csc "$CASE_DIR/hello.cs" compiled
lang_case "JavaScript" node "$CASE_DIR/hello.js" interpreted
lang_case "Visual Basic" vbc "$CASE_DIR/hello.vb" compiled
lang_case "SQL" sqlite3 "$CASE_DIR/hello.sql" interpreted
lang_case "R" Rscript "$CASE_DIR/hello.r" interpreted
lang_case "Delphi/Object Pascal" fpc "$CASE_DIR/hello.pas" compiled
lang_case "Perl" perl "$CASE_DIR/hello.pl" interpreted
lang_case "Fortran" gfortran "$CASE_DIR/hello.f90" compiled
lang_case "Rust" rustc "$CASE_DIR/hello.rs" compiled
lang_case "MATLAB" matlab "$CASE_DIR/hello.m" interpreted
lang_case "Go" go "$CASE_DIR/hello.go" compiled
lang_case "Assembly" nasm "$CASE_DIR/hello.asm" compiled
lang_case "PHP" php "$CASE_DIR/hello.php" interpreted
lang_case "Ada" gnatmake "$CASE_DIR/hello.adb" compiled
lang_case "Swift" swiftc "$CASE_DIR/hello.swift" compiled
lang_case "Prolog" swipl "$CASE_DIR/hello.pro" interpreted
lang_case "Kotlin" kotlinc "$CASE_DIR/hello.kt" compiled
lang_case "Classic Visual Basic" fbc "$CASE_DIR/hello.bas" compiled
lang_case "COBOL" cobc "$CASE_DIR/hello.cob" compiled
lang_case "Dart" dart "$CASE_DIR/hello.dart" interpreted

if ensure_tool twcli; then
  if run_mk "$CASE_DIR/hello.sb3" >/dev/null 2>&1; then
    record PASS "Scratch sb3"
    pass=$((pass + 1))
  else
    record FAIL "Scratch sb3"
    fail=$((fail + 1))
  fi
else
  record SKIP "Scratch sb3 (missing twcli)"
  skip=$((skip + 1))
fi

echo "" | tee -a "$RESULTS"
echo "SUMMARY pass=$pass fail=$fail skip=$skip" | tee -a "$RESULTS"

if [[ "$fail" -gt 0 ]]; then
  exit 1
fi
