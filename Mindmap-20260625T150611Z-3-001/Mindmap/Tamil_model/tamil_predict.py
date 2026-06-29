import tensorflow as tf
import pickle
import re
import sys
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Import Tamil generators
# ------------------------------------------------
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tamil_concept import generate_concept_map
from tamil_process import generate_process_map
from tamil_1 import generate_outline, draw_mindmap


# ------------------------------------------------
# Load classifier model
# ------------------------------------------------
model = tf.keras.models.load_model("Tamil_model/tamil_mindmap_model.h5")

with open("tamil_vocab.pkl","rb") as f:
    vocab = pickle.load(f)

with open("tamil_label_encoder.pkl","rb") as f:
    le = pickle.load(f)


# ------------------------------------------------
# Clean Tamil text
# ------------------------------------------------
def clean(text):

    text = text.lower()
    text = re.sub(r'[^\u0B80-\u0BFF ]','',text)

    return text


# ------------------------------------------------
# Encode text
# ------------------------------------------------
def encode(text):

    return [vocab.get(w,1) for w in text.split()]


# ------------------------------------------------
# Predict mindmap type
# ------------------------------------------------
def predict(sentence):

    sentence = clean(sentence)

    seq = encode(sentence)

    padded = pad_sequences([seq],maxlen=25)

    pred = model.predict(padded)

    label = le.inverse_transform([pred.argmax()])[0]

    return label


# ------------------------------------------------
# INPUT TEXT
# ------------------------------------------------
text = """
காற்று அரிப்பு என்பது நிலப்பகுதியில் உள்ள மண் மற்றும் பாறையின் அடுக்குகளை உடைத்து, இறுதியில் அவற்றை படிகமாக்குவதற்கு காரணமாகிறது. காற்று அரிப்பை ஏற்படுத்தக்கூடிய பல முக்கிய காரணங்கள் உள்ளன, அவற்றுள்:

1. வானிலை: காற்று அரிப்புக்கு முக்கிய காரணங்களில் ஒன்று வானிலை. கடுமையான வெப்பநிலை, ஈரப்பதம் மற்றும் காற்று போன்ற காரணிகளால் மண் மற்றும் பாறைகள் மிகவும் அரிப்புக்கு ஆளாகின்றன.

2. புயல்கள் மற்றும் சூறாவளி: காற்றின் வேகம் மற்றும் அரிப்பு அதிகமாக இருக்கும் போது, ​​அலைகள் மற்றும் சூறாவளிகள் போன்ற புயல்கள் மண் மற்றும் பாறைகளின் அடுக்குகளை உடைத்து, இறுதியில் அவற்றை படிகமாக்குகின்றன.

3. நிலச்சரிவுகள்: நிலச்சரிவுகள் மண் மற்றும் பாறை அடுக்குகளை உடைத்து, இறுதியில் அவற்றை படிகமாக்குவதற்கு காரணமாகின்றன.

4. மனித செயல்பாடு: மனித செயல்பாடுகளும் மண் மற்றும் பாறை அடுக்குகளை உடைக்க வழிவகுக்கும்
"""


# ------------------------------------------------
# Run classifier
# ------------------------------------------------
result = predict(text)

print("\nPrediction:", result)


# ------------------------------------------------
# Route to correct generator
# ------------------------------------------------
if result == "concept":

    print("\nRouting to Concept Map Generator...\n")

    generate_concept_map(text)


elif result == "process":

    print("\nRouting to Process Map Generator...\n")

    generate_process_map(text)


elif result == "hierarchical":

    print("\nRouting to Hierarchical Mindmap Generator...\n")

    outline = generate_outline(text)

    draw_mindmap(outline)