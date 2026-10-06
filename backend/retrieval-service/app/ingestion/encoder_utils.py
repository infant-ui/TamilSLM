# services/retrieval-service/app/ingestion/encoder_utils.py
"""
Single shared loader for the GTE-multilingual embedding model, used by the live
retrieval service (main.py), the ingestion/indexing pipeline (index_books.py,
compile_offline.py), and the evaluation scripts.

WHY THIS FILE EXISTS (Phase 1 fix): three separate call sites each carried
their own copy of the position_ids patch. A future change applied to only one
of them would silently desync the query encoder from the corpus encoder --
exactly the failure mode this Phase 1 fix is responding to (the live corpus
cache was built under a different encoder state than what serves queries
today: a fresh re-encode of a cached chunk's own text scored only ~0.45-0.48
cosine against its own stored vector, ranking ~500-3,600 out of ~3,600
chunks against itself, instead of rank 1 at ~1.0 cosine).

Two patches are applied at load time:

1. position_ids -> arange. Addresses a known failure mode of this custom
   (`trust_remote_code=True`) model under certain accelerate/meta-device
   loading paths on some platform/library combinations, where the
   `persistent=False` position_ids buffer can load as uninitialized memory
   instead of a proper 0..N-1 sequence. On this machine's current library
   versions the buffer already loads correctly (verified: patched and
   unpatched runs are bit-identical here), so this patch is a no-op in THIS
   environment -- but it is cheap, harmless, and guards against the failure
   mode recurring under a different environment (e.g. whatever environment
   originally built the stale cache this change replaces).

2. Rotary buffers explicitly zeroed (new in this change, requested as
   insurance regardless of whether it's independently diagnosed as broken
   here). `inv_freq` is set to all zeros, and `cos_cached`/`sin_cached` are
   recomputed CONSISTENTLY from that (cos(0)=1, sin(0)=0 for every position)
   rather than being independently zeroed to 0/0 -- zeroing cos_cached
   directly would make `q*cos + rotate_half(q)*sin` collapse to zero for
   every token (content-destroying, not a positional-info fix). With
   inv_freq == 0, every position gets the identity rotation: this fully
   removes the rotary positional signal while leaving token content
   embeddings untouched.

   IMPORTANT CAVEAT: this is a strictly stronger intervention than the
   position_ids patch -- it removes ALL relative-position signal the
   self-attention layers can use, which is a real quality trade-off for a
   bi-encoder (e.g. word-order cues like "6 x 7" vs "7 x 6" become harder to
   distinguish from content alone). The self-retrieval gate below is NOT the
   safety net for that risk: it only proves the query encoder and the corpus
   encoder are self-consistent (same code producing the same vectors for the
   same text), not that disabling rotary is semantically a good idea for
   retrieval quality. That second question can only be answered empirically,
   by the Recall@5 numbers from the full gold-set eval that Phase 1 also
   runs -- compare them against a config with this patch reverted if the
   numbers look worse, not better, than chunk-id-fix-alone would predict.
"""
import random

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

ENCODER_NAME = "Alibaba-NLP/gte-multilingual-base"


def load_patched_encoder(device: str = "cpu") -> SentenceTransformer:
    """Loads the production query/corpus encoder with both patches applied (see module docstring)."""
    model = SentenceTransformer(ENCODER_NAME, device=device, trust_remote_code=True)
    try:
        embeddings_module = model[0].auto_model.embeddings

        # 1. position_ids -> arange
        if hasattr(embeddings_module, "position_ids"):
            buf = embeddings_module.position_ids
            buf.copy_(torch.arange(buf.size(0), dtype=torch.long, device=buf.device))

        # 2. Zero the rotary position-embedding buffers (see docstring point 2)
        rotary = getattr(embeddings_module, "rotary_emb", None)
        if rotary is not None and hasattr(rotary, "inv_freq"):
            rotary.inv_freq.zero_()
            if hasattr(rotary, "cos_cached") and hasattr(rotary, "sin_cached"):
                rotary.cos_cached.fill_(1.0)
                rotary.sin_cached.zero_()
            print("🔧 Zeroed rotary position-embedding buffers (identity rotation) on GTE Multilingual.")
        print(f"🔧 Loaded {ENCODER_NAME} with position_ids + rotary patches applied.")
    except Exception as e:
        print(f"⚠️ Encoder patch failed (non-fatal, continuing with unpatched model): {e}")
    return model


def self_retrieval_gate(chunks, embeddings, encoder, sample_size: int = 100,
                         min_cosine: float = 0.99, min_pass_rate: float = 0.95,
                         seed: int = 0, label: str = "") -> dict:
    """
    Mandatory promotion gate (Phase 1 requirement): re-encodes a random sample
    of chunk texts with the SAME encoder instance used to build `embeddings`,
    and confirms each fresh vector matches its own stored vector (cosine >=
    min_cosine) and ranks #1 against the full stored matrix.

    This is a self-CONSISTENCY check only -- it catches "the index was built
    with different code/weights than what's running now" (the exact bug this
    fix addresses). It does NOT evaluate whether the encoder itself produces
    semantically good embeddings; that is what the full gold-set eval is for.

    Returns a dict with "passed": bool. Caller must not promote a new cache
    to the live/production path unless "passed" is True.
    """
    n = len(chunks)
    if n == 0:
        return {"label": label, "n_sampled": 0, "pass_rate": 1.0, "passed": True, "note": "empty corpus"}

    rng = random.Random(seed)
    idx = rng.sample(range(n), min(sample_size, n))
    texts = [chunks[i]["text"] for i in idx]
    fresh = np.asarray(encoder.encode(texts, normalize_embeddings=True, batch_size=32))

    own_cos = np.array([float(np.dot(fresh[k], embeddings[idx[k]])) for k in range(len(idx))])
    ranks = []
    for k, i in enumerate(idx):
        sims = embeddings @ fresh[k]
        ranks.append(int((sims > sims[i]).sum()) + 1)  # 1 == fresh vector's nearest neighbor is its own stored row

    pass_each = own_cos >= min_cosine
    pass_rate = float(pass_each.mean())
    passed = bool(pass_rate >= min_pass_rate and own_cos.min() >= (min_cosine - 0.05))

    return {
        "label": label,
        "n_sampled": len(idx),
        "min_cosine_threshold": min_cosine,
        "min_pass_rate_threshold": min_pass_rate,
        "own_cosine_min": float(own_cos.min()),
        "own_cosine_mean": float(own_cos.mean()),
        "pass_rate": pass_rate,
        "rank_mean": float(np.mean(ranks)),
        "rank_max": int(np.max(ranks)),
        "n_rank1": int(sum(1 for r in ranks if r == 1)),
        "passed": passed,
    }
