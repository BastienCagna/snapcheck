import { useEffect } from "react";
import type { BoardModel } from "@lepton/api-client";
import Board from "./board";
import "./main.css"
import { useSnapSession } from "../../contexts/SnapSessionContext";
import { TransformComponent, TransformWrapper } from "react-zoom-pan-pinch";

const BoardView: React.FC<{ sessionId: string, snapId: string, board: BoardModel | null }> = ({ sessionId, snapId, board }) => {
    if (!board) {
        return <div className="vertical-center">
            <p className='default-text'>No boards available.</p>
        </div>
    }

    return (
        <TransformWrapper 
            limitToBounds={false} 
            minScale={0.1} 
            maxScale={10} 
            panning={{"allowLeftClickPan": false, "allowRightClickPan": false}}
        >
            <TransformComponent wrapperStyle={{width: "100%", height: "calc(100vh - 50px)"}} >
                <Board sessionId={sessionId} snapId={snapId} board={board} />
            </TransformComponent>
        </TransformWrapper>
)};


const MainContent: React.FC<{}> = () => {
    const { snap, setCurrentBoard, currentBoardIndex, currentBoard, session } = useSnapSession();

    useEffect(() => {
        const handleTabKey = (event: KeyboardEvent) => {
            if (event.key === "Tab") {
                event.preventDefault();
                if (snap?.boards && snap.boards.length > 0) {
                    setCurrentBoard((currentBoardIndex + 1) % snap.boards.length);
                }
            }
        };
        window.addEventListener("keydown", handleTabKey);
        return () => {
            window.removeEventListener("keydown", handleTabKey);
        };
    }, [currentBoardIndex, snap, setCurrentBoard]);

    if (!snap) {
        return <div className="vertical-center">
            <p className='default-text'>Nothing to show.</p>
        </div>
    }

    return (
        <div>        
            <div className="main-header">
                {
                    snap?.boards?.length && (
                        <ul className='board-list'>
                            {snap.boards.map((board: BoardModel, index) => (
                                <li key={index} onClick={() => setCurrentBoard(index)} className={currentBoardIndex === index ? 'active' : ''}>
                                    {board.title}
                                </li>
                            ))}
                        </ul>
                    )
                }
                <span>{snap?.title}</span>
            </div>
            <BoardView
                sessionId={session?.id || ""}
                snapId={snap.id || ""}
                board={currentBoard}
            />
        </div>
    );       
}

export default MainContent;