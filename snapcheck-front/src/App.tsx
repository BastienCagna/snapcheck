import { useState, useEffect, useReducer } from 'react'
import './App.css'
import Sidebar from './pages/main/sidebar/sidebar';
import MainContent from './pages/main/main';
import Toolbar from './pages/main/toolbar/toolbar';
import { QCProvider } from './contexts/QCContext';
import TabSelector from './components/lib/tabSelector/tabSelector';
import Modal from './components/lib/modal/modal';
import { ModalProvider } from './contexts/ModalContext';

function App() {
    return (
        <div className='app'>
            <QCProvider>
                <ModalProvider>
                    <div className="page-container">
                        <div className='sidebar-container'>
                            <Sidebar />
                        </div>
                        <div className='main-container'>
                            <div className='toolbar-container'>
                                <TabSelector items={[
                                    { label: "Tab 1", onClick: () => { }, isActive: true },
                                ]} />
                            </div>
                            <div className="board-container">
                                <MainContent />
                            </div>
                        </div>
                        <div className='modal-container'>
                            <Modal />
                        </div>
                    </div>
                </ModalProvider>
            </QCProvider>        
        </div>
    )
}

export default App
