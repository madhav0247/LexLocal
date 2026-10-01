import docx
from typing import List
from src.models import Line

def parse_docx(file_path: str) -> List[Line]:
    doc = docx.Document(file_path)
    
    final_lines = []
    line_idx = 1
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
            
        style_name = para.style.name if para.style else None
        
        # Calculate bold ratio
        bold_chars = 0
        total_chars = sum(len(run.text) for run in para.runs)
        
        for run in para.runs:
            if run.bold:
                bold_chars += len(run.text)
                
        is_bold = False
        if total_chars > 0 and (bold_chars / total_chars) > 0.5:
            is_bold = True
            
        final_lines.append(Line(
            text=text,
            page=None,
            line_idx=line_idx,
            font_size=None,
            is_bold=is_bold,
            style=style_name
        ))
        line_idx += 1
        
    return final_lines
