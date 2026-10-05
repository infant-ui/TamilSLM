import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

# =====================================================
# CONFIG
# =====================================================

node_id = 0
num_layers = 2  # L in paper (try 1-3)
alpha_weights = [0.5, 0.5]  # [α₀, α₁] - weights for each layer

out_dir = "stage_outputs/stage1_gcn"
os.makedirs(out_dir, exist_ok=True)

# =====================================================
# CORRECT GCN IMPLEMENTATION (SA-DAAE Paper)
# =====================================================

def build_normalized_adjacency(A):
    """
    Build Â = D^(-1)(A + I) as per Equation 5
    
    Args:
        A: Adjacency matrix (N × N)
    
    Returns:
        A_norm: Normalized adjacency (N × N)
    """
    N = A.shape[0]
    
    # Add self-connections
    A_self = A + np.eye(N)
    
    # Compute degree matrix
    D = np.sum(A_self, axis=1)  # Degree of each node
    D_inv = 1.0 / np.clip(D, 1e-9, None)  # Avoid division by zero
    D_inv_diag = np.diag(D_inv) #This converts the vector into a diagonal matrix
    
    # Normalize: Â = D^(-1)(A + I)
    A_norm = D_inv_diag @ A_self #divides each row by its degree
    
    return A_norm


def gcn_forward_correct(X, A_norm, num_layers=2, alphas=None):
    """
    Correct GCN implementation from SA-DAAE paper.
    
    From Equation 4-6:
    X^(l) = Â X^(l-1)  (No weight matrix, no activation!)
    X̂ = Σ αₗ X^(l)
    
    Args:
        X: Input embeddings (N × D)
        A_norm: Normalized adjacency Â (N × N)
        num_layers: Number of propagation layers L
        alphas: Layer weights [α₀, α₁, ..., αₗ]
    
    Returns:
        H: Enhanced embeddings (N × D)
    """
    if alphas is None:
        # Equal weights for all layers
        alphas = [1.0 / (num_layers + 1)] * (num_layers + 1)
    
    # Store layer outputs
    layer_outputs = [X]  # X^(0) = X
    
    # Propagate through L layers
    X_current = X
    for l in range(num_layers):
        # X^(l) = Â X^(l-1)  [Equation 4]
        X_current = A_norm @ X_current  # Matrix multiplication only!
        layer_outputs.append(X_current)
    
    # Aggregate all layers [Equation 6]
    # X̂ = α₀X^(0) + α₁X^(1) + ... + αₗX^(L)
    H = np.zeros_like(X)
    for l, alpha in enumerate(alphas):
        H += alpha * layer_outputs[l]
    
    return H


def l2_normalize(X):
    """L2 normalize embeddings"""
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-9, None)
    return X / norms


def save_npy_and_txt(X, name):
    """Save numpy array and text summary"""
    np.save(os.path.join(out_dir, f"{name}.npy"), X)
    
    with open(os.path.join(out_dir, f"{name}.txt"), "w", encoding="utf-8") as f:
        f.write(f"{name} embeddings\n")
        f.write(f"Shape: {X.shape}\n\n")
        f.write(f"First 5 embeddings:\n")
        f.write(np.array2string(X[:5], precision=4, suppress_small=True))


# =====================================================
# t-SNE VISUALIZATION HELPERS
# =====================================================

def tsne_2d(X, seed=42):
    """Compute t-SNE 2D coordinates"""
    n = X.shape[0]
    perplexity = min(30, max(5, n // 3))
    
    tsne = TSNE(
        n_components=2,
        perplexity=perplexity,
        random_state=seed,
        init="random",
        learning_rate="auto"
    )
    return tsne.fit_transform(X)


def visualize_global_tsne(before, after, title, save_path, highlight_node=0):
    """
    Global: plot all nodes before vs after using t-SNE.
    Also labels each dot with its chunk id.
    """
    before_2d = tsne_2d(before, seed=42)
    after_2d = tsne_2d(after, seed=42)

    plt.figure(figsize=(16, 7))

    # --------------------------
    # BEFORE
    # --------------------------
    plt.subplot(1, 2, 1)
    plt.scatter(before_2d[:, 0], before_2d[:, 1], s=50, alpha=0.6)

    # Add chunk id labels
    for i in range(before_2d.shape[0]):
        plt.text(before_2d[i, 0], before_2d[i, 1], str(i), fontsize=8, ha="center")

    # Highlight one node
    plt.scatter(before_2d[highlight_node, 0], before_2d[highlight_node, 1],
                s=220, c="red", label=f"Node {highlight_node}", zorder=5)

    plt.title(f"{title} (Before GCN)")
    plt.xlabel("t-SNE-1")
    plt.ylabel("t-SNE-2")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # --------------------------
    # AFTER
    # --------------------------
    plt.subplot(1, 2, 2)
    plt.scatter(after_2d[:, 0], after_2d[:, 1], s=50, alpha=0.6)

    # Add chunk id labels
    for i in range(after_2d.shape[0]):
        plt.text(after_2d[i, 0], after_2d[i, 1], str(i), fontsize=8, ha="center")

    # Highlight one node
    plt.scatter(after_2d[highlight_node, 0], after_2d[highlight_node, 1],
                s=220, c="red", label=f"Node {highlight_node}", zorder=5)

    plt.title(f"{title} (After GCN)")
    plt.xlabel("t-SNE-1")
    plt.ylabel("t-SNE-2")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def visualize_local_neighbors_tsne(before, after, A, title, save_path, node_id=0):
    """
    Local: plot only node_id and its neighbors using t-SNE.
    Labels each dot with its real chunk id.
    """
    neighbors = np.where(A[node_id] > 0)[0]
    neighbors = neighbors[neighbors != node_id]

    if len(neighbors) == 0:
        print(f"[WARNING] Node {node_id} has no neighbors. Skipping local plot.")
        return

    subset_idx = np.array([node_id] + neighbors.tolist())

    before_sub = before[subset_idx]
    after_sub = after[subset_idx]

    before_2d = tsne_2d(before_sub, seed=42)
    after_2d = tsne_2d(after_sub, seed=42)

    plt.figure(figsize=(16, 7))

    # --------------------------
    # BEFORE
    # --------------------------
    plt.subplot(1, 2, 1)
    plt.scatter(before_2d[:, 0], before_2d[:, 1], s=90, alpha=0.6)

    # Highlight main node
    plt.scatter(before_2d[0, 0], before_2d[0, 1],
                s=260, c="red", label=f"Node {node_id}", zorder=5)

    # Label all points
    for i in range(len(subset_idx)):
        plt.text(before_2d[i, 0], before_2d[i, 1], str(subset_idx[i]),
                 fontsize=10, ha="center")

    plt.title(f"{title} Neighborhood (Before GCN)")
    plt.xlabel("t-SNE-1")
    plt.ylabel("t-SNE-2")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # --------------------------
    # AFTER
    # --------------------------
    plt.subplot(1, 2, 2)
    plt.scatter(after_2d[:, 0], after_2d[:, 1], s=90, alpha=0.6)

    # Highlight main node
    plt.scatter(after_2d[0, 0], after_2d[0, 1],
                s=260, c="red", label=f"Node {node_id}", zorder=5)

    # Label all points
    for i in range(len(subset_idx)):
        plt.text(after_2d[i, 0], after_2d[i, 1], str(subset_idx[i]),
                 fontsize=10, ha="center")

    plt.title(f"{title} Neighborhood (After GCN)")
    plt.xlabel("t-SNE-1")
    plt.ylabel("t-SNE-2")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()



# =====================================================
# INTRA-RELATION REPORT
# =====================================================

def intra_relation_report(X, H, A, lang_name, node_id=0, top_k=5):
    """Report on how GCN affects neighbor similarities"""
    neighbors = np.where(A[node_id] > 0)[0]
    neighbors = neighbors[neighbors != node_id]
    
    print(f"\n{'='*60}")
    print(f"{lang_name} INTRA-RELATION REPORT")
    print(f"{'='*60}")
    print(f"Node: {node_id}")
    print(f"Number of neighbors: {len(neighbors)}")
    
    if len(neighbors) == 0:
        print("No neighbors found.")
        return
    
    print(f"Neighbors: {neighbors.tolist()[:10]}{'...' if len(neighbors) > 10 else ''}")
    
    sims_before = []
    sims_after = []
    
    for n in neighbors:
        sim_b = cosine_similarity(X[node_id].reshape(1, -1), X[n].reshape(1, -1))[0][0]
        sim_a = cosine_similarity(H[node_id].reshape(1, -1), H[n].reshape(1, -1))[0][0]
        sims_before.append((n, sim_b))
        sims_after.append((n, sim_a))
    
    sims_before_sorted = sorted(sims_before, key=lambda x: x[1], reverse=True)
    sims_after_sorted = sorted(sims_after, key=lambda x: x[1], reverse=True)
    
    print(f"\nTop {top_k} neighbor similarities BEFORE GCN:")
    for n, s in sims_before_sorted[:top_k]:
        print(f"  Node {node_id} <-> Node {n:4d}: {s:.4f}")

    
    print(f"\nTop {top_k} neighbor similarities AFTER GCN:")
    for n, s in sims_after_sorted[:top_k]:
        print(f"  Node {node_id} <-> Node {n:4d}: {s:.4f}")

    
    avg_before = np.mean([s for _, s in sims_before])
    avg_after = np.mean([s for _, s in sims_after])
    
    print(f"\nAverage similarity BEFORE: {avg_before:.4f}")
    print(f"Average similarity AFTER : {avg_after:.4f}")
    print(f"Change: {(avg_after - avg_before):+.4f} ({((avg_after/avg_before - 1)*100):+.2f}%)")
    print(f"{'='*60}")


# =====================================================
# MAIN EXECUTION
# =====================================================

print("\n" + "="*60)
print("STAGE 1: SIMPLIFIED GCN (SA-DAAE Paper)")
print("="*60)

# Load embeddings
X_en = np.load("bilingual_embeddings/english_shared.npy")
X_ta = np.load("bilingual_embeddings/tamil_shared.npy")

# Load adjacency matrices
A_en = np.load("graphs/english/adjacency_normalized.npy")  # Original adjacency
A_ta = np.load("graphs/tamil/adjacency_normalized.npy")

print(f"\nEnglish embeddings: {X_en.shape}")
print(f"Tamil embeddings  : {X_ta.shape}")
print(f"English adjacency : {A_en.shape}")
print(f"Tamil adjacency   : {A_ta.shape}")

# =====================================================
# BUILD NORMALIZED ADJACENCY
# =====================================================

print("\nBuilding normalized adjacency matrices...")
A_norm_en = build_normalized_adjacency(A_en)
A_norm_ta = build_normalized_adjacency(A_ta)

print("Normalized adjacency matrices built")

# =====================================================
# APPLY CORRECT GCN
# =====================================================

print(f"\nApplying {num_layers}-layer GCN...")
print(f"Layer weights : {alpha_weights}")

H_en = gcn_forward_correct(X_en, A_norm_en, num_layers=num_layers, alphas=alpha_weights)
H_ta = gcn_forward_correct(X_ta, A_norm_ta, num_layers=num_layers, alphas=alpha_weights)

# L2 normalize
H_en = l2_normalize(H_en)
H_ta = l2_normalize(H_ta)

print("GCN forward pass complete")

# =====================================================
# REPORTS
# =====================================================

intra_relation_report(X_en, H_en, A_en, "ENGLISH", node_id=node_id)
intra_relation_report(X_ta, H_ta, A_ta, "TAMIL", node_id=node_id)

# =====================================================
# SAVE OUTPUTS
# =====================================================

print("\nSaving outputs...")
save_npy_and_txt(H_en, "english_gcn")
save_npy_and_txt(H_ta, "tamil_gcn")
print("Saved embeddings")

# =====================================================
# VISUALIZATION
# =====================================================

print("\nGenerating visualizations...")

# English global
visualize_global_tsne(
    X_en, H_en, "English Embeddings",
    os.path.join(out_dir, "english_global_tsne.png"),
    highlight_node=node_id
)

# English local
visualize_local_neighbors_tsne(
    X_en, H_en, A_en, "English",
    os.path.join(out_dir, "english_local_tsne.png"),
    node_id=node_id
)

# Tamil global
visualize_global_tsne(
    X_ta, H_ta, "Tamil Embeddings",
    os.path.join(out_dir, "tamil_global_tsne.png"),
    highlight_node=node_id
)

# Tamil local
visualize_local_neighbors_tsne(
    X_ta, H_ta, A_ta, "Tamil",
    os.path.join(out_dir, "tamil_local_tsne.png"),
    node_id=node_id
)

print(" Visualizations saved")

# =====================================================
# SUMMARY
# =====================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Output directory: {out_dir}")
print("\nFiles saved:")
print("  - english_gcn.npy + english_gcn.txt")
print("  - tamil_gcn.npy + tamil_gcn.txt")
print("  - english_global_tsne.png")
print("  - english_local_tsne.png")
print("  - tamil_global_tsne.png")
print("  - tamil_local_tsne.png")
print("="*60)