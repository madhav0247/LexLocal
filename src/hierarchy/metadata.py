import hashlib
from typing import List
from src.models import ClauseNode

def encode_metadata(file_path: str, nodes: List[ClauseNode]):
    with open(file_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()[:8]
        
    for node in nodes:
        node.version = file_hash
        node.token_count = int(len(node.text.split()) * 1.3)
        
def citation_str(node: ClauseNode) -> str:
    parts = []
    parts.append(node.doc_title)
    
    if node.path and node.path != ["flat"]:
        parts.append(" › ".join(node.path))
        
    if node.page_start is not None:
        if node.page_end and node.page_end > node.page_start:
             parts.append(f"p.{node.page_start}-{node.page_end}")
        else:
             parts.append(f"p.{node.page_start}")
    else:
        if node.line_end > node.line_start:
             parts.append(f"paras {node.line_start}-{node.line_end}")
        else:
             parts.append(f"para {node.line_start}")
        
    return ", ".join(parts)
