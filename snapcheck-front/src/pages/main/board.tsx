import React, { useEffect, useState, Suspense } from 'react';
import type { BoardModel } from '../../api';


const ImageComponent = React.lazy(() => import('../../components/elements/image'));

const renderElement = (element: any) => {
    // const { type, src, style } = element;

    switch (element.type) {
        case 'image':
            return (
                <Suspense fallback={<div>Loading...</div>}>
                    <ImageComponent src={element.src} style={element.style} />
                </Suspense>
            );
        //   case '3d':
        //     return (
        //       <Suspense fallback={<div>Loading...</div>}>
        //         <ThreeDComponent src={src} style={style} />
        //       </Suspense>
        //     );
        default:
            return <p className='error-text'>Unsupported element type: {element.type}</p>;
    }
};


const Board: React.FC<{ board: BoardModel }> = ({ board }) => {
    const [boardElements, setBoardElements] = useState<any[]>([]);

    useEffect(() => {
        if (board.elements) {
            setBoardElements(board.elements);
        }
    }, [board.elements]);

    return (
        <div className="board">
            <h2>{board.title}</h2>
            {board.description && <p>{board.description}</p>}
            {boardElements.map((element, index) => (
                <div key={index} className="board-element">
                    {renderElement(element)}
                </div>
            ))}
        </div>
    );
};

export default Board;