import networkx as nx
import matplotlib.pyplot as plt
import ollama
import os

# -----------------------------
# Extract steps using LLM (Tamil version)
# -----------------------------
def extract_process_steps(text):

    prompt = f"""
கொடுக்கப்பட்டுள்ள பத்தியிலிருந்து முக்கிய செயல்முறை படிகளைப் (process steps) பிரித்தெடுக்கவும்.

விதிகள்:
- ஒவ்வொரு படியும் அதிகபட்சம் 3 வார்த்தைகளாக இருக்க வேண்டும்
- படிகளை மட்டுமே திருப்பி அனுப்ப வேண்டும்
- ஒரு எண் பட்டியலாக (numbered list) திருப்பி அனுப்ப வேண்டும்
- விளக்கங்கள் எதுவும் எழுத வேண்டாம்

உரை:
{text}

எடுத்துக்காட்டு வெளியீடு:
1. ஆவியாதல்
2. சுருங்குதல்
3. மழைப்பொழிவு
4. சேகரிப்பு
"""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )

    steps_text = response["message"]["content"]

    steps = []

    for line in steps_text.split("\n"):

        if "." in line:

            step = line.split(".", 1)[1].strip() # removes numbering

            step = " ".join(step.split()[:3])

            steps.append(step)

    return steps


# -----------------------------
# Main process map generator
# -----------------------------
def generate_process_map(text):

    steps = extract_process_steps(text)

    if len(steps) == 0:
        print("No steps extracted")
        return

    print("\nExtracted Steps:")
    for s in steps:
        print(s)

    G = nx.DiGraph()

    for step in steps:
        G.add_node(step)

    for i in range(len(steps)-1):
        G.add_edge(steps[i], steps[i+1])

    pos = nx.spring_layout(G)

    plt.figure(figsize=(10,6))

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        node_size=4000,
        font_size=11
    )
    folder = "tamil_process"
    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, "tamil_process_map.png")

    plt.savefig(filepath)

    print("Process graph saved to:", filepath)
    plt.title("Tamil Process Mind Map")

    plt.show()
