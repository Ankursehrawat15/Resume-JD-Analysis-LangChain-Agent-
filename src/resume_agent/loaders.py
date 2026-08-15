from pathlib import Path

class InputError(Exception):
    """Bad user input (missing/empty/undreadable file)."""


"""Load the JD text from the given path"""

def load_jd_text(path: str | Path) -> str:
    p = Path(path)
    if not p.exists():
        raise InputError(f"jd File does not exist: {p}")
    if not p.is_file():
        raise InputError(f"JD path is not a file: {p}")

    text = p.read_text(encoding="utf-8".strip())
    if not text:
        raise InputError(f"JD file is empty: {p}")
    return text        

    