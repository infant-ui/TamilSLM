import tensorflow as tf
import pickle
import re
import sys

from tensorflow.keras.preprocessing.sequence import pad_sequences

# ------------------------------------------------
# Import Concept Generator
# ------------------------------------------------
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test1 import generate_hierarchical_map
from process import generate_process_map
from concept import generate_concept_map


# ------------------------------------------------
# Load trained model
# ------------------------------------------------
model = tf.keras.models.load_model("att2/mindmap_classifier_model.h5")

with open("vocab.pkl", "rb") as f:
    vocab = pickle.load(f)

with open("label_encoder.pkl", "rb") as f:
    le = pickle.load(f)


# ------------------------------------------------
# Text cleaning
# ------------------------------------------------
def clean(text):

    text = text.lower()
    text = re.sub(r'[^a-z ]','',text)

    return text


# ------------------------------------------------
# Encode sentence
# ------------------------------------------------
def encode(text):

    return [vocab.get(w,1) for w in text.split()]


# ------------------------------------------------
# Prediction function
# ------------------------------------------------
def predict(text):

    text = clean(text)

    seq = encode(text)

    seq = pad_sequences([seq], maxlen=25)

    print("Encoded sequence:", seq)

    pred = model.predict(seq)

    label = le.inverse_transform([pred.argmax()])[0]

    return label


# ------------------------------------------------
# Input Text
# ------------------------------------------------
text = """Regular exercise improves cardiovascular health.
Physical activity strengthens muscles and bones.
Exercise also reduces stress and improves mental wellbeing.
A healthy lifestyle depends on consistent physical activity.
"""

# ------------------------------------------------
# Run Prediction
# ------------------------------------------------
result = predict(text)

print("\nPrediction:", result)


# ------------------------------------------------
# Route to Correct Mindmap Generator
# ------------------------------------------------
if result == "concept":

    print("\nRouting to Concept Map Generator...\n")

    generate_concept_map(text)

elif result == "process":

    print("\nRouting to Process Map Generator...\n")

    generate_process_map(text)

elif result == "hierarchical":

    print("\nRouting to Hierarchical Map Generator...\n")
    generate_hierarchical_map(text)