from __future__ import annotations

import argparse as ap
import shlex


def get_tool_override(args: ap.Namespace) -> list[str]:
    raw_tool = getattr(args, 'tool', None)
    if raw_tool is None:
        return []

    tool = str(raw_tool).strip()
    if not tool:
        return []

    return shlex.split(tool)


def apply_tool_override(cmd: list[str], args: ap.Namespace) -> list[str]:
    override = get_tool_override(args)
    if not override:
        return list(cmd)

    return [*override, *cmd[1:]]
