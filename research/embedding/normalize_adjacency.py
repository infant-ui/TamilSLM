import numpy as np

# -------------------------------------------------
# 1. Load adjacency matrix
# -------------------------------------------------

A = np.load("bilingual_embeddings/knn_adjacency.npy")

print("Original adjacency shape:", A.shape)

N = A.shape[0]

# -------------------------------------------------
# 2. Add self-loops
# -------------------------------------------------

I = np.eye(N)
A_hat = A + I

# -------------------------------------------------
# 3. Compute degree matrix
# -------------------------------------------------

degree = np.sum(A_hat, axis=1)

# D^(-1/2)
D_inv_sqrt = np.diag(1.0 / np.sqrt(degree))

# -------------------------------------------------
# 4. Normalize adjacency
# -------------------------------------------------

A_normalized = D_inv_sqrt @ A_hat @ D_inv_sqrt

print("Normalized adjacency shape:", A_normalized.shape)

# -------------------------------------------------
# 5. Save normalized adjacency
# -------------------------------------------------

np.save("bilingual_embeddings/knn_adjacency_normalized.npy", A_normalized)

print("Normalized adjacency matrix saved as knn_adjacency_normalized.npy")
