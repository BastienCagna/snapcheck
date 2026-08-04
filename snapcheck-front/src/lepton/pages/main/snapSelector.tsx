import { useLObjectSession } from "@lepton/core/contexts/SessionContext";
import TabSelector from "../../components/lib/tabSelector/tabSelector";


export const SnapSelector: React.FC = () => {
    const { currentLObjectPath, objects, setCurrentLObject, closeLObject } = useLObjectSession();

    return (
        <TabSelector
            items={Object.entries(objects).filter(([path, snapState]) => snapState.data && snapState.data?.filename).map(([path, snapState]) => ({
                label: snapState.data?.filename + (snapState.data?.has_changed ? " *" : ""),
                onSelect: () => { setCurrentLObject(path) },
                onClose: () => { closeLObject(snapState.data?.id || "") },
                isActive: path == currentLObjectPath,
            }))}
        />
    );
};
