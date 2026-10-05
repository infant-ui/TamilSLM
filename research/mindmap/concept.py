import networkx as nx
import matplotlib.pyplot as plt
import ollama
import os

# -----------------------------
# Extract concept relationships
# -----------------------------
def extract_concepts(text):

    prompt = f"""
Extract concept relationships from the text.

Rules:
- Output ONLY triples
- Use this exact format:

Concept1 | Relation | Concept2

Example:
Water | evaporates from | Ocean
Clouds | produce | Rain

Do not write explanations.

Text:
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

    pos = nx.spring_layout(G, k=1)

    plt.figure(figsize=(10,7))

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        node_size=3500,
        font_size=10,
        arrows=True
    )

    edge_labels = nx.get_edge_attributes(G, "label")

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=9
    )

    plt.title("Concept Graph")

    folder = "concept"
    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, "concept_graph.png")

    plt.savefig(filepath)

    print("Concept graph saved to:", filepath)

    plt.show()