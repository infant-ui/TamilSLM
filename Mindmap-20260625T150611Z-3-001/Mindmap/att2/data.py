import pandas as pd
import itertools

process_subjects = [
"water","blood","air","energy","nutrients","rain","electricity",
"heat","gas","data","information","signals"
]

process_verbs = [
"flows","moves","circulates","passes","travels",
"transfers","changes","transforms","evaporates","condenses"
]

process_places = [
"through pipes","through the system","through stages",
"through the atmosphere","through the network","in the cycle"
]

hier_subjects = [
"animals","plants","computers","vehicles","networks",
"organizations","devices","books","languages","foods"
]

hier_words = [
"divided into","classified into","grouped into",
"organized into","arranged into"
]

hier_groups = [
"categories","types","classes","sections","groups"
]

concept_subjects = [
"gravity","temperature","education","exercise",
"technology","pollution","rainfall","light","energy"
]

concept_verbs = [
"influences","affects","changes","controls",
"improves","impacts","modifies"
]

concept_objects = [
"natural systems","human health","environment",
"economic growth","plant growth","weather patterns"
]

data = []

# Process sentences
for s,v,p in itertools.product(process_subjects,process_verbs,process_places):
    sentence = f"{s} {v} {p}"
    data.append([sentence,"process"])

# Hierarchical sentences
for s,w,g in itertools.product(hier_subjects,hier_words,hier_groups):
    sentence = f"{s} are {w} different {g}"
    data.append([sentence,"hierarchical"])

# Concept sentences
for s,v,o in itertools.product(concept_subjects,concept_verbs,concept_objects):
    sentence = f"{s} {v} {o}"
    data.append([sentence,"concept"])

df = pd.DataFrame(data, columns=["text","label"])

df.to_csv("att2/mindmap_dataset_large.csv", index=False)

print("Dataset created:", len(df))