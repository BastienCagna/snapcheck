import TabSelector from "../../components/lib/tabSelector/tabSelector";
import { useSnapSession } from "../../contexts/SnapSessionContext";


export const SnapSelector: React.FC = () => {
    const { snaps, currentSnapPath: currentSnapPath, closeSnap, openSnap } = useSnapSession();

    return (
        <TabSelector
            items={Object.entries(snaps).map(([path, snapState]) => ({
                label: (snapState.data?.filename || "Untitled") + (snapState.data?.has_changed ? " *" : ""),
                onSelect: () => {openSnap(path)},
                onClose: () => {closeSnap(path)},
                isActive: path == currentSnapPath,
            }))}
        />
    );
};
