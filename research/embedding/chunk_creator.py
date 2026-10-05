import fitz  # PyMuPDF
import nltk
import json
from nltk.tokenize import sent_tokenize

# -----------------------------
# NLTK setup
# -----------------------------
nltk.download("punkt")

# -----------------------------
# Extract text from PDF
# -----------------------------
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text()

    return full_text


# -----------------------------
# Load text from TXT file
# -----------------------------
def load_text_from_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        return f.read()


# -----------------------------
# Chunking function
# -----------------------------
def chunk_text(text, language, book_name, max_words):
    sentences = sent_tokenize(text)
    chunks = []

    current_chunk = []
    current_word_count = 0
    chunk_id = 0

    for sentence in sentences:
        words = sentence.split()
        word_count = len(words)

        if current_word_count + word_count <= max_words:
            current_chunk.append(sentence)
            current_word_count += word_count
        else:
            # Save current chunk
            chunks.append({
                "chunk_id": chunk_id,
                "language": language,
                "book": book_name,
                "word_count": current_word_count,
                "text": " ".join(current_chunk)
            })

            chunk_id += 1

            # Overlap last 10 words
            overlap_words = " ".join(current_chunk).split()[-10:]

            current_chunk = [" ".join(overlap_words), sentence]
            current_word_count = len(overlap_words) + word_count

    # Save final chunk
    if current_chunk:
        chunks.append({
            "chunk_id": chunk_id,
            "language": language,
            "book": book_name,
            "word_count": current_word_count,
            "text": " ".join(current_chunk)
        })

    return chunks


# -----------------------------
# Main execution
# -----------------------------
def main():
    # -------- English PDF --------
    english_text = extract_text_from_pdf(
        "data/english_bookk.pdf"
    )

    english_chunks = chunk_text(
        text=english_text,
        language="english",
        book_name="science_book",
        max_words=300
    )

    with open("chunks/english_chunks.json", "w", encoding="utf-8") as f:
        json.dump(english_chunks, f, ensure_ascii=False, indent=2)

    print(f"English chunks created: {len(english_chunks)}")

    # -------- Tamil TXT (OCR Output) --------
    tamil_text = load_text_from_txt(
        r"data\tamil_book_output (1).txt"
    )

    tamil_chunks = chunk_text(
        text=tamil_text,
        language="tamil",
        book_name="science_book",
        max_words=294
    )

    with open("chunks/tamil_chunks.json", "w", encoding="utf-8") as f:
        json.dump(tamil_chunks, f, ensure_ascii=False, indent=2)

    print(f"Tamil chunks created: {len(tamil_chunks)}")


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    main()
