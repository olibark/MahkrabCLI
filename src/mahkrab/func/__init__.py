from __future__ import annotations

import sys

from mahkrab.func import workflow as run


sys.modules[f'{__name__}.run'] = run

__all__ = ['run']
