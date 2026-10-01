import re
from typing import List, Tuple, Optional, Dict
from src.models import Line

def match_heading_pattern(text: str) -> Optional[Tuple[str, str, str]]:
    text = text.strip()
    
    # 1. Keyword headings
    m = re.match(r'^((?:PART|CHAPTER|ARTICLE|SCHEDULE|ANNEXURE|APPENDIX)\s+[IVXLC\d]+)([\.\:\-\s]*)(.*)', text, re.IGNORECASE)
    if m:
        return ("keyword", m.group(1).strip(), m.group(3).strip())
        
    m = re.match(r'^(SECTION\s+\d+[A-Z]?)([\.\:\-\s]*)(.*)', text, re.IGNORECASE)
    if m:
        return ("keyword", m.group(1).strip(), m.group(3).strip())
        
    # 2. Decimal numbering
    m = re.match(r'^(\d+\.\d+\.\d+\.?)([\.\:\-\s]*)(.*)', text)
    if m:
        return ("decimal_3", m.group(1).strip(), m.group(3).strip())
        
    m = re.match(r'^(\d+\.\d+\.?)([\.\:\-\s]*)(.*)', text)
    if m:
        return ("decimal_2", m.group(1).strip(), m.group(3).strip())
        
    m = re.match(r'^(\d+\.)\s+([A-Z].*)', text)
    if m:
        return ("decimal_1", m.group(1).strip(), m.group(2).strip())
        
    # 3. Bare section numbers (Indian statutes)
    m = re.match(r'^(\d+[A-Z]?\.)([\.\:\-\s]*)(.*)', text)
    if m:
        return ("bare_num", m.group(1).strip(), m.group(3).strip())
        
    # 4. Lettered sub-clauses and roman
    m = re.match(r'^(\([a-z]\))([\.\:\-\s]*)(.*)', text)
    if m:
        return ("letter", m.group(1).strip(), m.group(3).strip())
        
    m = re.match(r'^(\([ivxlc]+\))([\.\:\-\s]*)(.*)', text)
    if m:
        return ("roman", m.group(1).strip(), m.group(3).strip())
        
    m = re.match(r'^(\(\d+\))([\.\:\-\s]*)(.*)', text)
    if m:
        return ("paren_num", m.group(1).strip(), m.group(3).strip())
        
    # 5. Proviso / Explanation
    m = re.match(r'^(Provided that|Explanation|Illustration|Exception)(.*)', text, re.IGNORECASE)
    if m:
        return ("proviso", m.group(1).strip(), m.group(2).strip())
        
    return None

def is_strong_heading(line: Line, body_median_font: float) -> bool:
    word_count = len(line.text.split())
    if word_count > 12:
        return False
        
    if line.text.endswith('.'):
        return False
        
    is_large = line.font_size is not None and line.font_size > (body_median_font + 0.5)
    is_caps = line.text.isupper() and len(re.sub(r'[^a-zA-Z]', '', line.text)) > 3
    
    signals = sum([is_large, line.is_bold, is_caps])
    return signals >= 2

def detect_headings(lines: List[Line]) -> List[Dict]:
    font_sizes = [l.font_size for l in lines if l.font_size is not None]
    if font_sizes:
        sorted_fonts = sorted(font_sizes)
        body_median_font = sorted_fonts[len(sorted_fonts) // 2]
    else:
        body_median_font = 0.0
        
    results = []
    
    for line in lines:
        pattern_match = match_heading_pattern(line.text)
        strong_heading = is_strong_heading(line, body_median_font)
        
        is_heading = False
        pattern_type = None
        label = None
        heading_text = None
        
        if pattern_match:
            pattern_type, label, heading_text = pattern_match
            is_heading = True
        elif strong_heading:
            is_heading = True
            pattern_type = "style_based"
            label = ""
            heading_text = line.text
            
        results.append({
            "line": line,
            "is_heading": is_heading,
            "pattern_type": pattern_type,
            "label": label,
            "heading_text": heading_text
        })
        
    return results
