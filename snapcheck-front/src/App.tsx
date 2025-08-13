import { useState, useEffect } from 'react'
import { QcService } from './api/services/QcService';
import './App.css'
import type { NoteModel, QualityControlModel } from './api';
import Sidebar from './pages/main/sidebar/sidebar';
import MainContent from './pages/main/main';
import Toolbar from './pages/main/toolbar/toolbar';

function App() {
    const [error, setError] = useState<string | null>(null);
    const [qc, setQc] = useState<QualityControlModel | null>(null);
    const [boardIndex, setBoardIndex] = useState<number>(0);
    const qcService = new QcService();

    const load = () => {
        qcService.qcGetFullQc().then((qc) => {
            setQc(qc);
            setError(null);
        }).catch((error) => {
            setError("Failed to load QC File");
        });
    };

    const handleNoteChange = (note: NoteModel) => {
        qcService.qcUpdateNote(note).then(() => {
            setQc((prevQc) => {
                if (!prevQc || !prevQc.notes) return null;
                const updatedNotes = prevQc.notes.map((n) => (n.id === note.id ? note : n));
                return { ...prevQc, notes: updatedNotes };
            });
        });
    }

    return (
        <div className='app'>
            <div>
                <Toolbar qc={qc}
                    onLoadRequest={load} />
            </div>
            <div className="page-container">
                <div className='sidebar-container'>
                    <Sidebar
                        qc={qc}
                        onLoadRequest={load}
                        currentBoard={qc?.boards ? qc.boards[boardIndex] : null}
                        onNoteChanged={(note) => { handleNoteChange(note) }}
                    />
                </div>
                <div className="main-container">
                    <MainContent qc={qc} error={error} boardIndex={boardIndex} onBoardChange={(index) => setBoardIndex(index)} />
                </div>
            </div>
        </div>
    )
}

export default App
