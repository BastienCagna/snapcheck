import React from 'react';

const DefaultElementComponent: React.FC<{
    style?: React.CSSProperties;
    content?: React.ReactNode;
    contentIsHtml?: boolean;
}> = ({ style, content, contentIsHtml = false }) => {
    if (contentIsHtml && typeof content === 'string') {
        return <div style={style} dangerouslySetInnerHTML={{ __html: content }} />;
    }

    return <div style={style}>{content}</div>
};


export default DefaultElementComponent;


