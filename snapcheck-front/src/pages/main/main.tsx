import { useEffect, useState } from "react";
import type { BoardModel, QualityControlModel } from "../../api";
import Board from "./board";
import "./main.css"
import { useRef } from "react";
import { useQC } from "../../core/QCContext";

const BoardView: React.FC<{ board: BoardModel | null }> = ({ board }) => {
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
            <Board board={board} />
        </div>
    );
};


const MainContent: React.FC<{}> = () => {
    const { qc, error, setCurrentBoard, currentBoardIndex, currentBoard } = useQC();

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

    return <div>
        <div className="main-header">
            <span>{qc?.title}</span>
            {
                qc?.boards?.length && (
                    <ul className='board-list'>
                        {qc.boards.map((board: BoardModel, index) => (
                            <li key={index} onClick={() => setCurrentBoard(index)} className={currentBoardIndex === index ? 'active' : ''}>
                                {board.title}
                            </li>
                        ))}
                    </ul>
                )
            }
        </div>
        <BoardView
            board={currentBoard}
        />
    </div>
}

export default MainContent;