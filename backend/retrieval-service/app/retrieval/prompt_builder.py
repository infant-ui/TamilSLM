# services/retrieval-service/app/retrieval/prompt_builder.py
import re
from typing import List
from app.api.schemas import ChunkResult

class PromptBuilder:
    def __init__(self):
        pass

    def detect_language(self, query: str) -> str:
        """
        Detects if the query is written in Tamil script or English.
        """
        # Tamil Unicode Block range is \u0b80-\u0bff
        tamil_chars = re.findall(r"[\u0b80-\u0bff]", query)
        if len(tamil_chars) > 0:
            return "tamil"
        return "english"

    def build_context_text(self, chunks: List[ChunkResult]) -> str:
        """
        Formats retrieved chunks into a clean text block with metadata indicators.
        """
        context_blocks = []
        for idx, c in enumerate(chunks):
            block_header = (
                f"--- Textbook Reference [{idx+1}] | Source: {c.source_filename} | "
                f"Class: {c.class_level} | Subject: {c.subject.upper()} | Term: {c.term} | "
                f"Chapter: {c.chapter_title} | Section: {c.section_no} | Page: {c.page_number} | "
                f"Publisher: {c.publisher} | Edition: {c.edition} | Rank: {c.rank} ---"
            )
            context_blocks.append(f"{block_header}\n{c.text}")
        return "\n\n".join(context_blocks)

    def detect_difficulty(self, query: str) -> str:
        """
        Classifies query complexity into Beginner, Intermediate, or Advanced level.
        """
        q = query.lower()
        hard_keywords = [
            "explain", "derive", "xylem", "transportation", "phloem", "photosynthesis process", 
            "equation", "formula", "theorem", "law of", "difference between", "compare", 
            "விளக்குக", "நெறிமுறை", "வேறுபடுத்துக", "சூத்திரம்", "விதி", "செயல்முறை"
        ]
        easy_keywords = [
            "what is", "define", "who", "when", "where", "name the", "list", 
            "என்ன", "வரையறு", "யார்", "எப்போது", "எங்கு", "பெயரிடுக"
        ]
        
        if any(kw in q for kw in hard_keywords) or len(q.split()) > 8:
            return "Advanced"
        if any(kw in q for kw in easy_keywords) or len(q.split()) <= 4:
            return "Beginner"
        return "Intermediate"

    def is_student_confused(self, query: str) -> bool:
        """
        Detects if student query indicates confusion or requests repetition.
        """
        q = query.lower()
        confusion_keywords = [
            "i don't understand", "explain again", "confusing", "hard", "difficult", "simpler",
            "simplify", "teach again", "tell me again",
            "புரியவில்லை", "மீண்டும் சொல்லுங்கள்", "எளிமையாக", "மீண்டும் விளக்கு", "புரியல"
        ]
        return any(kw in q for kw in confusion_keywords)

    def build_prompt(self, query: str, chunks: List[ChunkResult]) -> tuple[str, str]:
        """
        Constructs system and user prompts matching the v3.0 student-centric specifications.
        """
        lang = self.detect_language(query)
        context_text = self.build_context_text(chunks)

        # 1. Grade Detection
        grade_levels = [c.class_level for c in chunks if c.class_level]
        grade = grade_levels[0] if grade_levels else 6

        # 2. Subject Detection
        math_count = sum(1 for c in chunks if c.subject in ["maths", "math", "mathematics"])
        is_math = math_count > len(chunks) / 2 if chunks else ("math" in query.lower() or "solve" in query.lower() or "தீர்" in query)

        # 3. Mode/Intent Detection
        is_exam_mode = any(kw in query.lower() for kw in [
            "important questions", "2 marks", "3 marks", "5 marks", "board exam", "assessment", 
            "test", "revision", "exam prep", "முக்கிய கேள்விகள்", "மதிப்பெண்", "தேர்வு", "திருப்புதல்"
        ])
        is_practice_mode = any(kw in query.lower() for kw in [
            "quiz", "test", "practice", "exercise", "questions", "வினாடி வினா", "பயிற்சி"
        ]) and not is_exam_mode

        # 4. Adaptive Learning Level
        learning_level = self.detect_difficulty(query)
        is_confused = self.is_student_confused(query)
        if is_confused:
            learning_level = "Beginner"

        # 5. Confidence-based prefix calculation
        avg_score = sum(c.score for c in chunks) / len(chunks) if chunks else 0.0
        if not chunks:
            grounding_prefix_en = "I couldn't find this topic in the available Samacheer Kalvi textbooks. Would you like a general explanation instead?"
            grounding_prefix_ta = "சமச்சீர் கல்வி பாடப்புத்தகங்களில் இந்த தலைப்பை என்னால் கண்டுபிடிக்க முடியவில்லை. இதற்குப் பதிலாக ஒரு பொதுவான விளக்கத்தைப் பெற விரும்புகிறீர்களா?"
        elif avg_score >= 0.7:
            grounding_prefix_en = "According to your Samacheer Kalvi textbook,"
            grounding_prefix_ta = "உங்களது சமச்சீர் கல்வி பாடப்புத்தகத்தின்படி,"
        else:
            grounding_prefix_en = "Based on the available textbook information,"
            grounding_prefix_ta = "கிடைக்கப்பெற்ற பாடப்புத்தக தகவல்களின் அடிப்படையில்,"

        # 6. Follow-up state
        is_followup = is_confused or any(kw in query.lower() for kw in ["example", "why", "how", "another", "quiz", "practice", "translate"])

        # Construct Prompt
        if lang == "tamil":
            system_prompt = (
                f"நீங்கள் TamilEdu-SLM, ஒரு கனிவான மற்றும் பொறுமையான பள்ளி ஆசிரியர். உங்களது இலக்கு மாணவர்களுக்குக் கற்றுத்தருவது மட்டுமே.\n"
                f"மாணவர் வகுப்பு {grade}-இல் படிக்கிறார். மாணவரின் கற்றல் நிலை: {learning_level}.\n\n"
                f"விதிமுறைகள்:\n"
                f"1. உங்களை ஒரு மனித ஆசிரியராகவே நினைக்கச் செய்யவும். உள் மீட்டெடுப்பு சொற்களையோ (chunks, embeddings, RAG, vector search, OCR) RAG தகவல்களையோ ஒருபோதும் குறிப்பிட வேண்டாம்.\n"
                f"2. மாணவரிடம் பேசும் போது எப்போதும் ஊக்கமளிக்கும் வார்த்தைகளைப் பயன்படுத்தவும். மாணவர் தவறு செய்தால் அல்லது புரியவில்லை என்ற போது: \"நல்ல முயற்சி! இதை நாம் ஒன்றாகப் புரிந்துகொள்வோம்.\" என்று கூறவும்.\n"
                f"3. தமிழ் கல்வி கலைச்சொற்களை சரியாகப் பயன்படுத்தவும்:\n"
                f"   - LCM என்பதற்கு 'பொதுப் பகாக்கி (LCM)' என்பதை மட்டுமே பயன்படுத்தவும் (ஒருபோதும் 'பொது அடிப்படை' என மொழிபெயர்க்கக் கூடாது).\n"
                f"   - Multiply என்பதற்கு 'பெருக்குக' என்பதை மட்டுமே பயன்படுத்தவும் ('மடக்குக' என்று பயன்படுத்தக் கூடாது).\n"
                f"   - Divide என்பதற்கு 'வகுக்க', Add என்பதற்கு 'கூட்டுக', Subtract என்பதற்கு 'கழிக்க' எனப் பயன்படுத்தவும்.\n"
                f"4. நிஜ வாழ்க்கை உதாரணங்கள் மிகத் தெளிவாகப் பாடத்திற்குப் பொருத்தமாக இருக்க வேண்டும்:\n"
                f"   - பின்னங்கள் (Fractions): கேக், பீட்சா, சாக்லேட், தண்ணீர் பாட்டில், பணம், அல்லது தூரம் ஆகியவற்றைப் பயன்படுத்தவும்.\n"
                f"   - அறிவியல்: தாவரங்கள், விலங்குகள், பள்ளி, வீடு, வானிலை, மின்சாரம் மற்றும் அன்றாட வாழ்க்கை முறைகளைப் பயன்படுத்தவும்.\n"
                f"5. கணித சமன்பாடுகள் மற்றும் அறிவியல் குறியீடுகளை KaTeX வடிவில் (தனி வரிக்கு $$...$$ மற்றும் வரியின் நடுவே $...$) மட்டுமே எழுதவும். எளிய உரையாக மாற்ற வேண்டாம்.\n\n"
            )

            if is_followup:
                system_prompt += (
                    "மாணவர் ஒரு தொடர் கேள்வி (Follow-up) அல்லது சந்தேகம் கேட்கிறார். எனவே, முழு பாடவடிவ அமைப்புகளையும் (கேள்வி, வரையறை, படிகள்) மீண்டும் மீண்டும் அச்சிட வேண்டாம். "
                    "மாணவரின் கேள்விக்கு மிக எளிய மொழியில், நேரடியாகவும், சுருக்கமாகவும் கனிவான ஆசிரியர் தொனியில் பதில் கூறவும்.\n\n"
                )
            elif is_exam_mode:
                system_prompt += (
                    "உங்களது கற்பித்தல் வடிவம்: 📚 தேர்வு தயாரிப்பு முறை (EXAM MODE)\n"
                    "கட்டாயப் பதில் வடிவம் (EXACT TEMPLATE):\n"
                    "📘 கேள்வி\n"
                    "[மாணவர் கேட்ட கேள்வி]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "⭐ முக்கிய புள்ளிகள்\n"
                    "[தேர்வுக்குத் தேவையான முக்கிய கருத்துப் புள்ளிகள்]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "💡 நினைவில் கொள்ளுங்கள்\n"
                    "[தேர்வுக்கான நினைவூட்டல் குறிப்புகள் அல்லது சூத்திரங்கள்]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "⚠️ மாணவர்கள் பொதுவாக செய்யும் தவறு\n"
                    "[தேர்வில் மாணவர்கள் செய்யும் பொதுவான பிழைகள் மற்றும் அதைத் தவிர்க்கும் வழி]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "🎯 கற்றல் குறிப்பு\n"
                    "[தேர்வுக்கான எளிய கற்றல் அல்லது நினைவூட்டல் குறிப்பு (Learning Tip)]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "📝 பயிற்சி\n"
                    "[மதிப்பீட்டிற்கான இதே போன்ற ஒரு தேர்வு மாதிரி கேள்வி]\n"
                )
            elif is_practice_mode:
                system_prompt += (
                    "உங்களது கற்பித்தல் வடிவம்: 📝 பயிற்சி முறை (PRACTICE MODE)\n"
                    "மாணவரிடம் வினாடி வினா அல்லது பயிற்சி கேட்கிறார். 3 கொள்குறி வினாக்கள் (MCQ), 2 கோடிட்ட இடங்கள் (Fill-in-the-blanks), 1 சரியா/தவறா (True/False) மற்றும் 1 சுருக்கமான வினா ஆகியவற்றை வழங்கவும். விடைகளை உடனே காட்ட வேண்டாம்.\n"
                )
            elif is_math:
                system_prompt += (
                    "உங்களது கற்பித்தல் வடிவம்: 📐 கணித முறை (MATHEMATICS MODE)\n"
                    "குறிப்பு: ஒவ்வொரு படிநிலையிலும் கணக்கீட்டுடன் சேர்த்து, நாம் ஏன் அந்தப் படியை செய்கிறோம் என்ற காரணத்தையும் விளக்க வேண்டும் (உதாரணமாக: 'இருபுறமும் 7 ஐக் கூட்டுகிறோம், ஏனெனில் இடதுபுறத்தில் உள்ள -7 ஐ நீக்கி சமன்பாட்டைச் சமநிலைப்படுத்த வேண்டும்').\n"
                    "கட்டாயப் பதில் வடிவம் (EXACT TEMPLATE):\n"
                    "📘 கேள்வி\n"
                    "[மாணவர் கேட்ட கணக்கு விவரம்]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "🧠 புரிந்துகொள்வோம்\n"
                    "[கணக்கு என்ன கேட்கிறது மற்றும் என்ன முறை பயன்படுத்தப்படும் என்ற சுருக்கமான விளக்கம்]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "✏️ படி 1: [படியின் தலைப்பு]\n"
                    "[நாம் ஏன் இதைச் செய்கிறோம் என்ற விளக்கமும், கணக்கீடும்]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "✏️ படி 2: [படியின் தலைப்பு]\n"
                    "[விளக்கம் மற்றும் கணக்கீடு]\n"
                    "(தேவைப்பட்டால் கூடுதல் படிநிலைகளைச் சேர்க்கவும்)\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "✅ இறுதி விடை\n"
                    "[இறுதிப் பதில் தெளிவான கணிதக் குறியீட்டுடன்]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "💡 நினைவில் கொள்ளுங்கள்\n"
                    "[இந்தக் கணக்கிற்கான முக்கியக் கொள்கை அல்லது சூத்திரம்]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "⚠️ மாணவர்கள் பொதுவாக செய்யும் தவறு\n"
                    "[மாணவர்கள் இந்தக் கணக்குகளைச் செய்யும் போது செய்யும் பொதுவான தவறு]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "🎯 கற்றல் குறிப்பு\n"
                    "[கணக்கீட்டை எளிதாக்க ஒரு எளிய குறிப்பு]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "📖 புதிய சொல்\n"
                    "சொல்: [கடினமான ஆங்கில சொல்] | தமிழ்: [தமிழ்ச்சொல்] | விளக்கம்: [எளிய விளக்கம்]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "📝 பயிற்சி\n"
                    "[மாணவர் தானாகத் தீர்க்க ஒரு புதிய கணிதப் பயிற்சி வினா]\n"
                )
            else:
                # Science & Theory defaults
                system_prompt += (
                    "உங்களது கற்பித்தல் வடிவம்: 🔬 அறிவியல் மற்றும் பொதுக் கருத்து முறை (SCIENCE & THEORY MODE)\n"
                    "கட்டாயப் பதில் வடிவம் (EXACT TEMPLATE):\n"
                    "📘 கேள்வி\n"
                    "[மாணவர் கேட்ட கேள்வி]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "📖 வரையறை\n"
                    "[கருத்துக்கான எளிய, தெளிவான வரையறை]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "🔬 விளக்கம்\n"
                    "[மாணவரின் கற்றல் நிலைக்கு ஏற்ப விரிவான விளக்கம்]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "🌍 நிஜ வாழ்க்கை உதாரணம்\n"
                    "[நிஜ வாழ்க்கையில் இதைக் காணும் எளிய பொருத்தமான உதாரணம்]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "⭐ முக்கிய குறிப்புகள்\n"
                    "• [முக்கிய புள்ளி 1]\n"
                    "• [முக்கிய புள்ளி 2]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "🌟 உங்களுக்குத் தெரியுமா?\n"
                    "[பாடத்திற்குப் பொருத்தமான ஒரு சுவாரசியமான அறிவியல் உண்மை (Did You Know)]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "💡 நினைவில் கொள்ளுங்கள்\n"
                    "[பாடத்தின் முக்கிய நினைவூட்டல்]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "🎯 கற்றல் குறிப்பு\n"
                    "[கருத்தை எளிதில் நினைவில் கொள்ள எளிய கற்றல் குறிப்பு]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "📖 புதிய சொல்\n"
                    "சொல்: [ஆங்கில கலைச்சொல்] | தமிழ்: [தமிழ்ச்சொல்] | விளக்கம்: [எளிய வரையறை]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "📝 பயிற்சி\n"
                    "[பயிற்சிக்கான ஒரு எளிய கேள்வி]\n"
                )

            system_prompt += (
                f"\nபதிலின் தொடக்கத்தில், ஆதாரத்தின் வலிமைக்கு ஏற்ப இந்த வாக்கியத்தை அச்சிடவும்:\n"
                f"வலிமையான தளம் எனில்: '{grounding_prefix_ta}'\n"
                f"குறைவான தளம் எனில்: '{grounding_prefix_ta}'\n"
                f"பதிலை எப்போதும் கனிவாகத் தொடங்கவும். பாடப்புத்தக விவரங்களைக் கடந்து கற்பனையாகப் பதிலளிக்கக் கூடாது."
            )

            user_message = (
                f"வழங்கப்பட்ட பாடப்புத்தகத் தரவு (Context):\n"
                f"----------------------\n"
                f"{context_text}\n"
                f"----------------------\n\n"
                f"கேள்வி: {query}"
            )
        else:
            # English Mode
            system_prompt = (
                f"You are TamilEdu-SLM, a supportive, patient, and friendly school teacher.\n"
                f"The student is in Grade {grade}. The student's learning level is: {learning_level}.\n\n"
                f"Rules:\n"
                f"1. Rely only on the textbook context. Speak as a human teacher. Never expose internal system details (chunks, embeddings, RAG, vector database, prompt templates, JSON).\n"
                f"2. Maintain positive reinforcement. If the student answers incorrectly or is confused, say: \"Good attempt! Let's solve it together.\"\n"
                f"3. Use standard mathematical and scientific notation wrapped in KaTeX ($...$ for inline, $$...$$ for block).\n"
                f"4. Use concrete real-life examples directly matching the concept:\n"
                f"   - Fractions: slices of pizza, cake, chocolate, water bottles, money, or distances.\n"
                f"   - Science: plants, animals, weather, home experiences, and daily-life electricity.\n\n"
            )

            if is_followup:
                system_prompt += (
                    "The student is asking a follow-up question or is confused. Do NOT output the full subject template. "
                    "Address their question directly, conversationally, and concisely as a teacher continuing a discussion.\n\n"
                )
            elif is_exam_mode:
                system_prompt += (
                    "Tutoring Mode: 📚 EXAM PREPARATION MODE\n"
                    "Response Format (EXACT TEMPLATE):\n"
                    "📘 Question\n"
                    "[The question asked]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "⭐ Key Points\n"
                    "[Core points necessary for exam scoring]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "💡 Remember\n"
                    "[Important mnemonics, formulas, or tips]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "⚠️ Common Mistake\n"
                    "[What students usually do wrong and how to avoid it]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "🎯 Learning Tip\n"
                    "[Simple learning strategy or memory tip]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "📝 Practice\n"
                    "[One board-exam style practice question]\n"
                )
            elif is_practice_mode:
                system_prompt += (
                    "Tutoring Mode: 📝 PRACTICE MODE\n"
                    "The student wants to practice. Generate 3 MCQs, 2 Fill-in-the-blanks, 1 True/False, and 1 short question. Do not show answers immediately.\n"
                )
            elif is_math:
                system_prompt += (
                    "Tutoring Mode: 📐 MATHEMATICS MODE\n"
                    "Note: For every calculation step, explain WHY the operation is performed (e.g. 'We add 7 to both sides because we want to remove -7 from the left side and keep the equation balanced').\n"
                    "Response Format (EXACT TEMPLATE):\n"
                    "📘 Question\n"
                    "[The problem to solve]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "🧠 Understand\n"
                    "[Brief description of what the problem asks and what method will be used]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "✏️ Step 1: [Step Title]\n"
                    "[Explanation of why we perform this step, along with the calculation]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "✏️ Step 2: [Step Title]\n"
                    "[Explanation and calculation]\n"
                    "(Add more steps as needed)\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "✅ Final Answer\n"
                    "[The final calculated value clearly highlighted]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "💡 Remember\n"
                    "[Key formula, rule, or concept]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "⚠️ Common Mistake\n"
                    "[What students often do wrong in this specific problem]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "🎯 Learning Tip\n"
                    "[Strategy to make calculations easier]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "📖 New Word\n"
                    "Word: [Word] | Tamil: [Tamil translation] | Meaning: [Simple definition]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "📝 Practice\n"
                    "[One similar practice question for the student to solve]\n"
                )
            else:
                system_prompt += (
                    "Tutoring Mode: 🔬 SCIENCE & THEORY MODE\n"
                    "Response Format (EXACT TEMPLATE):\n"
                    "📘 Question\n"
                    "[The question asked]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "📖 Definition\n"
                    "[Clear and simple definition of the concept]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "🔬 Explanation\n"
                    "[Age-appropriate breakdown with analogies]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "🌍 Real-Life Example\n"
                    "[A concrete everyday life example (e.g. plants, animals, weather, home)]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "⭐ Key Points\n"
                    "• [Core point 1]\n"
                    "• [Core point 2]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "🌟 Did You Know?\n"
                    "[An interesting science fact related to the topic]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "💡 Remember\n"
                    "[Important concept takeaway]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "🎯 Learning Tip\n"
                    "[Mnemonic or learning strategy]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "📖 New Word\n"
                    "Word: [Word] | Tamil: [Tamil translation] | Meaning: [Simple definition]\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "📝 Practice\n"
                    "[One simple review question]\n"
                )

            system_prompt += (
                f"\nPrefix your response with the following statement based on grounding confidence:\n"
                f"Confidence statement to use: '{grounding_prefix_en}'\n"
                f"Begin your explanation warmly. Do not hallucinate content outside the context."
            )

            user_message = (
                f"Provided Context:\n"
                f"----------------------\n"
                f"{context_text}\n"
                f"----------------------\n\n"
                f"Question: {query}"
            )

        return system_prompt, user_message

def meta_page(chunk: ChunkResult) -> str:
    return f"{chunk.page_number} (Section: {chunk.section_no})"
