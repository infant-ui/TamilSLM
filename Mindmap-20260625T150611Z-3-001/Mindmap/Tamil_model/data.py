import pandas as pd
import itertools

# Process sentences
process_subjects = [
"தண்ணீர்","இரத்தம்","காற்று","ஆற்றல்","மின்சாரம்","வெப்பம்"
]

process_verbs = [
"ஓடுகிறது","நகர்கிறது","சுழல்கிறது","பாய்கிறது","செல்கிறது"
]

process_places = [
"குழாய்களில்","அமைப்பில்","சுற்றுச்சூழலில்","வலையமைப்பில்"
]

# Hierarchical sentences
hier_subjects = [
"விலங்குகள்","தாவரங்கள்","கணினிகள்","வாகனங்கள்","மொழிகள்"
]

hier_words = [
"பிரிக்கப்படுகின்றன","வகைப்படுத்தப்படுகின்றன","ஒழுங்குபடுத்தப்படுகின்றன"
]

hier_groups = [
"வகைகளாக","பிரிவுகளாக","குழுக்களாக"
]

# Concept sentences
concept_subjects = [
"ஈர்ப்பு விசை","வெப்பநிலை","கல்வி","உடற்பயிற்சி","தொழில்நுட்பம்"
]

concept_verbs = [
"பாதிக்கிறது","மாற்றுகிறது","கட்டுப்படுத்துகிறது","மேம்படுத்துகிறது"
]

concept_objects = [
"சுற்றுச்சூழல்","மனித ஆரோக்கியம்","தாவர வளர்ச்சி","வானிலை"
]

data = []

# Process
for s,v,p in itertools.product(process_subjects,process_verbs,process_places):
    sentence = f"{s} {v} {p}"
    data.append([sentence,"process"])

# Hierarchical
for s,w,g in itertools.product(hier_subjects,hier_words,hier_groups):
    sentence = f"{s} {w} {g}"
    data.append([sentence,"hierarchical"])

# Concept
for s,v,o in itertools.product(concept_subjects,concept_verbs,concept_objects):
    sentence = f"{s} {v} {o}"
    data.append([sentence,"concept"])

df = pd.DataFrame(data,columns=["text","label"])

df.to_csv("Tamil_model/data.pytamil_dataset.csv",index=False)

print("Tamil dataset created:",len(df))