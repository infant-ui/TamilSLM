# services/retrieval-service/app/ingestion/logical_block_builder.py
from typing import List, Dict, Any
from app.ingestion.layout_analyzer import LayoutBlock

class LogicalBlock:
    def __init__(self, blocks: List[LayoutBlock], role: str, section_path: str):
        self.blocks = blocks
        self.role = role  # "definition", "example", "exercise", "activity", "general"
        self.section_path = section_path

    @property
    def text(self) -> str:
        return "\n".join(b.text for b in self.blocks)

    @property
    def bboxes(self) -> List[tuple]:
        return [b.bbox for b in self.blocks]

class LogicalBlockBuilder:
    def __init__(self):
        pass

    def build_logical_blocks(self, section_annotated_blocks: List[Dict[str, Any]]) -> List[LogicalBlock]:
        """
        Groups adjacent layout blocks that are semantically connected.
        e.g., definition banners + description, worked examples + formula blocks, list elements.
        """
        logical_blocks = []
        current_group = []
        current_role = "general"
        current_path = ""

        role_keywords = {
            "definition": ["வரையறை", "definition", "விதி", "law"],
            "example": ["எடுத்துக்காட்டு", "worked example", "தீர்க்கப்பட்ட கணக்கு", "தீர்வு"],
            "exercise": ["பயிற்சி", "exercise", "மதிப்பீடு", "evaluation", "கேள்வி-பதில்"],
            "activity": ["செயல்பாடு", "activity", "ஆராய்ந்து அறிக"]
        }

        def get_block_role(text: str) -> str:
            text_lower = text.lower()
            # If short title contains keywords
            if len(text_lower) < 60:
                for role, keywords in role_keywords.items():
                    if any(kw in text_lower for kw in keywords):
                        return role
            return "general"

        for item in section_annotated_blocks:
            block = item["block"]
            path = item["section_path"]
            
            block_role = get_block_role(block.text)
            
            # If we detect a new special educational unit starts, close the previous logical block
            if block_role != "general" and block_role != current_role:
                if current_group:
                    logical_blocks.append(LogicalBlock(current_group, current_role, current_path))
                current_group = [block]
                current_role = block_role
                current_path = path
                continue
                
            # If the path changed substantially or block type is structural heading, close previous block
            if block.type == "heading" or (current_path and path != current_path):
                if current_group:
                    logical_blocks.append(LogicalBlock(current_group, current_role, current_path))
                current_group = [block]
                current_role = block_role if block_role != "general" else "general"
                current_path = path
                continue
                
            # Otherwise, append to existing group
            current_group.append(block)
            if current_role == "general" and block_role != "general":
                current_role = block_role
            if not current_path:
                current_path = path

        # Append final group
        if current_group:
            logical_blocks.append(LogicalBlock(current_group, current_role, current_path))

        return logical_blocks
