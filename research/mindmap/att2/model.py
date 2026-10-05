import pandas as pd
import re
import pickle

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import precision_score, recall_score, f1_score

import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Embedding, GlobalAveragePooling1D, Dense

# =========================
# 1 Load Dataset
# =========================

data = pd.read_csv("mindmap_dataset_large.csv")

texts = data["text"].astype(str).tolist()
labels = data["label"].tolist()

# =========================
# 2 Text Cleaning
# =========================

def clean(text):
    text = text.lower()
    text = re.sub(r'[^a-z ]', '', text)
    return text

texts = [clean(t) for t in texts]

# =========================
# 3 Build Vocabulary
# =========================

word_index = {"<UNK>": 1}
index = 2

for text in texts:
    for word in text.split():
        if word not in word_index:
            word_index[word] = index
            index += 1

print("Vocabulary size:", len(word_index))

# =========================
# 4 Encode Sentences
# =========================

def encode(text):
    return [word_index.get(w, 1) for w in text.split()]

encoded = [encode(t) for t in texts]

X = pad_sequences(encoded, maxlen=25)

# =========================
# 5 Encode Labels
# =========================

le = LabelEncoder()
y = le.fit_transform(labels)

# =========================
# 6 Train/Test Split
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# 7 Build Model
# =========================

model = tf.keras.Sequential([
    Embedding(input_dim=len(word_index)+1, output_dim=128),
    GlobalAveragePooling1D(),
    Dense(64, activation='relu'),
    Dense(3, activation='softmax')
])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# =========================
# 8 Train Model
# =========================

model.fit(X_train, y_train, epochs=25, validation_data=(X_test, y_test))

# =========================
# 9 Evaluate Model
# =========================

# Predictions
y_pred_probs = model.predict(X_test)
y_pred = y_pred_probs.argmax(axis=1)

# Loss & Accuracy
loss, accuracy = model.evaluate(X_test, y_test)

# Other metrics
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

# =========================
# 10 Print Metrics
# =========================

print("\n=== Model Evaluation Metrics ===")
print(f"Loss        : {loss:.3f}")
print(f"Accuracy    : {accuracy:.4f}")
print(f"Precision   : {precision:.3f}")
print(f"Recall      : {recall:.4f}")
print(f"F1 Score    : {f1:.3f}")

# =========================
# 11 Save Everything
# =========================

model.save("att2/mindmap_classifier_model.h5")

with open("vocab.pkl", "wb") as f:
    pickle.dump(word_index, f)

with open("label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)

# Save metrics separately
metrics = {
    "Loss": loss,
    "Accuracy": accuracy,
    "Precision": precision,
    "Recall": recall,
    "F1 Score": f1
}

with open("metrics.pkl", "wb") as f:
    pickle.dump(metrics, f)

print("\nModel and all files saved successfully")