# -----------------------------
# Import required libraries
# -----------------------------
import json                      
import torch                    
import numpy as np               
from transformers import AutoTokenizer, AutoModel  
import os                       
import csv                      

# -----------------------------
# Select device (GPU if available, else CPU)
# -----------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -----------------------------
# Load Tamil BERT tokenizer and model
# -----------------------------
tokenizer = AutoTokenizer.from_pretrained("l3cube-pune/tamil-bert")
model = AutoModel.from_pretrained("l3cube-pune/tamil-bert").to(device)

# Set model to evaluation mode (disables dropout, etc.)
model.eval()

# -----------------------------
# Load chunked Tamil text data
# -----------------------------

with open("chunks/tamil_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)


embeddings = []
metadata = []


os.makedirs("embeddings", exist_ok=True)


txt_file = open("embeddings/tamil_embeddings_readable.txt", "w", encoding="utf-8")


csv_file = open("embeddings/tamil_embeddings.csv", "w", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)

# Create CSV header: chunk_id, text, followed by 768 embedding dimensions
header = ["chunk_id", "text"] + [f"dim_{i}" for i in range(768)]
csv_writer.writerow(header)

# -----------------------------
# Disable gradient computation for inference
# -----------------------------
with torch.no_grad():
    # Iterate over each text chunk
    for chunk in chunks:

        # Tokenize the Tamil text
        inputs = tokenizer(
            chunk["text"],           # Text to tokenize
            return_tensors="pt",     # Return PyTorch tensors
            truncation=True,         # Truncate text longer than max_length
            padding=True,            # Pad shorter sequences
            max_length=512           # Maximum sequence length for BERT
        ).to(device)                 # Move inputs to selected device

        # Pass tokenized input through the model
        outputs = model(**inputs)

        # Extract  (token-level embeddings)
        # Shape: (batch_size, sequence_length, 768)
        last_hidden = outputs.last_hidden_state

        # Mean pooling over token dimension to get one vector per chunk
        # Resulting shape: (768,)
        chunk_embedding = last_hidden.mean(dim=1).squeeze().cpu().numpy()

        # Store embedding and metadata
        embeddings.append(chunk_embedding)
        metadata.append(chunk)

        # -----------------------------
        # Write human-readable TXT output
        # -----------------------------
        txt_file.write(f"CHUNK ID: {chunk['chunk_id']}\n")
        txt_file.write("TEXT:\n")
        txt_file.write(chunk["text"] + "\n")
        txt_file.write("EMBEDDING (768 dimensions):\n")
        txt_file.write(str(np.round(chunk_embedding, 6).tolist()) + "\n")
        txt_file.write("-" * 140 + "\n")

        # -----------------------------
        # Write CSV output (one row per chunk)
        # -----------------------------
        csv_writer.writerow(
            [chunk["chunk_id"], chunk["text"]] +
            np.round(chunk_embedding, 6).tolist()
        )

# -----------------------------
# Close open files
# -----------------------------
txt_file.close()
csv_file.close()

# -----------------------------
# Save embeddings in NumPy format (machine-readable)
# -----------------------------
embeddings = np.array(embeddings)  # Convert list to NumPy array
np.save("embeddings/tamil_bert_embeddings.npy", embeddings)

# -----------------------------
# Save metadata (chunk info) as JSON
# -----------------------------
with open("embeddings/tamil_metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

# -----------------------------
# Final status messages
# -----------------------------
print("Tamil BERT embeddings saved")
print(".npy  -> full precision (machine)")
print(".txt  -> all 768 dims (human readable)")
print(".csv  -> all 768 dims (Excel)")
print("Shape:", embeddings.shape)
