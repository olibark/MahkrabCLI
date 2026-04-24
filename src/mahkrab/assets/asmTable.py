from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AssemblyDependencyEntry:
    compile_flags: tuple[str, ...] = ()
    link_flags: tuple[str, ...] = ()
    prefer_compiler_linker: bool = False
    add_no_pie: bool = False


ASSEMBLY_INCLUDE_TABLE = {
    'sdl2/sdl.inc': AssemblyDependencyEntry(link_flags=('-lSDL2',), prefer_compiler_linker=True),
    'sdl2/sdl_image.inc': AssemblyDependencyEntry(link_flags=('-lSDL2_image',), prefer_compiler_linker=True),
    'sdl2/sdl_ttf.inc': AssemblyDependencyEntry(link_flags=('-lSDL2_ttf',), prefer_compiler_linker=True),
    'sdl2/sdl_mixer.inc': AssemblyDependencyEntry(link_flags=('-lSDL2_mixer',), prefer_compiler_linker=True),
    'sdl2/sdl_net.inc': AssemblyDependencyEntry(link_flags=('-lSDL2_net',), prefer_compiler_linker=True),
}

ASSEMBLY_SYMBOL_TABLE = {
    'main': AssemblyDependencyEntry(prefer_compiler_linker=True, add_no_pie=True),
    'printf': AssemblyDependencyEntry(prefer_compiler_linker=True, add_no_pie=True),
    'puts': AssemblyDependencyEntry(prefer_compiler_linker=True, add_no_pie=True),
    'putchar': AssemblyDependencyEntry(prefer_compiler_linker=True, add_no_pie=True),
    'scanf': AssemblyDependencyEntry(prefer_compiler_linker=True, add_no_pie=True),
    'fprintf': AssemblyDependencyEntry(prefer_compiler_linker=True, add_no_pie=True),
    'sprintf': AssemblyDependencyEntry(prefer_compiler_linker=True, add_no_pie=True),
    'snprintf': AssemblyDependencyEntry(prefer_compiler_linker=True, add_no_pie=True),
    'malloc': AssemblyDependencyEntry(prefer_compiler_linker=True, add_no_pie=True),
    'calloc': AssemblyDependencyEntry(prefer_compiler_linker=True, add_no_pie=True),
    'realloc': AssemblyDependencyEntry(prefer_compiler_linker=True, add_no_pie=True),
    'free': AssemblyDependencyEntry(prefer_compiler_linker=True, add_no_pie=True),
    'exit': AssemblyDependencyEntry(prefer_compiler_linker=True, add_no_pie=True),
    'sin': AssemblyDependencyEntry(link_flags=('-lm',), prefer_compiler_linker=True),
    'cos': AssemblyDependencyEntry(link_flags=('-lm',), prefer_compiler_linker=True),
    'tan': AssemblyDependencyEntry(link_flags=('-lm',), prefer_compiler_linker=True),
    'asin': AssemblyDependencyEntry(link_flags=('-lm',), prefer_compiler_linker=True),
    'acos': AssemblyDependencyEntry(link_flags=('-lm',), prefer_compiler_linker=True),
    'atan': AssemblyDependencyEntry(link_flags=('-lm',), prefer_compiler_linker=True),
    'atan2': AssemblyDependencyEntry(link_flags=('-lm',), prefer_compiler_linker=True),
    'sqrt': AssemblyDependencyEntry(link_flags=('-lm',), prefer_compiler_linker=True),
    'pow': AssemblyDependencyEntry(link_flags=('-lm',), prefer_compiler_linker=True),
    'exp': AssemblyDependencyEntry(link_flags=('-lm',), prefer_compiler_linker=True),
    'log': AssemblyDependencyEntry(link_flags=('-lm',), prefer_compiler_linker=True),
    'log10': AssemblyDependencyEntry(link_flags=('-lm',), prefer_compiler_linker=True),
    'ceil': AssemblyDependencyEntry(link_flags=('-lm',), prefer_compiler_linker=True),
    'floor': AssemblyDependencyEntry(link_flags=('-lm',), prefer_compiler_linker=True),
    'round': AssemblyDependencyEntry(link_flags=('-lm',), prefer_compiler_linker=True),
    'fmod': AssemblyDependencyEntry(link_flags=('-lm',), prefer_compiler_linker=True),
}

ASSEMBLY_SYMBOL_PREFIX_TABLE = (
    ('pthread_', AssemblyDependencyEntry(link_flags=('-pthread',), prefer_compiler_linker=True)),
    ('sdl_', AssemblyDependencyEntry(link_flags=('-lSDL2',), prefer_compiler_linker=True)),
    ('img_', AssemblyDependencyEntry(link_flags=('-lSDL2_image',), prefer_compiler_linker=True)),
    ('ttf_', AssemblyDependencyEntry(link_flags=('-lSDL2_ttf',), prefer_compiler_linker=True)),
    ('mix_', AssemblyDependencyEntry(link_flags=('-lSDL2_mixer',), prefer_compiler_linker=True)),
    ('sdlnet_', AssemblyDependencyEntry(link_flags=('-lSDL2_net',), prefer_compiler_linker=True)),
    ('curl_', AssemblyDependencyEntry(link_flags=('-lcurl',), prefer_compiler_linker=True)),
    ('sqlite3_', AssemblyDependencyEntry(link_flags=('-lsqlite3',), prefer_compiler_linker=True)),
    ('png_', AssemblyDependencyEntry(link_flags=('-lpng',), prefer_compiler_linker=True)),
    ('uuid_', AssemblyDependencyEntry(link_flags=('-luuid',), prefer_compiler_linker=True)),
    ('ssl_', AssemblyDependencyEntry(link_flags=('-lssl', '-lcrypto'), prefer_compiler_linker=True)),
    ('evp_', AssemblyDependencyEntry(link_flags=('-lssl', '-lcrypto'), prefer_compiler_linker=True)),
    ('sha1_', AssemblyDependencyEntry(link_flags=('-lcrypto',), prefer_compiler_linker=True)),
    ('sha224_', AssemblyDependencyEntry(link_flags=('-lcrypto',), prefer_compiler_linker=True)),
    ('sha256_', AssemblyDependencyEntry(link_flags=('-lcrypto',), prefer_compiler_linker=True)),
    ('sha384_', AssemblyDependencyEntry(link_flags=('-lcrypto',), prefer_compiler_linker=True)),
    ('sha512_', AssemblyDependencyEntry(link_flags=('-lcrypto',), prefer_compiler_linker=True)),
    ('hmac_', AssemblyDependencyEntry(link_flags=('-lcrypto',), prefer_compiler_linker=True)),
)


def searchAssemblyIncludeTable(include_name: str) -> AssemblyDependencyEntry | None:
    return ASSEMBLY_INCLUDE_TABLE.get(str(include_name).strip().lower())


def searchAssemblySymbolTable(symbol_name: str) -> AssemblyDependencyEntry | None:
    normalized_symbol = str(symbol_name).strip().lower()
    if not normalized_symbol:
        return None

    direct_match = ASSEMBLY_SYMBOL_TABLE.get(normalized_symbol)
    if direct_match is not None:
        return direct_match

    if normalized_symbol.startswith('x') and normalized_symbol in {
        'xopendisplay',
        'xclosedisplay',
        'xcreatewindow',
        'xmapwindow',
        'xnextevent',
        'xpending',
        'xdefaultscreen',
        'xrootwindow',
        'xselectinput',
        'xstorename',
        'xflush',
    }:
        return AssemblyDependencyEntry(link_flags=('-lX11',), prefer_compiler_linker=True)

    for prefix, entry in ASSEMBLY_SYMBOL_PREFIX_TABLE:
        if normalized_symbol.startswith(prefix):
            return entry

    return None
