from typing import List, Dict, Any
from src.models import Line
from src.config import settings
from src.indexing.embedder import embed_texts
from src.indexing.vector_store import get_db
import pyarrow as pa

def generate_naive_chunks(doc_id: str, lines: List[Line]) -> List[Dict[str, Any]]:
    chunk_tokens = settings.baseline.chunk_tokens
    overlap_tokens = settings.baseline.overlap
    
    chunk_chars = chunk_tokens * 5
    overlap_chars = overlap_tokens * 5
    
    full_text = ""
    char_to_page = {}
    
    current_char = 0
    for line in lines:
        text = line.text + " "
        full_text += text
        
        if line.page:
            char_to_page[current_char] = line.page
            
        current_char += len(text)
        
    page_map = sorted(char_to_page.items())
    
    def get_page_for_char(char_idx: int) -> int:
        best_page = -1
        for start_c, pg in page_map:
            if char_idx >= start_c:
                best_page = pg
            else:
                break
        return best_page
        
    chunks = []
    start = 0
    idx = 1
    while start < len(full_text):
        end = min(start + chunk_chars, len(full_text))
        text_chunk = full_text[start:end].strip()
        
        if text_chunk:
            chunks.append({
                "chunk_id": f"{doc_id}:chunk_{idx}",
                "doc_id": doc_id,
                "text": text_chunk,
                "page_start": get_page_for_char(start),
                "char_start": start,
                "char_end": end
            })
            idx += 1
            
        if end == len(full_text):
            break
            
        start += (chunk_chars - overlap_chars)
        
    return chunks

def ingest_naive_chunks(chunks: List[Dict[str, Any]]):
    db = get_db()
    
    schema = pa.schema([
        pa.field("chunk_id", pa.string()),
        pa.field("doc_id", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), 384)),
        pa.field("text", pa.string()),
        pa.field("page_start", pa.int32()),
        pa.field("char_start", pa.int32()),
        pa.field("char_end", pa.int32())
    ])
    
    if "naive_chunks" not in db.table_names():
        table = db.create_table("naive_chunks", schema=schema)
    else:
        table = db.open_table("naive_chunks")
        
    if not chunks:
        return
        
    doc_ids = list(set(c["doc_id"] for c in chunks))
    for doc_id in doc_ids:
        table.delete(f"doc_id = '{doc_id}'")
        
    batch_size = settings.embedding.batch_size
    records = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        texts_to_embed = [c["text"] for c in batch]
        embeddings = embed_texts(texts_to_embed)
        for chunk, emb in zip(batch, embeddings):
            chunk["vector"] = emb
            records.append(chunk)
            
    if records:
        table.add(records)
