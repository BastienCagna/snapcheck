import Menu from "../../../components/lib/menu/menu";
import ServerContent from "../../../components/lib/serverContent";
import { useAppData } from "../../../contexts/AppDataContext";
import { useModal } from "../../../contexts/ModalContext";
import { useSnapSession } from "../../../contexts/SnapSessionContext";
import DebugPage from "../../debug/debug";
import SettingsPage from "../../settings/settings";
import { Close, FilterNone, Maximize, Minimize } from "@mui/icons-material";
import { SnapSelector } from "../snapSelector";
import { useEffect, useRef } from "react";
import "./topbar.css";


// Declare missing globals and types
declare const QWebChannel: any;


const TopBar: React.FC<{
}> = () => {
    const { snap, openSnap, currentBoard, closeCurrentSnap, toggleShowSidebar, toggleSyncBoards, saveSnap, saveSnapAs } = useSnapSession();
    const { showModal } = useModal();
    const { history } = useAppData();

    // Variables pour gérer le double-clic
    const dragTimer = useRef<number | null>(null);
    const isDragDelayed = useRef(false);

    // Gérer les événements globaux de mouse up
    useEffect(() => {
        const handleGlobalMouseUp = () => {
            // Annuler le drag delayed s'il y en a un
            if (dragTimer.current) {
                clearTimeout(dragTimer.current);
                dragTimer.current = null;
                isDragDelayed.current = false;
            }
            stopWindowDrag();
        };

        document.addEventListener('mouseup', handleGlobalMouseUp);
        return () => {
            document.removeEventListener('mouseup', handleGlobalMouseUp);
        };
    }, []);


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
            new QWebChannel((window as any).qt.webChannelTransport, function (channel: any) {
                (window as any).bridge = channel.objects.bridge;
                (window as any).bridge.close();
            });
        }
    }
    const maximize = () => {
        if (typeof window !== "undefined" && (window as any).qt) {
            new QWebChannel((window as any).qt.webChannelTransport, function (channel: any) {
                (window as any).bridge = channel.objects.bridge;
                (window as any).bridge.maximize();
            });
        }
    }
    const minimize = () => {
        if (typeof window !== "undefined" && (window as any).qt) {
            new QWebChannel((window as any).qt.webChannelTransport, function (channel: any) {
                (window as any).bridge = channel.objects.bridge;
                (window as any).bridge.minimize();
            });
        }
    }
    const restore = () => {
        if (typeof window !== "undefined" && (window as any).qt) {
            new QWebChannel((window as any).qt.webChannelTransport, function (channel: any) {
                (window as any).bridge = channel.objects.bridge;
                (window as any).bridge.restore();
            });
        }
    }
    const toggleWindowSize = () => {
        if (typeof window !== "undefined" && (window as any).qt) {
            new QWebChannel((window as any).qt.webChannelTransport, function (channel: any) {
                (window as any).bridge = channel.objects.bridge;
                (window as any).bridge.toggleWindowSize();
            });
        }
    }

    const startWindowDragDelayed = () => {
        if (typeof window !== "undefined" && (window as any).qt) {
            new QWebChannel((window as any).qt.webChannelTransport, function (channel: any) {
                (window as any).bridge = channel.objects.bridge;
                (window as any).bridge.startWindowDrag();
            });
        }
    };

    const stopWindowDrag = () => {
        if (typeof window !== "undefined" && (window as any).qt) {
            new QWebChannel((window as any).qt.webChannelTransport, function (channel: any) {
                (window as any).bridge = channel.objects.bridge;
                (window as any).bridge.stopWindowDrag();
            });
        }
    };

    const handleMouseDown = (e: React.MouseEvent) => {
        // Start window drag only if clicking directly on the topbar (not its children)
        if (e.currentTarget === e.target && e.button === 0) {
            // Délai de 200ms pour permettre la détection du double-clic
            dragTimer.current = window.setTimeout(() => {
                startWindowDragDelayed();
                isDragDelayed.current = true;
            }, 150);
        }
    };

    const handleDoubleClick = (e: React.MouseEvent) => {
        // Si c'est un double-clic, annuler le drag et faire l'action de double-clic
        if (e.currentTarget === e.target) {
            if (dragTimer.current) {
                clearTimeout(dragTimer.current);
                dragTimer.current = null;
                isDragDelayed.current = false;
            }
            // Action de double-clic : toggle maximize/restore
            toggleWindowSize();
        }
    };


    return <div className="topbar"
        onMouseDown={handleMouseDown}
        onDoubleClick={handleDoubleClick}
    >
        <div>
            <Menu items={[
                {
                    label: "File", children: [
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
                        { label: "Save", onClick: () => { snap?.id && saveSnap(snap.id) }, disabled: !snap?.has_changed },
                        { label: "Save As...", onClick: () => { snap?.id && saveSnapAs(snap.id, "newPath") }, disabled: !snap?.has_changed },
                        { label: "Close", onClick: closeCurrentSnap, disabled: !snap },
                        { label: "Close All", onClick: () => { }, disabled: !snap },
                        { type: "separator" },
                        { label: "Export to PDF", onClick: () => { }, disabled: !snap },
                        { label: "Export to HTML", onClick: () => { }, disabled: !snap },
                        { type: "separator" },
                        { label: "Settings...", onClick: () => { showModal(<SettingsPage />) } },
                        { type: "separator" },
                        { label: "Quit", onClick: close }
                    ]
                },
                {
                    label: "Edit", children: [
                        { label: "Cancel", onClick: () => { }, disabled: !snap?.is_cancellable },
                        { label: "Redo", onClick: () => { }, disabled: !snap?.is_redoable }
                    ]
                },
                {
                    label: "View", children: [
                        { label: "Show Sidebar", onClick: toggleShowSidebar },
                        { label: "Sync boards", onClick: toggleSyncBoards, disabled: !snap || !currentBoard }
                    ]
                },
                {
                    label: "More", children: [
                        { label: "About", onClick: () => { showModal(<ServerContent path="about.html" />) } },
                        { label: "Debug", onClick: () => { showModal(<DebugPage />) } },
                    ]
                },
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
}

export default TopBar;