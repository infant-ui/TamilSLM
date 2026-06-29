import os
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity

# =====================================================
# CONFIG
# =====================================================

k = 5
base_out_dir = "graphs"

english_path = "bilingual_embeddings\english_shared.npy"
tamil_path = "bilingual_embeddings\\tamil_shared.npy"

PRINT_FULL_MATRIX_IF_N_LEQ = 50
PRINT_BLOCK_SIZE = 20 #Small graph → print everything

# =====================================================
# FUNCTIONS
# =====================================================

def l2_normalize(X):
    return X / np.linalg.norm(X, axis=1, keepdims=True)

def normalize_adjacency(A):
    """
    GCN normalization:
    A_hat = A + I
    D_hat = diag(sum(A_hat))
    A_norm = D^-1/2 * A_hat * D^-1/2
    """
    N = A.shape[0] #A is your adjacency matrix
    I = np.eye(N)#identity matrix

    A_hat = A + I #self-loops
    D_hat = np.sum(A_hat, axis=1) #Degree of each node
    D_inv_sqrt = np.diag(1.0 / np.sqrt(D_hat + 1e-9)) 
    #This creates a diagonal matrix with:
    #1/sqrt(degree),nodes with more neighbors get a smaller weight.
    A_norm = D_inv_sqrt @ A_hat @ D_inv_sqrt
    return A_norm

def build_knn_graph(X, k):
    """
    Returns:
      A (0/1 adjacency)
      A_weighted (cosine similarity weights)
    """
    N = X.shape[0]
    sim = cosine_similarity(X) #creates a similarity matrix of shape (N, N)

    A = np.zeros((N, N))
    A_weighted = np.zeros((N, N)) # store similarity values

    for i in range(N):
        neighbors = np.argsort(sim[i])[-(k + 1):-1]  # exclude itself,top k similar nodes for node i

        for j in neighbors:
            A[i, j] = 1
            A[j, i] = 1  # undirected

            A_weighted[i, j] = sim[i, j]
            A_weighted[j, i] = sim[j, i]

    return A, A_weighted

def save_matrix_npy_and_txt(matrix, npy_path, txt_path, title):
    np.save(npy_path, matrix)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(title + "\n")
        f.write("Shape: " + str(matrix.shape) + "\n\n")
        f.write(np.array2string(matrix, precision=4, suppress_small=True))

def print_matrix_in_terminal(matrix, name):
    N = matrix.shape[0]

    print(f"\n{name} (shape={matrix.shape})")

    if N <= PRINT_FULL_MATRIX_IF_N_LEQ:
        print(matrix)
    else:
        print(f"(Matrix too large. Showing first {PRINT_BLOCK_SIZE}x{PRINT_BLOCK_SIZE})\n")
        print(matrix[:PRINT_BLOCK_SIZE, :PRINT_BLOCK_SIZE])

def visualize_graph(A_weighted, title, save_path):
    """
    Visualize weighted graph using NetworkX.
    """
    G = nx.from_numpy_array(A_weighted)

    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)

    nx.draw_networkx_nodes(G, pos, node_size=450)
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.7)
    nx.draw_networkx_labels(G, pos, font_size=9)

    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

# =====================================================
# MAIN
# =====================================================

os.makedirs(base_out_dir, exist_ok=True)

for lang, path in [("english", english_path), ("tamil", tamil_path)]:

    print(f"\n================ {lang.upper()} KNN GRAPH =================")

    out_dir = os.path.join(base_out_dir, lang)
    os.makedirs(out_dir, exist_ok=True)

    # Load embeddings
    X = np.load(path)
    print("Loaded:", path)
    print("Embedding shape:", X.shape)

    # Normalize embeddings
    X = l2_normalize(X)

    # Build adjacency
    A, A_weighted = build_knn_graph(X, k=k)
    A_norm = normalize_adjacency(A)

    # Print adjacency in terminal
    print_matrix_in_terminal(A, f"{lang.upper()} Adjacency Matrix (0/1)")
    print_matrix_in_terminal(A_norm, f"{lang.upper()} Normalized Adjacency Matrix")

    # Save matrices as .npy + .txt
    save_matrix_npy_and_txt(
        A,
        os.path.join(out_dir, "adjacency.npy"),
        os.path.join(out_dir, "adjacency.txt"),
        f"{lang.upper()} Adjacency Matrix (0/1)"
    )

    save_matrix_npy_and_txt(
        A_weighted,
        os.path.join(out_dir, "adjacency_weighted.npy"),
        os.path.join(out_dir, "adjacency_weighted.txt"),
        f"{lang.upper()} Weighted Adjacency Matrix (Cosine Similarity)"
    )

    save_matrix_npy_and_txt(
        A_norm,
        os.path.join(out_dir, "adjacency_normalized.npy"),
        os.path.join(out_dir, "adjacency_normalized.txt"),
        f"{lang.upper()} Normalized Adjacency Matrix for GCN"
    )

    print("\nSaved all .npy + .txt matrices inside:", out_dir)

    # Save visualization
    graph_img_path = os.path.join(out_dir, "graph.png")
    visualize_graph(A_weighted, f"{lang.upper()} KNN Graph (k={k})", graph_img_path)

    print("Graph visualization saved:", graph_img_path)

print("\nALL DONE. English and Tamil graphs created + saved in human-readable format.")
