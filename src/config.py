import yaml
from pathlib import Path
from pydantic import BaseModel

class PathsConfig(BaseModel):
    data_dir: str = "data"
    models_dir: str = "models"

class ParsingConfig(BaseModel):
    min_headings_for_structure: int = 3
    drop_repeating_headers: bool = True

class EmbeddingConfig(BaseModel):
    model: str = "BAAI/bge-small-en-v1.5"
    batch_size: int = 32
    max_tokens: int = 512

class RetrievalConfig(BaseModel):
    n_bm25: int = 20
    n_dense: int = 20
    top_k: int = 5
    fusion: str = "rrf"
    rrf_k: int = 60
    use_summary_boost: bool = False

class ContextConfig(BaseModel):
    max_tokens: int = 3000
    max_xrefs_per_hit: int = 2

class BaselineConfig(BaseModel):
    chunk_tokens: int = 512
    overlap: int = 64

class LlmConfig(BaseModel):
    backend: str = "null"

class Settings(BaseModel):
    paths: PathsConfig
    parsing: ParsingConfig
    embedding: EmbeddingConfig
    retrieval: RetrievalConfig
    context: ContextConfig
    baseline: BaselineConfig
    llm: LlmConfig

def load_settings(config_path: str = "config/settings.yaml") -> Settings:
    try:
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
        return Settings(**data)
    except Exception as e:
        # Provide defaults if not found (mostly for tests if paths differ)
        return Settings(
            paths=PathsConfig(),
            parsing=ParsingConfig(),
            embedding=EmbeddingConfig(),
            retrieval=RetrievalConfig(),
            context=ContextConfig(),
            baseline=BaselineConfig(),
            llm=LlmConfig()
        )

settings = load_settings()
