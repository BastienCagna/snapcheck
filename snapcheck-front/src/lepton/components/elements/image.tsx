import React, { useEffect } from 'react';
import { OpenAPI } from '@lepton/api-client';

const ImageElementComponent: React.FC<{
    sessionId: string;
    snapId: string;
    src: string;
    style?: React.CSSProperties;
}> = ({ sessionId, snapId, src, style }) => {

    const [imageUrl, setImageUrl] = React.useState<string | null>(null);

    useEffect(() => {
        let url: string | null = null;
        const fetchImage = async () => {
            try {
                const response = await fetch(
                    `${OpenAPI.BASE}/snap/${sessionId}/${snapId}/image/${src}`,
                    {
                        method: 'GET',
                        headers: OpenAPI.HEADERS || {}
                    }
                );
                if (!response.ok) throw new Error('Image not found');
                const blob = await response.blob();
                url = URL.createObjectURL(blob);
                setImageUrl(url);
            } catch (error) {
                console.error('Error fetching image:', error);
                setImageUrl(null);
            }
        };
        fetchImage();
        // Cleanup function for useEffect
        return () => {
            if (url) {
                URL.revokeObjectURL(url);
            }
        };
    }, [sessionId, snapId, src]);

    return imageUrl ? (
        <img src={imageUrl} alt={src} style={style} />
    ) : (
        <div>Loading...</div>
    );
};


export default ImageElementComponent;


