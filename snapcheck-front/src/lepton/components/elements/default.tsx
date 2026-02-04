import React from 'react';

const DefaultElementComponent: React.FC<{
    style?: React.CSSProperties;
    content?: React.ReactNode;
}> = ({ style, content }) => {
    return <div style={style}>{content}</div>
};


export default DefaultElementComponent;


