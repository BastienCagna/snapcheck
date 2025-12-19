import TabSelector from "../../components/lib/tabSelector/tabSelector";
import { useSnapSession } from "../../contexts/SnapSessionContext";


export const SnapSelector: React.FC = () => {
    const { snaps, currentSnapPath: currentSnapPath, closeSnap, viewSnap } = useSnapSession();

    return (
        <TabSelector
            items={Object.entries(snaps).map(([path, snapState]) => ({
                label: snapState.snap?.filename || "Untitled",
                onSelect: () => {viewSnap(path)},
                onClose: () => {closeSnap(path)},
                isActive: path == currentSnapPath,
            }))}
        />
    );
};
