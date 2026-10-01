from fastembed import TextEmbedding
from typing import List
import os

# Disable HuggingFace symlinks warning on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from src.config import settings

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = TextEmbedding(model_name=settings.embedding.model)
    return _embedder

def embed_texts(texts: List[str], is_query: bool = False) -> List[List[float]]:
    embedder = get_embedder()
    if is_query:
        texts = [f"Represent this sentence for searching relevant passages: {t}" for t in texts]
    
    embeddings = list(embedder.embed(texts, batch_size=settings.embedding.batch_size))
    return [e.tolist() for e in embeddings]
