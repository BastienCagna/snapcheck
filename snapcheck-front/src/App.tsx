import { useState, useEffect } from 'react'
import { QcService } from './api/services/QcService';
import './App.css'
import type { QualityControlModel } from './api';
import Sidebar from './components/main/sidebar';
import MainContent from './components/main/main';

function App() {
    const [error, setError] = useState<string | null>(null);
    const [qc, setQc] = useState<QualityControlModel | null>(null);
    const qcService = new QcService();

    const load = () => {
        qcService.qcGetFullQc().then((qc) => {
            setQc(qc);
            setError(null);
        }).catch((error) => {
            setError("Failed to load QC File: " + error.message);
        });
    };

    return (
        <div className='app'>
            <div className='sidebar-container'><Sidebar qc={qc} onLoadRequest={load} /></div>
            <div className="main-container">
                <MainContent qc={qc} error={error} />
            </div>
        </div>
    )
}

export default App
