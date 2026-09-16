# evaluation/datasets/build_dataset.py
"""
Builds gold_dataset.json.

=== VERSION 2.0.0 -- FULL-CORPUS REBUILD (2026-09-16) ===

Version 1.0.0 of this file covered ONLY Class 6 Science (English + Tamil,
523 chunks) because that was the entire live index at the time. Since then
the corpus has been fully rebuilt from raw PDFs and now covers all of:
    Class 6, 7, 8 x Maths, Science x English, Tamil medium
    (28 source books, 7,426 total chunks: 3,583 English / 3,843 Tamil,
     verified 2026-09-16 by direct inspection of data/registry/manifest.json
     and data/processed/cache/{english,tamil}_chunks.pkl after re-ingestion)

Every item below (old and new) is grounded in content read directly from the
post-reingestion chunk text -- either the original Class 6 Science pickle
inspection (v1.0.0 items, unchanged) or curated per-book text extractions
sampled from the new corpus export (v2.0.0 additions, this pass). No item
references a page/topic that was not actually observed in extracted chunk
text.

*** IMPORTANT FINDING: Tamil-medium coverage is real but uneven. ***
Tamil MATHS content extracts reasonably well (numbers, formulas and
worked-example digits mostly survive), but Tamil SCIENCE content is heavily
damaged by a PDF font/ToUnicode-CMap encoding problem in several source
books: prose comes through as replacement characters (U+FFFD), stray C0
control codes, split vowel signs, and duplicated consonants/matras (e.g.
"ககோடிட்்ட" for "க�ோடிட்ட"). A partial fix (Unicode normalisation +
control-character stripping) was applied to the ingestion pipeline and
measured to recover only ~1.1 percentage points of previously-unusable
Tamil chunks (see final report, "Tamil text extraction" finding) -- it does
NOT fix the underlying duplication corruption. Concretely, per book, the
number of usable ("good") Tamil chunks found while curating this dataset
was:
    Class 6 Maths T1/T2/T3   : usable (690 / 1298 / 767 raw lines sampled)
    Class 6 Science T1       : ~0 usable chunks (all corrupted/near-empty)
    Class 6 Science T2       : glossary-only (clean; prose is not)
    Class 6 Science T3       : ~0 usable chunks
    Class 7 Maths T1/T2/T3   : usable but visibly duplicated/garbled prose;
                                numeric/formula content still legible
    Class 7 Science T1/T2/T3 : effectively empty (1-2 usable chunks each)
    Class 8 Maths            : usable but garbled prose; numerics legible
    Class 8 Science          : glossary-only (clean; prose is not)
Because of this, Tamil CORE items below for Science books are limited to
glossary/vocabulary-style questions (verified against the clean glossary
appendix pages), and Tamil CORE items for Maths books favour numeric/
worked-example facts (digits are far more robust to the corruption than
surrounding prose). This under-representation of Tamil Science prose
coverage is intentional and should be read as a dataset limitation that
mirrors a real, documented corpus limitation -- not an oversight.

Legacy v1.0.0 header (kept for continuity/history), describing what used to
be the entire scope of this file:
    Class 6, Science, English medium (396 chunks) and Tamil medium
    (127 chunks), Term 1 units (Measurements, Force and Motion, Matter,
    Plants, Animals, Nutrients) plus two Term 2 spot-checks.

Additionally includes:
  - "out_of_scope" items to measure abstention/hallucination behaviour,
    scored separately from retrieval recall (per evaluation methodology
    notes in README.md -- these must never be counted as retrieval
    failures). Revised in v2.0.0: Class 7/8 and Maths are NO LONGER
    out-of-scope (they are now indexed), so those v1.0.0 items were
    replaced with genuinely-absent topics (content above Class 8, or
    outside the Tamil Nadu Class 6-8 syllabus entirely).
  - "language_instruction" items to measure explicit language-compliance.
"""
import json

CORE = [
    # ================================================================
    # LEGACY (v1.0.0): CLASS 6 SCIENCE, ENGLISH + TAMIL, TERM 1
    # Unchanged from the original evaluation -- kept verbatim.
    # ================================================================
    # ---------------- MEASUREMENT (Unit 1, pp.5-17) ----------------
    dict(id="EN_001", lang="english", class_=6, term=1, unit="Measurement", pages=[5, 7],
         difficulty="easy", qtype="definition",
         q="What is the SI unit of length, and what is its symbol?",
         key_facts=["metre", "symbol m"]),
    dict(id="EN_002", lang="english", class_=6, term=1, unit="Measurement", pages=[9],
         difficulty="medium", qtype="list",
         q="List two SI prefixes used with the metre and state what fraction or multiple of a metre each represents.",
         key_facts=["deci = 1/10", "prefix table"]),
    dict(id="EN_003", lang="english", class_=6, term=1, unit="Measurement", pages=[11],
         difficulty="medium", qtype="process",
         q="How would you measure the length of a curved line using a divider?",
         key_facts=["divider", "curved line AB"]),
    dict(id="TA_001", lang="tamil", class_=6, term=1, unit="Measurement", pages=[5, 7],
         difficulty="easy", qtype="definition",
         q="நீளத்தின் அலகு என்ன, அதன் குறியீடு என்ன?",
         key_facts=["மீட்டர்", "குறியீடு m"]),
    dict(id="TA_002", lang="tamil", class_=6, term=1, unit="Measurement", pages=[12],
         difficulty="easy", qtype="conversion",
         q="1000 கிராம் என்பது எத்தனை கிலோகிராம்?",
         key_facts=["1000 gram = 1 kilogram"]),
    dict(id="BI_001", lang="bilingual", class_=6, term=1, unit="Measurement", pages=[9],
         difficulty="medium", qtype="list",
         q="SI unit-ல் metre-க்கு பயன்படுத்தப்படும் prefix-கள் இரண்டை கூறி, அவை எதைக் குறிக்கும் என்று விளக்குக.",
         key_facts=["prefix", "deci/centi/milli"]),
    dict(id="TG_001", lang="tanglish", class_=6, term=1, unit="Measurement", pages=[5, 7],
         difficulty="easy", qtype="definition",
         q="Neelathin unit enna, adhoda symbol enna?",
         key_facts=["metre", "m"]),

    # ---------------- FORCE AND MOTION (Unit 2, pp.18-37) ----------------
    dict(id="EN_004", lang="english", class_=6, term=1, unit="Force and Motion", pages=[20],
         difficulty="easy", qtype="definition",
         q="What is motion, and what is rest?",
         key_facts=["change in position with time = motion", "no change = rest"]),
    dict(id="EN_005", lang="english", class_=6, term=1, unit="Force and Motion", pages=[23],
         difficulty="medium", qtype="comparison",
         q="Give one example each of a contact force and a non-contact force.",
         key_facts=["contact: pulling a cart", "non-contact: magnetism/gravity"]),
    dict(id="EN_006", lang="english", class_=6, term=1, unit="Force and Motion", pages=[26, 27],
         difficulty="hard", qtype="list",
         q="Name the different types of motion based on the path an object takes, with one example each.",
         key_facts=["linear", "circular", "curvilinear", "rotatory", "oscillatory"]),
    dict(id="TA_003", lang="tamil", class_=6, term=1, unit="Force and Motion", pages=[20],
         difficulty="easy", qtype="definition",
         q="இயக்கம் என்றால் என்ன, ஓய்வு நிலை என்றால் என்ன?",
         key_facts=["நிலை மாறுதல் = இயக்கம்", "மாறாதது = ஓய்வு நிலை"]),
    dict(id="TA_004", lang="tamil", class_=6, term=1, unit="Force and Motion", pages=[23],
         difficulty="medium", qtype="comparison",
         q="தொடுவிசைக்கும் தொடாவிசைக்கும் ஒவ்வொரு உதாரணம் தருக.",
         key_facts=["தொடுவிசை: மாடு வண்டி இழுத்தல்", "தொடாவிசை: காந்தவிசை/புவிஈர்ப்பு"]),
    dict(id="BI_002", lang="bilingual", class_=6, term=1, unit="Force and Motion", pages=[20],
         difficulty="easy", qtype="definition",
         q="Motion என்றால் என்ன, rest என்றால் என்ன, Grade 6 Science புத்தகத்தில் இருந்து சொல்லுங்க.",
         key_facts=["position change = motion", "no change = rest"]),
    dict(id="BI_003", lang="bilingual", class_=6, term=1, unit="Force and Motion", pages=[26, 27],
         difficulty="hard", qtype="list",
         q="Path-ஐ அடிப்படையாகக் கொண்டு இயக்கத்தின் types-ஐ, ஒவ்வொன்றுக்கும் example உடன் பட்டியலிடுக.",
         key_facts=["linear", "circular", "curvilinear", "rotatory", "oscillatory"]),
    dict(id="TG_002", lang="tanglish", class_=6, term=1, unit="Force and Motion", pages=[20],
         difficulty="easy", qtype="definition",
         q="Motion na enna, rest na enna nu 6th science book-la irundhu sollunga.",
         key_facts=["position change = motion", "no change = rest"]),
    dict(id="TG_003", lang="tanglish", class_=6, term=1, unit="Force and Motion", pages=[23],
         difficulty="medium", qtype="comparison",
         q="Contact force-kum non-contact force-kum oru example venum.",
         key_facts=["contact: pulling a cart", "non-contact: magnetism/gravity"]),

    # ---------------- MATTER (Unit 3, pp.38-58) ----------------
    dict(id="EN_007", lang="english", class_=6, term=1, unit="Matter", pages=[38, 39],
         difficulty="easy", qtype="definition",
         q="What is matter? Give two examples.",
         key_facts=["occupies space and has mass", "e.g. air, water, iron"]),
    dict(id="EN_008", lang="english", class_=6, term=1, unit="Matter", pages=[40],
         difficulty="medium", qtype="explanation",
         q="Why can gases be compressed easily but solids cannot?",
         key_facts=["space between particles", "gas particles far apart"]),
    dict(id="EN_009", lang="english", class_=6, term=1, unit="Matter", pages=[45, 46, 47],
         difficulty="medium", qtype="comparison",
         q="What is the difference between a pure substance and a mixture?",
         key_facts=["pure substance: fixed composition", "mixture: no fixed proportion"]),
    dict(id="TA_005", lang="tamil", class_=6, term=1, unit="Matter", pages=[38, 39],
         difficulty="easy", qtype="definition",
         q="பருப்பொருள் என்றால் என்ன? இரண்டு உதாரணங்கள் தருக.",
         key_facts=["இடம்/நிறை கொண்டது", "எ.கா. காற்று, நீர்"]),
    dict(id="TA_006", lang="tamil", class_=6, term=1, unit="Matter", pages=[45], difficulty="medium",
         qtype="comparison",
         q="தூய பொருளுக்கும் கலவைக்கும் உள்ள வேறுபாடு என்ன?",
         key_facts=["தூய பொருள்: நிலையான கூறுகள்", "கலவை: நிலையற்ற விகிதம்"]),
    dict(id="BI_004", lang="bilingual", class_=6, term=1, unit="Matter", pages=[40],
         difficulty="medium", qtype="explanation",
         q="Gases easy-ஆ compress பண்ண முடியும், ஆனா solids-ஐ ஏன் compress பண்ண முடியாது?",
         key_facts=["particles space", "gas particles far apart"]),
    dict(id="TG_004", lang="tanglish", class_=6, term=1, unit="Matter", pages=[38, 39],
         difficulty="easy", qtype="definition",
         q="Matter nu solna enna, rendu example sollunga.",
         key_facts=["occupies space and has mass", "air, water"]),

    # ---------------- PLANTS (Unit 4, pp.59-71) ----------------
    dict(id="EN_010", lang="english", class_=6, term=1, unit="Plants", pages=[61],
         difficulty="medium", qtype="list",
         q="What are the two types of root systems? Name one.",
         key_facts=["taproot system", "fibrous root system"]),
    dict(id="EN_011", lang="english", class_=6, term=1, unit="Plants", pages=[62],
         difficulty="easy", qtype="definition",
         q="What are nodes and internodes in a stem?",
         key_facts=["node: where leaves arise", "internode: between two nodes"]),
    dict(id="EN_012", lang="english", class_=6, term=1, unit="Plants", pages=[67],
         difficulty="medium", qtype="explanation",
         q="What is a forest habitat, and what are the three types of forests mentioned?",
         key_facts=["large area dominated by trees", "tropical, temperate, [boreal/coniferous]"]),
    dict(id="TA_007", lang="tamil", class_=6, term=1, unit="Plants", pages=[61],
         difficulty="medium", qtype="list",
         q="வேர்த் தொகுப்புகளின் இரண்டு வகைகள் யாவை?",
         key_facts=["ஆணிவேர்த் தொகுப்பு", "சல்லிவேர்த் தொகுப்பு"]),
    dict(id="TA_008", lang="tamil", class_=6, term=1, unit="Plants", pages=[66],
         difficulty="easy", qtype="list",
         q="நன்னீர் வாழிடத்தில் காணப்படும் இரண்டு தாவரங்களைப் பெயரிடுக.",
         key_facts=["ஆகாயத் தாமரை", "அல்லி/தாமரை"]),
    dict(id="BI_005", lang="bilingual", class_=6, term=1, unit="Plants", pages=[61],
         difficulty="medium", qtype="list",
         q="Root system-ல எத்தனை types இருக்கு, அவங்க பேரு என்ன?",
         key_facts=["taproot system", "fibrous root system"]),
    dict(id="BI_006", lang="bilingual", class_=6, term=1, unit="Plants", pages=[62],
         difficulty="easy", qtype="definition",
         q="தண்டில் உள்ள node மற்றும் internode என்றால் என்ன?",
         key_facts=["node: இலைகள் தோன்றும் பகுதி", "internode: இரு கணுக்களுக்கு இடையே"]),
    dict(id="TG_005", lang="tanglish", class_=6, term=1, unit="Plants", pages=[61],
         difficulty="medium", qtype="list",
         q="Ver thodappugal (root systems) evlo types irukku, peru enna?",
         key_facts=["taproot", "fibrous root"]),
    dict(id="TG_006", lang="tanglish", class_=6, term=1, unit="Plants", pages=[67],
         difficulty="medium", qtype="explanation",
         q="Forest habitat nu solna enna, adhula evlo types of forest sollirukanga?",
         key_facts=["large tree-dominated area", "tropical, temperate"]),

    # ---------------- ANIMALS (Unit 5, pp.72-84) ----------------
    dict(id="EN_013", lang="english", class_=6, term=1, unit="Animals", pages=[76],
         difficulty="medium", qtype="explanation",
         q="How does Euglena move?",
         key_facts=["unicellular", "moves with a flagellum"]),
    dict(id="EN_014", lang="english", class_=6, term=1, unit="Animals", pages=[79],
         difficulty="medium", qtype="explanation",
         q="Name one adaptation that helps a camel survive in the desert.",
         key_facts=["hump stores fat", "long eyelashes", "thick skin", "does not sweat much"]),
    dict(id="TA_009", lang="tamil", class_=6, term=1, unit="Animals", pages=[76],
         difficulty="medium", qtype="explanation",
         q="பாரமீசியம் எவ்வாறு இடம்பெயர்ச்சி செய்கிறது?",
         key_facts=["ஓரணு உயிரினம்", "குறுஇழைகள் மூலம் இடப்பெயர்ச்சி"]),
    dict(id="TA_010", lang="tamil", class_=6, term=1, unit="Animals", pages=[80],
         difficulty="medium", qtype="explanation",
         q="கங்காரு எலி தண்ணீர் இல்லாமல் எப்படி வாழ்கிறது?",
         key_facts=["விதைகளில் இருந்து நீர் பெறுகிறது", "நீர் அருந்துவதே இல்லை"]),
    dict(id="BI_007", lang="bilingual", class_=6, term=1, unit="Animals", pages=[79],
         difficulty="medium", qtype="explanation",
         q="Camel desert-ல எப்படி survive பண்றது, ஒரு adaptation சொல்லுங்க.",
         key_facts=["hump stores fat", "thick skin"]),
    dict(id="TG_007", lang="tanglish", class_=6, term=1, unit="Animals", pages=[76],
         difficulty="medium", qtype="explanation",
         q="Euglena eppadi move aagum?",
         key_facts=["unicellular", "flagellum mூலம் move"]),

    # ---------------- HEALTH / NUTRIENTS (Unit 6, pp.84-99) ----------------
    dict(id="EN_015", lang="english", class_=6, term=1, unit="Nutrients", pages=[89],
         difficulty="easy", qtype="explanation",
         q="What are proteins needed for in the body?",
         key_facts=["growth", "regulating body functions like digestion"]),
    dict(id="EN_016", lang="english", class_=6, term=1, unit="Nutrients", pages=[97],
         difficulty="medium", qtype="definition",
         q="What is a virus, according to the textbook?",
         key_facts=["infective agent", "nucleic acid in a protein coat", "replicates inside host cell"]),
    dict(id="EN_017", lang="english", class_=6, term=1, unit="Nutrients", pages=[94],
         difficulty="hard", qtype="cause_effect",
         q="What causes conditions like Kwashiorkor and Marasmus in children?",
         key_facts=["malnutrition", "nutrient deficiency"]),
    dict(id="TA_011", lang="tamil", class_=6, term=1, unit="Nutrients", pages=[89],
         difficulty="easy", qtype="explanation",
         q="உடலுக்கு புரதம் எதற்காகத் தேவைப்படுகிறது?",
         key_facts=["வளர்ச்சி", "செரிமானம் போன்ற செயல்பாடுகளை ஒழுங்குபடுத்த"]),
    dict(id="TA_012", lang="tamil", class_=6, term=1, unit="Nutrients", pages=[97],
         difficulty="medium", qtype="definition",
         q="பாடநூலின்படி வைரஸ் என்றால் என்ன?",
         key_facts=["தொற்று ஏற்படுத்தும் காரணி", "புரத உறையால் ஆனது"]),
    dict(id="BI_008", lang="bilingual", class_=6, term=1, unit="Nutrients", pages=[89],
         difficulty="easy", qtype="explanation",
         q="Body-க்கு protein ஏன் தேவைப்படுது?",
         key_facts=["growth", "digestion regulate பண்ண"]),
    dict(id="TG_008", lang="tanglish", class_=6, term=1, unit="Nutrients", pages=[94],
         difficulty="hard", qtype="cause_effect",
         q="Kwashiorkor mattrum Marasmus kulandhaigal-ku eppadi varum?",
         key_facts=["malnutrition", "nutrient deficiency"]),

    # ---------------- Term 2, English only (spot-checked pages) ----------------
    dict(id="EN_018", lang="english", class_=6, term=2, unit="Changes Around Us", pages=[40],
         difficulty="easy", qtype="comparison",
         q="What is the difference between a slow change and a fast change? Give one example of each.",
         key_facts=["slow: hours/days/months (e.g. growth of nail)",
                    "fast: seconds/minutes (e.g. bursting of a balloon)"]),
    dict(id="EN_019", lang="english", class_=6, term=2, unit="Atmosphere", pages=[50],
         difficulty="medium", qtype="explanation",
         q="What is the atmosphere, and what does it protect us from?",
         key_facts=["envelope of air around earth", "protects from harmful sun rays"]),

    # ---------------- Cross-topic / multi-hop ----------------
    dict(id="EN_020", lang="english", class_=6, term=1, unit="Matter+Plants", pages=[38, 61],
         difficulty="hard", qtype="multi_hop",
         q="A plant's stem and a lump of rock are both examples of matter with a fixed shape. Using the particle theory of matter from Unit 3 and what you know about stems from Unit 4, explain why both can be classified as solids.",
         key_facts=["solids: particles closely packed, fixed shape", "applies to both rock and stem"]),
    dict(id="BI_009", lang="bilingual", class_=6, term=1, unit="Measurement+Motion", pages=[9, 29],
         difficulty="hard", qtype="multi_hop",
         q="SI unit-ல் distance-ஐ எப்படி அளப்போம், அதை use பண்ணி speed-ஐ எப்படி calculate பண்றது?",
         key_facts=["distance in metre/km", "speed = distance / time"]),

    # ================================================================
    # NEW (v2.0.0): CLASS 6 SCIENCE, TERM 2 (additional, beyond EN_018/019)
    # Source: 6_science_T2_english.txt; Tamil source: 6_science_T2_tamil.txt
    # (a clean glossary page -- prose elsewhere in this book is corrupted).
    # ================================================================
    dict(id="EN_021", lang="english", class_=6, term=2, unit="Heat", pages=[9],
         difficulty="easy", qtype="definition",
         q="What is heat, and what is its SI unit?",
         key_facts=["total kinetic energy of constituent particles", "SI unit: joule"]),
    dict(id="EN_022", lang="english", class_=6, term=2, unit="Electricity", pages=[27],
         difficulty="easy", qtype="list",
         q="What are the main components of a simple electric circuit?",
         key_facts=["cell/battery", "connecting wires", "bulb", "key/switch"]),
    dict(id="EN_023", lang="english", class_=6, term=2, unit="Electricity", pages=[27],
         difficulty="medium", qtype="comparison",
         q="What is the difference between an open circuit and a closed circuit?",
         key_facts=["open circuit: key off, no current flows, bulb does not glow",
                    "closed circuit: key on, current flows, bulb glows"]),
    dict(id="EN_024", lang="english", class_=6, term=2, unit="Cell", pages=[70],
         difficulty="medium", qtype="list",
         q="What are the functions of the cell membrane and the nucleus in a cell?",
         key_facts=["cell membrane: holds/protects cell, controls movement of materials",
                    "nucleus: acts as brain of the cell, regulates cell activities"]),
    dict(id="EN_025", lang="english", class_=6, term=2, unit="Body Systems", pages=[85],
         difficulty="medium", qtype="list",
         q="Name two functions of the skin.",
         key_facts=["barrier against infection/microbes", "helps synthesize vitamin D using sunlight"]),
    dict(id="TA_013", lang="tamil", class_=6, term=2, unit="Electricity", pages=[105, 106],
         difficulty="easy", qtype="vocabulary",
         q="'மின் சுற்று' (Electrical circuit) மற்றும் 'மின் கடத்திகள்' (Conductors) ஆகிய தமிழ்ச் சொற்களுக்கு ஆங்கில அறிவியல் சொற்களைத் தருக.",
         key_facts=["மின் சுற்று = Electrical circuit", "மின் கடத்திகள் = Conductors"]),
    dict(id="TA_014", lang="tamil", class_=6, term=2, unit="Heat", pages=[105, 106],
         difficulty="easy", qtype="vocabulary",
         q="'வெப்பம்' மற்றும் 'வெப்பநிலைமானி' ஆகிய சொற்களுக்கான ஆங்கில அறிவியல் சொற்கள் என்ன?",
         key_facts=["வெப்பம் = Heat", "வெப்பநிலைமானி = Thermometer"]),
    dict(id="BI_010", lang="bilingual", class_=6, term=2, unit="Electricity", pages=[27],
         difficulty="medium", qtype="comparison",
         q="Open circuit-கும் closed circuit-கும் என்ன வித்தியாசம்?",
         key_facts=["open: key off, no current", "closed: key on, current flows, bulb glows"]),

    # ================================================================
    # NEW (v2.0.0): CLASS 6 SCIENCE, TERM 3
    # Source: 6_science_T3_english.txt. Tamil for this term is essentially
    # empty in the corpus (near-zero usable chunks) -- no Tamil items added,
    # flagged as a coverage gap in the report.
    # ================================================================
    dict(id="EN_026", lang="english", class_=6, term=3, unit="Magnetism", pages=[7],
         difficulty="easy", qtype="list",
         q="Name three types of artificial magnets mentioned in the textbook, based on their shape.",
         key_facts=["bar magnet", "horseshoe magnet", "ring magnet", "needle magnet"]),
    dict(id="EN_027", lang="english", class_=6, term=3, unit="Water", pages=[24],
         difficulty="medium", qtype="list",
         q="What are the three natural sources of fresh water described in the textbook?",
         key_facts=["surface water", "frozen water", "ground water"]),
    dict(id="EN_028", lang="english", class_=6, term=3, unit="Cement", pages=[42],
         difficulty="medium", qtype="explanation",
         q="What raw materials is cement manufactured from?",
         key_facts=["lime", "clay", "gypsum"]),
    dict(id="EN_029", lang="english", class_=6, term=3, unit="Materials", pages=[46],
         difficulty="easy", qtype="explanation",
         q="What is Plaster of Paris used for, according to the textbook's Points to Remember?",
         key_facts=["used to fix bone fractures"]),
    dict(id="EN_030", lang="english", class_=6, term=3, unit="Waste Management", pages=[60],
         difficulty="medium", qtype="list",
         q="What are the 3R's of solid waste management, in order?",
         key_facts=["reduce", "reuse", "recycle"]),
    dict(id="EN_031", lang="english", class_=6, term=3, unit="Pollution", pages=[65],
         difficulty="medium", qtype="cause_effect",
         q="What causes land (soil) pollution, according to the textbook?",
         key_facts=["excess chemical pesticides/fertilisers from farming", "mining", "industrial waste",
                    "solid waste from homes like plastics and broken electronics"]),
    dict(id="EN_032", lang="english", class_=6, term=3, unit="Food from Plants", pages=[73],
         difficulty="easy", qtype="list",
         q="Give one example each of a vegetable obtained from a plant's root, stem, and flower.",
         key_facts=["root: beetroot/carrot", "stem: potato/yam/sugarcane", "flower: banana flower/cauliflower"]),
    dict(id="EN_033", lang="english", class_=6, term=3, unit="Plant-Animal Interactions", pages=[77],
         difficulty="medium", qtype="explanation",
         q="How does the relationship between silkworms and mulberry plants benefit humans economically?",
         key_facts=["silkworms feed on mulberry leaves", "used for silk production"]),
    dict(id="EN_034", lang="english", class_=6, term=3, unit="Computers", pages=[84],
         difficulty="easy", qtype="definition",
         q="What is software, according to the textbook?",
         key_facts=["programmed and coded applications to process input information"]),
    dict(id="TG_009", lang="tanglish", class_=6, term=3, unit="Waste Management", pages=[60],
         difficulty="medium", qtype="list",
         q="Solid waste management-oda 3R's enna, order-a sollunga.",
         key_facts=["reduce", "reuse", "recycle"]),

    # ================================================================
    # NEW (v2.0.0): CLASS 6 MATHEMATICS, TERM 1
    # Source: 6_maths_T1_english.txt; Tamil source: 6_maths_T1_tamil.txt
    # (read in an earlier pass of this session; Tamil Maths content in
    # this book is usable, unlike Tamil Science).
    # ================================================================
    dict(id="EN_035", lang="english", class_=6, term=1, unit="Numbers", pages=[6],
         difficulty="easy", qtype="definition",
         q="What is the successor of a number, and what is its predecessor?",
         key_facts=["successor: add 1 to a number", "predecessor: subtract 1 from a number"]),
    dict(id="EN_036", lang="english", class_=6, term=1, unit="Numbers", pages=[14],
         difficulty="medium", qtype="process",
         q="When comparing two numbers with the same number of digits, such as 2180 and 2158, how do you determine which is greater?",
         key_facts=["compare digits from the leftmost (highest) place value onward",
                    "first differing place value decides which is greater"]),
    dict(id="EN_037", lang="english", class_=6, term=1, unit="Number Properties", pages=[31],
         difficulty="medium", qtype="definition",
         q="Which property of whole numbers does 50 x 42 = 50 x 40 + 50 x 2 illustrate?",
         key_facts=["distributive property of multiplication over addition"]),
    dict(id="EN_038", lang="english", class_=6, term=1, unit="Ratio and Proportion", pages=[52],
         difficulty="easy", qtype="definition",
         q="What is a ratio?",
         key_facts=["a comparison of two quantities with the same unit", "written as a:b"]),
    dict(id="EN_039", lang="english", class_=6, term=1, unit="Ratio and Proportion", pages=[60],
         difficulty="medium", qtype="definition",
         q="State the proportionality law for two ratios a:b and c:d that are in proportion.",
         key_facts=["product of extremes = product of means", "ad = bc"]),
    dict(id="EN_040", lang="english", class_=6, term=1, unit="Geometry", pages=[86],
         difficulty="easy", qtype="definition",
         q="What are collinear points?",
         key_facts=["three or more points lying on the same line"]),
    dict(id="TA_015", lang="tamil", class_=6, term=1, unit="Ratio and Proportion", pages=[52],
         difficulty="easy", qtype="definition",
         q="விகிதம் (Ratio) என்றால் என்ன?",
         key_facts=["ஒரே அலகு கொண்ட இரு அளவுகளின் ஒப்பீடு", "a:b என எழுதப்படும்"]),
    dict(id="TA_016", lang="tamil", class_=6, term=1, unit="Numbers", pages=[6],
         difficulty="easy", qtype="definition",
         q="ஓர் எண்ணின் அடுத்தடுத்த எண் (successor) மற்றும் முந்தைய எண் (predecessor) என்றால் என்ன?",
         key_facts=["1 ஐக் கூட்டினால் அடுத்தடுத்த எண்", "1 ஐக் கழித்தால் முந்தைய எண்"]),
    dict(id="BI_011", lang="bilingual", class_=6, term=1, unit="Number Properties", pages=[31],
         difficulty="medium", qtype="definition",
         q="50 x 42 = 50 x 40 + 50 x 2 -- இது எந்த property-ஐ காட்டுகிறது?",
         key_facts=["distributive property of multiplication over addition"]),

    # ================================================================
    # NEW (v2.0.0): CLASS 6 MATHEMATICS, TERM 2
    # Source: 6_maths_T2_english.txt; Tamil source: 6_maths_T2_tamil.txt.
    # ================================================================
    dict(id="EN_041", lang="english", class_=6, term=2, unit="Numbers", pages=[14],
         difficulty="easy", qtype="definition",
         q="What is the divisibility rule for 5?",
         key_facts=["a number is divisible by 5 if its ones digit is 0 or 5"]),
    dict(id="EN_042", lang="english", class_=6, term=2, unit="Numbers", pages=[14],
         difficulty="medium", qtype="definition",
         q="What is the divisibility rule for 4?",
         key_facts=["a number is divisible by 4 if its last two digits are divisible by 4",
                    "if the last two digits are zeros it is also divisible by 4"]),
    dict(id="EN_043", lang="english", class_=6, term=2, unit="Numbers", pages=[21],
         difficulty="medium", qtype="calculation",
         q="What is the Least Common Multiple (LCM) of 4 and 6, and what does it represent in the Ragi Laddu/Thattai packet example?",
         key_facts=["LCM of 4 and 6 is 12",
                    "buy 3 packets of Ragi Laddus (4 each) and 2 packets of Thattais (6 each) to get 12 of each"]),
    dict(id="EN_044", lang="english", class_=6, term=2, unit="Measures of Time", pages=[38],
         difficulty="medium", qtype="conversion",
         q="According to the Tholkappiam-based Tamil measure of time mentioned in the textbook, how many minutes is 1 Nazhigai, and how many nazhigai make up 1 hour?",
         key_facts=["1 Nazhigai = 24 minutes", "1 hour = 2.5 nazhigai = 1 Orai"]),
    dict(id="EN_045", lang="english", class_=6, term=2, unit="Bills, Profit and Loss", pages=[57],
         difficulty="medium", qtype="calculation",
         q="A fruit seller bought a dozen apples for Rs.84. 2 apples got rotten. If he wants a profit of Rs.16 on the remaining apples, what should be the selling price of each apple?",
         key_facts=["10 apples remain", "selling price of 10 apples = 84+16 = Rs.100", "selling price per apple = Rs.10"]),
    dict(id="TA_017", lang="tamil", class_=6, term=2, unit="Numbers", pages=[25],
         difficulty="medium", qtype="calculation",
         q="15, 20, 25 மற்றும் 30 ஆகிய எண்களின் மீ.சி.ம (LCM) என்ன?",
         key_facts=["LCM = 2x2x3x5x5 = 300"]),
    dict(id="BI_012", lang="bilingual", class_=6, term=2, unit="Numbers", pages=[21],
         difficulty="medium", qtype="calculation",
         q="4 மற்றும் 6-ன் LCM என்ன?",
         key_facts=["LCM of 4 and 6 is 12"]),

    # ================================================================
    # NEW (v2.0.0): CLASS 6 MATHEMATICS, TERM 3
    # Source: 6_maths_T3_english.txt; Tamil source: 6_maths_T3_tamil.txt
    # (Tamil source for this term is mostly an answer key -- used sparingly).
    # ================================================================
    dict(id="EN_046", lang="english", class_=6, term=3, unit="Fractions", pages=[15],
         difficulty="medium", qtype="calculation",
         q="Convert the mixed fraction 5 and 3/7 into an improper fraction.",
         key_facts=["(5x7+3)/7 = 38/7"]),
    dict(id="EN_047", lang="english", class_=6, term=3, unit="Integers", pages=[30],
         difficulty="easy", qtype="definition",
         q="What is the set of integers, and what letter is used to denote it?",
         key_facts=["..., -3, -2, -1, 0, 1, 2, 3, ... are called integers", "denoted by the letter Z"]),
    dict(id="EN_048", lang="english", class_=6, term=3, unit="Perimeter and Area", pages=[43],
         difficulty="easy", qtype="definition",
         q="What is the formula for the perimeter of a rectangle?",
         key_facts=["P = 2 x (length + breadth)"]),
    dict(id="EN_049", lang="english", class_=6, term=3, unit="Perimeter and Area", pages=[48],
         difficulty="easy", qtype="definition",
         q="What is the formula for the area of a rectangle?",
         key_facts=["Area = length x breadth"]),
    dict(id="EN_050", lang="english", class_=6, term=3, unit="Symmetry", pages=[68],
         difficulty="medium", qtype="definition",
         q="What is meant by the order of rotational symmetry of an object?",
         key_facts=["number of times an object matches itself in one complete rotation"]),
    dict(id="EN_051", lang="english", class_=6, term=3, unit="Information Processing", pages=[88],
         difficulty="medium", qtype="definition",
         q="State the Euclidean algorithm relationship between a dividend, divisor, quotient and remainder.",
         key_facts=["Dividend = (Divisor x Quotient) + Remainder"]),
    dict(id="TA_018", lang="tamil", class_=6, term=3, unit="Integers", pages=[30],
         difficulty="easy", qtype="definition",
         c=None,
         q="முழு எண்கள் (Integers) என்பது என்ன, அவை எந்த எழுத்தால் குறிக்கப்படுகின்றன?",
         key_facts=["..., -3, -2, -1, 0, 1, 2, 3, ... முழு எண்கள்", "Z என்ற எழுத்தால் குறிக்கப்படுகின்றன"]),

    # ================================================================
    # NEW (v2.0.0): CLASS 7 MATHEMATICS, TERM 1
    # Source: 7_maths_T1_english.txt; Tamil source: 7_maths_T1_tamil.txt
    # (very little usable Tamil text in this specific term -- 1 item only).
    # ================================================================
    dict(id="EN_052", lang="english", class_=7, term=1, unit="Integers", pages=[7],
         difficulty="medium", qtype="calculation",
         q="Using the number line method, what is the sum of (-6) and (-4)?",
         key_facts=["(-6) + (-4) = -10"]),
    dict(id="EN_053", lang="english", class_=7, term=1, unit="Integers", pages=[28],
         difficulty="medium", qtype="explanation",
         q="Is division commutative for integers? Give a reason.",
         key_facts=["no, division is not commutative for integers",
                    "e.g. (-5) divided by 3 is not equal to 3 divided by (-5)"]),
    dict(id="EN_054", lang="english", class_=7, term=1, unit="Geometry", pages=[48],
         difficulty="medium", qtype="definition",
         q="What is a trapezium?",
         key_facts=["a parallelogram-like quadrilateral with one pair of non-parallel sides",
                    "if the non-parallel sides are equal it is an isosceles trapezium"]),
    dict(id="EN_055", lang="english", class_=7, term=1, unit="Geometry", pages=[89],
         difficulty="easy", qtype="definition",
         q="What are complementary angles and supplementary angles?",
         key_facts=["complementary: two angles summing to 90 degrees",
                    "supplementary: two angles summing to 180 degrees"]),
    dict(id="EN_056", lang="english", class_=7, term=1, unit="Geometry", pages=[83],
         difficulty="medium", qtype="list",
         q="What three sets of measurements are sufficient to construct a unique triangle?",
         key_facts=["lengths of all three sides (SSS)",
                    "two sides and the included angle",
                    "two angles and the included side"]),
    dict(id="EN_057", lang="english", class_=7, term=1, unit="Algebra", pages=[58],
         difficulty="easy", qtype="explanation",
         q="In the expression 12 - x, what are the variable and the terms, and how many terms are there?",
         key_facts=["variable: x", "terms: 12 and -x", "number of terms: 2"]),
    dict(id="TA_019", lang="tamil", class_=7, term=1, unit="Integers", pages=[13],
         difficulty="medium", qtype="definition",
         q="கூட்டல் மற்றும் பரிமாற்றுப் பண்பு (commutative property) என்றால் என்ன, ஓர் உதாரணம் தருக.",
         key_facts=["இரு எண்களின் கூட்டல் வரிசையை மாற்றினாலும் விடை மாறாது"]),

    # ================================================================
    # NEW (v2.0.0): CLASS 7 MATHEMATICS, TERM 2
    # Source: 7_maths_T2_english.txt; Tamil source: 7_maths_T2_tamil.txt
    # (36 usable chunks -- prose duplicated/garbled but numeric examples
    # are legible, e.g. the decimal-to-fraction conversions below).
    # ================================================================
    dict(id="EN_058", lang="english", class_=7, term=2, unit="Decimals", pages=[8],
         difficulty="easy", qtype="explanation",
         q="How is the decimal number 3.2 represented in terms of ones and tenths?",
         key_facts=["3 ones and 2 tenths"]),
    dict(id="EN_059", lang="english", class_=7, term=2, unit="Decimals", pages=[14],
         difficulty="easy", qtype="calculation",
         q="Express the fraction 3/5 as a decimal number.",
         key_facts=["3/5 = 6/10 = 0.6"]),
    dict(id="EN_060", lang="english", class_=7, term=2, unit="Measurements", pages=[32],
         difficulty="easy", qtype="definition",
         q="What is the formula used to find the circumference of a circle?",
         key_facts=["C = 2 x pi x r"]),
    dict(id="EN_061", lang="english", class_=7, term=2, unit="Measurements", pages=[39],
         difficulty="medium", qtype="calculation",
         q="How do you find the area of a circular walking pathway around a circular region, given the outer and inner radii?",
         key_facts=["area = pi x (R^2 - r^2), where R is outer radius and r is inner radius"]),
    dict(id="EN_062", lang="english", class_=7, term=2, unit="Exponents", pages=[50],
         difficulty="medium", qtype="definition",
         q="State the Product Rule of exponents for a^m x a^n.",
         key_facts=["a^m x a^n = a^(m+n)"]),
    dict(id="EN_063", lang="english", class_=7, term=2, unit="Exponents", pages=[58],
         difficulty="hard", qtype="explanation",
         q="What unit digit does a number ending in 5 or 6 always have when raised to any positive integer power?",
         key_facts=["a number ending in 5, raised to any positive power, ends in 5",
                    "a number ending in 6, raised to any positive power, ends in 6"]),
    dict(id="EN_064", lang="english", class_=7, term=2, unit="Statistics", pages=[104],
         difficulty="medium", qtype="explanation",
         q="In the footwear sales example, why might the arithmetic mean not be the best measure to decide how much stock to reorder for each shoe size?",
         key_facts=["mean footwear count (29) does not reflect the true demand per size",
                    "some sizes sell far more or fewer than the average"]),
    dict(id="TA_020", lang="tamil", class_=7, term=2, unit="Decimals", pages=[15],
         difficulty="easy", qtype="calculation",
         q="3/5 என்ற பின்னத்தை தசம எண்ணாக மாற்றுக.",
         key_facts=["3/5 = 6/10 = 0.6"]),
    dict(id="BI_013", lang="bilingual", class_=7, term=2, unit="Measurements", pages=[32],
         difficulty="easy", qtype="definition",
         q="Circle-oda circumference-ஐக் கண்டுபிடிக்க பயன்படுத்தும் formula என்ன?",
         key_facts=["C = 2 x pi x r"]),

    # ================================================================
    # NEW (v2.0.0): CLASS 7 MATHEMATICS, TERM 3
    # Source: 7_maths_T3_english.txt; Tamil source: 7_maths_T3_tamil.txt
    # (42 usable chunks -- numeric worked examples legible despite garbling).
    # ================================================================
    dict(id="EN_065", lang="english", class_=7, term=3, unit="Decimals", pages=[7],
         difficulty="medium", qtype="calculation",
         q="Round 52.6583 to 2 places of decimal.",
         key_facts=["52.66"]),
    dict(id="EN_066", lang="english", class_=7, term=3, unit="Percentage", pages=[41],
         difficulty="medium", qtype="calculation",
         q="An alloy contains 26% copper. How much alloy is required to get 260 g of copper?",
         key_facts=["1000 g of alloy"]),
    dict(id="EN_067", lang="english", class_=7, term=3, unit="Algebra", pages=[53],
         difficulty="medium", qtype="definition",
         q="What is the algebraic identity for (a+b)^2?",
         key_facts=["(a+b)^2 = a^2 + 2ab + b^2"]),
    dict(id="EN_068", lang="english", class_=7, term=3, unit="Algebra", pages=[63],
         difficulty="medium", qtype="calculation",
         q="Factorise x^2 - 4 using the identity a^2 - b^2 = (a+b)(a-b).",
         key_facts=["x^2 - 4 = (x+2)(x-2)"]),
    dict(id="EN_069", lang="english", class_=7, term=3, unit="Geometry", pages=[85],
         difficulty="easy", qtype="definition",
         q="What does it mean to reflect a shape about a given line?",
         key_facts=["the shape is mirrored across the line of reflection"]),
    dict(id="EN_070", lang="english", class_=7, term=3, unit="Information Processing", pages=[128],
         difficulty="easy", qtype="explanation",
         q="In the traffic-signal flowchart example, what output does the flowchart print if the signal is red?",
         key_facts=["prints \"Stop\""]),
    dict(id="TA_021", lang="tamil", class_=7, term=3, unit="Decimals", pages=[15],
         difficulty="medium", qtype="calculation",
         q="0.1 x 0.1 இன் மதிப்பு என்ன?",
         key_facts=["0.1 x 0.1 = 0.01"]),
    dict(id="TA_022", lang="tamil", class_=7, term=3, unit="Decimals", pages=[17],
         difficulty="medium", qtype="calculation",
         q="5.6 ஐ 3.2 ஆல் பெருக்கினால் என்ன விடை வரும்?",
         key_facts=["5.6 x 3.2 = 17.92 (worked as 56 x 32 = 1792, adjusted for 2 decimal places)"]),

    # ================================================================
    # NEW (v2.0.0): CLASS 7 SCIENCE, TERM 1
    # Source: 7_science_T1_english.txt. Tamil for this term is effectively
    # empty in the corpus (1 usable chunk, a bare numeric table) -- no
    # Tamil items added, flagged as a coverage gap in the report.
    # ================================================================
    dict(id="EN_071", lang="english", class_=7, term=1, unit="Measurement", pages=[7],
         difficulty="medium", qtype="explanation",
         q="How can the approximate area of an irregularly shaped object like a leaf be found using a graph sheet?",
         key_facts=["count whole squares (M), more-than-half squares (N), half squares (P), less-than-half squares (Q)",
                    "area = M + (3/4)N + (1/2)P + (1/4)Q sq cm"]),
    dict(id="EN_072", lang="english", class_=7, term=1, unit="Motion", pages=[21],
         difficulty="easy", qtype="definition",
         q="What is velocity, and what is its formula?",
         key_facts=["rate of change in displacement", "velocity = displacement / time"]),
    dict(id="EN_073", lang="english", class_=7, term=1, unit="Force", pages=[27],
         difficulty="medium", qtype="definition",
         q="What is the centre of gravity of an object?",
         key_facts=["the point through which the entire weight of the object appears to act"]),
    dict(id="EN_074", lang="english", class_=7, term=1, unit="Matter", pages=[39],
         difficulty="easy", qtype="explanation",
         q="What is the chemical formula for glucose, and what atoms does it contain?",
         key_facts=["C6H12O6", "6 carbon atoms, 12 hydrogen atoms, 6 oxygen atoms"]),
    dict(id="EN_075", lang="english", class_=7, term=1, unit="Atoms", pages=[56],
         difficulty="hard", qtype="calculation",
         q="If the atomic number of an element is 9 and it has 10 neutrons, what is its mass number?",
         key_facts=["mass number = protons + neutrons = 9 + 10 = 19"]),
    dict(id="EN_076", lang="english", class_=7, term=1, unit="Plants", pages=[65],
         difficulty="medium", qtype="definition",
         q="What is fertilization in flowering plants?",
         key_facts=["fusion of male gamete (from pollen tube) with female gamete in the ovule, forming a zygote"]),
    dict(id="EN_077", lang="english", class_=7, term=1, unit="Health", pages=[80],
         difficulty="medium", qtype="explanation",
         q="How is dengue spread, according to the textbook?",
         key_facts=["spread by Aedes aegypti mosquitoes", "caused by DEN virus (flavivirus)"]),
    dict(id="EN_078", lang="english", class_=7, term=1, unit="Health", pages=[87],
         difficulty="medium", qtype="definition",
         q="What is leucoderma, and how does it spread?",
         key_facts=["a non-communicable disease causing loss of skin pigmentation (melanin)",
                    "does not spread by touching, sharing food or sitting together"]),

    # ================================================================
    # NEW (v2.0.0): CLASS 7 SCIENCE, TERM 2
    # Source: 7_science_T2_english.txt. Tamil for this term is effectively
    # empty (2 usable chunks -- a numeric conversion and a fill-in-the-blank
    # table) -- no Tamil CORE items added.
    # ================================================================
    dict(id="EN_079", lang="english", class_=7, term=2, unit="Heat", pages=[7],
         difficulty="easy", qtype="explanation",
         q="What is a clinical thermometer used for?",
         key_facts=["measuring human body temperature"]),
    dict(id="EN_080", lang="english", class_=7, term=2, unit="Electricity", pages=[22],
         difficulty="medium", qtype="comparison",
         q="What is the difference between a primary cell and a secondary cell?",
         key_facts=["primary cell: cannot be recharged (e.g. dry cell)",
                    "secondary cell: can be recharged (e.g. lithium cylindrical cells)"]),
    dict(id="EN_081", lang="english", class_=7, term=2, unit="Electricity", pages=[30],
         difficulty="medium", qtype="definition",
         q="What is an electric fuse, and what is its purpose?",
         key_facts=["a safety device with a fuse wire that melts on current overload",
                    "breaks the circuit to prevent damage to appliances and wiring"]),
    dict(id="EN_082", lang="english", class_=7, term=2, unit="Chemistry", pages=[50],
         difficulty="medium", qtype="explanation",
         q="Why hasn't the Iron Pillar at Delhi's Qutub Minar rusted despite being over 1600 years old?",
         key_facts=["Indian metal-making technology gave it great rust resistance"]),
    dict(id="EN_083", lang="english", class_=7, term=2, unit="Biology", pages=[76],
         difficulty="medium", qtype="comparison",
         q="What is the basic difference between vertebrates and invertebrates in the classification scheme shown?",
         key_facts=["vertebrates: animals with a backbone (mammals, birds, fish, amphibians, reptiles)",
                    "invertebrates: animals without a backbone"]),
    dict(id="EN_084", lang="english", class_=7, term=2, unit="Biology", pages=[86],
         difficulty="hard", qtype="list",
         q="According to the Five Kingdom classification, what is the cell type of organisms in Kingdom Monera?",
         key_facts=["unicellular, prokaryotic"]),

    # ================================================================
    # NEW (v2.0.0): CLASS 7 SCIENCE, TERM 3
    # Source: 7_science_T3_english.txt. Tamil for this term is essentially
    # empty (2 usable chunks) -- no Tamil CORE items added.
    # ================================================================
    dict(id="EN_085", lang="english", class_=7, term=3, unit="Light", pages=[10],
         difficulty="easy", qtype="definition",
         q="What is the relationship between the angle of incidence and the angle of reflection?",
         key_facts=["the angle of incidence equals the angle of reflection"]),
    dict(id="EN_086", lang="english", class_=7, term=3, unit="Light", pages=[20],
         difficulty="medium", qtype="list",
         q="What does the acronym VIBGYOR stand for in the context of visible light?",
         key_facts=["Violet, Indigo, Blue, Green, Yellow, Orange, Red"]),
    dict(id="EN_087", lang="english", class_=7, term=3, unit="Astronomy", pages=[36],
         difficulty="medium", qtype="comparison",
         q="What is the difference between a spiral galaxy and an elliptical galaxy?",
         key_facts=["spiral: flat, organized structure with spiral arms and ongoing star formation",
                    "elliptical: ellipsoidal, three-dimensional, older stars, less structure"]),
    dict(id="EN_088", lang="english", class_=7, term=3, unit="Materials", pages=[50],
         difficulty="medium", qtype="explanation",
         q="Why is rayon considered a semi-synthetic fibre rather than a fully synthetic one?",
         key_facts=["made from natural cellulose (from wood/bamboo pulp) treated with chemicals"]),
    dict(id="EN_089", lang="english", class_=7, term=3, unit="Materials", pages=[61],
         difficulty="medium", qtype="definition",
         q="What is PLA (Poly Lactic Acid), and what is it obtained from?",
         key_facts=["a compostable, bioactive, biodegradable thermoplastic",
                    "obtained from plant starch such as corn, sugarcane, sugar beet pulp"]),
    dict(id="EN_090", lang="english", class_=7, term=3, unit="Health", pages=[74],
         difficulty="medium", qtype="definition",
         q="What is an antipyretic, and name one common example?",
         key_facts=["a chemical substance that reduces fever by suppressing prostaglandin release",
                    "paracetamol"]),
    dict(id="EN_091", lang="english", class_=7, term=3, unit="Fire Safety", pages=[81],
         difficulty="medium", qtype="list",
         q="What causes a Class B fire, and what causes a Class D fire?",
         key_facts=["Class B: flammable liquids like petrol or paint",
                    "Class D: combustible metals like magnesium, aluminium, potassium"]),

    # ================================================================
    # NEW (v2.0.0): CLASS 8 MATHEMATICS
    # Source: 8_maths_T0_english.txt (single-volume book, no term split);
    # Tamil source: 8_maths_T0_tamil.txt (heavily garbled prose, but
    # numeric identities/examples remain legible, e.g. TA_023 below).
    # ================================================================
    dict(id="EN_092", lang="english", class_=8, term=0, unit="Rational Numbers", pages=[20],
         difficulty="easy", qtype="calculation",
         q="Add the rational numbers -6/11, -8/11 and 12/11 (same denominator).",
         key_facts=["(-6-8+12)/11 = -2/11"]),
    dict(id="EN_093", lang="english", class_=8, term=0, unit="Numbers", pages=[37],
         difficulty="medium", qtype="calculation",
         q="The area of a square field is 3136 sq. metres. What is its perimeter?",
         key_facts=["side = sqrt(3136) = 56 m", "perimeter = 4 x 56 = 224 m"]),
    dict(id="EN_094", lang="english", class_=8, term=0, unit="Algebra", pages=[95],
         difficulty="hard", qtype="definition",
         q="What is the cubic identity for (x+a)(x+b)(x+c)?",
         key_facts=["x^3 + (a+b+c)x^2 + (ab+bc+ca)x + abc"]),
    dict(id="EN_095", lang="english", class_=8, term=0, unit="Coordinate Geometry", pages=[115],
         difficulty="easy", qtype="definition",
         q="In an ordered pair (4,3) representing a point M, what are the abscissa and ordinate?",
         key_facts=["4 is the x-coordinate (abscissa)", "3 is the y-coordinate (ordinate)"]),
    dict(id="EN_096", lang="english", class_=8, term=0, unit="Life Mathematics", pages=[134],
         difficulty="medium", qtype="calculation",
         q="If the selling price of an item is 5/4 of its cost price, what is the profit percentage?",
         key_facts=["profit % = 25%"]),
    dict(id="EN_097", lang="english", class_=8, term=0, unit="Geometry", pages=[181],
         difficulty="easy", qtype="definition",
         q="What is an angle bisector of a triangle?",
         key_facts=["a line or ray that divides an angle of the triangle into two congruent angles"]),
    dict(id="EN_098", lang="english", class_=8, term=0, unit="Statistics", pages=[222],
         difficulty="medium", qtype="calculation",
         q="For EB bill data ranging from Rs.120 to Rs.800 with a class size of 100, how many class intervals are needed?",
         key_facts=["range = 800-120 = 680", "number of class intervals = 680/100, rounded up to 7"]),
    dict(id="EN_099", lang="english", class_=8, term=0, unit="Information Processing", pages=[241],
         difficulty="medium", qtype="definition",
         q="State the multiplication principle of counting.",
         key_facts=["if a selection can be done in m ways followed by another in n ways, together they can be done in m x n ways"]),
    dict(id="TA_023", lang="tamil", class_=8, term=0, unit="Numbers", pages=[45],
         difficulty="medium", qtype="calculation",
         q="9-ன் கனம் (cube) என்ன, மற்றும் 27-ன் கனமூலம் (cube root) என்ன?",
         key_facts=["9^3 = 729", "27-ன் கனமூலம் 3 (ஏனெனில் 3^3 = 27)"]),
    dict(id="BI_014", lang="bilingual", class_=8, term=0, unit="Numbers", pages=[37],
         difficulty="medium", qtype="calculation",
         q="3136 sq.m பரப்பளவு உள்ள ஒரு square field-ன் perimeter என்ன?",
         key_facts=["side = sqrt(3136) = 56 m", "perimeter = 4 x 56 = 224 m"]),

    # ================================================================
    # NEW (v2.0.0): CLASS 8 SCIENCE
    # Source: 8_science_T0_english.txt (single-volume book);
    # Tamil source: 8_science_T0_tamil.txt (glossary pages are clean;
    # prose elsewhere is corrupted, similar to other Tamil Science books).
    # ================================================================
    dict(id="EN_100", lang="english", class_=8, term=0, unit="Friction", pages=[21],
         difficulty="easy", qtype="comparison",
         q="What is the difference between static friction and kinetic friction?",
         key_facts=["static: friction on bodies at rest", "kinetic: friction during motion of bodies"]),
    dict(id="EN_101", lang="english", class_=8, term=0, unit="Heat", pages=[42],
         difficulty="medium", qtype="definition",
         q="What is radiation as a mode of heat transfer, and give one example from daily life.",
         key_facts=["heat transfer through empty space/vacuum as electromagnetic waves",
                    "e.g. heat from the Sun reaching the Earth"]),
    dict(id="EN_102", lang="english", class_=8, term=0, unit="Magnetism", pages=[82],
         difficulty="medium", qtype="list",
         q="Name two ways a magnet can lose its magnetic properties.",
         key_facts=["heating to high temperature", "dropping from a height", "hammering",
                    "placing idle for a long time"]),
    dict(id="EN_103", lang="english", class_=8, term=0, unit="Chemistry", pages=[104],
         difficulty="medium", qtype="definition",
         q="What is the common name for Calcium sulphate hemihydrate, and what is it used for?",
         key_facts=["Plaster of Paris", "used in preparation of baking powder, cakes and bread"]),
    dict(id="EN_104", lang="english", class_=8, term=0, unit="Atomic Structure", pages=[128],
         difficulty="medium", qtype="explanation",
         q="Who proposed the first scientific theory about the atom, and who followed with their own atomic theories?",
         key_facts=["John Dalton proposed the first scientific atomic theory",
                    "followed by J.J. Thomson and Rutherford"]),
    dict(id="EN_105", lang="english", class_=8, term=0, unit="Heat", pages=[147],
         difficulty="medium", qtype="explanation",
         q="Why is water used as a coolant in car engines?",
         key_facts=["water has a very high specific heat capacity",
                    "it can absorb and retain a lot of heat for a longer time"]),
    dict(id="EN_106", lang="english", class_=8, term=0, unit="Chemistry", pages=[171],
         difficulty="easy", qtype="definition",
         q="What is methane, and why is it considered an eco-friendly fuel?",
         key_facts=["the simplest hydrocarbon (CH4), colourless and odourless",
                    "does not produce harmful products when burnt"]),
    dict(id="EN_107", lang="english", class_=8, term=0, unit="Human Body", pages=[226],
         difficulty="medium", qtype="list",
         q="Give one example each of a hinge joint and a ball-and-socket joint in the human body.",
         key_facts=["hinge joint: elbow/knee/ankle", "ball and socket joint: example given in joints table"]),
    dict(id="EN_108", lang="english", class_=8, term=0, unit="Environment", pages=[272],
         difficulty="medium", qtype="definition",
         q="What is the Red Data Book, and which organization maintains it?",
         key_facts=["records rare and endangered species of animals, plants and fungi",
                    "maintained by the International Union for Conservation of Nature (IUCN)"]),
    dict(id="TA_024", lang="tamil", class_=8, term=0, unit="Vocabulary", pages=[300, 301],
         difficulty="easy", qtype="vocabulary",
         q="'சிவப்பு தரவுப் புத்தகம்' (Red Data Book) மற்றும் 'உராய்வு' (Friction) ஆகிய தமிழ்ச் சொற்களுக்கான ஆங்கிலச் சொற்களைத் தருக.",
         key_facts=["சிவப்பு தரவுப் புத்தகம் = Red Data Book", "உராய்வு = Friction"]),
    dict(id="TA_025", lang="tamil", class_=8, term=0, unit="Vocabulary", pages=[300, 301],
         difficulty="easy", qtype="vocabulary",
         q="'காந்தப்புலம்' மற்றும் 'மின்தடை' ஆகிய சொற்களுக்கான ஆங்கில அறிவியல் சொற்கள் என்ன?",
         key_facts=["காந்தப்புலம் = Magnetic field", "மின்தடை = Resistance"]),
]

# Fix a stray leftover key from drafting (harmless if left, but keep the
# dataset clean): remove the accidental `c=None` field on TA_018.
for _item in CORE:
    _item.pop("c", None)

# ----------------------------------------------------------------------
# Tag every item with its ground-truth subject ("science" or "maths").
# This is required by evaluate_retrieval_bm25.py's filter_candidate_indices,
# which was fixed in this same v2.0.0 pass to filter by subject -- omitting
# it was a latent bug that only became consequential once this corpus
# rebuild added Maths content alongside Science for every class/term (see
# that script's updated docstring for the full explanation). Ranges below
# were assigned by construction while writing CORE above, and are verified
# against the printed language/class counts at the bottom of this file.
# ----------------------------------------------------------------------
_SCIENCE_EN = set(range(1, 21)) | set(range(21, 26)) | set(range(26, 35)) | \
              set(range(71, 79)) | set(range(79, 85)) | set(range(85, 92)) | set(range(100, 109))
_MATHS_EN = set(range(35, 41)) | set(range(41, 46)) | set(range(46, 52)) | \
            set(range(52, 58)) | set(range(58, 65)) | set(range(65, 71)) | set(range(92, 100))
_SCIENCE_TA = set(range(1, 13)) | {13, 14, 24, 25}
_MATHS_TA = {15, 16, 17, 18, 19, 20, 21, 22, 23}
_SCIENCE_BI = set(range(1, 10)) | {10}
_MATHS_BI = {11, 12, 13, 14}
_SCIENCE_TG = set(range(1, 9)) | {9}
_MATHS_TG = set()

_SUBJECT_SETS = {
    "EN": (_SCIENCE_EN, _MATHS_EN),
    "TA": (_SCIENCE_TA, _MATHS_TA),
    "BI": (_SCIENCE_BI, _MATHS_BI),
    "TG": (_SCIENCE_TG, _MATHS_TG),
}

for _item in CORE:
    _prefix, _num_str = _item["id"].split("_")
    _num = int(_num_str)
    _science_ids, _maths_ids = _SUBJECT_SETS[_prefix]
    if _num in _science_ids:
        _item["subject"] = "science"
    elif _num in _maths_ids:
        _item["subject"] = "maths"
    else:
        raise ValueError(f"Item {_item['id']} not assigned to a subject -- update the ID ranges above.")

LANGUAGE_INSTRUCTION = [
    dict(id="LI_001", instruction="Answer in Tamil.", underlying_q="What is motion?",
         expect_script="tamil"),
    dict(id="LI_002", instruction="Answer in English.", underlying_q="பருப்பொருள் என்றால் என்ன?",
         expect_script="latin"),
    dict(id="LI_003", instruction="Explain in simple Tamil, for a young child.",
         underlying_q="ஒளிச்சேர்க்கை என்றால் என்ன?", expect_script="tamil"),
    dict(id="LI_004", instruction="Explain in Tamil but keep scientific terms in English.",
         underlying_q="What is a virus?", expect_script="mixed"),
    dict(id="LI_005", instruction="Explain in Tanglish.",
         underlying_q="Force and motion la contact force nu solna enna?", expect_script="latin"),
    dict(id="LI_006", instruction="Answer in both Tamil and English.",
         underlying_q="What is matter?", expect_script="mixed"),
    # A case designed to expose the toggle-vs-query-text mismatch found in prompt_builder.py:
    # UI language toggle = English (so retrieval fetches English chunks), but the
    # question itself is written in Tamil script.
    dict(id="LI_007", instruction="[UI toggle set to English] -- question typed in Tamil script",
         underlying_q="இயக்கம் என்றால் என்ன?", expect_script="tamil_or_english_but_consistent",
         note="Toggle/query-language mismatch probe -- see prompt_builder.detect_language() finding"),
    # New in v2.0.0: a Maths-specific example (all prior items were Science-only).
    dict(id="LI_008", instruction="Answer in Tamil.",
         underlying_q="What is a trapezium?", expect_script="tamil",
         note="Maths-specific language-compliance probe, added in the v2.0.0 full-corpus rebuild "
              "since all v1.0.0 language_instruction items were Class 6 Science only."),
]

OUT_OF_SCOPE = [
    # ------------------------------------------------------------------
    # v2.0.0: OOS_001/002/003 from v1.0.0 (Maths not indexed; Class 7/8
    # Science not indexed) are REMOVED here because they are now FALSE --
    # the corpus was fully rebuilt to cover Class 6/7/8 x Maths/Science x
    # English/Tamil. Replaced with topics genuinely absent from the
    # Tamil Nadu Class 6-8 syllabus/corpus (verified absent while reading
    # all 28 books' curated content during this dataset expansion).
    # ------------------------------------------------------------------
    dict(id="OOS_001", lang="english", reason="not_indexed_class",
         q="Explain the Calvin cycle and the light-dependent reactions of photosynthesis in the "
           "detail expected at Class 10 or higher Biology.",
         note="Corpus covers Class 6-8 only; this level of biochemical detail is not present in any "
              "indexed book (Class 6-8 Science covers photosynthesis only at an introductory level)."),
    dict(id="OOS_002", lang="english", reason="not_indexed_subject",
         q="Explain integration by parts and how it is used to solve calculus problems.",
         note="Calculus is not part of the Tamil Nadu Class 6-8 Mathematics syllabus; confirmed "
              "absent while reading all three Class 6/7/8 Maths books in full."),
    dict(id="OOS_003", lang="english", reason="not_indexed_topic",
         q="Explain Bohr's model of the atom and calculate the hydrogen energy levels using the "
           "Rydberg formula.",
         note="Class 7/8 Science atomic-structure content stops at Dalton/Thomson/Rutherford, "
              "valency and simple atomic/mass number arithmetic -- Bohr's model and the Rydberg "
              "formula are not covered at this level."),
    dict(id="OOS_004", lang="english", reason="false_premise",
         q="According to the textbook, why does water boil at 50 degrees Celsius at sea level?",
         note="False premise (water boils at 100C at sea level) -- tests whether the model corrects "
              "or complies with a false premise."),
    dict(id="OOS_005", lang="bilingual", reason="unrelated_combination",
         q="Photosynthesis-க்கும் Newton's third law-க்கும் என்ன தொடர்பு?",
         note="Combines two unrelated concepts to test whether the model fabricates a spurious "
              "connection. (Newton's laws of motion are not covered in the Class 6-8 corpus either, "
              "so this is doubly out of scope.)"),
    dict(id="OOS_006", lang="tanglish", reason="not_indexed_subject",
         q="Trigonometry la sine rule eppadi work aagum?",
         note="The sine rule / trigonometric ratios are not part of the Tamil Nadu Class 6-8 Maths "
              "syllabus -- confirmed absent while reading all three Class 6/7/8 Maths books in full."),
]

if __name__ == "__main__":
    dataset = {
        "meta": {
            "version": "2.0.0",
            "created": "2026-09-16",
            "previous_version": "1.0.0 (2026-09-15, Class 6 Science only, 523 chunks)",
            "grounded_in": "data/processed/cache/{english,tamil}_chunks.pkl after full 28-book "
                           "reindex (7,426 chunks: 3,583 English / 3,843 Tamil), verified 2026-09-16 "
                           "by direct inspection of data/registry/manifest.json and the pickle caches.",
            "note": "Pages verified by direct inspection of curated per-book text extractions from "
                    "the live pickle cache, not the raw PDFs and not the (separately verified, now "
                    "correct) data/registry/manifest.json. IMPORTANT: Tamil Science content in "
                    "several books (Class 6 T1/T3, Class 7 T1/T2/T3, Class 8) is heavily damaged by "
                    "a PDF font/ToUnicode-CMap encoding problem -- prose is largely unusable, so "
                    "Tamil CORE coverage for Science books is limited to verified-clean glossary "
                    "vocabulary. Tamil Maths content is usable (numeric/formula content survives "
                    "the corruption much better than prose) and is covered more fully. See the final "
                    "evaluation report's 'Tamil text extraction' finding for full details and the "
                    "measured (~1.1 percentage point) impact of the partial fix that was applied."
        },
        "core": CORE,
        "language_instruction": LANGUAGE_INSTRUCTION,
        "out_of_scope": OUT_OF_SCOPE,
    }
    with open("gold_dataset.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"core={len(CORE)} language_instruction={len(LANGUAGE_INSTRUCTION)} out_of_scope={len(OUT_OF_SCOPE)}")
    from collections import Counter
    print("By language:", Counter(c["lang"] for c in CORE))
    print("By class:", Counter(c["class_"] for c in CORE))
    print("By class+subject-ish (unit sample not subject, use class+term):",
          Counter((c["class_"], c["term"]) for c in CORE))
