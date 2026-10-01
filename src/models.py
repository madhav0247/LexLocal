from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class NodeType(str, Enum):
    root = "root"
    part = "part"
    chapter = "chapter"
    article = "article"
    section = "section"
    subsection = "subsection"
    clause = "clause"
    subclause = "subclause"
    schedule = "schedule"
    paragraph = "paragraph"
    flat = "flat"

class Line(BaseModel):
    text: str
    page: Optional[int]
    line_idx: int
    font_size: Optional[float]
    is_bold: bool
    style: Optional[str]

class ClauseNode(BaseModel):
    node_id: str
    doc_id: str
    doc_title: str
    node_type: NodeType
    level: int
    label: str
    heading: Optional[str] = None
    text: str
    parent_id: Optional[str] = None
    children_ids: List[str] = Field(default_factory=list)
    path: List[str] = Field(default_factory=list)
    order: int
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    line_start: int
    line_end: int
    xrefs_raw: List[str] = Field(default_factory=list)
    xrefs_resolved: List[str] = Field(default_factory=list)
    version: str
    token_count: int

class Hit(BaseModel):
    node_id: str
    score: float
    source: str # "bm25", "dense", "fused"
    rank: int

class ContextItem(BaseModel):
    clause: ClauseNode
    parent_chain: List[ClauseNode]
    xref_clauses: List[ClauseNode]
    citation_str: str

class ContextBundle(BaseModel):
    query: str
    mode: str # "hierarchical" or "naive"
    hits: List[Hit]
    items: List[ContextItem]
    total_tokens: int
