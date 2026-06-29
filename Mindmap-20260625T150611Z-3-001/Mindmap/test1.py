import ollama
import json
import networkx as nx
import matplotlib.pyplot as plt


# ---------------------------------------------------
# STEP 1: Generate Hierarchical Structure from LLM
# ---------------------------------------------------
def generate_outline(text):

    prompt = f"""
    Extract a clean hierarchical mind map from the text.

    STRICT RULES:
    - Do NOT repeat topics.
    - Do NOT shorten names.
    - Keep siblings at same level.
    - Do NOT nest unrelated topics.
    - No placeholder words.
    - Output ONLY valid JSON.
    - No explanation text.

    Format:
    {{
      "Main Topic": {{
        "Subtopic": {{
          "Sub-subtopic": {{}}
        }}
      }}
    }}

    Text:
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

    data = json.loads(json_string) #JSON string to dictionary

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

                sub_clean = {   #Remove self-nesting
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

        nextx = xcenter - width / 2 - dx / 2 #calculates where the first child should start

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
# STEP 5: Draw Mind Map
# ---------------------------------------------------
def create_mindmap(data):

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
        font_weight="bold",
        arrows=True
    )

    plt.title("Hierarchical Mind Map")

    filename = "hierarchical_mindmap.png"

    plt.savefig(filename, dpi=300, bbox_inches="tight")

    print("\nMind map saved as:", filename)

    plt.show()


# ---------------------------------------------------
# MAIN FUNCTION FOR CLASSIFIER
# ---------------------------------------------------
def generate_hierarchical_map(text):

    outline = generate_outline(text)

    print("\nGenerated Structure:\n")
    print(json.dumps(outline, indent=2))

    create_mindmap(outline)