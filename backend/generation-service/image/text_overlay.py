import os
import re
from PIL import Image, ImageDraw, ImageFont

COORDINATE_MAP = {
    "human heart": {
        "aorta": (0.5, 0.25),
        "superior vena cava": (0.35, 0.3),
        "pulmonary artery": (0.6, 0.35),
        "right atrium": (0.35, 0.5),
        "right ventricle": (0.4, 0.7),
        "left atrium": (0.65, 0.5),
        "left ventricle": (0.6, 0.7),
        "inferior vena cava": (0.4, 0.85),
    },
    "human eye": {
        "cornea": (0.15, 0.5),
        "pupil": (0.25, 0.5),
        "lens": (0.35, 0.5),
        "iris": (0.25, 0.4),
        "retina": (0.75, 0.5),
        "optic nerve": (0.85, 0.5),
        "sclera": (0.5, 0.25),
        "macula": (0.75, 0.6)
    },
    "plant cell": {
        "cell wall": (0.15, 0.5),
        "cell membrane": (0.2, 0.5),
        "nucleus": (0.5, 0.5),
        "vacuole": (0.65, 0.4),
        "chloroplast": (0.35, 0.3),
        "mitochondria": (0.4, 0.75),
        "mitochondrion": (0.4, 0.75),
        "cytoplasm": (0.5, 0.7),
        "golgi apparatus": (0.6, 0.6)
    }
}

def extract_english_key(label: str) -> str:
    """Extracts the English term for dictionary matching."""
    match = re.search(r'\((.*?)\)', label)
    if match:
        return match.group(1).lower().strip()
    return label.lower().strip()

def add_legend_to_image(base_image_path: str, labels: list[str], subject: str = "unknown", language: str = "bilingual") -> str:
    """
    Takes an image, and if the subject is supported, draws labels with leader lines over it.
    If unsupported, falls back to appending a legend below the image.
    """
    if not labels:
        return base_image_path

    try:
        base_img = Image.open(base_image_path)
    except Exception as e:
        print(f"Error opening image for overlay: {e}")
        return base_image_path

    width, height = base_img.size
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "NotoSansTamil-Regular.ttf")
    
    font_size = max(16, int(width * 0.03)) 
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("Warning: NotoSansTamil not found. Falling back to default font. Tamil may not render correctly.")
        font = ImageFont.load_default()
        font_size = 16

    # Check if subject is supported
    subject_key = subject.lower().strip()
    
    # Simple heuristic to match subject to coordinate map
    matched_map = None
    for k in COORDINATE_MAP.keys():
        if k in subject_key or subject_key in k:
            matched_map = COORDINATE_MAP[k]
            break

    if not matched_map:
        # Fallback to standard legend
        return _draw_fallback_legend(base_img, base_image_path, labels, font, font_size, width, height, font_path)

    # Supported subject: Draw overlay labels with leader lines
    draw = ImageDraw.Draw(base_img)
    
    left_labels = []
    right_labels = []
    
    for label in labels:
        eng_key = extract_english_key(label)
        # Attempt to match with coordinate map
        coord = None
        for k, v in matched_map.items():
            if k in eng_key or eng_key in k:
                coord = v
                break
                
        if not coord:
            # If a specific part isn't in map, default to the right side near bottom
            coord = (0.5, 0.9)
            
        x_rel, y_rel = coord
        x_abs = int(x_rel * width)
        y_abs = int(y_rel * height)
        
        # Categorize to left or right margin
        if x_rel < 0.5:
            left_labels.append({"text": label, "target": (x_abs, y_abs), "y_rel": y_rel})
        else:
            right_labels.append({"text": label, "target": (x_abs, y_abs), "y_rel": y_rel})

    # Sort vertically to prevent collisions
    left_labels.sort(key=lambda item: item["y_rel"])
    right_labels.sort(key=lambda item: item["y_rel"])
    
    def get_text_bbox(text):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    line_spacing = font_size + 20
    margin = int(width * 0.02)
    
    # Process left labels
    current_y = margin
    for item in left_labels:
        tw, th = get_text_bbox(item["text"])
        target_y = max(current_y, int(item["target"][1] - th/2))
        
        # Text position
        x_text = margin
        y_text = target_y
        
        # Draw background rectangle for readability
        draw.rectangle([x_text - 5, y_text - 5, x_text + tw + 5, y_text + th + 5], fill="white", outline="black")
        draw.text((x_text, y_text), item["text"], fill="black", font=font)
        
        # Draw leader line from right edge of text box to target
        line_start = (x_text + tw + 5, y_text + th // 2)
        draw.line([line_start, item["target"]], fill="black", width=2)
        
        current_y = y_text + th + line_spacing

    # Process right labels
    current_y = margin
    for item in right_labels:
        tw, th = get_text_bbox(item["text"])
        target_y = max(current_y, int(item["target"][1] - th/2))
        
        # Text position
        x_text = width - margin - tw
        y_text = target_y
        
        draw.rectangle([x_text - 5, y_text - 5, x_text + tw + 5, y_text + th + 5], fill="white", outline="black")
        draw.text((x_text, y_text), item["text"], fill="black", font=font)
        
        # Draw leader line from left edge of text box to target
        line_start = (x_text - 5, y_text + th // 2)
        draw.line([line_start, item["target"]], fill="black", width=2)
        
        current_y = y_text + th + line_spacing

    base_img.save(base_image_path)
    return base_image_path


def _draw_fallback_legend(base_img, path, labels, font, font_size, width, height, font_path):
    padding = 20
    line_spacing = font_size + 10
    legend_height = padding * 2 + (len(labels) * line_spacing) + 40

    new_img = Image.new("RGB", (width, height + legend_height), "white")
    new_img.paste(base_img, (0, 0))

    draw = ImageDraw.Draw(new_img)
    y_text = height + padding
    x_text = padding

    title_font_size = max(18, int(width * 0.035))
    try:
        title_font = ImageFont.truetype(font_path, title_font_size)
    except IOError:
        title_font = font
        
    draw.text((x_text, y_text), "Legend / குறிப்பு:", fill="black", font=title_font)
    y_text += title_font_size + 15

    for i, label in enumerate(labels, 1):
        text = f"{i}. {label}"
        draw.text((x_text, y_text), text, fill="black", font=font)
        y_text += line_spacing

    new_img.save(path)
    return path
