import json
import numpy as np
import os
import csv
import torch
from transformers import AutoTokenizer, AutoModel

# -----------------------------
# Device setup
# -----------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -----------------------------
# Load English BERT
# -----------------------------
print("Loading English BERT model...")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased").to(device)
model.eval()
print("English BERT loaded!")

# -----------------------------
# Load English chunks
# -----------------------------
with open("chunks/english_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

embeddings = []
metadata = []

os.makedirs("embeddings", exist_ok=True)

# -----------------------------
# TXT (human readable)
# -----------------------------
txt_file = open(
    "embeddings/english_bert_embeddings_readable.txt",
    "w",
    encoding="utf-8"
)

# -----------------------------
# CSV (Excel friendly)
# -----------------------------
csv_file = open(
    "embeddings/english_bert_embeddings.csv",
    "w",
    newline="",
    encoding="utf-8"
)
csv_writer = csv.writer(csv_file)

# CSV header (768 dims)
header = ["chunk_id", "text"] + [f"dim_{i}" for i in range(768)]
csv_writer.writerow(header)

# -----------------------------
# Generate embeddings
# -----------------------------
with torch.no_grad():
    for chunk in chunks:
        text = chunk["text"]

        # Tokenize
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )

        inputs = {k: v.to(device) for k, v in inputs.items()}

        # BERT forward pass
        outputs = model(**inputs)

        # Token embeddings: [1, seq_len, 768]
        token_embeddings = outputs.last_hidden_state.squeeze(0)

        # Attention mask
        attention_mask = inputs["attention_mask"].squeeze(0).unsqueeze(-1)

        # Mean pooling (mask-aware)
        masked_embeddings = token_embeddings * attention_mask
        sum_embeddings = masked_embeddings.sum(dim=0)
        valid_tokens = attention_mask.sum()

        if valid_tokens > 0:
            chunk_embedding = (sum_embeddings / valid_tokens).cpu().numpy()
        else:
            chunk_embedding = np.zeros(768)

        embeddings.append(chunk_embedding)
        metadata.append(chunk)

        # ---------- TXT OUTPUT ----------
        txt_file.write(f"CHUNK ID: {chunk['chunk_id']}\n")
        txt_file.write("TEXT:\n")
        txt_file.write(text + "\n")
        txt_file.write("EMBEDDING (768 dimensions):\n")
        txt_file.write(str(np.round(chunk_embedding, 6).tolist()) + "\n")
        txt_file.write("-" * 120 + "\n")

        # ---------- CSV OUTPUT ----------
        csv_writer.writerow(
            [chunk["chunk_id"], text] +
            np.round(chunk_embedding, 6).tolist()
        )

# -----------------------------
# Close files
# -----------------------------
txt_file.close()
csv_file.close()

# -----------------------------
# Save machine-readable embeddings
# -----------------------------
embeddings = np.array(embeddings)
np.save("embeddings/english_bert_embeddings.npy", embeddings)

# -----------------------------
# Save metadata
# -----------------------------
with open("embeddings/english_metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print("English BERT embeddings saved")
print("• .npy → full precision (machine)")
print("• .txt → all 768 dims (human readable)")
print("• .csv → all 768 dims (Excel)")
print("Shape:", embeddings.shape)
