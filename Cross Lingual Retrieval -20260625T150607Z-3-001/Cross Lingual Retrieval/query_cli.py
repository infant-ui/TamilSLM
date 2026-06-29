"""
query_cli.py
------------
Command-line interface to query the RAG system without launching the web UI.

Usage:
    python query_cli.py "What is photosynthesis?"
    python query_cli.py "ஒளிச்சேர்க்கை என்றால் என்ன?"
    python query_cli.py --top-k 8 "Explain Newton's first law"
    python query_cli.py --interactive   # interactive chat loop
"""

import argparse
import sys
from dotenv import load_dotenv

from embedder import load_index, get_model
from rag_pipeline import ask, get_client

load_dotenv()


def single_query(query: str, top_k: int):
    index, metadata = load_index()
    model = get_model()
    client = get_client()
    ask(query, index, metadata, model, client, top_k=top_k, save=True)


def interactive_loop(top_k: int):
    print("\n" + "=" * 60)
    print("  Cross-lingual Science RAG — Interactive Mode")
    print("  Type 'quit' or 'exit' to stop")
    print("=" * 60 + "\n")

    index, metadata = load_index()
    model = get_model()
    client = get_client()

    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        ask(query, index, metadata, model, client, top_k=top_k, save=True)


def main():
    parser = argparse.ArgumentParser(description="Query the cross-lingual Science RAG system")
    parser.add_argument("query", nargs="?", help="Question in English or Tamil")
    parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive loop")
    args = parser.parse_args()

    if args.interactive:
        interactive_loop(args.top_k)
    elif args.query:
        single_query(args.query, args.top_k)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
