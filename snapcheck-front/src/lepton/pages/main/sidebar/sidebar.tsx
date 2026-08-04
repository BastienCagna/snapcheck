import React from 'react';
import FileCopyIcon from '@mui/icons-material/FileCopy';
import EditNoteIcon from '@mui/icons-material/EditNote';
import ViewListIcon from '@mui/icons-material/ViewList';
import { type Tab, Tabs } from '../../../components/lib/tabs/tabs';
import DictionaryTable from '../../../components/lib/table/dictTable';
import type { BoardModel, RatingModel, SnapModel } from '@lepton/api-client';
import InlineToggle from '../../../components/lib/inlineToggle';
import FilesBrowser from '../../../components/files/browser/browser';
import RatingInput from '../../../components/specials/ratinginput/ratinginput';
import VerticalStackLayout, { type StackSection } from '../../../components/lib/layouts/verticalStackLayout';
import { useLObjectSession, useSessionActions } from '@lepton/core/contexts/SessionContext';
import './sidebar.css';


function boardHasRating(board: BoardModel, rating: RatingModel) {
    const allIntendedRatings = board.elements?.flatMap(el => el.intended_ratings || []) || [];
    for (const intendedRating of allIntendedRatings
    ) {
        if (intendedRating.id === rating.id) {
            return true;
        }
    }
    return false;
}

const FilesControl: React.FC<{
}> = () => {
    const [currentPath, setCurrentPath] = React.useState<string | null>(null);
    const { openLObject, setCurrentLObject, setLObjectSetting } = useLObjectSession();

    return <FilesBrowser
        path={currentPath}
        onPathChange={(p) => setCurrentPath(p)}
        onFileSelect={(path: string) => { openLObject(path); setCurrentLObject(path); setLObjectSetting("currentBoard", 0, path); }}
        extensions={[".snpk"]}
    />
}

const SnapControl: React.FC<{}> = () => {
    const { currentObject: snap, setLObjectSetting, currentObjectSettings, session, updateFieldDebounced } = useLObjectSession();
    const currentBoardIndex = currentObjectSettings.currentBoard || 0;
    const currentBoard = snap?.boards ? snap.boards[currentBoardIndex] : null;
    const [showAllratings, setShowAllRatings] = React.useState(true);

    const updateRatingField = (id: string, field: string, value: any) => {
        console.log("Updating rating field", id, field, value);
        updateFieldDebounced(snap?.id || "", `ratings.{id:${id}}.${field}`, value);
    };
    return <div className="snap-control-panel">
        <div className="panel-header">
            <div>
                <InlineToggle
                    off="Board" on="All"
                    value={showAllratings}
                    onChange={(value) => setShowAllRatings(value)} />
            </div>
        </div>

        <div className="ratings-list">
            {snap?.id && (snap?.ratings?.filter((rating) => currentBoard && (showAllratings || boardHasRating(currentBoard, rating))).map((rating) => (
                <RatingInput
                    key={rating.id}
                    rating={rating}
                    onChange={updateRatingField}
                    highlight={(showAllratings && currentBoard && boardHasRating(currentBoard, rating)) || false} />
            )))}
        </div>
    </div>
}


const MetadataControl: React.FC<{
    snap: SnapModel | null;
}> = ({ snap }) => {

    return <div className="metadata-control-panel">
        <DictionaryTable dictionary={snap?.metadata || {}} />
    </div>
}

const Sidebar: React.FC<{}> = ({ }) => {
    // const { snap: snap } = useSnapSession();

    const menuItems: StackSection[] = [
        { id: "files", title: "Files", content: <FilesControl /> },
        { id: "snap", title: "Ratings", content: <SnapControl /> },
        // { id: "metadata", title: "Metadata", content: <MetadataControl snap={snap} /> },
    ];

    return (
        <VerticalStackLayout sections={menuItems} height="100%">
        </VerticalStackLayout>
    );
};

export default Sidebar;