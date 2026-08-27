// ⚠️ DEAD CODE / DO NOT WIRE UP AS-IS: nothing in the app currently imports this
// module (verified: no references to `generateImage` from this file anywhere in
// src/App.js or src/components). generation-service's /generate/image endpoint
// requires an `x-generation-service-admin-key` header (see backend/generation-service
// /app.py). That key must never be shipped to the browser -- any REACT_APP_* env var
// is baked in plaintext into the public JS bundle, so adding the admin key here would
// leak it to every visitor. The actual, safe image-generation path is the gateway's
// SSE branch in App.js, where the admin key is attached server-side. If this module
// is ever revived, it must call the gateway (no secret needed client-side), not
// generation-service directly.
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
