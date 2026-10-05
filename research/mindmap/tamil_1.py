import ollama
import json
import networkx as nx
import matplotlib.pyplot as plt
import os
import time

# ---------------------------------------------------
# STEP 1: Generate Hierarchical Structure from LLM (Tamil version)
# ---------------------------------------------------
def generate_outline(text):

    prompt = f"""
    கொடுக்கப்பட்டுள்ள உரையிலிருந்து சுத்தமான படிநிலை மன வரைபடத்தை (hierarchical mind map) பிரித்தெடுக்கவும்.

    கடுமையான விதிகள்:
    - தலைப்புகளை மீண்டும் செய்ய வேண்டாம்.
    - பெயர்களை சுருக்க வேண்டாம்.
    - உடன்பிறந்த தலைப்புகளை ஒரே மட்டத்தில் வைக்கவும்.
    - தொடர்பில்லாத தலைப்புகளை ஒன்றோடொன்று இணைக்க வேண்டாம்.
    - வெற்று வார்த்தைகள் அல்லது தற்காலிக வார்த்தைகளைப் பயன்படுத்த வேண்டாம்.
    - செல்லுபடியாகும் JSON ஐ மட்டுமே வெளியிடவும்.
    - விளக்க உரை எதுவும் எழுத வேண்டாம்.

    வடிவமைப்பு:
    {{
      "முக்கிய தலைப்பு": {{
        "துணைத் தலைப்பு": {{
          "துணை துணைத் தலைப்பு": {{}}
        }}
      }}
    }}

    உரை:
    {text}
    """

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response["message"]["content"]

    start = content.find("{")
    end = content.rfind("}") + 1

    if start == -1 or end == -1:
        raise ValueError("Model did not return valid JSON.")

    json_string = content[start:end]

    data = json.loads(json_string) # JSON string to dictionary

    return clean_structure(data)


# ---------------------------------------------------
# STEP 2: Clean Structure
# ---------------------------------------------------
def clean_structure(data):

    cleaned = {}

    for key, value in data.items():

        key = key.strip()

        if key not in cleaned:

            if isinstance(value, dict):

                sub_clean = clean_structure(value)

                sub_clean = { # Remove self-nesting
                    k: v for k, v in sub_clean.items()
                    if k.lower() != key.lower()
                }

                cleaned[key] = sub_clean

            else:
                cleaned[key] = value

    return cleaned


# ---------------------------------------------------
# STEP 3: Add Graph Nodes
# ---------------------------------------------------
def add_nodes_edges(graph, parent, data):

    for key, value in data.items():

        graph.add_edge(parent, key)

        if isinstance(value, dict):
            add_nodes_edges(graph, key, value)


# ---------------------------------------------------
# STEP 4: Layout
# ---------------------------------------------------
def hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):

    pos = {root: (xcenter, vert_loc)}

    children = list(G.successors(root))

    if children:

        dx = width / len(children)

        nextx = xcenter - width / 2 - dx / 2 # calculates where the first child should start

        for child in children:

            nextx += dx

            pos.update(
                hierarchy_pos(
                    G,
                    child,
                    width=dx,
                    vert_gap=vert_gap,
                    vert_loc=vert_loc - vert_gap,
                    xcenter=nextx
                )
            )

    return pos


# ---------------------------------------------------
# STEP 5: Draw Mind Map (Tamil version)
# ---------------------------------------------------
def draw_mindmap(data):

    G = nx.DiGraph()

    root = list(data.keys())[0]

    G.add_node(root)

    add_nodes_edges(G, root, data[root])

    pos = hierarchy_pos(G, root)

    plt.figure(figsize=(12,8))

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=4000,
        node_color="lightblue",
        font_size=10,
        font_weight="bold"
    )

    plt.title("Tamil Hierarchical Mind Map")

    folder = "tamil_out"
    os.makedirs(folder, exist_ok=True)

    timestamp = time.strftime("%H%M%S")
    filename = os.path.join(folder, f"mindmap_{timestamp}.png")

    plt.savefig(filename, dpi=300, bbox_inches="tight")

    print("\nMind map saved as:", filename)

    plt.show()
