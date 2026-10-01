import json
import os
from typing import List
from src.models import ClauseNode
from src.config import settings

def save_tree(doc_id: str, nodes: List[ClauseNode]):
    os.makedirs(os.path.join(settings.paths.data_dir, "trees"), exist_ok=True)
    tree_path = os.path.join(settings.paths.data_dir, "trees", f"{doc_id}.json")
    
    with open(tree_path, "w", encoding="utf-8") as f:
        json.dump([n.model_dump() for n in nodes], f, indent=2)
        
def load_tree(doc_id: str) -> List[ClauseNode]:
    tree_path = os.path.join(settings.paths.data_dir, "trees", f"{doc_id}.json")
    if not os.path.exists(tree_path):
        return []
        
    with open(tree_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [ClauseNode(**d) for d in data]
