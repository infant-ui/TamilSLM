# Example Questions & Expected Answers
# Based on actual content in your files

Confirmed topics in **Tamil book** (`data/texts/tamil_book_output.txt`):
  ஒளிச்சேர்க்கை | நியூட்டன் விதிகள் | அமிலம்/காரம் | செல் | மரபணு

Confirmed topics in **Web PDFs** (`data/pdfs/add/`):
  speed, motion, distance-time graph, photosynthesis (gecu110), light (gecu111),
  measurement, oscillation, pendulum (web2, gecu108)

Confirmed topics in **English book** (`data/pdfs/english_bookk.pdf`):
  derived quantities, area, volume, density, speed, motion, Newton's laws,
  measurement, acids/bases, cells, photosynthesis

---

## ✅ ENGLISH Questions — Content exists in BOTH English book AND web

### Q1 — What is photosynthesis?
**Book chunk (english_bookk)** should have: chlorophyll, glucose, CO₂, sunlight
**Web chunk (add/gecu110)** should have: leaves, starch, chlorophyll, food factory
**Expected answer:**
Photosynthesis is the process by which green plants make food using sunlight,
water, and carbon dioxide. Chlorophyll in leaves absorbs sunlight. The products
are glucose (stored as starch) and oxygen. It occurs in chloroplasts.

---

### Q2 — What are derived quantities?
**Book chunk (english_bookk p.6)** should have: area, volume, speed, density, m², m³
**Web chunk** — may not find strong match (this is mainly in book)
**Expected answer:**
Derived quantities are physical quantities obtained by combining fundamental
quantities. Examples: Area (length × breadth, m²), Volume (m³), Speed (m/s),
Density (kg/m³). Their units are called derived units.

---

### Q3 — What is speed and how is it calculated?
**Book chunk (english_bookk)** should have: distance/time, m/s, uniform motion
**Web chunk (add/web2, add/gecu108)** should have: distance-time graph, speed calculation
**Expected answer:**
Speed is the distance moved by an object per unit time. It is calculated as
Distance ÷ Time. The SI unit is metres per second (m/s). An object with
higher speed covers more distance in the same time.

---

### Q4 — Explain Newton's first law of motion.
**Book chunk (english_bookk)** should have: inertia, rest, straight line
**Web chunk (add/gecu108 or add/web2)** may have: Newton's laws content
**Expected answer:**
Newton's first law states that an object at rest stays at rest, and an object
in motion continues in a straight line at constant speed, unless acted upon by
an external force. This property is called inertia.

---

### Q5 — What is the difference between acids and bases?
**Book chunk (english_bookk)** should have: H⁺, OH⁻, pH, HCl, NaOH
**Web chunk** — may or may not have chemistry content
**Expected answer:**
Acids release hydrogen ions (H⁺) in water and have a pH below 7.
Bases release hydroxyl ions (OH⁻) and have a pH above 7.
A neutral substance has pH 7. Examples of acids: HCl, H₂SO₄.
Examples of bases: NaOH, KOH.

---

## ✅ TAMIL Questions — Content exists in Tamil book (confirmed)

### Q6 — ஒளிச்சேர்க்கை என்றால் என்ன?
**Tamil chunk** should have: குளோரோஃபில், கார்பன் டையாக்சைடு, குளுக்கோஸ்
**Web chunk (add/gecu110)** may match via cross-lingual embedding
**Expected answer (Tamil):**
ஒளிச்சேர்க்கை என்பது தாவரங்கள் சூரிய ஒளியை உணவாக மாற்றும் செயல்முறையாகும்.
இலைகளில் உள்ள குளோரோஃபில் சூரிய ஒளியை உறிஞ்சி, கார்பன் டையாக்சைடு மற்றும்
நீரை பயன்படுத்தி குளுக்கோஸ் உற்பத்தி செய்கின்றன. ஆக்சிஜன் வெளியிடப்படுகிறது.

---

### Q7 — நியூட்டனின் முதல் இயக்க விதி என்ன?
**Tamil chunk** should have: ஓய்வு நிலை, நேர்கோட்டில், விசை
**Expected answer (Tamil):**
ஒரு பொருள் ஓய்வு நிலையில் இருந்தால் தொடர்ந்து ஓய்வு நிலையிலேயே இருக்கும்.
இயங்கிக்கொண்டிருந்தால் அதே வேகத்தில் நேர்கோட்டில் இயங்கும், வெளியில் இருந்து
விசை செயல்படாத வரை. இது நிலை விதி என்று அழைக்கப்படுகிறது.

---

### Q8 — அமிலங்கள் மற்றும் காரங்கள் என்றால் என்ன?
**Tamil chunk** should have: ஹைட்ரோஜன் அயனிகள், pH அளவு, HCl, NaOH
**Expected answer (Tamil):**
அமிலங்கள் நீரில் கரையும்போது H⁺ அயனிகளை வெளியிடுகின்றன (உ.ம்: HCl, H₂SO₄).
காரங்கள் OH⁻ அயனிகளை வெளியிடுகின்றன (உ.ம்: NaOH). pH 0–6 அமிலத்தன்மை,
7 நடுநிலை, 8–14 காரத்தன்மை.

---

### Q9 — செல் என்றால் என்ன?
**Tamil chunk** should have: உயிரினங்களின் அடிப்படை அலகு, மைட்டோகாண்டிரியா
**Expected answer (Tamil):**
செல் என்பது உயிரினங்களின் அடிப்படை அலகு ஆகும். தாவர செல்கள் மற்றும் விலங்கு
செல்கள் என இரு வகை உண்டு. செல் சுவர், செல் சவ்வு, உட்கரு, மைட்டோகாண்டிரியா
ஆகியவை முக்கிய பாகங்கள்.

---

## Score Guide — Is retrieval working?

| Score range | Meaning |
|---|---|
| ≥ 0.65 | Excellent match — correct content |
| 0.45–0.64 | Good match |
| 0.35–0.44 | Weak but accepted |
| < 0.35 (book) or < 0.38 (web) | Dropped by threshold ✅ |

## ⚠️ If Tamil chunks show garbled text (like `40 17" ட லு "9201-12`)
This is OCR noise from the original PDF that was converted to text.
Fix: Open `data/texts/tamil_book_output.txt`, remove the garbled pages,
keep only clean Tamil text. The sample file in `data/texts/` is already clean.

## ⚠️ If Web shows irrelevant content (plants for motion question)
The web PDF doesn't have that topic. This is correct behaviour — threshold drops it.
Add more PDFs to `data/pdfs/add/` that cover the topic.
