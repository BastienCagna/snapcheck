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
import { useSnapSession } from '../../../contexts/SnapSessionContext';
import Toolbar from '../toolbar/toolbar';


function boardHasNote(board: BoardModel, note: NoteModel) {
    for (const intendedNote of board.intended_notes) {
        if (intendedNote.id === note.id) {
            return true;
        }
    }
    return false;
}

const FilesControl: React.FC<{
}> = () => {
    const [currentPath, setCurrentPath] = React.useState<string | null>(null);
    const { openSnap } = useSnapSession();

    return <div className="files-control-panel">
        <div className="panel-header">
            <h3>Files</h3>
            <div>
            </div>
        </div>
        <FilesBrowser
            path={currentPath}
            onPathChange={(p) => setCurrentPath(p)}
            onFileSelect={openSnap}
            extensions={[".snpk"]}
        />
    </div>
}

const QCControl: React.FC<{
    onNoteChanged?: (note: NoteModel) => void;
}> = ({onNoteChanged }) => {
    const { snap, currentBoard } = useSnapSession();
    const [showAllNotes, setShowAllNotes] = React.useState(true);

    return <div className="qc-control-panel">
        <div className="panel-header">
            <h3>Ratings</h3>
            <div>
                <InlineToggle
                    off="Board" on="All"
                    value={showAllNotes}
                    onChange={(value) => setShowAllNotes(value)} />
            </div>
        </div>

        {/* {qc && <NoteStatBar qc={qc} />} */}
        <div className="notes-list">
            {snap?.ratings?.filter((rating) => currentBoard && (showAllNotes || boardHasNote(currentBoard, rating))).map((rating) => (
                <NoteInput
                    key={rating.id}
                    note={rating}
                    onChange={(rating) => { if (onNoteChanged) onNoteChanged(rating) }}
                    highlight={(showAllNotes && currentBoard && boardHasNote(currentBoard, rating)) || false} />
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

const Sidebar: React.FC<{}> = ({ }) => {
    const { snap: qc, currentBoard, updateNote } = useSnapSession();
    const menuItems: Tab[] = [
        { title: <FileCopyIcon />, content: <FilesControl /> },
        { title: <EditNoteIcon />, content: <QCControl qc={qc} board={currentBoard} onNoteChanged={updateNote} /> },
        { title: <ViewListIcon />, content: <MetadataControl qc={qc} /> },
    ];

    return (
        <div className="sidebar">
            <Toolbar />
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