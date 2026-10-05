import json
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE

import dash
from dash import dcc, html, Input, Output
import plotly.express as px


# =====================================================
# CONFIG
# =====================================================

node_id = 3

english_embed_before_path = "bilingual_embeddings/english_shared.npy"
english_embed_after_path  = "stage_outputs/stage1_gcn/english_gcn.npy"

english_adj_path = "graphs/english/adjacency_weighted.npy"
english_chunk_json = "chunks/english_chunks.json"


# =====================================================
# LOAD CHUNKS FROM JSON
# =====================================================

def load_chunks_from_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "chunks" in data:
        data = data["chunks"]

    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], str):
        return [str(x).strip() for x in data]

    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        if "text" in data[0]:
            if "id" in data[0]:
                data_sorted = sorted(data, key=lambda x: int(x.get("id", 0)))
                return [str(x.get("text", "")).strip() for x in data_sorted]
            return [str(x.get("text", "")).strip() for x in data]

    if isinstance(data, dict):
        keys = sorted(data.keys(), key=lambda k: int(k))
        return [str(data[k]).strip() for k in keys]

    raise ValueError("Unsupported JSON format")


# =====================================================
# WORD OVERLAP HIGHLIGHT (RED)
# =====================================================

def tokenize_simple(text):
    return text.split()

def get_common_words(text_a, text_b):
    wa = set([w.lower() for w in tokenize_simple(text_a)])
    wb = set([w.lower() for w in tokenize_simple(text_b)])
    common = wa.intersection(wb)
    common = set([w for w in common if len(w) > 2])
    return common

def render_text_with_red_highlight(text, common_words):
    tokens = tokenize_simple(text)
    out = []
    for w in tokens:
        clean = w.lower()
        if clean in common_words:
            out.append(html.Span(w + " ", style={"color": "red", "fontWeight": "bold"}))
        else:
            out.append(html.Span(w + " "))
    return out


# =====================================================
# NORMALIZE WEIGHTED ADJACENCY
# A_hat = D^-1(A + I)
# =====================================================

def build_A_hat_weighted(A):
    N = A.shape[0]
    A_self = A.copy()

    # self-loop = +1
    np.fill_diagonal(A_self, A_self.diagonal() + 1.0)

    D = np.sum(A_self, axis=1)
    D_inv = 1.0 / np.clip(D, 1e-9, None)

    A_hat = (D_inv[:, None]) * A_self
    return A_hat


# =====================================================
# LOAD DATA
# =====================================================

X_before = np.load(english_embed_before_path)
X_after  = np.load(english_embed_after_path)

A = np.load(english_adj_path)
texts = load_chunks_from_json(english_chunk_json)

K = min(len(X_before), len(X_after), len(texts))
X_before = X_before[:K]
X_after  = X_after[:K]
A = A[:K, :K]
texts = texts[:K]

A_hat = build_A_hat_weighted(A)


# =====================================================
# NEIGHBORS OF FIXED NODE
# =====================================================

neighbors = np.where(A[node_id] > 0)[0]
neighbors = neighbors[neighbors != node_id]

subset_idx = np.array([node_id] + neighbors.tolist())


# =====================================================
# t-SNE BEFORE + AFTER
# =====================================================

def compute_tsne(X_sub):
    tsne = TSNE(
        n_components=2,
        perplexity=min(10, len(X_sub) - 1),
        random_state=42,
        init="random",
        learning_rate="auto"
    )
    return tsne.fit_transform(X_sub)

coords_before = compute_tsne(X_before[subset_idx])
coords_after  = compute_tsne(X_after[subset_idx])


# =====================================================
# BUILD FIGURES
# =====================================================

df_before = pd.DataFrame({
    "x": coords_before[:, 0],
    "y": coords_before[:, 1],
    "chunk_id": subset_idx
})
df_after = pd.DataFrame({
    "x": coords_after[:, 0],
    "y": coords_after[:, 1],
    "chunk_id": subset_idx
})

df_before["type"] = df_before["chunk_id"].apply(lambda cid: "FIXED" if cid == node_id else "OTHER")
df_after["type"]  = df_after["chunk_id"].apply(lambda cid: "FIXED" if cid == node_id else "OTHER")

df_before["hover"] = df_before["chunk_id"].apply(lambda cid: f"chunk_id={cid}")
df_after["hover"]  = df_after["chunk_id"].apply(lambda cid: f"chunk_id={cid}")


fig_before = px.scatter(
    df_before,
    x="x", y="y",
    text="chunk_id",
    color="type",
    hover_name="hover",
    title="BEFORE GCN (Local Neighbors)"
)

fig_after = px.scatter(
    df_after,
    x="x", y="y",
    text="chunk_id",
    color="type",
    hover_name="hover",
    title="AFTER GCN (Local Neighbors)"
)

fig_before.update_traces(marker=dict(size=18), textposition="top center")
fig_after.update_traces(marker=dict(size=18), textposition="top center")

# fixed node pink
fig_before.for_each_trace(
    lambda t: t.update(marker=dict(color="hotpink", size=30))
    if t.name == "FIXED" else None
)
fig_after.for_each_trace(
    lambda t: t.update(marker=dict(color="hotpink", size=30))
    if t.name == "FIXED" else None
)


# =====================================================
# DASH APP
# =====================================================

app = dash.Dash(__name__)

app.layout = html.Div(
    style={"fontFamily": "Arial", "padding": "20px"},
    children=[

        html.H2("Local Viewer: BEFORE vs AFTER GCN"),

        html.P(f"Fixed node = {node_id} | Neighbors = {len(neighbors)}"),

        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
            children=[
                dcc.Graph(id="graph_before", figure=fig_before),
                dcc.Graph(id="graph_after", figure=fig_after),
            ]
        ),

        html.Hr(),

        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "25px"},
            children=[

                html.Div(
                    children=[
                        html.H3(f"Fixed Node {node_id} Text"),
                        html.Div(id="fixed_text", style={
                            "whiteSpace": "pre-wrap",
                            "border": "1px solid #ccc",
                            "padding": "10px",
                            "borderRadius": "8px",
                            "height": "260px",
                            "overflowY": "auto"
                        })
                    ]
                ),

                html.Div(
                    children=[
                        html.H3("Clicked Node Text"),
                        html.Div(id="clicked_text", style={
                            "whiteSpace": "pre-wrap",
                            "border": "1px solid #ccc",
                            "padding": "10px",
                            "borderRadius": "8px",
                            "height": "260px",
                            "overflowY": "auto"
                        })
                    ]
                ),

            ]
        ),

        html.Br(),

        html.Div(
            children=[
                html.H3("Full Calculation Output"),
                html.Pre(id="sim_details", style={
                    "whiteSpace": "pre-wrap",
                    "border": "1px solid #ccc",
                    "padding": "12px",
                    "borderRadius": "8px",
                    "fontSize": "14px"
                })
            ]
        )
    ]
)


# =====================================================
# HELPER: CLICKED ID
# =====================================================

def extract_chunk_id(clickData):
    hover = clickData["points"][0].get("hovertext", "")
    if "chunk_id=" in hover:
        return int(hover.split("chunk_id=")[-1].strip())
    return int(clickData["points"][0]["text"])


# =====================================================
# CALLBACK
# =====================================================

@app.callback(
    Output("fixed_text", "children"),
    Output("clicked_text", "children"),
    Output("sim_details", "children"),
    Input("graph_before", "clickData"),
    Input("graph_after", "clickData")
)
def update_text(clickData_before, clickData_after):

    fixed_text = texts[node_id]

    if clickData_before is None and clickData_after is None:
        return (
            render_text_with_red_highlight(fixed_text, set()),
            "Click any node in BEFORE or AFTER graph.",
            "Full cosine + rank + avg similarity + A_hat calculation will appear here."
        )

    clickData = clickData_after if clickData_after is not None else clickData_before
    clicked_chunk_id = extract_chunk_id(clickData)
    clicked_text = texts[clicked_chunk_id]

    # -------------------------
    # cosine similarity
    # -------------------------
    sim_before = cosine_similarity(
        X_before[node_id].reshape(1, -1),
        X_before[clicked_chunk_id].reshape(1, -1)
    )[0][0]

    sim_after = cosine_similarity(
        X_after[node_id].reshape(1, -1),
        X_after[clicked_chunk_id].reshape(1, -1)
    )[0][0]

    diff = sim_after - sim_before

    # -------------------------
    # rank among neighbors
    # -------------------------
    sims_neighbors_before = []
    sims_neighbors_after = []

    for n in neighbors:
        sb = cosine_similarity(X_before[node_id].reshape(1, -1), X_before[n].reshape(1, -1))[0][0]
        sa = cosine_similarity(X_after[node_id].reshape(1, -1), X_after[n].reshape(1, -1))[0][0]
        sims_neighbors_before.append((n, sb))
        sims_neighbors_after.append((n, sa))

    sims_neighbors_before_sorted = sorted(sims_neighbors_before, key=lambda x: x[1], reverse=True)
    sims_neighbors_after_sorted = sorted(sims_neighbors_after, key=lambda x: x[1], reverse=True)

    neighbor_ids_before = [n for n, _ in sims_neighbors_before_sorted]
    neighbor_ids_after = [n for n, _ in sims_neighbors_after_sorted]

    if clicked_chunk_id in neighbor_ids_before:
        before_rank = neighbor_ids_before.index(clicked_chunk_id) + 1
        after_rank = neighbor_ids_after.index(clicked_chunk_id) + 1
    else:
        before_rank = None
        after_rank = None

    # -------------------------
    # avg similarity to neighbors
    # -------------------------
    avg_before = float(np.mean([s for _, s in sims_neighbors_before_sorted]))
    avg_after = float(np.mean([s for _, s in sims_neighbors_after_sorted]))

    # -------------------------
    # weighted influence
    # -------------------------
    weighted_deg = float(np.sum(A[node_id]))
    weighted_deg_self = weighted_deg + 1.0
    a_hat_ij = float(A_hat[node_id, clicked_chunk_id])

    # -------------------------
    # highlight overlap
    # -------------------------
    common_words = get_common_words(fixed_text, clicked_text)
    fixed_render = render_text_with_red_highlight(fixed_text, common_words)
    clicked_render = render_text_with_red_highlight(clicked_text, common_words)

    # -------------------------
    # report
    # -------------------------
    lines = []

    lines.append(f"Clicked chunk id: {clicked_chunk_id}")
    lines.append("")

    lines.append("1) COSINE SIMILARITY")
    lines.append(f"   sim_before = cos(X_before[{node_id}], X_before[{clicked_chunk_id}]) = {sim_before:.4f}")
    lines.append(f"   sim_after  = cos(X_after [{node_id}], X_after [{clicked_chunk_id}]) = {sim_after:.4f}")
    lines.append(f"   difference = sim_after - sim_before = {diff:+.4f}")
    lines.append("")

    lines.append("2) RANK AMONG FIXED NODE's NEIGHBORS (kNN graph)")
    lines.append(f"   total neighbors of node {node_id} = {len(neighbors)}")
    if before_rank is None:
        lines.append("   clicked node is NOT a direct neighbor of fixed node.")
    else:
        lines.append(f"   rank BEFORE = {before_rank} / {len(neighbors)}")
        lines.append(f"   rank AFTER  = {after_rank} / {len(neighbors)}")
    lines.append("")

    lines.append("3) AVERAGE SIMILARITY TO ALL NEIGHBORS")
    lines.append(f"   avg_before = {avg_before:.4f}")
    lines.append(f"   avg_after  = {avg_after:.4f}")
    lines.append(f"   change     = {avg_after - avg_before:+.4f}")
    lines.append("")

    lines.append("4) WEIGHTED GCN INFLUENCE (Paper Eq(5): A_hat = D^-1(A + I))")
    lines.append(f"   weighted deg(node {node_id}) = sum_j A({node_id},j) = {weighted_deg:.4f}")
    lines.append(f"   after self-loop: deg + 1 = {weighted_deg_self:.4f}")
    lines.append("")
    lines.append(f"   A_hat({node_id},{clicked_chunk_id}) = {a_hat_ij:.6f}")
    lines.append(f"   meaning: node {clicked_chunk_id} contributes {a_hat_ij*100:.3f}% into node {node_id}'s update.")
    lines.append("")

    return fixed_render, clicked_render, "\n".join(lines)


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    print("\nOpen this in your browser after running:")
    print("http://127.0.0.1:8050/\n")
    app.run(debug=True)
