import React, { useEffect } from 'react';
import { QcService } from '../../api';

const ImageComponent: React.FC<{
    src: string;
    style?: React.CSSProperties;
}> = ({ src, style }) => {

    useEffect(() => {
        const fetchImage = async () => {
            try {
                await QcService.qcGetImage(src);
            } catch (error) {
                console.error('Error fetching image:', error);
            }
        };

        fetchImage();
    }, [src]);
    return <img src={`http://127.0.0.1:8000/qc/image/` + src} alt={src} style={style} />;
};

export default ImageComponent;


