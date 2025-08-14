import React from 'react';
import Button from '../../../components/lib/button';
import NoteInput from '../../../components/specials/noteinput/noteinput';

import FileCopyIcon from '@mui/icons-material/FileCopy';
import EditNoteIcon from '@mui/icons-material/EditNote';
import ViewListIcon from '@mui/icons-material/ViewList';
import { type Tab, Tabs } from '../../../components/lib/tabs/tabs';
import DictionaryTable from '../../../components/lib/table/dictTable';
import type { NoteModel, QualityControlModel, BoardModel } from '../../../api';
import InlineToggle from '../../../components/lib/inlineToggle';
import NoteStatBar from '../../../components/specials/notestatbar/notestatbar';
import FilesBrowser from '../../../components/files/browser/browser';
import './sidebar.css';


function boardHasNote(board: BoardModel, note: NoteModel) {
    for (const intendedNote of board.intended_notes) {
        if (intendedNote.id === note.id) {
            return true;
        }
    }
    return false;
}

const FilesControl: React.FC<{
    qc: QualityControlModel | null;
}> = ({ qc }) => {
    const [currentPath, setCurrentPath] = React.useState<string | null>(null);

    return <div className="files-control-panel">
        <div className="panel-header">
            <h3>Files</h3>
            <div>
            </div>
        </div>
        <FilesBrowser
            path={currentPath}
            onPathChange={(p) => setCurrentPath(p)}
            onFileSelect={(f) => console.log(f)}
            extensions={[".snpk"]}
        />
    </div>
}

const QCControl: React.FC<{
    qc: QualityControlModel | null;
    board: BoardModel | null;
    onNoteChanged?: (note: NoteModel) => void;
}> = ({ qc, board, onNoteChanged }) => {
    const [showAllNotes, setShowAllNotes] = React.useState(true);

    return <div className="qc-control-panel">
        <div className="panel-header">
            <h3>Notes</h3>
            <div>
                <InlineToggle
                    off="Board" on="All"
                    value={showAllNotes}
                    onChange={(value) => setShowAllNotes(value)} />
            </div>
        </div>

        {qc && <NoteStatBar qc={qc} />}
        <div className="notes-list">
            {qc?.notes?.filter((note) => board && (showAllNotes || boardHasNote(board, note))).map((note) => (
                <NoteInput
                    key={note.id}
                    note={note}
                    onChange={(note) => { if (onNoteChanged) onNoteChanged(note) }}
                    highlight={(showAllNotes && board && boardHasNote(board, note)) || false} />
            ))}
        </div>
    </div>
}


const MetadataControl: React.FC<{
    qc: QualityControlModel | null;
}> = ({ qc }) => {

    return <div className="metadata-control-panel">
        <div className="panel-header">
            <h3>Metadata</h3>
            <div>
            </div>
        </div>
        <div className="">
            <DictionaryTable dictionary={qc?.metadata || {}} />
        </div>
    </div>
}

const Sidebar: React.FC<{
    qc: QualityControlModel | null;
    currentBoard: BoardModel | null;
    onLoadRequest?: () => void;
    onNoteChanged?: (note: NoteModel) => void;
}> = ({ qc, onLoadRequest, currentBoard, onNoteChanged }) => {
    const menuItems: Tab[] = [
        { title: <FileCopyIcon />, content: <FilesControl qc={qc} /> },
        { title: <EditNoteIcon />, content: <QCControl qc={qc} board={currentBoard} onNoteChanged={(note) => { if (onNoteChanged) onNoteChanged(note) }} /> },
        { title: <ViewListIcon />, content: <MetadataControl qc={qc} /> },
    ];

    return (
        <div className="sidebar">
            <div className='sidebar-header'>
            </div>
            <div className='sidebar-content'>
                <Tabs tabs={menuItems} />
            </div>
            <div>
            </div>
        </div>
    );
};

export default Sidebar;