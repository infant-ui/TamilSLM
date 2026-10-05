import networkx as nx
import matplotlib.pyplot as plt
import ollama
import os

# -----------------------------
# Extract concept relationships (Tamil version)
# -----------------------------
def extract_concepts(text):

    prompt = f"""
கொடுக்கப்பட்டுள்ள உரையிலிருந்து கருத்து உறவுகளை (concept relationships) பிரித்தெடுக்கவும்.

விதிகள்:
- மூன்று பகுதிகளைக் கொண்ட தொடர்புகளை (triples) மட்டுமே வெளியிடவும்.
- இந்த துல்லியமான வடிவமைப்பைப் பயன்படுத்தவும்:

கருத்து1 | உறவு | கருத்து2

எடுத்துக்காட்டு:
நீர் | ஆவியாகிறது | பெருங்கடல்
மேகங்கள் | பொழிகிறது | மழை

விளக்கங்கள் எதுவும் எழுத வேண்டாம்.

உரை:
{text}
"""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )

    output = response["message"]["content"]

    triples = []

    for line in output.split("\n"):
        line = line.strip()

        if "|" in line:
            parts = [p.strip() for p in line.split("|")]

            if len(parts) == 3:
                triples.append((parts[0], parts[1], parts[2]))

    return triples


# -----------------------------
# Main concept generator
# -----------------------------
def generate_concept_map(text):

    triples = extract_concepts(text)

    if len(triples) == 0:
        print("No relationships extracted")
        return

    G = nx.DiGraph()

    for c1, rel, c2 in triples:
        G.add_edge(c1, c2, label=rel)

    # Use spring layout
    pos = nx.spring_layout(G, k=1)

    plt.figure(figsize=(10,7))

    # Support Tamil font rendering if system fonts are available; fall back to default
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        node_size=3500,
        font_size=10
    )

    edge_labels = nx.get_edge_attributes(G, "label")

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=9
    )

    plt.title("Tamil Concept Graph")

    folder = "tamil_concept"
    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, "concept_graph.png")

    plt.savefig(filepath)

    print("Concept graph saved to:", filepath)

    # Note: plt.show() might block if run from headless scripts, but matches original design
    plt.show()
