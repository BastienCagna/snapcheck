import React from 'react';
import FileCopyIcon from '@mui/icons-material/FileCopy';
import EditNoteIcon from '@mui/icons-material/EditNote';
import ViewListIcon from '@mui/icons-material/ViewList';
import { type Tab, Tabs } from '../../../components/lib/tabs/tabs';
import DictionaryTable from '../../../components/lib/table/dictTable';
import type { BoardModel, RatingModel, SnapModel } from '../../../api';
import InlineToggle from '../../../components/lib/inlineToggle';
import FilesBrowser from '../../../components/files/browser/browser';
import './sidebar.css';
import { useSnapSession } from '../../../contexts/SnapSessionContext';
import RatingInput from '../../../components/specials/ratinginput/ratinginput';
import VerticalStackLayout, { type StackSection } from '../../../components/lib/layouts/verticalStackLayout';


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
    const { openSnap } = useSnapSession();

    return <FilesBrowser
            path={currentPath}
            onPathChange={(p) => setCurrentPath(p)}
            onFileSelect={openSnap}
            extensions={[".snpk"]}
        />
}

const SnapControl: React.FC<{
    onRatingChanged?: (sessionId: string | null, snapId: string | null, rating: RatingModel) => void;
}> = ({onRatingChanged }) => {
    const { session, snap, currentBoard } = useSnapSession();
    const [showAllratings, setShowAllRatings] = React.useState(true);

    return <div className="snap-control-panel">
        <div className="panel-header">
            <div>
                <InlineToggle
                    off="Board" on="All"
                    value={showAllratings}
                    onChange={(value) => setShowAllRatings(value)} />
            </div>
        </div>

        {/* {snap && <RatingStatBar snap={snap} />} */}
        <div className="ratings-list">
            {snap?.ratings?.filter((rating) => currentBoard && (showAllratings || boardHasRating(currentBoard, rating))).map((rating) => (
                <RatingInput
                    key={rating.id}
                    rating={rating}
                    onChange={(rating) => { if (onRatingChanged) onRatingChanged(session?.id || null, snap?.id || null, rating) }}
                    highlight={(showAllratings && currentBoard && boardHasRating(currentBoard, rating)) || false} />
            ))}
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
    const { snap: snap, updateRating } = useSnapSession();

    // Adapter to match SnapControl's expected onRatingChanged signature
    const handleRatingChanged = (
        sessionId: string | null,
        snapId: string | null,
        rating: RatingModel
    ) => {
        // Only call updateRating if both IDs are present
        if (snapId && rating) {
            // updateRating expects (snapId: string, rating: any)
            updateRating(snapId, rating);
        }
    };

    const menuItems: StackSection[] = [
        { id: "files", title: "Files", content: <FilesControl /> },
        { id: "snap", title: "Ratings", content: <SnapControl onRatingChanged={handleRatingChanged} /> },
        { id: "metadata", title: "Metadata", content: <MetadataControl snap={snap} /> },
    ];

    return (
        <VerticalStackLayout sections={menuItems} height="100%">
        </VerticalStackLayout>
    );
};

export default Sidebar;