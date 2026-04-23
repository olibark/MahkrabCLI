from __future__ import annotations

import platform

SUPPORTED_TARGET_OSES = ('linux', 'macos', 'windows')

TARGET_OS_ALIASES = {
    'linux': 'linux',
    'unix': 'linux',
    'unixlike': 'linux',
    'macos': 'macos',
    'mac': 'macos',
    'darwin': 'macos',
    'osx': 'macos',
    'windows': 'windows',
    'win': 'windows',
}


def detectHostOs() -> str:
    system = platform.system().lower()
    if system.startswith('win'):
        return 'windows'
    if system == 'darwin':
        return 'macos'
    if system == 'linux':
        return 'linux'

    return 'linux'


def normalizeTargetOs(value: object) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip().lower()
    if not normalized:
        return None

    return TARGET_OS_ALIASES.get(normalized)
