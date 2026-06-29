# services/retrieval-service/app/ingestion/chunker.py
import re
from typing import List, Dict, Any
from pydantic import BaseModel
from app.ingestion.logical_block_builder import LogicalBlock

class ChunkUnit(BaseModel):
    chunk_id: str
    text: str
    metadata: Dict[str, Any]

class ScienceChunker:
    def __init__(self, target_word_size: int = 500, overlap_word_size: int = 75):
        self.target_word_size = target_word_size
        self.overlap_word_size = overlap_word_size

    def clean_text(self, text: str) -> str:
        # Standard cleanups
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def get_word_count(self, text: str) -> int:
        return len(text.split())

    def format_chunk_text(self, path: str, content: str) -> str:
        """
        Formats chunk text with hierarchical context paths.
        """
        prefix = f"[Context: {path}]" if path else ""
        return f"{prefix}\n\n{content}".strip()

    def chunk_textbook_blocks(self, logical_blocks: List[LogicalBlock], doc_metadata: Dict[str, Any]) -> List[ChunkUnit]:
        """
        Textbook chunking logic. Iterates through logical blocks, grouping them
        until the word limit is reached. Prepends context headers.
        """
        chunks = []
        doc_id = doc_metadata.get("document_id", "unknown")
        
        current_blocks = []
        current_words = 0
        current_path = ""
        chunk_count = 0

        for l_block in logical_blocks:
            block_words = self.get_word_count(l_block.text)
            
            # If a single logical block (e.g. a huge table or activity) is larger than target_word_size,
            # we write out whatever was in the accumulator first, then split the huge block itself.
            if block_words > self.target_word_size:
                if current_blocks:
                    # Flush accumulated blocks
                    chunk_text = "\n\n".join(b.text for b in current_blocks)
                    formatted_text = self.format_chunk_text(current_path, chunk_text)
                    chunks.append(ChunkUnit(
                        chunk_id=f"{doc_id}_tb_{chunk_count}",
                        text=formatted_text,
                        metadata={**doc_metadata, "section_path": current_path, "content_role": "general"}
                    ))
                    chunk_count += 1
                    current_blocks = []
                    current_words = 0

                # Split the large block using overlap window
                words = l_block.text.split()
                idx = 0
                step = self.target_word_size - self.overlap_word_size
                while idx < len(words):
                    sub_words = words[idx : idx + self.target_word_size]
                    sub_text = " ".join(sub_words)
                    formatted_sub = self.format_chunk_text(l_block.section_path, sub_text)
                    
                    chunks.append(ChunkUnit(
                        chunk_id=f"{doc_id}_tb_{chunk_count}",
                        text=formatted_sub,
                        metadata={**doc_metadata, "section_path": l_block.section_path, "content_role": l_block.role}
                    ))
                    chunk_count += 1
                    idx += step
                continue

            # Check if adding this block exceeds target size or if section path changed
            if (current_words + block_words > self.target_word_size) or (current_path and l_block.section_path != current_path):
                if current_blocks:
                    # Flush accumulated blocks
                    chunk_text = "\n\n".join(b.text for b in current_blocks)
                    formatted_text = self.format_chunk_text(current_path, chunk_text)
                    chunks.append(ChunkUnit(
                        chunk_id=f"{doc_id}_tb_{chunk_count}",
                        text=formatted_text,
                        metadata={**doc_metadata, "section_path": current_path, "content_role": "general"}
                    ))
                    chunk_count += 1
                
                # Apply overlap from the tail of current_blocks if path is same
                if l_block.section_path == current_path:
                    # Keep the last block as overlap if it is small enough
                    last_block = current_blocks[-1] if current_blocks else None
                    if last_block and self.get_word_count(last_block.text) < self.overlap_word_size:
                        current_blocks = [last_block, l_block]
                        current_words = self.get_word_count(last_block.text) + block_words
                    else:
                        current_blocks = [l_block]
                        current_words = block_words
                else:
                    current_blocks = [l_block]
                    current_words = block_words
                    
                current_path = l_block.section_path
            else:
                current_blocks.append(l_block)
                current_words += block_words
                if not current_path:
                    current_path = l_block.section_path

        # Flush any remaining blocks
        if current_blocks:
            chunk_text = "\n\n".join(b.text for b in current_blocks)
            formatted_text = self.format_chunk_text(current_path, chunk_text)
            chunks.append(ChunkUnit(
                chunk_id=f"{doc_id}_tb_{chunk_count}",
                text=formatted_text,
                metadata={**doc_metadata, "section_path": current_path, "content_role": "general"}
            ))

        return chunks

    def chunk_guide_qa(self, text: str, doc_metadata: Dict[str, Any]) -> List[ChunkUnit]:
        """
        Guide chunking logic. Splitting is done strictly on Q&A block boundaries
        to preserve complete question and answer pairs.
        """
        # Split on typical guide Q&A markers
        qa_pattern = re.compile(
            r"(?=(?:Question|Q\d+|கேள்வி|\d+\.\s+)\s*:?)", 
            re.IGNORECASE
        )
        raw_qa_blocks = qa_pattern.split(text)
        chunks = []
        doc_id = doc_metadata.get("document_id", "unknown")
        chunk_count = 0

        for block in raw_qa_blocks:
            cleaned = self.clean_text(block)
            if len(cleaned) < 30: # Skip small noise artifacts
                continue
                
            block_words = self.get_word_count(cleaned)
            
            # If Q&A block exceeds target size, split recursively but prefix question
            if block_words > self.target_word_size:
                # Extract the question prefix (usually the first sentence/line)
                lines = cleaned.split("\n")
                question_prefix = lines[0] if lines else "Question"
                
                words = cleaned.split()
                sub_idx = 0
                step = self.target_word_size - self.overlap_word_size
                while sub_idx < len(words):
                    sub_words = words[sub_idx : sub_idx + self.target_word_size]
                    sub_text = " ".join(sub_words)
                    
                    if sub_idx > 0:
                        sub_text = f"[Parent Question: {question_prefix}]\n\n(Continued) {sub_text}"
                        
                    chunks.append(ChunkUnit(
                        chunk_id=f"{doc_id}_gd_{chunk_count}",
                        text=sub_text,
                        metadata={**doc_metadata, "content_role": "exercise"}
                    ))
                    chunk_count += 1
                    sub_idx += step
            else:
                chunks.append(ChunkUnit(
                    chunk_id=f"{doc_id}_gd_{chunk_count}",
                    text=cleaned,
                    metadata={**doc_metadata, "content_role": "exercise"}
                ))
                chunk_count += 1

        return chunks
