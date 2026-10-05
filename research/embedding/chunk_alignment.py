import numpy as np
import json
import os
import sys
import matplotlib.pyplot as plt

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

sys.stdout.reconfigure(encoding="utf-8")

# =====================================================
# Helper: Safe normalization
# =====================================================
def normalize(x):
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-9, None)
    return x / norms


# =====================================================
# Helper: Annotate points with chunk_id
# =====================================================
def annotate_points(points_2d, meta, color="black"):
    for i in range(len(points_2d)):
        plt.text(
            points_2d[i, 0],
            points_2d[i, 1],
            str(meta[i]["chunk_id"]),
            fontsize=9,
            color=color
        )


# =====================================================
# 1. LOAD DATA (CORRECT FILES)
# =====================================================

# English BERT embeddings (768D)
english = np.load("embeddings/english_bert_embeddings.npy")

# Tamil BERT embeddings (768D)  ✅ FIX
tamil = np.load("embeddings/tamil_bert_embeddings.npy")

# Metadata
eng_meta = json.load(open("embeddings/english_metadata.json", encoding="utf-8"))
tam_meta = json.load(open("embeddings/tamil_metadata.json", encoding="utf-8"))

# -----------------------------------------------------
# Safety: equal length
# -----------------------------------------------------
K = min(len(english), len(tamil), len(eng_meta), len(tam_meta))

english = english[:K]
tamil = tamil[:K]
eng_meta = eng_meta[:K]
tam_meta = tam_meta[:K]

print("Total bilingual pairs:", K)
print("English shape:", english.shape)
print("Tamil shape  :", tamil.shape)

assert english.shape[1] == tamil.shape[1] == 768, "Embedding dimension mismatch!"


# =====================================================
# 2. NORMALIZATION
# =====================================================

english_norm = normalize(english)
tamil_norm = normalize(tamil)


# =====================================================
# 3. ORTHOGONAL PROCRUSTES ALIGNMENT
# =====================================================

# M ∈ R^(768 × 768)
M = tamil_norm.T @ english_norm

U, _, Vt = np.linalg.svd(M)
W = U @ Vt

# Align Tamil → English space
tamil_aligned = tamil_norm @ W


# =====================================================
# 4. SAVE MACHINE-READABLE OUTPUTS
# =====================================================

os.makedirs("bilingual_embeddings", exist_ok=True)

np.save("bilingual_embeddings/english_shared.npy", english_norm)
np.save("bilingual_embeddings/tamil_shared.npy", tamil_aligned)
np.save("bilingual_embeddings/alignment_matrix.npy", W)


# =====================================================
# 5. SAVE HUMAN-READABLE TXT FILES
# =====================================================

eng_txt = open("bilingual_embeddings/english_shared_readable.txt", "w", encoding="utf-8")
tam_txt = open("bilingual_embeddings/tamil_shared_readable.txt", "w", encoding="utf-8")

for i in range(K):
    eng_txt.write(f"CHUNK ID: {eng_meta[i]['chunk_id']}\n")
    eng_txt.write("TEXT:\n")
    eng_txt.write(eng_meta[i]["text"] + "\n")
    eng_txt.write("VECTOR (768D):\n")
    eng_txt.write(str(np.round(english_norm[i], 6).tolist()) + "\n")
    eng_txt.write("-" * 120 + "\n")

    tam_txt.write(f"CHUNK ID: {tam_meta[i]['chunk_id']}\n")
    tam_txt.write("TEXT:\n")
    tam_txt.write(tam_meta[i]["text"] + "\n")
    tam_txt.write("VECTOR (768D, ALIGNED):\n")
    tam_txt.write(str(np.round(tamil_aligned[i], 6).tolist()) + "\n")
    tam_txt.write("-" * 120 + "\n")

eng_txt.close()
tam_txt.close()


# =====================================================
# 6. DEMONSTRATION (ONE PAIR)
# =====================================================

idx = 0

E = english_norm[idx]
T_before = tamil_norm[idx]
T_after = tamil_aligned[idx]

sim_before = cosine_similarity(E.reshape(1, -1), T_before.reshape(1, -1))[0][0]
sim_after = cosine_similarity(E.reshape(1, -1), T_after.reshape(1, -1))[0][0]

print("\n================== DEMONSTRATION ==================\n")
print("CHUNK ID:", eng_meta[idx]["chunk_id"])
print("\nCosine BEFORE alignment:", round(sim_before, 4))
print("Cosine AFTER alignment :", round(sim_after, 4))
print("\n===================================================")


# =====================================================
# 7. PCA VISUALIZATION
# =====================================================

N = min(200, K)

combined = np.vstack([
    english_norm[:N],
    tamil_norm[:N],
    tamil_aligned[:N]
])

pca = PCA(n_components=2, random_state=42)
combined_2d = pca.fit_transform(combined)

E_2d = combined_2d[:N]
T_before_2d = combined_2d[N:2*N]
T_after_2d = combined_2d[2*N:3*N]

plt.figure(figsize=(10, 7))
plt.scatter(E_2d[:, 0], E_2d[:, 1], label="English")
plt.scatter(T_before_2d[:, 0], T_before_2d[:, 1], label="Tamil BEFORE")
plt.scatter(T_after_2d[:, 0], T_after_2d[:, 1], label="Tamil AFTER")

plt.legend()
plt.grid(True)
plt.title("Bilingual Alignment (PCA 2D)")
plt.savefig("bilingual_embeddings/alignment_visualization_pca.png", dpi=300)
plt.show()



# =====================================================
# 8. t-SNE VISUALIZATION (AFTER PCA)
# =====================================================

# Reduce first with PCA (important for t-SNE stability)
pca_tsne = PCA(n_components=50, random_state=42)
combined_pca = pca_tsne.fit_transform(combined)

tsne = TSNE(
    n_components=2,
    perplexity=30,
    learning_rate=200,
    max_iter=1000,
    init="pca",
    random_state=42
)


combined_tsne_2d = tsne.fit_transform(combined_pca)

E_tsne = combined_tsne_2d[:N]
T_before_tsne = combined_tsne_2d[N:2*N]
T_after_tsne = combined_tsne_2d[2*N:3*N]

plt.figure(figsize=(10, 7))

plt.scatter(
    E_tsne[:, 0],
    E_tsne[:, 1],
    label="English",
    alpha=0.7
)

plt.scatter(
    T_before_tsne[:, 0],
    T_before_tsne[:, 1],
    label="Tamil BEFORE",
    alpha=0.7
)

plt.scatter(
    T_after_tsne[:, 0],
    T_after_tsne[:, 1],
    label="Tamil AFTER",
    alpha=0.7
)

plt.legend()
plt.grid(True)
plt.title("Bilingual Alignment (t-SNE Visualization)")
plt.tight_layout()
plt.savefig(
    "bilingual_embeddings/alignment_visualization_tsne.png",
    dpi=300
)
plt.show()
