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
            block_header = f"--- Textbook Reference [{idx+1}] | Source: {c.source_filename} | Page: {meta_page(c)} | Chapter: {c.chapter_title} ---"
            context_blocks.append(f"{block_header}\n{c.text}")
        return "\n\n".join(context_blocks)

    def build_prompt(self, query: str, chunks: List[ChunkResult]) -> tuple[str, str]:
        """
        Selects language-specific system prompt and constructs context boundaries.
        Returns a tuple (system_prompt, user_message).
        """
        lang = self.detect_language(query)
        context_text = self.build_context_text(chunks)

        if lang == "tamil":
            system_prompt = (
                "நீங்கள் ஒரு திறமையான அறிவியல் ஆசிரியர். கீழே வழங்கப்பட்டுள்ள பாடப்புத்தகத் தரவை (Context) மட்டுமே "
                "அடிப்படையாகக் கொண்டு மாணவரின் கேள்விக்கு பதிலளிக்கவும்.\n"
                "பதிலளிப்பதற்கான விதிகள்:\n"
                "1. வழங்கப்பட்ட தகவலில் இருந்து மட்டுமே பதிலளிக்கவும். உங்கள் சொந்த அறிவிலிருந்து எதையும் சேர்க்க வேண்டாம்.\n"
                "2. கேள்விக்கான விடை வழங்கப்பட்ட தகவலில் இல்லை எனில், \"விடை பாடப்புத்தகத்தில் இல்லை\" என்று மட்டும் கூறவும். பொய் தகவலை உருவாக்க வேண்டாம்.\n"
                "3. பதிலின் இறுதியில் ஆதாரத்தை [ஆதாரம்: நூல் பெயர், பக்கம் X] என துல்லியமாக குறிப்பிடவும்.\n"
                "4. பதிலைத் தெளிவான தமிழ் மொழியில் விளக்கவும்."
            )
            user_message = (
                f"வழங்கப்பட்ட பாடப்புத்தகத் தரவு (Context):\n"
                f"----------------------\n"
                f"{context_text}\n"
                f"----------------------\n\n"
                f"கேள்வி: {query}"
            )
        else:
            system_prompt = (
                "You are an expert science tutor. Answer the student's question using ONLY the provided textbook context.\n"
                "Instructions:\n"
                "1. Ground your answer strictly in the context. Do not add outside knowledge or assumptions.\n"
                "2. If the context does not contain the answer, reply with: \"The requested information is not available in the textbook.\" Do not make up information.\n"
                "3. Cite sources at the end of your answer in the format: [Source: filename, Page X].\n"
                "4. Output your response in clear, grammatical English."
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
    # Dynamically extract and return the page number and section number
    return f"{chunk.page_number} (Section: {chunk.section_no})"
