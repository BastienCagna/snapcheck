import React, { useEffect, useState } from 'react';
import { ContentService } from '../../api';

type ServerContentProps = {
    path: string;
    className?: string;
};

const ServerContent: React.FC<ServerContentProps> = ({ path, className }) => {
    const [html, setHtml] = useState<string>('');
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let isMounted = true;
        ContentService.getStaticContent(path)
            .then((data) => {
                if (isMounted) setHtml(data.content);
            })
            .catch((err) => {
                if (isMounted) setError(err.message);
            });
        return () => {
            isMounted = false;
        };
    }, [path]);

    if (error) return <div className={className}>Error : {error}</div>;
    if (!html) return <div className={className}>Loading...</div>;

    return (
        <div
            className={className}
            dangerouslySetInnerHTML={{ __html: html }}
        />
    );
};

export default ServerContent;