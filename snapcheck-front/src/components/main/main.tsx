import type { QualityControlModel } from "../../api";
import Board from "./board";
import "./main.css"


const BoardView: React.FC<{ qc: QualityControlModel }> = ({ qc }) => {
    if (!qc || !qc.boards || qc.boards.length === 0) {
        return <div className="vertical-center">
            <p className='default-text'>No boards available.</p>
        </div>
    }
    return (
        <div className="board-view">
            {qc.boards.length === 0 && <p className='default-text'>No boards available.</p>}
            <Board board={qc.boards[0]} />
        </div>
    );
}



const MainContent: React.FC<{
    qc: QualityControlModel | null;
    error: string | null;
}> = ({ qc, error }) => {
    if (!qc && !error) {
        return <div className="vertical-center">
            <p className='default-text'>Nothing to show.</p>
        </div>
    }
    if (error) {
        return <div className="vertical-center">
            <p className='error-text'>{error}</p>
        </div>
    }

    return <BoardView qc={qc!} />
}

export default MainContent;