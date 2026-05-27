import { useEffect, useState } from "react";
import type { BoardModel } from "@lepton/api-client";
import Board from "./board";
import "./main.css"
import { useSnapSession } from "../../contexts/SnapSessionContext";
import { TransformComponent, TransformWrapper } from "react-zoom-pan-pinch";
import Viewer3D from "../../components/elements/viewer3d";
import { useLObjectSession } from "@lepton/core/contexts/SessionContext";

const BoardView: React.FC<{ snapId: string, board: BoardModel | null }> = ({ snapId, board }) => {
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
            panning={{ "allowLeftClickPan": false, "allowRightClickPan": false }}
        >
            <TransformComponent wrapperStyle={{ width: "100%", height: "calc(100vh - 50px)" }} >
                <Board snapId={snapId} board={board} />
            </TransformComponent>
        </TransformWrapper>
    )
};


const MainContent: React.FC<{}> = () => {
    // const { snap, setCurrentBoard, currentBoardIndex, currentBoard, session } = useSnapSession();
    const {currentObject: snap, setLObjectSetting, currentObjectSettings, session} = useLObjectSession();
    const currentBoardIndex = currentObjectSettings.currentBoard || 0;
    const currentBoard = snap?.boards ? snap.boards[currentBoardIndex] : null;

    const setCurrentBoard = (index: number) => {
        setLObjectSetting("currentBoard", index);
    }

    useEffect(() => {
        const handleTabKey = (event: KeyboardEvent) => {
            if (event.key === "Tab") {
                event.preventDefault();
                if (snap?.boards && snap.boards.length > 0) {
                    setCurrentBoard((currentObjectSettings.currentBoard + 1) % snap.boards.length);
                }
            }
        };
        window.addEventListener("keydown", handleTabKey);
        return () => {
            window.removeEventListener("keydown", handleTabKey);
        };
    }, [currentObjectSettings.currentBoard, snap, setCurrentBoard]);

    // if (!snap) {
    //     return <div className="vertical-center">
    //         <Viewer3D>
    //         </Viewer3D>
    //     </div>
    // }

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
                sessionId={session || ""}
                snapId={snap?.id || ""}
                board={currentBoard}
            />
        </div>
    );
}

export default MainContent;