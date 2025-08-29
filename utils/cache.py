# utils/cache.py
import hashlib
from cachetools import TTLCache
from functools import wraps

# small in-memory caches (per-process)
SEARCH_CACHE = TTLCache(maxsize=1000, ttl=60 * 30)   # 30 minutes
GEN_CACHE    = TTLCache(maxsize=1000, ttl=60 * 60)   # 60 minutes
EMB_CACHE    = TTLCache(maxsize=5000, ttl=60 * 60 * 24)  # embeddings longer-lived

def _make_hash_key(*parts) -> str:
    h = hashlib.sha256("||".join(map(str, parts)).encode("utf-8")).hexdigest()
    return h

def cached_search(fn):
    @wraps(fn)
    def wrapper(query, top_k=5, mode="hybrid", *args, **kwargs):
        key = _make_hash_key("search", mode, top_k, query)
        if key in SEARCH_CACHE:
            return SEARCH_CACHE[key]
        res = fn(query, top_k=top_k, mode=mode, *args, **kwargs)
        SEARCH_CACHE[key] = res
        return res
    return wrapper

def cached_gen(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        key = _make_hash_key("gen", str(args), str(kwargs))
        if key in GEN_CACHE:
            return GEN_CACHE[key]
        res = fn(*args, **kwargs)
        GEN_CACHE[key] = res
        return res
    return wrapper

def cached_embedding(fn):
    @wraps(fn)
    def wrapper(text, *args, **kwargs):
        key = _make_hash_key("emb", text)
        if key in EMB_CACHE:
            return EMB_CACHE[key]
        v = fn(text, *args, **kwargs)
        EMB_CACHE[key] = v
        return v
    return wrapper

# helpers to clear caches (call on re-ingest)
def clear_all_caches():
    SEARCH_CACHE.clear()
    GEN_CACHE.clear()
    EMB_CACHE.clear()
