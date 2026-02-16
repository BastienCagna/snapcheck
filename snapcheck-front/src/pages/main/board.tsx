import React, { useEffect, useState, Suspense } from 'react';
import type { BoardModel } from '../../api';
import { ContextualMenu } from '../../components/lib/contextualMenu/contextualMenu';
import { useSnapSessionActions } from '../../contexts/SnapSessionContext';


const DefaultElementComponent = React.lazy(() => import('../../components/elements/default'));
const ImageElementComponent = React.lazy(() => import('../../components/elements/image'));

const renderElement = (sessionId: string, snapId: string, element: any) => {
    console.log("render", element);
    if(!element?.type) {
        if(!element?.content) return element;
        return element.content;
    }

    switch (element.type) {
        case 'image':
            return (
                <Suspense fallback={<div>Loading...</div>}>
                    <ImageElementComponent sessionId={sessionId} snapId={snapId} src={element.src} style={element.style} title={element.title} />
                </Suspense>
            );
        //   case '3d':
        //     return (
        //       <Suspense fallback={<div>Loading...</div>}>
        //         <ThreeDComponent src={src} style={style} />
        //       </Suspense>
        //     );
        case "row":
            return <div style={{ display: 'flex', flexDirection: 'row', ...element.style }}>
                {element.content?.map((child: any, index: number) => (
                    <div key={index} style={{ marginRight: index < element.content.length - 1 ? '8px' : '0' }}>
                        {renderElement(sessionId, snapId, child)}
                    </div>
                ))}
            </div>;
        case "default":
            return <DefaultElementComponent style={element.style} content={renderElement(sessionId, snapId, element.content)} />
        default:
            return <p className='error-text'>Unsupported element type: {element.type}</p>;
    }
};


const BoardElement: React.FC<{ sessionId: string, snapId: string, board: BoardModel, element: any}> = ({ sessionId, snapId, board, element }) => {
    const { updateFieldDebounced } = useSnapSessionActions();

    const allIntendedRatings = board.elements?.flatMap(el => el.intended_ratings || []) || [];

    const menuItems: any[] = [
        {label: "Show this board in all files", onClick: () => console.log('Show this board in all views clicked')},
        ...allIntendedRatings.map(rating => ({
            label: rating.name,
            items: [
                ...(rating.scale?.ratings.map((rate, index) => ({
                    label: rate.name,
                    onClick: () => updateFieldDebounced(snapId, `ratings.{id:${rating.id}}.value`, rate.value),
                    style:{ backgroundColor: rate.color || "" }
                })) || []),
                { label: "Comment", onClick: () => console.log('Comment clicked') },
                { label: "Infos", onClick: () => console.log('Infos clicked') },
            ]
        }))
    ];

    return (
        <ContextualMenu parentClass="board" items={[]}>
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