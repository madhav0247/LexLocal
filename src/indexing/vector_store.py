import os
import lancedb
import pyarrow as pa
from typing import List, Dict, Any
from src.models import ClauseNode
from src.config import settings
from src.indexing.embedder import embed_texts
from lancedb.pydantic import LanceModel, Vector

def get_db():
    os.makedirs(settings.paths.data_dir, exist_ok=True)
    db_path = os.path.join(settings.paths.data_dir, "lancedb")
    return lancedb.connect(db_path)

def _chunk_text(text: str, max_words: int = 350) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunks.append(" ".join(words[i:i+max_words]))
    return chunks or [""]

def ingest_clauses(nodes: List[ClauseNode]):
    db = get_db()
    
    schema = pa.schema([
        pa.field("node_id", pa.string()),
        pa.field("doc_id", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), 384)),
        pa.field("text", pa.string()),
        pa.field("path_str", pa.string()),
        pa.field("level", pa.int32()),
        pa.field("node_type", pa.string()),
        pa.field("page_start", pa.int32()),
        pa.field("line_start", pa.int32()),
        pa.field("version", pa.string()),
        pa.field("window_idx", pa.int32())
    ])
    
    if "clauses" not in db.table_names():
        table = db.create_table("clauses", schema=schema)
    else:
        table = db.open_table("clauses")
        
    doc_ids = list(set(n.doc_id for n in nodes))
    for doc_id in doc_ids:
        table.delete(f"doc_id = '{doc_id}'")
        
    record_meta = []
    texts_to_embed = []
    
    for node in nodes:
        path_str = " > ".join(node.path) if node.path else node.doc_title
        contextual_prefix = f"{path_str}: {node.heading or ''}. "
        
        chunks = _chunk_text(node.text)
        
        for idx, chunk in enumerate(chunks):
            full_text = contextual_prefix + chunk
            texts_to_embed.append(full_text)
            
            record_meta.append({
                "node_id": node.node_id,
                "doc_id": node.doc_id,
                "text": node.text,
                "path_str": path_str,
                "level": node.level,
                "node_type": node.node_type.value,
                "page_start": node.page_start or -1,
                "line_start": node.line_start,
                "version": node.version,
                "window_idx": idx
            })
            
    batch_size = settings.embedding.batch_size
    for i in range(0, len(texts_to_embed), batch_size):
        batch_texts = texts_to_embed[i:i+batch_size]
        batch_meta = record_meta[i:i+batch_size]
        
        embeddings = embed_texts(batch_texts)
        
        batch_records = []
        for meta, emb in zip(batch_meta, embeddings):
            meta["vector"] = emb
            batch_records.append(meta)
            
        if batch_records:
            table.add(batch_records)
