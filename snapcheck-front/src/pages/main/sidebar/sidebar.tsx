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
import Toolbar from '../toolbar/toolbar';
import RatingInput from '../../../components/specials/ratinginput/ratinginput';
import { useAppData } from '../../../contexts/AppDataContext';


function boardHasRating(board: BoardModel, rating: RatingModel) {
    for (const intendedRating of board.intended_ratings
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

    return <div className="files-control-panel">
        <div className="panel-header">
            <h3>Files</h3>
        </div>
        <FilesBrowser
            path={currentPath}
            onPathChange={(p) => setCurrentPath(p)}
            onFileSelect={openSnap}
            extensions={[".snpk"]}
        />
    </div>
}

const SnapControl: React.FC<{
    onRatingChanged?: (sessionId: string | null, snapId: string | null, rating: RatingModel) => void;
}> = ({onRatingChanged }) => {
    const { session, snap, currentBoard } = useSnapSession();
    const [showAllratings, setShowAllRatings] = React.useState(true);

    return <div className="snap-control-panel">
        <div className="panel-header">
            <h3>Ratings</h3>
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
        <div className="panel-header">
            <h3>Metadata</h3>
            <div>
            </div>
        </div>
        <div className="">
            <DictionaryTable dictionary={snap?.metadata || {}} />
        </div>
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

    const menuItems: Tab[] = [
        { title: <FileCopyIcon />, content: <FilesControl /> },
        { title: <EditNoteIcon />, content: <SnapControl onRatingChanged={handleRatingChanged} /> },
        { title: <ViewListIcon />, content: <MetadataControl snap={snap} /> },
    ];

    return (
        <div className="sidebar">
            <Toolbar />
            <div className='sidebar-header'>
            </div>
            <div className='sidebar-content'>
                <Tabs tabs={menuItems} />
            </div>
            <div>
            </div>
        </div>
    );
};

export default Sidebar;