# services/retrieval-service/app/retrieval/transliteration.py
"""
Phase 2: Tanglish (romanized Tamil) -> Tamil-script transliteration, used to give
Tanglish queries a second retrieval leg against the Tamil corpus in its own script,
alongside the original Latin-script form against the English corpus.

Uses the `indic-transliteration` library (ITRANS scheme) rather than hand-rolled
rules, per the Phase 2 instruction to prefer an existing lightweight library. ITRANS
assumes a fairly formal/consistent romanization convention and colloquial Tanglish is
informal, so the output is approximate, not a clean orthographic transliteration (e.g.
"enna" -> "ஏந்ந" rather than the orthographically correct "என்ன") -- it is intended to
get BM25/dense retrieval closer to the real Tamil-script vocabulary than the raw Latin
query would be against a Tamil-script index, not to produce publication-quality Tamil.
"""
import logging

logger = logging.getLogger("retrieval.transliteration")

try:
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate as _transliterate
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    logger.warning("indic_transliteration not installed; Tanglish transliteration leg will be skipped.")


def transliterate_tanglish_to_tamil(query: str) -> str:
    """
    Best-effort romanized-Tamil -> Tamil-script transliteration. Returns the
    original query unchanged if the library isn't available or transliteration
    fails for any reason -- callers must treat an unchanged return value as "no
    transliteration happened" and skip the extra retrieval leg, not treat it as
    a (coincidentally identical) transliteration result.
    """
    if not _AVAILABLE or not query or not query.strip():
        return query
    try:
        return _transliterate(query, sanscript.ITRANS, sanscript.TAMIL)
    except Exception as e:
        logger.warning(f"Transliteration failed for query (falling back to original text): {e}")
        return query


def is_tanglish(query: str) -> bool:
    """
    Heuristic: a query is "Tanglish" (romanized Tamil, as distinct from genuine
    bilingual code-mixed text that already contains real Tamil script) if it
    contains NO Tamil Unicode characters (U+0B80-U+0BFF) at all but does contain
    at least one common Tanglish marker word. This mirrors how gold_dataset.json
    itself distinguishes the "bilingual" (mixed-script) and "tanglish" (pure
    Latin-script, romanized) query categories.
    """
    import re
    if re.search(r"[஀-௿]", query):
        return False  # real Tamil script present -> this is "bilingual", not "tanglish"
    markers = ("enna", "irukku", "venum", "sollunga", "nu ", "na ", "oda ", "adhu", "idhu",
               "evlo", "yen", "epdi", "eppadi", "pannunga", "irundhu", "kudu", "vanga")
    q = query.lower()
    return any(m in q for m in markers)
