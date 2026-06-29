import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go


# =====================================================
# CONFIG
# =====================================================

english_latent_path = "stage_outputs/stage2_dae/english_latent_Zx.npy"
tamil_latent_path   = "stage_outputs/stage2_dae/tamil_latent_Zy.npy"

english_chunk_json = "chunks/english_chunks.json"
tamil_chunk_json   = "chunks/tamil_chunks.json"

VIS_METHOD = "tsne"   # "pca" or "tsne"
K_VIS = 206           # show all pairs
TOPK_SHOW = 5         # show top-k matches
SHOW_TOP2 = 1         # show top-1 match visually + in text


# =====================================================
# LOAD CHUNKS FROM JSON
# =====================================================

def load_chunks_from_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "chunks" in data:
        data = data["chunks"]

    # List[str]
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], str):
        return [str(x).strip() for x in data]

    # List[dict]
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        if "text" in data[0]:
            # If chunk ids exist, sort by id to keep alignment stable
            if "id" in data[0]:
                data_sorted = sorted(data, key=lambda x: int(x.get("id", 0)))
                return [str(x.get("text", "")).strip() for x in data_sorted]
            return [str(x.get("text", "")).strip() for x in data]

    # Dict
    if isinstance(data, dict):
        keys = sorted(data.keys(), key=lambda k: int(k))
        return [str(data[k]).strip() for k in keys]

    raise ValueError("Unsupported JSON format for chunks file")


# =====================================================
# LOAD DATA
# =====================================================

Zx = np.load(english_latent_path)
Zy = np.load(tamil_latent_path)

en_texts = load_chunks_from_json(english_chunk_json)
ta_texts = load_chunks_from_json(tamil_chunk_json)

K = min(len(Zx), len(Zy), len(en_texts), len(ta_texts))
Zx = Zx[:K]
Zy = Zy[:K]
en_texts = en_texts[:K]
ta_texts = ta_texts[:K]

# Normalize (cosine)
Zx = Zx / np.clip(np.linalg.norm(Zx, axis=1, keepdims=True), 1e-9, None)
Zy = Zy / np.clip(np.linalg.norm(Zy, axis=1, keepdims=True), 1e-9, None)

print("Loaded Stage-2 latents:")
print("Zx:", Zx.shape, "Zy:", Zy.shape)
print("Total aligned pairs K =", K)

K_vis = min(K_VIS, K)
Zx_vis = Zx[:K_vis]
Zy_vis = Zy[:K_vis]


# =====================================================
# IMPORTANT: SINGLE COMBINED SPACE
# =====================================================

Z_all = np.vstack([Zx_vis, Zy_vis])  # (2*K_vis, dim)

def project_2d(X, method="tsne"):
    if method == "pca":
        pca = PCA(n_components=2)
        return pca.fit_transform(X)

    if method == "tsne":
        tsne = TSNE(
            n_components=2,
            perplexity=min(30, max(5, len(X) // 7)),
            random_state=42,
            init="random",
            learning_rate="auto"
        )
        return tsne.fit_transform(X)

    raise ValueError("VIS_METHOD must be 'pca' or 'tsne'")

coords_all = project_2d(Z_all, VIS_METHOD)

coords_en = coords_all[:K_vis]
coords_ta = coords_all[K_vis:]


# =====================================================
# PRECOMPUTE SIMILARITY (VIS SUBSET)
# =====================================================

S_vis = cosine_similarity(Zx_vis, Zy_vis)  # (K_vis,K_vis)


# =====================================================
# BUILD BASE FIGURE (EN IDs, TA hover only)
# =====================================================

def build_base_figure():
    fig = go.Figure()

    # English points (WITH IDs printed)
    fig.add_trace(go.Scatter(
        x=coords_en[:, 0],
        y=coords_en[:, 1],
        mode="markers+text",
        text=[str(i) for i in range(K_vis)],
        textposition="top center",
        marker=dict(size=10, opacity=0.85),
        name="English",
        customdata=[("EN", i) for i in range(K_vis)],
        hovertemplate="English<br>chunk_id=%{text}<extra></extra>"
    ))

    # Tamil points (NO printed IDs, only hover)
    fig.add_trace(go.Scatter(
        x=coords_ta[:, 0],
        y=coords_ta[:, 1],
        mode="markers",
        marker=dict(size=10, opacity=0.85),
        name="Tamil",
        customdata=[("TA", i) for i in range(K_vis)],
        hovertemplate="Tamil<br>chunk_id=%{customdata[1]}<extra></extra>"
    ))

    fig.update_layout(
        title=f"Stage-2 Alignment (English ↔ Tamil)",
        height=740,
        clickmode="event+select",
        legend=dict(x=0.86, y=0.98),
        margin=dict(l=20, r=20, t=70, b=20)
    )

    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)

    return fig


fig_base = build_base_figure()


# =====================================================
# HELPERS
# =====================================================

def parse_click(clickData):
    if clickData is None:
        return None, None
    lang, idx = clickData["points"][0]["customdata"]
    return lang, int(idx)


def topk_matches_for_english_vis(en_id, topk=5):
    sims = S_vis[en_id]
    order = np.argsort(sims)[::-1]
    return [(int(j), float(sims[j])) for j in order[:topk]]


def topk_matches_for_tamil_vis(ta_id, topk=5):
    sims = S_vis[:, ta_id]
    order = np.argsort(sims)[::-1]
    return [(int(i), float(sims[i])) for i in order[:topk]]


def add_click_connection_top2(fig, en_id, ta_ids):
    """
    Clicked English -> highlight English + top Tamil match (ONLY 1)
    """
    fig2 = go.Figure(fig)

    # EN highlight
    fig2.add_trace(go.Scatter(
        x=[coords_en[en_id, 0]],
        y=[coords_en[en_id, 1]],
        mode="markers+text",
        text=[f"EN {en_id}"],
        textposition="top center",
        marker=dict(size=26, symbol="star"),
        name="EN_SELECTED"
    ))

    # Only top-1
    ta_id = ta_ids[0]

    # connection line
    fig2.add_trace(go.Scatter(
        x=[coords_en[en_id, 0], coords_ta[ta_id, 0]],
        y=[coords_en[en_id, 1], coords_ta[ta_id, 1]],
        mode="lines",
        line=dict(width=3),
        opacity=0.75,
        name="Match 1"
    ))

    # TA highlight
    fig2.add_trace(go.Scatter(
        x=[coords_ta[ta_id, 0]],
        y=[coords_ta[ta_id, 1]],
        mode="markers+text",
        text=[f"TA {ta_id}"],
        textposition="top center",
        marker=dict(size=24, symbol="star"),
        name="TA_MATCH_1"
    ))

    return fig2


def add_click_connection_top2_reverse(fig, ta_id, en_ids):
    """
    Clicked Tamil -> highlight Tamil + top English match (ONLY 1)
    """
    fig2 = go.Figure(fig)

    # TA highlight
    fig2.add_trace(go.Scatter(
        x=[coords_ta[ta_id, 0]],
        y=[coords_ta[ta_id, 1]],
        mode="markers+text",
        text=[f"TA {ta_id}"],
        textposition="top center",
        marker=dict(size=26, symbol="star"),
        name="TA_SELECTED"
    ))

    # Only top-1
    en_id = en_ids[0]

    # connection line
    fig2.add_trace(go.Scatter(
        x=[coords_en[en_id, 0], coords_ta[ta_id, 0]],
        y=[coords_en[en_id, 1], coords_ta[ta_id, 1]],
        mode="lines",
        line=dict(width=3),
        opacity=0.75,
        name="Match 1"
    ))

    # EN highlight
    fig2.add_trace(go.Scatter(
        x=[coords_en[en_id, 0]],
        y=[coords_en[en_id, 1]],
        mode="markers+text",
        text=[f"EN {en_id}"],
        textposition="top center",
        marker=dict(size=24, symbol="star"),
        name="EN_MATCH_1"
    ))

    return fig2


def format_two_chunks(prefix, ids_sims, texts):
    """
    ids_sims: [(id, sim)] (length 1 only now)
    """
    out = []
    for rank, (cid, sim) in enumerate(ids_sims, start=1):
        out.append(f"[TOP-{rank}] {prefix} chunk_id = {cid} | sim={sim:.4f}")
        out.append("")
        out.append(texts[cid])

        if rank != len(ids_sims):
            out.append("\n" + "=" * 80 + "\n")
    return "\n".join(out)


# =====================================================
# DASH APP
# =====================================================

app = dash.Dash(__name__)

app.layout = html.Div(
    style={"fontFamily": "Arial", "padding": "18px"},
    children=[

        html.H2("Stage-2 Semantic Alignment Viewer"),

       

        dcc.Graph(id="graph_all", figure=fig_base),

        html.Hr(),

        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
            children=[

                html.Div(children=[
                    html.H3("English Chunk"),
                    html.Div(id="en_text", style={
                        "whiteSpace": "pre-wrap",
                        "border": "1px solid #ccc",
                        "padding": "10px",
                        "borderRadius": "8px",
                        "height": "300px",
                        "overflowY": "auto"
                    })
                ]),

                html.Div(children=[
                    html.H3("Tamil Chunk"),
                    html.Div(id="ta_text", style={
                        "whiteSpace": "pre-wrap",
                        "border": "1px solid #ccc",
                        "padding": "10px",
                        "borderRadius": "8px",
                        "height": "300px",
                        "overflowY": "auto"
                    })
                ]),

            ]
        ),

        html.Br(),

        html.Div(children=[
            html.H3("Semantic Similarity Details"),
            html.Pre(id="sim_details", style={
                "whiteSpace": "pre-wrap",
                "border": "1px solid #ccc",
                "padding": "12px",
                "borderRadius": "8px",
                "fontSize": "14px"
            })
        ])
    ]
)


# =====================================================
# CALLBACK
# =====================================================

@app.callback(
    Output("graph_all", "figure"),
    Output("en_text", "children"),
    Output("ta_text", "children"),
    Output("sim_details", "children"),
    Input("graph_all", "clickData")
)
def update_view(clickData):

    if clickData is None:
        return (
            fig_base,
            "Click an English or Tamil point.",
            "Tamil chunk(s) will appear here.",
            "Cosine similarity + rank + top-k retrieval will appear here."
        )

    lang, cid = parse_click(clickData)
    if lang is None:
        return fig_base, "Invalid click.", "", ""

    # =====================================================
    # CLICK ENGLISH -> TOP-1 TAMIL
    # =====================================================
    if lang == "EN":
        en_id = cid

        matches = topk_matches_for_english_vis(en_id, TOPK_SHOW)
        top2 = matches[:SHOW_TOP2]  # now only 1 item

        ta_ids = [tid for tid, _ in top2]
        fig2 = add_click_connection_top2(fig_base, en_id=en_id, ta_ids=ta_ids)

        # correct pair rank
        order = np.argsort(S_vis[en_id])[::-1]
        rank_correct = int(np.where(order == en_id)[0][0]) + 1
        sim_correct = float(S_vis[en_id, en_id])

        en_render = en_texts[en_id]
        ta_render = format_two_chunks("Tamil", top2, ta_texts)

        lines = []
        lines.append(f"CLICKED: English chunk_id = {en_id}")
        lines.append("")
        lines.append(f"1) TAMIL MATCH (within plotted subset)")
        for r, (tid, simv) in enumerate(top2, start=1):
            lines.append(f"   Rank {r:02d}: Tamil {tid} | sim={simv:.4f}")

        lines.append("")
        lines.append("2) CORRECT PAIR CHECK")
        lines.append(f"   correct pair is Tamil chunk_id = {en_id}")
        lines.append(f"   cosine(correct pair) = {sim_correct:.4f}")
        lines.append(f"   rank(correct pair among plotted Tamil) = {rank_correct} / {K_vis}")

       
        return fig2, en_render, ta_render, "\n".join(lines)

    # =====================================================
    # CLICK TAMIL -> TOP-1 ENGLISH
    # =====================================================
    else:
        ta_id = cid

        matches = topk_matches_for_tamil_vis(ta_id, TOPK_SHOW)
        top2 = matches[:SHOW_TOP2]  # now only 1 item

        en_ids = [eid for eid, _ in top2]
        fig2 = add_click_connection_top2_reverse(fig_base, ta_id=ta_id, en_ids=en_ids)

        # correct pair rank
        order = np.argsort(S_vis[:, ta_id])[::-1]
        rank_correct = int(np.where(order == ta_id)[0][0]) + 1
        sim_correct = float(S_vis[ta_id, ta_id])

        ta_render = ta_texts[ta_id]
        en_render = format_two_chunks("English", top2, en_texts)

        lines = []
        lines.append(f"CLICKED: Tamil chunk_id = {ta_id}")
        lines.append("")
        lines.append(f"1) ENGLISH MATCH (within plotted subset)")
        for r, (eid, simv) in enumerate(top2, start=1):
            lines.append(f"   Rank {r:02d}: English {eid} | sim={simv:.4f}")

        lines.append("")
        lines.append("2) CORRECT PAIR CHECK")
        lines.append(f"   correct pair is English chunk_id = {ta_id}")
        lines.append(f"   cosine(correct pair) = {sim_correct:.4f}")
        lines.append(f"   rank(correct pair among plotted English) = {rank_correct} / {K_vis}")

        lines.append("")
        
        return fig2, en_render, ta_render, "\n".join(lines)


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    print("\nOpen this in your browser after running:")
    print("http://127.0.0.1:8050/\n")
    app.run(debug=True)
