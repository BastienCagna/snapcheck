import Sidebar from './lepton/pages/main/sidebar/sidebar';
import MainContent from './lepton/pages/main/main';
import Modal from './lepton/components/lib/modal/modal';
import TopBar from './lepton/pages/main/topbar/topbar';
import { useEffect } from 'react';
import { useLObjectSession } from '@lepton/core/contexts/SessionContext';
import './Snapcheck.css'
import { useAppUIState } from './contexts/AppUIStateContext';


const ShortCuts: React.FC<{
}> = () => {
    const { showSidebar, setState } = useAppUIState();

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // ctrl+b toggle sidebar
            if (e.ctrlKey && e.key.toLowerCase() === "b") {
                e.preventDefault();
                setState({ showSidebar: !showSidebar });
            }
        };
        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    });

    return <></>
}

function SnapCheck() {
    // const { session, openLObject, currentLObjectPath } = useLObjectSession();
    const { showSidebar } = useAppUIState();
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
                    {/* <div className='modal-container'>
                        <Modal />
                    </div> */}
                </div>
            </div>

        </div>
    )
}

export default SnapCheck
