from typing import List
from src.models import Hit
from src.indexing.embedder import embed_texts
from src.indexing.vector_store import get_db
from src.indexing.bm25_index import load_bm25, tokenize
from src.retrieval.fusion import reciprocal_rank_fusion
from src.config import settings
import pandas as pd

def search_dense(query: str, doc_ids: List[str] = None, table_name: str = "clauses") -> List[Hit]:
    query_vector = embed_texts([query], is_query=True)[0]
    db = get_db()
    if table_name not in db.table_names():
        return []
    table = db.open_table(table_name)
    
    search = table.search(query_vector).limit(settings.retrieval.n_dense * 3)
    if doc_ids:
        filter_str = " OR ".join([f"doc_id = '{d}'" for d in doc_ids])
        search = search.where(filter_str)
        
    results = search.to_pandas()
    if results.empty:
        return []
        
    results['score'] = 1 / (1 + results['_distance'])
    id_col = "node_id" if table_name == "clauses" else "chunk_id"
    agg = results.groupby(id_col)['score'].max().reset_index()
    agg = agg.sort_values(by='score', ascending=False).head(settings.retrieval.n_dense)
    
    hits = []
    for rank, row in enumerate(agg.itertuples()):
        hits.append(Hit(
            node_id=getattr(row, id_col),
            score=row.score,
            source="dense",
            rank=rank + 1
        ))
    return hits

def search_sparse(query: str, corpus_name: str = "default") -> List[Hit]:
    bm25_obj, node_ids = load_bm25(corpus_name)
    if not bm25_obj:
        return []
        
    query_tokens = tokenize(query)
    scores = bm25_obj.get_scores(query_tokens)
    
    results = sorted(zip(node_ids, scores), key=lambda x: x[1], reverse=True)
    top_results = results[:settings.retrieval.n_bm25]
    
    hits = []
    for rank, (node_id, score) in enumerate(top_results):
        if score <= 0:
            continue
        hits.append(Hit(
            node_id=node_id,
            score=score,
            source="bm25",
            rank=rank + 1
        ))
    return hits

def hybrid_search(query: str, doc_ids: List[str] = None, corpus_name: str = "default") -> List[Hit]:
    dense_hits = search_dense(query, doc_ids)
    sparse_hits = search_sparse(query, corpus_name)
    
    if doc_ids:
        allowed_docs = set(doc_ids)
        sparse_hits = [h for h in sparse_hits if h.node_id.split(':')[0] in allowed_docs]
        
    fused_hits = reciprocal_rank_fusion(dense_hits, sparse_hits)
    return fused_hits[:settings.retrieval.top_k]
