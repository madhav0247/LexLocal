import re
from typing import List
from src.models import ClauseNode

def detect_xrefs(nodes: List[ClauseNode]):
    patterns = [
        r'(Section\s+\d+(?:\(\d+\))?(?:\([a-z]\))?)',
        r'(clause\s+\d+\.\d+)',
        r'(Article\s+[IVXLC]+)',
        r'(paragraph\s+\([a-z]\))',
        r'(Schedule\s+\d+)',
        r'(sub-section\s+\(\d+\))'
    ]
    
    combined_pattern = re.compile('|'.join(patterns), re.IGNORECASE)
    
    for node in nodes:
        raw_xrefs = []
        for match in combined_pattern.finditer(node.text):
            raw_xref = match.group().strip()
            if raw_xref not in raw_xrefs:
                raw_xrefs.append(raw_xref)
        node.xrefs_raw = raw_xrefs

def resolve_xrefs(nodes: List[ClauseNode]):
    label_to_id = {}
    
    for node in nodes:
        if node.label:
            normalized = re.sub(r'\s+', '', node.label.lower())
            label_to_id[normalized] = node.node_id
            
    for node in nodes:
        resolved = []
        for raw in node.xrefs_raw:
            core_match = re.search(r'([\d\.]+|[IVXLC]+|\([a-z0-9]+\)+)', raw, re.IGNORECASE)
            if core_match:
                core = re.sub(r'\s+', '', core_match.group(1).lower())
                if core in label_to_id:
                    resolved.append(label_to_id[core])
        node.xrefs_resolved = list(set(resolved))
