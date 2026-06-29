import pandas as pd

data = pd.read_csv("att2/mindmap_dataset_large.csv")

print("Rows:", len(data))
print("Unique sentences:", data["text"].nunique())