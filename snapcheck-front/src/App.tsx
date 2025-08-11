import { useState, useEffect } from 'react'
import { QcService } from './api/services/QcService';
import './App.css'
import type { NoteModel, QualityControlModel } from './api';
import Sidebar from './pages/main/sidebar/sidebar';
import MainContent from './pages/main/main';

function App() {
    const [error, setError] = useState<string | null>(null);
    const [qc, setQc] = useState<QualityControlModel | null>(null);
    const [boardIndex, setBoardIndex] = useState<number>(0);
    const [hasChanged, setHasChanged] = useState<boolean>(false);
    const qcService = new QcService();

    const load = () => {
        qcService.qcGetFullQc().then((qc) => {
            setQc(qc);
            setError(null);
        }).catch((error) => {
            setError("Failed to load QC File");
        });
    };

    const onNoteChanged = (note: NoteModel) => {
        if (qc) {
            // const updatedNotes = qc.notes.map((n) => (n.id === note.id ? note : n));
            // setQc({ ...qc, notes: updatedNotes });
            setHasChanged(true);
        }
    };

    return (
        <div className='app'>
            <div className='sidebar-container'>
                <Sidebar 
                    qc={qc} 
                    onLoadRequest={load} 
                    hasChanged={hasChanged}
                    onBoardChange={(idx) => { setBoardIndex(idx); }} 
                    onNoteChanged={(note) => { if (onNoteChanged) onNoteChanged(note) }} 
                />
            </div>
            <div className="main-container">
                <MainContent qc={qc} error={error} boardIndex={boardIndex} />
            </div>
        </div>
    )
}

export default App
