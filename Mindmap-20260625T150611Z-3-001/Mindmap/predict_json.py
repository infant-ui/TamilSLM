import os
import sys
import json
import pickle
import re
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import ollama

# Set UTF-8 encoding for stdout/stderr to prevent charmap encoding errors under Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# Low memory/CPU usage limits for TensorFlow
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)

# Helper for stderr logs
def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# ------------------------------------------------
# 1. Classification Setup
# ------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
att2_dir = os.path.join(BASE_DIR, "att2")

log("⏳ Loading Mindmap Classifier Keras model...")
classifier = tf.keras.models.load_model(os.path.join(att2_dir, "mindmap_classifier_model.h5"))

with open(os.path.join(att2_dir, "vocab.pkl"), "rb") as f:
    vocab = pickle.load(f)

with open(os.path.join(att2_dir, "label_encoder.pkl"), "rb") as f:
    le = pickle.load(f)

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z ]', '', text)
    return text

def encode_text(text):
    return [vocab.get(w, 1) for w in text.split()]

def classify_text(text):
    cleaned = clean_text(text)
    seq = encode_text(cleaned)
    padded = pad_sequences([seq], maxlen=25)
    pred = classifier.predict(padded, verbose=0)
    label = le.inverse_transform([pred.argmax()])[0]
    return label

# ------------------------------------------------
# 2. Graph Generator Functions
# ------------------------------------------------
def get_concept_graph(text, language="english"):
    # Prompts for Concept Extraction
    model = "llama3.1" if language == "tamil" else "mistral"
    if language == "tamil":
        prompt = f"""
கீழே உள்ள உரையிலிருந்து கருத்து உறவுகளை (Concept relationships) பிரித்தெடுக்கவும்.

விதிமுறைகள்:
- மூன்று பகுதிகளை மட்டுமே கொண்ட வரிகளை மட்டுமே வெளியிடவும் (Concept1 | Relation | Concept2)
- உன்னுடைய கூடுதல் விளக்கங்களை எழுத வேண்டாம்.

எடுத்துக்காட்டு:
நீர் | ஆவியாகிறது | கடல்
மேகம் | பொழிகிறது | மழை

உரை:
{text}
"""
    else:
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
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    output = response["message"]["content"]
    
    triples = []
    nodes = set()
    edges = []
    
    for line in output.split("\n"):
        line = line.strip()
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) == 3:
                c1, rel, c2 = parts[0], parts[1], parts[2]
                triples.append((c1, rel, c2))
                nodes.add(c1)
                nodes.add(c2)
                edges.append({
                    "id": f"e-{c1}-{c2}",
                    "source": c1,
                    "target": c2,
                    "label": rel
                })
                
    node_list = [{"id": n, "label": n, "type": "concept"} for n in nodes]
    return {"type": "concept", "nodes": node_list, "edges": edges}

def get_process_graph(text, language="english"):
    model = "llama3.1" if language == "tamil" else "mistral"
    if language == "tamil":
        prompt = f"""
கீழே உள்ள உரையிலிருந்து முக்கிய செயல்முறை படிகளை (Process steps) வரிசையாக பிரித்தெடுக்கவும்.

விதிமுறைகள்:
- ஒவ்வொரு படியும் அதிகபட்சம் 3 வார்த்தைகளாக இருக்க வேண்டும்
- வரிசைப்படுத்தப்பட்ட பட்டியலாக மட்டுமே எழுத வேண்டும்
- கூடுதல் விளக்கங்கள் எழுத வேண்டாம்

எடுத்துக்காட்டு வெளியீடு:
1. ஆவியாதல்
2. சுருங்குதல்
3. பொழிதல்
4. சேகரித்தல்

உரை:
{text}
"""
    else:
        prompt = f"""
Extract the main process steps from the paragraph.

Rules:
- Each step must be maximum 3 words
- Return only the steps
- Return as a numbered list
- Do not write explanations

Text:
{text}

Example output:
1. Evaporation
2. Condensation
3. Precipitation
4. Collection
"""

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    steps_text = response["message"]["content"]
    
    steps = []
    for line in steps_text.split("\n"):
        if "." in line:
            step = line.split(".", 1)[1].strip()
            step = " ".join(step.split()[:3])
            if step:
                steps.append(step)
                
    nodes = [{"id": s, "label": s, "type": "process"} for s in steps]
    edges = []
    for i in range(len(steps) - 1):
        edges.append({
            "id": f"e-p-{i}",
            "source": steps[i],
            "target": steps[i+1],
            "label": "next"
        })
    return {"type": "process", "nodes": nodes, "edges": edges}

def get_hierarchical_graph(text, language="english"):
    model = "llama3.1" if language == "tamil" else "mistral"
    if language == "tamil":
        prompt = f"""
உரையிலிருந்து படிநிலை வரைபடத்தை (Hierarchical mind map) பிரித்தெடுக்கவும்.

விதிமுறைகள்:
- சரியான JSON வடிவத்தை மட்டுமே வெளியிடவும்.
- கூடுதல் விளக்கங்கள் எழுத வேண்டாம்.

வடிவம்:
{{
  "முக்கிய தலைப்பு": {{
    "துணை தலைப்பு": {{
      "உள் துணை தலைப்பு": {{}}
    }}
  }}
}}

உரை:
{text}
"""
    else:
        prompt = f"""
Extract a clean hierarchical mind map from the text.

STRICT RULES:
- Output ONLY valid JSON.
- No explanation text.
- Format:
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
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    content = response["message"]["content"]
    
    start = content.find("{")
    end = content.rfind("}") + 1
    if start == -1 or end == -1:
        raise ValueError("Model did not return valid JSON outline.")
        
    json_string = content[start:end]
    data = json.loads(json_string)
    
    nodes = []
    edges = []
    node_set = set()
    
    def traverse(node, parent=None):
        if not node:
            return
        if isinstance(node, dict):
            for key, val in node.items():
                clean_key = key.strip()
                if clean_key not in node_set:
                    node_set.add(clean_key)
                    nodes.append({"id": clean_key, "label": clean_key, "type": "hierarchical"})
                if parent:
                    edges.append({
                        "id": f"e-h-{parent}-{clean_key}",
                        "source": parent,
                        "target": clean_key,
                        "label": "sub"
                    })
                traverse(val, clean_key)
        elif isinstance(node, list):
            for item in node:
                if isinstance(item, str):
                    clean_item = item.strip()
                    if clean_item not in node_set:
                        node_set.add(clean_item)
                        nodes.append({"id": clean_item, "label": clean_item, "type": "hierarchical"})
                    if parent:
                        edges.append({
                            "id": f"e-h-{parent}-{clean_item}",
                            "source": parent,
                            "target": clean_item,
                            "label": "sub"
                        })
                        
    traverse(data)
    return {"type": "hierarchical", "nodes": nodes, "edges": edges}

# ------------------------------------------------
# 3. Main Runner
# ------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        log("Usage: python predict_json.py '<text>' [<language>] [<output_file>]")
        sys.exit(1)
        
    text_content = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "english"
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    log(f"Processing mindmap generation request. Lang: {language}, Output path: {output_file}")
    
    try:
        # Classify the concept/process/hierarchical route
        predicted_class = classify_text(text_content)
        log(f"Classification result: {predicted_class}")
        
        # Extract graph data based on type
        if predicted_class == "concept":
            graph = get_concept_graph(text_content, language)
        elif predicted_class == "process":
            graph = get_process_graph(text_content, language)
        else:  # hierarchical
            graph = get_hierarchical_graph(text_content, language)
            
        graph["predicted_class"] = predicted_class
        graph_json = json.dumps(graph, ensure_ascii=False)
        
        # Save output
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(graph_json)
            log(f"✅ Saved graph json to {output_file}")
        else:
            print(graph_json)
            
    except Exception as e:
        error_info = {"status": "error", "error": str(e)}
        log(f"❌ Error during generation: {str(e)}")
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(error_info))
        else:
            print(json.dumps(error_info))
        sys.exit(1)
