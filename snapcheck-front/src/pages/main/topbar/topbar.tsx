import { useEffect } from "react";
import Menu from "../../../components/lib/menu/menu";
import ServerContent from "../../../components/lib/serverContent";
import { useAppData } from "../../../contexts/AppDataContext";
import { useModal } from "../../../contexts/ModalContext";
import { useSnapSession } from "../../../contexts/SnapSessionContext";
import DebugPage from "../../debug/debug";
import SettingsPage from "../../settings/settings";
import "./topbar.css";
import { Close, FilterNone, Maximize, Minimize, Restore } from "@mui/icons-material";
import { SnapSelector } from "../snapSelector";

// Declare missing globals and types
declare const QWebChannel: any;


const TopBar: React.FC<{
}> = () => {
    const { snap, openSnap, currentBoard, closeCurrentSnap, toggleShowSidebar, toggleSyncBoards} = useSnapSession();
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
 
    const close = () => {
        if (typeof window !== "undefined" && (window as any).qt) {
            new QWebChannel((window as any).qt.webChannelTransport, function(channel: any) {
                (window as any).bridge = channel.objects.bridge;
                (window as any).bridge.close();
            });
        }
    }
    const maximize = () => {
        if (typeof window !== "undefined" && (window as any).qt) {
            new QWebChannel((window as any).qt.webChannelTransport, function(channel: any) {
                (window as any).bridge = channel.objects.bridge;
                (window as any).bridge.maximize();
            });
        }
    }
    const minimize = () => {
        if (typeof window !== "undefined" && (window as any).qt) {
            new QWebChannel((window as any).qt.webChannelTransport, function(channel: any) {
                (window as any).bridge = channel.objects.bridge;
                (window as any).bridge.minimize();
            });
        }
    }
    const restore = () => {
        if (typeof window !== "undefined" && (window as any).qt) {
            new QWebChannel((window as any).qt.webChannelTransport, function(channel: any) {
                (window as any).bridge = channel.objects.bridge;
                (window as any).bridge.restore();
            });
        }
    }

    return (
        <div className="topbar">
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
                        { label: "Save", onClick: () => {}, disabled: !snap?.has_changed },
                        { label: "Save As...", onClick: () => { }, disabled: !snap?.has_changed },
                        { label: "Close", onClick:closeCurrentSnap, disabled: !snap},
                        { label: "Close All", onClick: () => { }, disabled: !snap},
                        { type: "separator" },
                        { label: "Export to PDF", onClick: () => { }, disabled: !snap },
                        { label: "Export to HTML", onClick: () => { }, disabled: !snap },
                        { type: "separator" },
                        {label: "Settings...", onClick: () => { showModal(<SettingsPage />)}},
                        { type: "separator" },
                        { label: "Quit", onClick: close }
                    ]},
                    {label: "Edit", children: [
                        { label: "Cancel", onClick: () => { }, disabled: !snap?.is_cancellable },
                        { label: "Redo", onClick: () => { }, disabled: !snap?.is_redoable }
                    ]},
                    {label: "View", children: [
                        { label: "Show Sidebar", onClick: toggleShowSidebar},
                        {label: "Sync boards", onClick: toggleSyncBoards, disabled: !snap || !currentBoard}
                    ]},
                    {label: "More", children: [
                        { label: "About", onClick: () => { showModal(<ServerContent path="about.html" />) }},
                        { label: "Debug", onClick: () => { showModal(<DebugPage />) }},
                    ]},
                ]} />
            </div>
            <div className="snap-selector-container">
                <SnapSelector />
            </div>
            <div className="topbar-buttons">
                <div onClick={minimize}><Minimize /></div>
                <div onClick={maximize}><Maximize /></div>
                <div onClick={restore}><FilterNone /></div>
                <div onClick={close}><Close /></div>
            </div>
        </div>
    );
};

export default TopBar;