import pymupdf
import re
from typing import List
from collections import defaultdict
from src.models import Line
import logging

logger = logging.getLogger(__name__)

def parse_pdf(file_path: str) -> List[Line]:
    doc = pymupdf.open(file_path)
    

    # 1st pass: collect text blocks and detect repeating headers/footers
    y_pos_counts = defaultdict(lambda: defaultdict(int)) # text -> y_pos -> count
    total_pages = len(doc)
    
    raw_pages = []
    text_length = 0
    
    for page_num in range(total_pages):
        page = doc[page_num]
        page_dict = page.get_text("dict")
        page_data = []
        for block in page_dict.get("blocks", []):
            if "lines" in block:
                # Group spans on the same line
                for line in block["lines"]:
                    line_text = ""
                    max_font_size = 0.0
                    is_bold = False
                    y_pos = 0.0
                    
                    for span in line["spans"]:
                        span_text = span["text"].strip()
                        if not span_text:
                            continue
                        
                        line_text += span["text"]
                        max_font_size = max(max_font_size, span["size"])
                        if "bold" in span["font"].lower() or "black" in span["font"].lower() or "heavy" in span["font"].lower():
                            is_bold = True
                        y_pos = round(span["bbox"][1])
                    
                    line_text = line_text.strip()
                    if line_text:
                        text_length += len(line_text)
                        y_pos_counts[line_text][y_pos] += 1
                        
                        page_data.append({
                            "text": line_text,
                            "page": page_num + 1,
                            "y_pos": y_pos,
                            "font_size": max_font_size,
                            "is_bold": is_bold
                        })
        raw_pages.append(page_data)
    
    if text_length < 100 and total_pages > 0:
        logger.warning(f"PDF {file_path} likely scanned; OCR not enabled in Phase A.")
    
    # 2nd pass: filter headers/footers and bare page numbers, build lines
    final_lines = []
    line_idx = 1
    
    for page_data in raw_pages:
        for span in page_data:
            text = span["text"]
            y_pos = span["y_pos"]
            
            # Check if it's a repeating header/footer
            if total_pages > 2 and y_pos_counts[text][y_pos] > (total_pages * 0.5):
                continue
                
            # Check if it's a bare page number
            if re.match(r'^[\d\-\sIVXLCivxlc]+$', text) and len(text) < 10:
                continue
                
            final_lines.append(Line(
                text=text,
                page=span["page"],
                line_idx=line_idx,
                font_size=span["font_size"],
                is_bold=span["is_bold"],
                style=None
            ))
            line_idx += 1
            
    return final_lines
