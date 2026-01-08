import subprocess, sys

def list(level: int) -> None:
    subprocess.run(
        ["tree", "-L", str(level), "."],
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True
        )
