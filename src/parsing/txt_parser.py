from typing import List
from src.models import Line

def parse_txt(file_path: str) -> List[Line]:
    final_lines = []
    line_idx = 1
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    blocks = content.split("\n\n")
    
    for block in blocks:
        text = block.strip()
        # remove internal newlines
        text = " ".join(text.split())
        
        if not text:
            continue
            
        final_lines.append(Line(
            text=text,
            page=None,
            line_idx=line_idx,
            font_size=None,
            is_bold=False,
            style=None
        ))
        line_idx += 1
        
    return final_lines
