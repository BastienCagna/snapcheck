import React, { useEffect, useState, Suspense } from 'react';
import type { BoardModel } from '../../api';
import { ContextualMenu } from '../../components/lib/contextualMenu/contextualMenu';
import { useSnapSession } from '../../contexts/SnapSessionContext';


const ImageComponent = React.lazy(() => import('../../components/elements/image'));

const renderElement = (sessionId: string, snapId: string, element: any) => {
    // const { type, src, style } = element;

    switch (element.type) {
        case 'image':
            return (
                <Suspense fallback={<div>Loading...</div>}>
                    <ImageComponent sessionId={sessionId} snapId={snapId} src={element.src} style={element.style} />
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


const BoardElement: React.FC<{ sessionId: string, snapId: string, board: BoardModel, element: any}> = ({ sessionId, snapId, board, element }) => {
    const { updateRating } = useSnapSession();

    const allIntendedRatings = board.elements?.flatMap(el => el.intended_ratings || []) || [];
    
    const menuItems: any[] = [
        {label: "Show this board in all files", onClick: () => console.log('Show this board in all views clicked')},
        ...allIntendedRatings.map(rating => ({
            label: rating.name,
            items: [
                ...(rating.scale?.ratings.map((rate, index) => ({
                    label: rate.name,
                    onClick: () => updateRating(snapId,{ ...rating, value: Number(rate.value)}),
                    style:{ backgroundColor: rate.color || "" }
                })) || []),
                { label: "Comment", onClick: () => console.log('Comment clicked') },
                { label: "Infos", onClick: () => console.log('Infos clicked') },
            ]
        }))
    ];

    return (
        <ContextualMenu parentClass="board" items={menuItems}>
            <div className="board-element">
                    {renderElement(sessionId, snapId, element)}
            </div>
        </ContextualMenu> 
    );
}

const Board: React.FC<{ sessionId: string, snapId: string, board: BoardModel }> = ({ sessionId, snapId, board }) => {
    const [boardElements, setBoardElements] = useState<any[]>([]);

    useEffect(() => {
        if (board.elements) {
            setBoardElements(board.elements);
        }
    }, [board.elements]);

    return (
        <div className="board">
            {board.description && <p>{board.description}</p>}
            {boardElements.map((element, index) => <BoardElement key={index} sessionId={sessionId} snapId={snapId} board={board} element={element} />)}       
        </div>
    );
};

export default Board;