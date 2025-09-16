import { useEffect, useState } from "react";
import type { BoardModel, QualityControlModel } from "../../api";
import Board from "./board";
import "./main.css"
import { useRef } from "react";
import { useSnapSession } from "../../contexts/SnapSessionContext";
import TabSelector from "../../components/lib/tabSelector/tabSelector";

const BoardView: React.FC<{ sessionId: string, snapId: string, board: BoardModel | null }> = ({ sessionId, snapId, board }) => {
    const boardViewRef = useRef<HTMLDivElement>(null);
    const [scale, setScale] = useState(1);
    const [isDragging, setIsDragging] = useState(false);
    const [dragStart, setDragStart] = useState<{ x: number; y: number } | null>(null);
    const [position, setPosition] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
    const [zoomFactor, setZoomFactor] = useState<number>(0.2); // Adjust zoom sensitivity
    const [zoomMin, setZoomMin] = useState<number>(0.5);
    const [zoomMax, setZoomMax] = useState<number>(2.5);

    const handleKeyDown = (event: KeyboardEvent) => {
        if (event.key === "œ" || event.key === "Œ") {
            // Zoom
            const newScale = (prevScale: number) => prevScale + (event.shiftKey == true ? -zoomFactor : zoomFactor);
            setScale((prevScale) => Math.max(zoomMin, Math.min(newScale(prevScale), zoomMax)));
        }
    };

    const handleMouseDown = (event: React.MouseEvent) => {
        if (event.button === 1) { // Middle mouse button
            setIsDragging(true);
            setDragStart({ x: event.clientX, y: event.clientY });
        }
    };

    const handleMouseMove = (event: React.MouseEvent) => {
        if (isDragging && dragStart) {
            const deltaX = event.clientX - dragStart.x;
            const deltaY = event.clientY - dragStart.y;
            setPosition((prevPosition) => ({
                x: prevPosition.x + deltaX,
                y: prevPosition.y + deltaY,
            }));
            setDragStart({ x: event.clientX, y: event.clientY });
        }
    };

    const handleMouseUp = () => {
        setIsDragging(false);
        setDragStart(null);
    };

    useEffect(() => {
        const boardViewElement = boardViewRef.current;
        if (boardViewElement) {
            boardViewElement.style.transform = `scale(${scale}) translate(${position.x}px, ${position.y}px)`;
        }
    }, [scale, position]);

    useEffect(() => {
        window.addEventListener("keydown", handleKeyDown);
        return () => {
            window.removeEventListener("keydown", handleKeyDown);
        };
    }, []);

    if (!board) {
        return <div className="vertical-center">
            <p className='default-text'>No boards available.</p>
        </div>
    }

    return (
        <div
            className="board-view"
            ref={boardViewRef}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
        >
            <Board sessionId={sessionId} snapId={snapId} board={board} />
        </div>
    );
};


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