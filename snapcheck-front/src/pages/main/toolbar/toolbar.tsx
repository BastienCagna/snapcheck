import Menu from "../../../components/lib/menu/menu";
import ServerContent from "../../../components/lib/serverContent";
import { useModal } from "../../../contexts/ModalContext";
import { useSnapSession } from "../../../contexts/SnapSessionContext";
import DebugPage from "../../debug/debug";
import SettingsPage from "../../settings/settings";
import "./toolbar.css";

const Toolbar: React.FC<{
}> = () => {
    const { snap: qc, openQC, currentBoard, closeCurrentQc} = useSnapSession();
    const { showModal} = useModal();

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
                openQC(file.path);
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
                        { label: "Open recent...", onClick: openQC },
                        { type: "separator" },
                        { label: "Reload", onClick: openQC, disabled: !qc },
                        { label: "Save", onClick: () => { }, disabled: !qc?.has_changed },
                        { label: "Save As...", onClick: () => { }, disabled: !qc?.has_changed },
                        { label: "Close", onClick:closeCurrentQc, disabled: !qc},
                        { label: "Close All", onClick: () => { }, disabled: !qc},
                        { type: "separator" },
                        { label: "Export to PDF", onClick: () => { }, disabled: !qc },
                        { label: "Export to HTML", onClick: () => { }, disabled: !qc },
                        { type: "separator" },
                        {label: "Settings...", onClick: () => { showModal(<SettingsPage />)}},
                        { type: "separator" },
                        { label: "Quit", onClick: () => { }}
                    ]},
                    {label: "Edit", children: [
                        { label: "Cancel", onClick: () => { }, disabled: !qc?.is_cancellable },
                        { label: "Redo", onClick: () => { }, disabled: !qc?.is_redoable }
                    ]},
                    {label: "View", children: [
                        { label: "Show Sidebar", onClick: () => { } },
                        {label: "Show this board in all files", onClick: () => {}, disabled: !qc || !currentBoard}
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