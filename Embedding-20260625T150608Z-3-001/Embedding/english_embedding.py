import json
import numpy as np
import os
import csv
from gensim.models import KeyedVectors

# Load FastText .vec model using gensim
print("Loading FastText model...")
model = KeyedVectors.load_word2vec_format("models/fasttext/cc.en.300.vec", binary=False)
model = KeyedVectors.load_word2vec_format(
    "models/fasttext/cc.en.300.vec",
    binary=False,
    limit=200000
)
print("FastText model loaded!")


# Load English chunks
with open("chunks/english_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

embeddings = []
metadata = []

os.makedirs("embeddings", exist_ok=True)

# ---------- TXT (human readable) ----------
txt_file = open("embeddings/english_embeddings_readable.txt", "w", encoding="utf-8")

# ---------- CSV (Excel friendly) ----------
csv_file = open("embeddings/english_embeddings.csv", "w", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)

# CSV header: dimension names
header = ["chunk_id", "text"] + [f"dim_{i}" for i in range(300)]
csv_writer.writerow(header)

for chunk in chunks:
    words = chunk["text"].split()
    vectors = []

    for word in words:
        if word in model:
            vectors.append(model[word])

    if vectors:
        chunk_embedding = np.mean(vectors, axis=0)
    else:
        chunk_embedding = np.zeros(300)

    embeddings.append(chunk_embedding)
    metadata.append(chunk)

    # ---------- TXT OUTPUT (ALL 300 DIMS) ----------
    txt_file.write(f"CHUNK ID: {chunk['chunk_id']}\n")
    txt_file.write("TEXT:\n")
    txt_file.write(chunk["text"] + "\n")
    txt_file.write("EMBEDDING (300 dimensions):\n")
    txt_file.write(str(np.round(chunk_embedding, 6).tolist()) + "\n")
    txt_file.write("-" * 120 + "\n")

    # ---------- CSV OUTPUT (ALL 300 DIMS) ----------
    csv_writer.writerow(
        [chunk["chunk_id"], chunk["text"]] +
        np.round(chunk_embedding, 6).tolist()
    )

# Close files
txt_file.close()
csv_file.close()

# ---------- Save machine-readable embeddings ----------
embeddings = np.array(embeddings)
np.save("embeddings/english_fasttext_embeddings.npy", embeddings)

# ---------- Save metadata ----------
with open("embeddings/english_metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print("English FastText embeddings saved")
print("• .npy → full precision (machine)")
print("• .txt → all 300 dims (human readable)")
print("• .csv → all 300 dims (Excel)")
print("Shape:", embeddings.shape)
