import React, { useEffect, useState } from 'react';
import { FilesService, type DirectoryItemModel, type DirectoryModel } from '../../../api';


import './browser.css';
import { Folder } from '@mui/icons-material';

const FilesBrowser: React.FC<{
    path: string | null
    extensions?: string[];
    onFileSelect?: (file: string) => void;
    onPathChange?: (path: string | null) => void;
}> = ({ path, extensions, onFileSelect, onPathChange }) => {
    const [isLoading, setIsLoading] = useState(false);
    const [directory, setDirectory] = useState<DirectoryModel | null>(null);

    useEffect(() => {
        const fetchFiles = async () => {
            setIsLoading(true);
            const directory = await FilesService.filesListDirectory(path || undefined, extensions);
            setDirectory(directory);
            setIsLoading(false);
        };

        fetchFiles();
    }, [path]);

    const handleFileSelect = (item: DirectoryItemModel) => {
        if (item.isdir) {
            if (onPathChange) {
                onPathChange(item.path);
            }
        }
        else if (onFileSelect) {
            onFileSelect(item.path);
        }
    };

    const goto = (p: string | null) => {
        if (onPathChange) {
            onPathChange(p);
        }
    };

    return <div>
        <span>{path}</span>
        {
            directory && (
                <ul className="files-browser-items">
                    {directory.parent != undefined && directory.parent != null && (
                        <li onClick={() => goto(directory.parent)}>
                            ..
                        </li>
                    )}
                    {directory?.content.map(item => (
                        <li
                            key={item.path}
                            onClick={() => { if (item.isdir) goto(item.path) }}
                            onDoubleClick={() => { if (!item.isdir) handleFileSelect(item) }}
                            className={item.isdir ? 'fb-dir-item' : ''}
                        >
                            {item.isdir && <Folder className='fb-item-icon' />} 
                            <span>{item.filename}</span>
                        </li>
                    ))}
                </ul>
            )
        }
    </div>
};

export default FilesBrowser;