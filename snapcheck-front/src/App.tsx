import { useState, useEffect, useReducer } from 'react'
import './App.css'
import Sidebar from './pages/main/sidebar/sidebar';
import MainContent from './pages/main/main';
import Toolbar from './pages/main/toolbar/toolbar';
import { QCProvider } from './contexts/QCContext';

function App() {
    const [error, setError] = useState<string | null>(null);

    return (
        <div className='app'>
            <QCProvider>
                <div>
                    <Toolbar />
                </div>
                <div className="page-container">
                    <div className='sidebar-container'>
                        <Sidebar />
                    </div>
                    <div className="main-container">
                        <MainContent error={error} />
                    </div>
                </div>
            </QCProvider>
        </div>
    )
}

export default App
