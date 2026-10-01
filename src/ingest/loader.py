import os
from typing import List
from src.models import Line
from src.parsing.pdf_parser import parse_pdf
from src.parsing.docx_parser import parse_docx
from src.parsing.txt_parser import parse_txt

def load_document(file_path: str) -> List[Line]:
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return parse_docx(file_path)
    elif ext == ".txt":
        return parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
