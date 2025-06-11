import { useEffect, useState } from "react";
import type { QualityControlModel } from "../../api";
import Board from "./board";
import "./main.css"
import { useRef } from "react";

const BoardView: React.FC<{ qc: QualityControlModel }> = ({ qc }) => {
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

    if (!qc || !qc.boards || qc.boards.length === 0) {
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
            {qc.boards.length === 0 && <p className='default-text'>No boards available.</p>}
            <Board board={qc.boards[0]} />
        </div>
    );
};


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