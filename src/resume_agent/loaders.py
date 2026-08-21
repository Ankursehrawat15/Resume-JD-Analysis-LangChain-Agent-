from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader 
from resume_agent.schemas import ResumeDocument

class InputError(Exception):
    """Bad user input (missing/empty/undreadable file)."""


"""Load the JD text from the given path"""

def load_jd_text(path: str | Path) -> str:
    p = Path(path)
    if not p.exists():
        raise InputError(f"jd File does not exist: {p}")
    if not p.is_file():
        raise InputError(f"JD path is not a file: {p}")

    text = p.read_text(encoding="utf-8").strip()
    if not text:
        raise InputError(f"JD file is empty: {p}")
    return text        


def load_resume(path: str | Path) -> ResumeDocument:
    p = Path(path)
    if not p.exists():
        raise InputError(f"Resume file not found: {p}")
    if not p.is_file():
        raise InputError(f"Resume path is not a file: {p}")
    
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        # check cleanUp is requried or not 
        try:
            loader = PyPDFLoader(str(p))
            resume_doc = loader.load()
        except Exception as exc:
            raise InputError(f"Could not read resume PDF: {p}")
        raw = "\n".join(doc.page_content for doc in resume_doc)
        page_count = len(resume_doc)    
        
    else:
        raise InputError(f"Unsupported resume type {suffix}, Use .pdf file")

    if not raw:
        raise InputError(f"Resume file is empty: {p}")
    return ResumeDocument(
        raw_text=raw,
        source_path=str(p),
        page_count=page_count
    )     