import os
from PIL import Image, ImageDraw, ImageFont

def add_legend_to_image(base_image_path: str, labels: list[str]) -> str:
    """
    Takes an image, appends a white canvas at the bottom, and draws the labels
    as a numbered legend using Noto Sans Tamil.
    Returns the path to the updated image.
    """
    if not labels:
        return base_image_path

    # Load base image
    try:
        base_img = Image.open(base_image_path)
    except Exception as e:
        print(f"Error opening image for overlay: {e}")
        return base_image_path

    width, height = base_img.size

    # Load Tamil Font
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "NotoSansTamil-Regular.ttf")
    
    # Try loading font, fallback to default if not found
    try:
        # Standardize font size relative to image width, bounded min/max
        font_size = max(16, int(width * 0.03)) 
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("Warning: NotoSansTamil not found. Falling back to default font. Tamil may not render correctly.")
        font = ImageFont.load_default()
        font_size = 16

    # Calculate required height for the legend
    padding = 20
    line_spacing = font_size + 10
    legend_height = padding * 2 + (len(labels) * line_spacing) + 40 # extra for title

    # Create new image with extra height
    new_img = Image.new("RGB", (width, height + legend_height), "white")
    new_img.paste(base_img, (0, 0))

    # Draw text
    draw = ImageDraw.Draw(new_img)
    y_text = height + padding
    x_text = padding

    # Title for legend
    title_font_size = max(18, int(width * 0.035))
    try:
        title_font = ImageFont.truetype(font_path, title_font_size)
    except IOError:
        title_font = font
        
    draw.text((x_text, y_text), "Legend / குறிப்பு:", fill="black", font=title_font)
    y_text += title_font_size + 15

    # Draw each label
    for i, label in enumerate(labels, 1):
        text = f"{i}. {label}"
        draw.text((x_text, y_text), text, fill="black", font=font)
        y_text += line_spacing

    # Save and overwrite the original file
    new_img.save(base_image_path)
    return base_image_path
