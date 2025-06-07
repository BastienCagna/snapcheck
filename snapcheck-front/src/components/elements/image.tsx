import React, { useEffect } from 'react';
import { QcService } from '../../api';

const ImageComponent: React.FC<{
    src: string;
    style?: React.CSSProperties;
}> = ({ src, style }) => {
    const qcService = new QcService();

    useEffect(() => {
        const fetchImage = async () => {
            try {
                await qcService.qcGetImage(src);
            } catch (error) {
                console.error('Error fetching image:', error);
            }
        };

        fetchImage();
    }, [src]);
    return <img src={`http://127.0.0.1:8000/qc/image/` + src} alt={src} style={style} />;
};

export default ImageComponent;


