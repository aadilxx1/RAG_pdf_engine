# models/dense_encoder.py
from sentence_transformers import SentenceTransformer
_model = None
from utils.cache import cached_embedding


def get_model(name="sentence-transformers/all-MiniLM-L6-v2"):
    global _model
    if _model is None:
        _model = SentenceTransformer(name)
    return _model

def encode(texts):
    """
    texts: list[str] -> returns numpy array or list of vectors
    """
    model = get_model()
    return model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
