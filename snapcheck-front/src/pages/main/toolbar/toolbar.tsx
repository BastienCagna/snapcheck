import Menu from "../../../components/lib/menu/menu";
import ServerContent from "../../../components/lib/serverContent";
import { useAppData } from "../../../contexts/AppDataContext";
import { useModal } from "../../../contexts/ModalContext";
import { useSnapSession } from "../../../contexts/SnapSessionContext";
import DebugPage from "../../debug/debug";
import SettingsPage from "../../settings/settings";
import "./toolbar.css";

const Toolbar: React.FC<{
}> = () => {
    const { snap, openSnap, currentBoard, closeCurrentSnap } = useSnapSession();
    const { showModal } = useModal();
    const { history } = useAppData();

    const openFile = () => {
        const input = document.createElement("input");
        input.type = "file";
        input.onchange = (e: any) => {
            const file = e.target.files?.[0];
            if (file) {
                // Traitez le fichier ici, par exemple :
                // const reader = new FileReader();
                // reader.onload = (event) => { ... };
                // reader.readAsText(file);
                console.log("user selected:", file.path, file)
                openSnap(file.path);
            }
        };
        input.click();
    }

    return (
        <div className="toolbar">
            <div>
                <Menu items={[
                    {label: "File", children: [  
                        { label: "Open file...", onClick: openFile },
                        { 
                            label: "Open recent...", 
                            children: history && history.length > 0 
                                ? history.map(file => ({
                                    label: file.length > 20 ? `...${file.slice(-20)}` : file,
                                    onClick: () => openSnap(file)
                                })) 
                                : [{ label: "No recent files", disabled: true }] 
                        },
                        { type: "separator" },
                        { label: "Reload", onClick: openSnap, disabled: !snap },
                        { label: "Save", onClick: () => { }, disabled: !snap?.has_changed },
                        { label: "Save As...", onClick: () => { }, disabled: !snap?.has_changed },
                        { label: "Close", onClick:closeCurrentSnap, disabled: !snap},
                        { label: "Close All", onClick: () => { }, disabled: !snap},
                        { type: "separator" },
                        { label: "Export to PDF", onClick: () => { }, disabled: !snap },
                        { label: "Export to HTML", onClick: () => { }, disabled: !snap },
                        { type: "separator" },
                        {label: "Settings...", onClick: () => { showModal(<SettingsPage />)}},
                        { type: "separator" },
                        { label: "Quit", onClick: () => { }}
                    ]},
                    {label: "Edit", children: [
                        { label: "Cancel", onClick: () => { }, disabled: !snap?.is_cancellable },
                        { label: "Redo", onClick: () => { }, disabled: !snap?.is_redoable }
                    ]},
                    {label: "View", children: [
                        { label: "Show Sidebar", onClick: () => { } },
                        {label: "Show this board in all files", onClick: () => {}, disabled: !snap || !currentBoard}
                    ]},
                    {label: "More", children: [
                        { label: "About", onClick: () => { showModal(<ServerContent path="about.html" />) }},
                        { label: "Debug", onClick: () => { showModal(<DebugPage />) }},
                    ]},
                ]} />
            </div>
        </div>
    );
};

export default Toolbar;