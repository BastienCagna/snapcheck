import { useState, useEffect } from 'react'
import { QcService } from './api/services/QcService';
import './App.css'
import type { QualityControlModel } from './api';
import Sidebar from './pages/main/sidebar/sidebar';
import MainContent from './pages/main/main';

function App() {
    const [error, setError] = useState<string | null>(null);
    const [qc, setQc] = useState<QualityControlModel | null>(null);
    const qcService = new QcService();

    const load = () => {
        qcService.qcGetFullQc().then((qc) => {
            setQc(qc);
            setError(null);
        }).catch((error) => {
            setError("Failed to load QC File");
        });
    };

    return (
        <div className='app'>
            <div className='sidebar-container'>
                <Sidebar qc={qc} onLoadRequest={load} />
            </div>
            <div className="main-container">
                <MainContent qc={qc} error={error} />
            </div>
        </div>
    )
}

export default App
