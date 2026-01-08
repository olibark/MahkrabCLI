import subprocess

from mahkrab.assets.headerTable import searchHeaderTable

def findDependencies(fileLocation: str) -> list[str]:
    flags = [] #holds the flags needed in source
    try:
        with open(fileLocation, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                line = line.strip()
                if not line.startswith('#include'):
                    continue #ignoring non-include lines
                header = (
                    line.replace('#include', '')
                        .replace('<', '').replace('>', '')
                        .replace('"', '').strip() #extracts the file name of the header
                )

                flags = searchHeaderTable(header, flags)

    except FileNotFoundError:
        return []

    expanded_flags = []
    for flag in flags:
        if flag.startswith("pkg-config "):
            try:
                result = subprocess.run(
                    flag.split(),
                    check=True,
                    capture_output=True,
                    text=True,
                )
                expanded_flags.extend(result.stdout.split())
            except (FileNotFoundError, subprocess.CalledProcessError):
                expanded_flags.append(flag)
        else:
            expanded_flags.append(flag)

    return expanded_flags
