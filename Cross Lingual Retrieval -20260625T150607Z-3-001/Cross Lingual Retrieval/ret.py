"""
ret.py — Tamil LLaMA Answer Generator
--------------------------------------
TWO MODES:

  1. STANDALONE  (python ret.py)
     Reads hardcoded `text` variable, generates Tamil explanation via Ollama llama3.

  2. MODULE MODE  (called from rag_pipeline.py)
     Call generate_tamil_answer(retrieved_text, query) to get Tamil answer string.
     The rag_pipeline.py automatically calls this when it detects a Tamil query.

FLOW in RAG system:
  Tamil query detected
       ↓
  embedder.retrieve_structured()  →  retrieves Tamil book + Web chunks
       ↓
  ret.generate_tamil_answer(chunks_text, tamil_query)
       ↓
  Ollama llama3  →  Tamil answer
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import ollama


# ============================================================
# MODULE INTERFACE  (used by rag_pipeline.py)
# ============================================================

def generate_tamil_answer(retrieved_text: str, query: str, model: str = "llama3") -> str:
    """
    Generate a Tamil answer from retrieved RAG content.

    Args:
        retrieved_text : concatenated chunk texts from the retriever
        query          : original Tamil query from the user
        model          : Ollama model to use (default: llama3)

    Returns:
        Tamil answer string
    """
    prompt = f"""நீங்கள் ஒரு தமிழ் அறிவியல் ஆசிரியர்.

மாணவர் கேள்வி: {query}

கீழே உள்ள பாட உள்ளடக்கத்தை படித்து:
- முழுவதும் தமிழில்
- எளிமையாக
- விளக்கமாக
- கேள்விக்கு நேரடியாக பதில் சொல்லவும்.

ஆங்கிலம் பயன்படுத்தக்கூடாது.

பாட உள்ளடக்கம்:
{retrieved_text}
"""
    print(f"⏳ Generating Tamil answer via Ollama ({model})...")
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    result = response["message"]["content"]
    print("✅ Tamil answer generated.")
    return result


# ============================================================
# STANDALONE MODE  (python ret.py)
# ============================================================

if __name__ == "__main__":

    # ── STEP 1: INPUT TEXT ──────────────────────────────────
    text = """மதிப்பாகும்‌. 'கி.மீ' என்பது தொலைவு என்ற இயற்பியல்‌ அளவின்‌ மதிப்பினைக்‌ குறிப்பதற்குப்‌ பயன்பரும்‌ அலகாகும்‌. இந்தப்‌ பாடப்பகுதியில்‌, அடிப்படை அளவுகள்‌, பரப்பளவு கன அளவு மற்றும்‌ மிகப்‌ பெரிய அளவுகளை அளவிருதல்‌ ஆகியவற்றைப்‌ பற்றிக்‌ காண்போம்‌. AO Erie ௫) ண்‌ | பொதுவாக இயற்பியல்‌ அளவுகள்‌ இரண்டு வகைப்பரும்‌. அவை அடிப்படை அளவுகள்‌ மற்றும்‌ வழி அளவுகள்‌. 1,1.1 அடிப்படை அளவுகள்‌ வேறு எந்த இயற்பியல்‌ அளவுகளாலம்‌ குறிப்பிடப்பட இயலாத இயற்பியல்‌ அளவுகள்‌ அடிப்படை அளவுகள்‌ எனப்பரும்‌. எ.கா: நீளம்‌, நிறை, காலம்‌. அடிப்படை அளவுகளை அளந்தறியப்‌ பயன்பரும்‌ அலகுகள்‌ அடிப்படை அலகுகள்‌ எனப்பரும்‌. த (௫ International பார்‌ அலகு முறையில்‌ ஏழு அடிப்படை அளவுகள்‌ உள்ளன. அடிப்படை அளவுகளும்‌ அவற்றின்‌ அலகுகளும்‌ அட்டவணை 11 ல்‌ கொருக்கப்பட்டுள்ளன. அட்டவணை 1.1 அடிப்படை அளவுகள்‌ மற்றும்‌ அலகுகள்‌ a. epee சாராவை | சரடு அளவுகள்‌ இ இப்படை வு | நீளம்‌ மீட்டர்‌ (ரர) | 'நிறை , கிலோகிராம்‌ (ஐ) | காலம்‌ வினாடி (6) | 'வெப்பநிலை கெல்வின்‌ (9 | tas wo sas மின்னோட்டம்‌ ஆம்பியர்‌ ( &) | aaa அளவு மோல்‌ (௦) | இளிச்சறிவு_ _ கேண்டிலா(௦0) |] ட] | 'VI Std Science Term-L TM Unit Lindd 2 --- RIGHT COLUMN --- 1.1.2 வழி அளவுகள்‌ அடிப்படை அளவுகளைப்பெருக்கியோ, வகுத்தோ அல்லது கணித முறைப்படி இணைத்தோ பெறப்பரும்‌ பிற இயற்பியல்‌ அளவு
FUNDAMENTAL QUANTITIES (DETAILED NOTES) 1. Definition: Fundamental quantities are the basic physical quantities that do not depend on any other quantities. They form the foundation of all physical measurements and are used to derive other quantities. Importance: - Provide a standard system of measurement (SI system) - Used to express all physical laws - Help avoid confusion in measurements worldwide 3. The Seven Fundamental Quantities: 1) Length (meter, m) Definition: Distance between two points.
"""

    # Save input file
    with open("input.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("✅ input.txt created")

    # ── STEP 2: READ FILE ───────────────────────────────────
    with open("input.txt", "r", encoding="utf-8") as f:
        data = f.read()

    # ── STEP 3: GENERATE ────────────────────────────────────
    # Use a generic standalone query since we're running without a user question
    standalone_query = "இந்த பாட உள்ளடக்கத்தை விளக்கவும்"
    result = generate_tamil_answer(data, standalone_query, model="llama3")

    # ── STEP 4: PRINT OUTPUT ────────────────────────────────
    print("\n" + "="*60)
    print("📌 FINAL TAMIL OUTPUT:\n")
    print(result)
    print("="*60)

    # ── STEP 5: SAVE OUTPUT ─────────────────────────────────
    with open("output_tamil.txt", "w", encoding="utf-8") as f:
        f.write(result)
    print("✅ Saved as output_tamil.txt")
