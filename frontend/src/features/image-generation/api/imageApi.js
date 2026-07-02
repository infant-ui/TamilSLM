const API_BASE_URL = process.env.REACT_APP_GENERATION_SERVICE_URL || 'http://localhost:8001';

export const generateImage = async (prompt, size, numImages, style, educationMode) => {
    const response = await fetch(`${API_BASE_URL}/generate/image`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            prompt,
            size,
            num_images: numImages,
            style,
            education_mode: educationMode
        })
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to generate image');
    }

    const data = await response.json();
    
    // Resolve relative URLs to absolute based on backend host
    if (data.images && Array.isArray(data.images)) {
        data.images = data.images.map(url => `${API_BASE_URL}${url}`);
    }
    
    return data;
};
