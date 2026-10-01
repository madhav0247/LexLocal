from typing import List
from src.models import Hit
from collections import defaultdict
from src.config import settings

def reciprocal_rank_fusion(dense_hits: List[Hit], sparse_hits: List[Hit]) -> List[Hit]:
    scores = defaultdict(float)
    k = settings.retrieval.rrf_k
    
    for idx, hit in enumerate(dense_hits):
        scores[hit.node_id] += 1.0 / (k + idx + 1)
        
    for idx, hit in enumerate(sparse_hits):
        scores[hit.node_id] += 1.0 / (k + idx + 1)
        
    fused = []
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    for rank, (node_id, score) in enumerate(sorted_scores):
        fused.append(Hit(
            node_id=node_id,
            score=score,
            source="fused",
            rank=rank + 1
        ))
        
    return fused
