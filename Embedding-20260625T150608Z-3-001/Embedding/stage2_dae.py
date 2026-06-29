import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# =====================================================
# CONFIG
# =====================================================

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

input_dim = 768
latent_dim = 768

epochs = 250
batch_size = 32
lr = 1e-3

alpha_rec = 1.0
alpha_pair = 3.0        # 🔥 IMPORTANT
alpha_prior = 0.1

out_dir = "stage_outputs/stage2_dae"
os.makedirs(out_dir, exist_ok=True)

torch.manual_seed(42)
np.random.seed(42)

# =====================================================
# LOAD STAGE-1 OUTPUTS
# =====================================================

X_en = np.load("stage_outputs/stage1_gcn/english_gcn.npy")
X_ta = np.load("stage_outputs/stage1_gcn/tamil_gcn.npy")

K = min(len(X_en), len(X_ta))
X_en = X_en[:K]
X_ta = X_ta[:K]

X_en = torch.tensor(X_en, dtype=torch.float32).to(device)
X_ta = torch.tensor(X_ta, dtype=torch.float32).to(device)

# =====================================================
# MODELS
# =====================================================

class Encoder(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.fc = nn.Linear(dim, dim)

    def forward(self, x):
        return self.fc(x)


class Decoder(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.fc = nn.Linear(dim, dim)

    def forward(self, z):
        return self.fc(z)


Encx = Encoder(latent_dim).to(device)
Ency = Encoder(latent_dim).to(device)
Decx = Decoder(latent_dim).to(device)
Decy = Decoder(latent_dim).to(device)

# =====================================================
# LOSSES
# =====================================================

mse = nn.MSELoss()

def cosine_pair_loss(zx, zy):
    zx = nn.functional.normalize(zx, dim=1)
    zy = nn.functional.normalize(zy, dim=1)
    return torch.mean(1.0 - torch.sum(zx * zy, dim=1))

# =====================================================
# OPTIMIZER
# =====================================================

optimizer = optim.Adam(
    list(Encx.parameters()) +
    list(Ency.parameters()) +
    list(Decx.parameters()) +
    list(Decy.parameters()),
    lr=lr
)

# =====================================================
# TRAINING
# =====================================================

print("\nTraining Stage-2 with explicit semantic alignment...")

for epoch in range(1, epochs + 1):

    perm = torch.randperm(K)
    X_en_shuf = X_en[perm]
    X_ta_shuf = X_ta[perm]

    total_loss = 0.0

    for i in range(0, K, batch_size):
        x = X_en_shuf[i:i + batch_size]
        y = X_ta_shuf[i:i + batch_size]

        zx = Encx(x)
        zy = Ency(y)

        xr = Decx(zx)
        yr = Decy(zy)

        # Reconstruction
        Lrec = mse(xr, x) + mse(yr, y)

        # 🔥 Pairwise semantic alignment
        Lpair = cosine_pair_loss(zx, zy)

        # Latent regularization
        Lprior = mse(zx.mean(0), zy.mean(0))

        loss = alpha_rec * Lrec + alpha_pair * Lpair + alpha_prior * Lprior

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    if epoch % 25 == 0 or epoch == 1:
        print(f"Epoch {epoch:03d} | Loss={total_loss:.4f} | Pair={Lpair.item():.4f}")

print("Training complete.")

# =====================================================
# SAVE LATENTS
# =====================================================

with torch.no_grad():
    Zx = Encx(X_en).cpu().numpy()
    Zy = Ency(X_ta).cpu().numpy()

np.save(f"{out_dir}/english_latent_Zx.npy", Zx)
np.save(f"{out_dir}/tamil_latent_Zy.npy", Zy)

# =====================================================
# VISUALIZATION (PCA + t-SNE)
# =====================================================

K_vis = min(150, K)

Z_all = np.vstack([
    Zx[:K_vis],
    Zy[:K_vis]
])

Z_all = Z_all / np.linalg.norm(Z_all, axis=1, keepdims=True)

# ----- PCA -----
pca = PCA(n_components=2)
Z_pca = pca.fit_transform(Z_all)

# ----- t-SNE -----
tsne = TSNE(n_components=2, perplexity=30, random_state=42)
Z_tsne = tsne.fit_transform(Z_all)

def plot(Z2d, title, fname):
    plt.figure(figsize=(9, 7))
    plt.scatter(Z2d[:K_vis,0], Z2d[:K_vis,1], label="English", alpha=0.8)
    plt.scatter(Z2d[K_vis:,0], Z2d[K_vis:,1], label="Tamil", alpha=0.8)

    for i in range(K_vis):
        plt.plot(
            [Z2d[i,0], Z2d[i+K_vis,0]],
            [Z2d[i,1], Z2d[i+K_vis,1]],
            alpha=0.3
        )

    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{out_dir}/{fname}", dpi=300)
    plt.show()

plot(Z_pca, "Stage-2 Semantic Alignment (PCA)", "stage2_pca.png")
plot(Z_tsne, "Stage-2 Semantic Alignment (t-SNE)", "stage2_tsne.png")

print("\nAll outputs saved in:", out_dir)

def plot_tsne_with_labels(Z2d, title, fname):
    """
    t-SNE plot with numeric chunk-id labels on BOTH English and Tamil nodes.
    No labels on alignment edges.
    """

    plt.figure(figsize=(14, 11))

    # English nodes
    plt.scatter(
        Z2d[:K_vis, 0],
        Z2d[:K_vis, 1],
        label="English",
        alpha=0.85
    )

    # Tamil nodes
    plt.scatter(
        Z2d[K_vis:, 0],
        Z2d[K_vis:, 1],
        label="Tamil",
        alpha=0.85
    )

    # Draw alignment lines (NO labels here)
    for i in range(K_vis):
        plt.plot(
            [Z2d[i, 0], Z2d[i + K_vis, 0]],
            [Z2d[i, 1], Z2d[i + K_vis, 1]],
            alpha=0.25
        )

    # Add numeric labels ON NODES
    for i in range(K_vis):
        # English label
        plt.text(
            Z2d[i, 0],
            Z2d[i, 1],
            str(i),
            fontsize=8,
            ha="right",
            va="bottom"
        )

        # Tamil label
        plt.text(
            Z2d[i + K_vis, 0],
            Z2d[i + K_vis, 1],
            str(i),
            fontsize=8,
            ha="left",
            va="top"
        )

    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{out_dir}/{fname}", dpi=300)
    plt.show()



plot_tsne_with_labels(
    Z_tsne,
    "Stage-2 Semantic Alignment (t-SNE with Chunk IDs)",
    "stage2_tsne_labelled.png"
)
