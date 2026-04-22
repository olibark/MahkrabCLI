from __future__ import annotations

import argparse as ap

from mahkrab.func.executors.compiled import asmexec


SUPPORTED_LANGUAGES = (
    'Python',
    'C',
    'C++',
    'Java',
    'C#',
    'JavaScript',
    'Visual Basic',
    'SQL',
    'R',
    'Delphi/Object Pascal',
    'Perl',
    'Scratch',
    'Fortran',
    'Rust',
    'MATLAB',
    'Go',
    'Assembly',
    'PHP',
    'Ada',
    'Swift',
    'Prolog',
    'Kotlin',
    'Classic Visual Basic',
    'COBOL',
    'Dart',
)

LANGUAGE_ALIASES = {
    'python': 'python',
    'py': 'python',
    'c': 'c',
    'cpp': 'cpp',
    'c++': 'cpp',
    'cxx': 'cpp',
    'cc': 'cpp',
    'java': 'java',
    'c#': 'csharp',
    'csharp': 'csharp',
    'cs': 'csharp',
    'javascript': 'javascript',
    'js': 'javascript',
    'node': 'javascript',
    'nodejs': 'javascript',
    'typescript': 'typescript',
    'ts': 'typescript',
    'visual basic': 'visual_basic',
    'visualbasic': 'visual_basic',
    'vb': 'visual_basic',
    'sql': 'sql',
    'r': 'r',
    'delphi': 'pascal',
    'object pascal': 'pascal',
    'delphi object pascal': 'pascal',
    'pascal': 'pascal',
    'perl': 'perl',
    'pl': 'perl',
    'scratch': 'scratch',
    'sb3': 'scratch',
    'fortran': 'fortran',
    'rust': 'rust',
    'rs': 'rust',
    'matlab': 'matlab',
    'go': 'go',
    'golang': 'go',
    'php': 'php',
    'ada': 'ada',
    'swift': 'swift',
    'prolog': 'prolog',
    'kotlin': 'kotlin',
    'classic visual basic': 'classic_visual_basic',
    'classicvisualbasic': 'classic_visual_basic',
    'freebasic': 'classic_visual_basic',
    'free basic': 'classic_visual_basic',
    'cobol': 'cobol',
    'dart': 'dart',
    'ruby': 'ruby',
    'rb': 'ruby',
    'lua': 'lua',
    'bash': 'bash',
    'shell': 'bash',
    'sh': 'bash',
    'powershell': 'powershell',
    'pwsh': 'powershell',
    'binary': 'binary',
    'bin': 'binary',
    'executable': 'binary',
}
LANGUAGE_ALIASES.update(asmexec.get_language_aliases())

LANGUAGE_LABELS = {
    'python': 'Python',
    'c': 'C',
    'cpp': 'C++',
    'java': 'Java',
    'csharp': 'C#',
    'javascript': 'JavaScript',
    'typescript': 'TypeScript',
    'visual_basic': 'Visual Basic',
    'sql': 'SQL',
    'r': 'R',
    'pascal': 'Delphi/Object Pascal',
    'perl': 'Perl',
    'scratch': 'Scratch',
    'fortran': 'Fortran',
    'rust': 'Rust',
    'matlab': 'MATLAB',
    'go': 'Go',
    'assembly': 'Assembly',
    'assembly_nasm': 'Assembly (NASM)',
    'assembly_gas': 'Assembly (GNU assembler)',
    'php': 'PHP',
    'ada': 'Ada',
    'swift': 'Swift',
    'prolog': 'Prolog',
    'kotlin': 'Kotlin',
    'classic_visual_basic': 'Classic Visual Basic',
    'cobol': 'COBOL',
    'dart': 'Dart',
    'ruby': 'Ruby',
    'lua': 'Lua',
    'bash': 'Bash',
    'powershell': 'PowerShell',
    'binary': 'Binary',
}

EXTENSION_LANGUAGE_MAP = {
    '.py': 'python',
    '.c': 'c',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.java': 'java',
    '.cs': 'csharp',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.vb': 'visual_basic',
    '.sql': 'sql',
    '.r': 'r',
    '.pas': 'pascal',
    '.pl': 'perl',
    '.sb3': 'scratch',
    '.f': 'fortran',
    '.for': 'fortran',
    '.f77': 'fortran',
    '.f90': 'fortran',
    '.f95': 'fortran',
    '.f03': 'fortran',
    '.f08': 'fortran',
    '.rs': 'rust',
    '.m': 'matlab',
    '.go': 'go',
    '.php': 'php',
    '.adb': 'ada',
    '.ada': 'ada',
    '.swift': 'swift',
    '.pro': 'prolog',
    '.prolog': 'prolog',
    '.plg': 'prolog',
    '.kt': 'kotlin',
    '.bas': 'classic_visual_basic',
    '.cob': 'cobol',
    '.cbl': 'cobol',
    '.dart': 'dart',
    '.rb': 'ruby',
    '.lua': 'lua',
    '.sh': 'bash',
    '.ps1': 'powershell',
    '': 'binary',
    '.exe': 'binary',
}
EXTENSION_LANGUAGE_MAP.update(asmexec.get_extension_language_map())


def normalize_language(language: str | None) -> str | None:
    if language is None:
        return None

    normalized = str(language).strip().lower().replace('_', ' ').replace('-', ' ')
    if not normalized:
        return None

    return LANGUAGE_ALIASES.get(normalized)


def aliases_for_language(language_key: str) -> tuple[str, ...]:
    return tuple(
        alias
        for alias, mapped_language in LANGUAGE_ALIASES.items()
        if mapped_language == language_key
    )


def resolve_language(args: ap.Namespace, ext: str) -> tuple[str | None, str]:
    lang_override = normalize_language(getattr(args, 'lang', None))
    if getattr(args, 'lang', None) and lang_override is None:
        return None, 'override'

    if lang_override:
        return lang_override, 'override'

    return EXTENSION_LANGUAGE_MAP.get(ext), 'extension'
