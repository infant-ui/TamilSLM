"""
build_index.py
--------------
One-time script: loads all documents and builds the FAISS vector index.

Usage:
    python build_index.py
    python build_index.py --pdf-dir data/pdfs --text-dir data/texts
"""

import argparse #Used to take input from command line
from document_loader import load_all_documents
from embedder import build_index


def main():
    parser = argparse.ArgumentParser(description="Build FAISS index for the RAG system")
    parser.add_argument("--pdf-dir",  default="data/pdfs",  help="Directory containing PDF files")
    parser.add_argument("--text-dir", default="data/texts", help="Directory containing .txt files")
    args = parser.parse_args() #reads user input files

    print("=" * 60)
    print("  Cross-lingual RAG — Index Builder")
    print("=" * 60)

    # 1. Load all documents
    chunks = load_all_documents(pdf_dir=args.pdf_dir, text_dir=args.text_dir)

    if not chunks:
        print("[ERROR] No documents found. Please add PDFs to data/pdfs/ and/or .txt files to data/texts/")
        return

    # 2. Embed and index
    index, metadata, model = build_index(chunks)#text → embeddings,Stores in FAISS index,Keeps metadata

    print("\n✅ Index built successfully!")
    print(f"   Vectors indexed : {index.ntotal}")
    print(f"   Index saved to  : embeddings/faiss.index")
    print(f"   Metadata saved  : embeddings/metadata.pkl")
    print("\nNext step: run  python app.py  to launch the UI")


if __name__ == "__main__":
    main()
