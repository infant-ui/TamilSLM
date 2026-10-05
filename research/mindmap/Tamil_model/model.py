import pandas as pd
import pickle
import re

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Embedding, GlobalAveragePooling1D, Dense

# Load dataset
data = pd.read_csv("Tamil_model\data.pytamil_dataset.csv")

texts = data["text"].astype(str).tolist()
labels = data["label"].tolist()

# Clean Tamil text
def clean(text):
    text = text.lower()
    text = re.sub(r'[^\u0B80-\u0BFF ]','',text)
    return text

texts = [clean(t) for t in texts]

# Build vocabulary
word_index = {"<UNK>":1}
index = 2

for text in texts:
    for word in text.split():
        if word not in word_index:
            word_index[word] = index
            index += 1

print("Vocabulary size:",len(word_index))

# Encode sentences
def encode(text):
    return [word_index.get(w,1) for w in text.split()]

encoded = [encode(t) for t in texts]

X = pad_sequences(encoded,maxlen=25)

# Encode labels
le = LabelEncoder()
y = le.fit_transform(labels)

# Train/Test split
X_train,X_test,y_train,y_test = train_test_split(
    X,y,test_size=0.2,random_state=42
)

# Model
model = tf.keras.Sequential([
    Embedding(input_dim=len(word_index)+1,output_dim=128),
    GlobalAveragePooling1D(),
    Dense(64,activation='relu'),
    Dense(3,activation='softmax')
])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# Train
model.fit(X_train,y_train,epochs=25,validation_data=(X_test,y_test))

# Save model
model.save("Tamil_model/tamil_mindmap_model.h5")

with open("tamil_vocab.pkl","wb") as f:
    pickle.dump(word_index,f)

with open("tamil_label_encoder.pkl","wb") as f:
    pickle.dump(le,f)

print("Tamil model saved successfully")