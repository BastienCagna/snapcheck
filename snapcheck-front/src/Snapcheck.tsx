import Sidebar from './lepton/pages/main/sidebar/sidebar';
import MainContent from './lepton/pages/main/main';
import Modal from './lepton/components/lib/modal/modal';
import { useSnapSession } from './lepton/contexts/SnapSessionContext';
import TopBar from './lepton/pages/main/topbar/topbar';
import { useEffect } from 'react';
import './Snapcheck.css'


const ShortCuts: React.FC<{
}> = () => {
    const { snap, toggleShowSidebar } = useSnapSession();

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // ctrl+b toggle sidebar
            if (e.ctrlKey && e.key.toLowerCase() === "b") {
                e.preventDefault();
                toggleShowSidebar();
            }
        };
        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [snap]);

    return <></>
}

function SnapCheck() {
    const { showSidebar } = useSnapSession();
    return (
        <div className='app'>
            <ShortCuts />
            <div className='app-topbar'>
                <TopBar />
            </div>
            <div className="page-container">
                <div className='sidebar-container' style={{ display: showSidebar ? "block" : "none" }}>
                    <Sidebar />
                </div>
                <div className='main-container'>
                    <div className="board-container">
                        <MainContent />
                    </div>
                    <div className='modal-container'>
                        <Modal />
                    </div>
                </div>
            </div>
        </div>
    )
}

export default SnapCheck
