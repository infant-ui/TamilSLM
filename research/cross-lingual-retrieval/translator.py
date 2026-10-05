"""
translator.py
-------------
Language detection + Tamil translation.

Translation priority:
  1. Anthropic Claude API  (no network issues, no rate limits for local use)
  2. deep-translator / Google Translate  (fallback if ANTHROPIC_API_KEY missing)
  3. argostranslate  (offline fallback)

Set ANTHROPIC_API_KEY in your .env to enable priority-1.
"""

import os
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 42

# ---------------------------------------------------------------------------
# Backend 1 — Anthropic Claude API  (best quality, no external network needed)
# ---------------------------------------------------------------------------

def _translate_anthropic(text: str, from_code: str, to_code: str) -> str:
    """Translate using the Anthropic Claude API."""
    try:
        import requests as _req
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return None

        lang_names = {"en": "English", "ta": "Tamil"}
        src_name   = lang_names.get(from_code, from_code)
        tgt_name   = lang_names.get(to_code,   to_code)

        if to_code == "ta":
            instruction = (
                f"Translate the following {src_name} science text into fluent, "
                f"natural {tgt_name}. Output ONLY the translated text — no explanations, "
                f"no labels, no English. Use proper Tamil Unicode characters.\n\n"
                f"Text to translate:\n{text}"
            )
        else:
            instruction = (
                f"Translate the following {src_name} text into {tgt_name}. "
                f"Output ONLY the translated text — no explanations, no labels.\n\n"
                f"Text to translate:\n{text}"
            )

        payload = {
            "model": "claude-haiku-4-5-20251001",   # fast + cheap for translation
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": instruction}],
        }
        resp = _req.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()["content"][0]["text"].strip()
        print(f"[TRANSLATOR] Anthropic API ({from_code}→{to_code}) succeeded ✅")
        return result
    except Exception as e:
        print(f"[WARN] Anthropic translation ({from_code}→{to_code}) failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Backend 2 — Google Translate via deep-translator
# ---------------------------------------------------------------------------

def _translate_google(text: str, from_code: str, to_code: str) -> str:
    try:
        from deep_translator import GoogleTranslator
        result = GoogleTranslator(source=from_code, target=to_code).translate(text)
        return result or None
    except Exception as e:
        print(f"[WARN] deep-translator ({from_code}→{to_code}) failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Backend 3 — argostranslate (offline)
# ---------------------------------------------------------------------------

def _translate_argos(text: str, from_code: str, to_code: str) -> str:
    try:
        import argostranslate.translate as argo
        result = argo.translate(text, from_code, to_code)
        return result or None
    except Exception as e:
        print(f"[WARN] argostranslate ({from_code}→{to_code}) failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Dispatcher — tries backends in priority order
# ---------------------------------------------------------------------------

def _translate(text: str, from_code: str, to_code: str) -> str:
    for name, fn in [
        ("Anthropic API",  lambda: _translate_anthropic(text, from_code, to_code)),
        ("Google Translate", lambda: _translate_google(text, from_code, to_code)),
        ("argostranslate",  lambda: _translate_argos(text, from_code, to_code)),
    ]:
        result = fn()
        if result and result != text:
            return result
        if result is None:
            print(f"[WARN] {name} unavailable for {from_code}→{to_code}")

    print(f"[WARN] All translation backends failed for {from_code}→{to_code}")
    return text


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def detect_language(text: str) -> str:
    try:
        lang = detect(text[:500])
        return lang if lang in ("ta", "en") else "unknown"
    except Exception:
        return "unknown"


def translate_to_english(text: str) -> str:
    lang = detect_language(text)
    if lang == "en":
        return text
    return _translate(text, from_code="ta", to_code="en")


def translate_to_tamil(text: str) -> str:
    """
    Translate *text* to Tamil.
    Validates result contains actual Tamil Unicode (U+0B80–U+0BFF).
    Returns None if translation failed.
    """
    lang = detect_language(text)
    if lang == "ta":
        return text

    result = _translate(text, from_code="en", to_code="ta")

    if result and any('\u0B80' <= c <= '\u0BFF' for c in result):
        return result

    print("[WARN] Translation did not produce Tamil characters — returning None")
    return None


def maybe_translate_query(query: str) -> dict:
    lang = detect_language(query)

    if lang == "ta":
        query_en = translate_to_english(query)
        query_ta = query
    elif lang == "en":
        query_en = query
        query_ta = translate_to_tamil(query) or query
    else:
        query_en = query
        query_ta = query

    return {
        "original_lang": lang,
        "query_en":      query_en,
        "query_ta":      query_ta,
        "original":      query,
    }


def install_language_packages():
    """Download argostranslate language packages (optional offline fallback)."""
    import argostranslate.package as pkg
    print("[TRANSLATOR] Fetching available language packages …")
    pkg.update_package_index()
    available = pkg.get_available_packages()

    pairs = [("en", "ta"), ("ta", "en")]
    for from_code, to_code in pairs:
        match = next(
            (p for p in available if p.from_code == from_code and p.to_code == to_code),
            None,
        )
        if match:
            installed = pkg.get_installed_packages()
            already = any(
                p.from_code == from_code and p.to_code == to_code
                for p in installed
            )
            if not already:
                print(f"[TRANSLATOR] Installing {from_code} → {to_code} …")
                pkg.install_from_path(match.download())
            else:
                print(f"[TRANSLATOR] {from_code} → {to_code} already installed ✅")
        else:
            print(f"[TRANSLATOR] WARNING: no package found for {from_code} → {to_code}")
