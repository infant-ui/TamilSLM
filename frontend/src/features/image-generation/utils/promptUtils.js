// Heuristic to detect if the user wants to generate an image
export const isImageGenerationPrompt = (text) => {
    const lowercaseText = text.toLowerCase();
    const imageKeywords = [
        'draw',
        'generate an image',
        'create a picture',
        'generate a diagram',
        'illustrate',
        'show a picture of',
        'create a poster',
        'create a diagram',
        'வரை' // Tamil for 'draw'
    ];

    return imageKeywords.some(keyword => lowercaseText.includes(keyword));
};

export const extractImagePrompt = (text) => {
    // Basic extraction - could be refined to remove the verb (e.g. "draw a cat" -> "a cat")
    return text.trim();
};
