from typing import List
from sentence_transformers import SentenceTransformer

# Load once and reuse
_model = None

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

def _load_model():
    global _model

    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    return _model

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts."""

    model = _load_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    return embeddings.tolist()

def embed_query(text: str) -> List[float]:
    """Generate embedding for a user query."""

    return embed_texts([text])[0]