import os
import pickle
import re
from typing import List, Tuple
from rank_bm25 import BM25Okapi
from src.models import ClauseNode
from src.config import settings

STOPWORDS = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}

def tokenize(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    tokens = text.split()
    return [t for t in tokens if t not in STOPWORDS]

def get_bm25_path(corpus_name: str = "default"):
    os.makedirs(os.path.join(settings.paths.data_dir, "bm25"), exist_ok=True)
    return os.path.join(settings.paths.data_dir, "bm25", f"{corpus_name}.pkl")

def build_bm25(nodes: List[ClauseNode], corpus_name: str = "default"):
    tokenized_corpus = []
    node_ids = []
    
    for node in nodes:
        path_str = " > ".join(node.path) if node.path else node.doc_title
        full_text = f"{path_str} {node.heading or ''} {node.text}"
        tokenized_corpus.append(tokenize(full_text))
        node_ids.append(node.node_id)
        
    bm25 = BM25Okapi(tokenized_corpus)
    
    path = get_bm25_path(corpus_name)
    with open(path, "wb") as f:
        pickle.dump({"bm25": bm25, "node_ids": node_ids}, f)

def load_bm25(corpus_name: str = "default") -> Tuple[BM25Okapi, List[str]]:
    path = get_bm25_path(corpus_name)
    if not os.path.exists(path):
        return None, []
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data["bm25"], data["node_ids"]
