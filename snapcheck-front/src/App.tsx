import Sidebar from './pages/main/sidebar/sidebar';
import MainContent from './pages/main/main';
import { SnapSessionProvider } from './contexts/SnapSessionContext';
import Modal from './components/lib/modal/modal';
import { ModalProvider } from './contexts/ModalContext';
import { SnapSelector } from './pages/main/snapSelector';
import { SettingsProvider } from './contexts/SettingsContext';
import './App.css'

function App() {
    return (
        <div className='app'>
            <SettingsProvider>
                <SnapSessionProvider>
                    <ModalProvider>
                        <div className="page-container">
                            <div className='sidebar-container'>
                                <Sidebar />
                            </div>
                            <div className='main-container'>
                                <div className='toolbar-container'>
                                    <SnapSelector />
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
                </SnapSessionProvider>       
            </SettingsProvider> 
        </div>
    )
}

export default App
