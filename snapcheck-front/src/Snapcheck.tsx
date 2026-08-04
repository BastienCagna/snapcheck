import Sidebar from './lepton/pages/main/sidebar/sidebar';
import MainContent from './lepton/pages/main/main';
import Modal from './lepton/components/lib/modal/modal';
import TopBar from './lepton/pages/main/topbar/topbar';
import { useEffect } from 'react';
import { useLObjectSession } from '@lepton/core/contexts/SessionContext';
import { ModalProvider } from '@lepton/core/contexts/ModalContext';
import { useAppUIState } from './contexts/AppUIStateContext';
import './Snapcheck.css'


const ShortCuts: React.FC<{
}> = () => {
    const { showSidebar, setState } = useAppUIState();
    const { saveLObject, saveLObjectAs, currentObject, closeLObject } = useLObjectSession();

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // ctrl+b toggle sidebar
            if (e.ctrlKey && e.key.toLowerCase() === "b") {
                e.preventDefault();
                setState({ showSidebar: !showSidebar });
            }

            // ctrl+s to save snap
            if (e.ctrlKey && e.key.toLowerCase() === "s") {
                e.preventDefault();
                if(currentObject && currentObject.id) {
                    saveLObject(currentObject.id);
                }
            }

            // ctrl+shift+s to save snap as
            if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === "s") {
                e.preventDefault();
                if(currentObject && currentObject.id) {
                    const newName = prompt("Enter the save path:");
                    if(newName) {
                        saveLObjectAs(currentObject.id, newName);
                    }
                }
            }

            // ctrl+w to close snap
            if (e.ctrlKey && e.key.toLowerCase() === "w") {
                e.preventDefault();
                if(currentObject && currentObject.id) {
                    const confirmClose = confirm("Are you sure you want to close the snap? Unsaved changes will be lost.");
                    if(confirmClose) {
                        closeLObject(currentObject.id);
                    }
                }
            }
        };
        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, []);

    return <></>
}

function SnapCheck() {
    // const { session, openLObject, currentLObjectPath } = useLObjectSession();
    const { showSidebar } = useAppUIState();
    return (
        <ModalProvider>
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
        </ModalProvider>
    );
}

export default SnapCheck
