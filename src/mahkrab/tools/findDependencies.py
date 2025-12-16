from mahkrab.assets.headerTable import searchHeaderTable

def findDependencies(fileLocation: str) -> str:
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
        return ''
    return ' ' + ' '.join(flags) if flags else ''