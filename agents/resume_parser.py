from pypdf import PdfReader


def read_resume_text(resume_path: str) -> str:
    reader = PdfReader(resume_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text.strip()