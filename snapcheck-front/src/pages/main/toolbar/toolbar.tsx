import Menu from "../../../components/lib/menu/menu";
import ServerContent from "../../../components/lib/serverContent";
import { useModal } from "../../../contexts/ModalContext";
import { useQC } from "../../../contexts/QCContext";
import "./toolbar.css";

const Toolbar: React.FC<{
}> = () => {
    const { qc, loadQC } = useQC();
    const { showModal} = useModal();
    return (
        <div className="toolbar">
            <div>
                <Menu items={[
                    {label: "File", children: [  
                        { label: "Open file...", onClick: loadQC },
                        { label: "Open recent...", onClick: loadQC },
                        { type: "separator" },
                        { label: "Reload", onClick: loadQC },
                        { label: "Save", onClick: () => { }, disabled: !qc?.has_changed },
                        { label: "Save As...", onClick: () => { }, disabled: !qc?.has_changed },
                        { label: "Close", onClick: () => { }},
                        { label: "Close All", onClick: () => { }},
                        { type: "separator" },
                        { label: "Export to PDF", onClick: () => { }, disabled: !qc },
                        { label: "Export to HTML", onClick: () => { }, disabled: !qc },
                        { type: "separator" },
                        {label: "Settings..."},
                        { type: "separator" },
                        { label: "Quit", onClick: () => { }}
                    ]},
                    {label: "Edit", children: [
                        { label: "Cancel", onClick: () => { }, disabled: !qc?.is_cancellable },
                        { label: "Redo", onClick: () => { }, disabled: !qc?.is_redoable }
                    ]},
                    { label: "About", onClick: () => { showModal(<ServerContent path="about.html" />) }}
                ]} />
            </div>
        </div>
    );
};

export default Toolbar;