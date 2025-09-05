import Sidebar from './pages/main/sidebar/sidebar';
import MainContent from './pages/main/main';
import Modal from './components/lib/modal/modal';
import { SnapSelector } from './pages/main/snapSelector';
import './App.css'
import { useSnapSession } from './contexts/SnapSessionContext';

function App() {
    const {showSidebar} = useSnapSession();
    return (
        <div className='app'>
            <div className="page-container">
                <div className='sidebar-container' style={{display: showSidebar ? "block" : "none"}}>
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
        </div>
    )
}

export default App
