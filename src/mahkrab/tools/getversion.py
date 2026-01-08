from importlib.metadata import PackageNotFoundError, version as pkg_version

def get_version() -> str:
    try:
        return pkg_version("mahkrab")
    except PackageNotFoundError:
        return "unknown"