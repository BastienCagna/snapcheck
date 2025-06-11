import React from 'react';
import './sidebar.css';
import Button from '../../../components/lib/button';
import NoteInput from '../../../components/noteinput';

import FileCopyIcon from '@mui/icons-material/FileCopy';
import EditNoteIcon from '@mui/icons-material/EditNote';
import ViewListIcon from '@mui/icons-material/ViewList';
import { type Tab, Tabs } from '../../../components/lib/tabs/tabs';
import DictionaryTable from '../../../components/lib/table/dictTable';
import type { QualityControlModel } from '../../../api';



const QCControl: React.FC<{
    qc: QualityControlModel | null;
    onBoardChange?: (boardId: string) => void;
}> = ({ qc }) => {
    return <div className="qc-control-panel">
        {
            qc?.boards?.length ? (
                <ul className='board-list'>
                    {qc.boards.map((board, index) => (
                        <li key={index}>
                            <Button>{board.title}</Button>
                        </li>
                    ))}
                </ul>
            ) : (
                <p className='default-text'>No boards available.</p>
            )
        }

        <h3>Notes</h3>
        {qc?.notes?.map((note) => (<NoteInput key={note.name} note={note} />))}
    </div>
}

const Sidebar: React.FC<{
    qc: QualityControlModel | null;
    onLoadRequest?: () => void;
    onBoardChange?: (boardId: string) => void;
}> = ({ qc, onLoadRequest, onBoardChange }) => {
    const menuItems: Tab[] = [
        { title: <FileCopyIcon />, content: <><h3>Coucou</h3></> },
        { title: <EditNoteIcon />, content: <QCControl qc={qc} onBoardChange={(idx) => { onBoardChange && onBoardChange(idx) }} /> },
        { title: <ViewListIcon />, content: <DictionaryTable dictionary={qc?.metadata || {}} /> },
    ];

    return (
        <div className="sidebar">
            <div className='sidebar-header'>
                <Button onClick={onLoadRequest}>Load</Button>
                <Button onClick={() => { }}>Save</Button>
                <Button onClick={() => { }}>Export</Button>
                <h2>{qc?.title || 'Untitled'}</h2>
            </div>
            <div className='sidebar-content'>
                <Tabs tabs={menuItems} />
            </div>
        </div>
    );
};

export default Sidebar;