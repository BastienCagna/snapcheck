import { createContext, useCallback, useContext, useEffect, useReducer } from 'react';
import type { DefaultProps } from '../core/types';
import { SnapService, type BoardModel, type SnapCheckSessionModel, type SnapModel } from '../api';


type SnapState = {
    snap: SnapModel | null;
    currentBoardIndex: number;
    currentBoard: BoardModel | null;
    loading: boolean;
}
const defaultSnapState: SnapState = {
    snap: null,
    currentBoardIndex: -1,
    currentBoard: null,
    loading: false,
};

type SnapSessionState = {
    session: SnapCheckSessionModel | null;
    loading: boolean;
    snaps: Record<string, SnapState>;
    currentSnapPath: string | null;
}
const defaultSnapSessionState: SnapSessionState = {
    session: null,
    loading: false,
    snaps: {},
    currentSnapPath: null,
};

/*
    The reducer is in charge to modify the SnapState based on an action type and its args
    This modify only the state, it doesn't do any async work by itself (like loading data)
*/
type SnapSessionAction =
    | { type: 'WAIT_SESSION'}
    | { type: 'SET_SESSION'; session: SnapCheckSessionModel}
    | { type: 'SET_CURRENT'; path: string }
    | { type: 'SET_SNAP_DATA'; path?: string, payload: SnapModel }
    | { type: 'REMOVE'; path: string}
    | { type: 'SET_BOARD'; boardIndex: number }

function qcReducer(state: SnapSessionState, action: SnapSessionAction): SnapSessionState {
    const qc = state.snaps[state.currentSnapPath!];

    switch (action.type) {
        case 'WAIT_SESSION':
            return {...defaultSnapSessionState, loading: true}
        case 'SET_SESSION':
            return {...state, session: action.session, loading: false}
        case 'SET_CURRENT':
            if (state.snaps[action.path]) {
                return { ...state, currentSnapPath: action.path };
            } else {
                const qcState = { ...defaultSnapState, loading: true };
                return {
                    ...state,
                    snaps: { ...state.snaps, [action.path]: qcState },
                    currentSnapPath: action.path
                };
            }
        case 'SET_SNAP_DATA':
            if(!action.path) {
                if (!state.currentSnapPath) {
                    console.error("No current Snap path set");
                    return state;
                }
                action.path = state.currentSnapPath;
            }
            return {
                ...state,
                snaps: {
                    ...state.snaps,
                    [action.path]: {
                        ...state.snaps[action.path],
                        snap: action.payload,
                        loading: false,
                    }
                }
            };
        case 'REMOVE':
            if (!state.snaps[action.path]) return state;

            const removeCurrent = action.path == state.currentSnapPath;
            const { [action.path]: removedQc, ...remainingQcs } = state.snaps;
            if(removedQc?.snap?.has_changed) {
                if (!window.confirm("Are you sure you want to close this quality control? Unsaved changes will be lost.")) {
                    return state;
                }
            }
            const remainingKeys = Object.keys(remainingQcs);
            const newCurrent = removeCurrent ? remainingKeys.length > 0 ? remainingKeys[remainingKeys.length - 1] : null : state.currentSnapPath;
            return { ...state, snaps: remainingQcs, currentSnapPath: newCurrent };
        case 'SET_BOARD':
            if (!qc) return { ...state};
            if (action.boardIndex < 0) {
                return { ...state, snaps: { ...state.snaps, [state.currentSnapPath!]: { ...qc, currentBoardIndex: -1, currentBoard: null } } };
            }
            if (!qc.snap || !qc.snap.boards) return { ...state};
            const idx = Math.min(action.boardIndex, qc.snap.boards.length!);
            return {
                ...state,
                snaps: { ...state.snaps, [state.currentSnapPath!]: { ...qc, currentBoardIndex: action.boardIndex, currentBoard: qc.snap.boards[idx] || null } }
            };
        default:
            return state;
    }
}

const SnapSessionContext = createContext<SnapSessionState | undefined>(undefined);
export const SnapSessionDispatchContext = createContext<React.Dispatch<SnapSessionAction> | null>(null);

export function SnapSessionProvider(props: DefaultProps) {
    const [state, dispatch] = useReducer(qcReducer, defaultSnapSessionState);

    // Auto-create session on mount
    useEffect(() => {
        const autoCreateSession = async () => {
            if(!state.session && !state.loading) {
                dispatch({ type: 'WAIT_SESSION'});
                try {
                    const session = await SnapService.createSession();
                    dispatch({ type: 'SET_SESSION', session});
                } catch (error) {
                    console.error("Session creation failed", error);
                }
            }
        };
        autoCreateSession();
    }, [])

    return (
        <SnapSessionContext.Provider value={state}>
            <SnapSessionDispatchContext.Provider value={dispatch}>
                {props.children}
            </SnapSessionDispatchContext.Provider>
        </SnapSessionContext.Provider>
    );
}

/*
    Use this function to manage the Snap
    This centralizes all the actions here
    It perfoms all async works and dispatches the actions
*/
export function useSnapSessionActions() {
    const dispatch = useContext(SnapSessionDispatchContext);

    const state = useContext(SnapSessionContext);

    const openSnap = useCallback(
        async (path?: string) => {
            if (!dispatch) throw new Error('useSnapSessionActions must be used within a SnapSessionProvider');
            if (!state) throw new Error('useSnapSessionActions must be used within a SnapSessionProvider');
            if (!path) { throw new Error('Path is required to open a Snap'); }
            const sid = state.session?.id || "";

            console.log("Opening snap", sid, path, state);
            dispatch({ type: 'SET_CURRENT', path: path });

            try {
                const snap = await SnapService.openSnap(sid, path);
                dispatch({ type: 'SET_SNAP_DATA', path: path, payload: snap });
            } catch (error) {
                const errorMessage = error instanceof Error ? error.message : 'Failed to load Snap';
                console.error(errorMessage);
            }
        },
        [dispatch, state]
    );

    const viewSnap = openSnap;

    const setCurrentBoard = useCallback((boardIndex: number) => {
        if (!dispatch) throw new Error('useSnapActions must be used within a SnapProvider');
        dispatch({ type: 'SET_BOARD', boardIndex });
    }, [dispatch]);

    const updateRating = useCallback(
        async (snapId: string, rating: any) => {
            if (!dispatch) throw new Error('useSnapActions must be used within a SnapProvider');
            if (!state) throw new Error('useSnapSessionActions must be used within a SnapSessionProvider');
            const sid = state.session?.id || "";

            try {
                await SnapService.updateRating(sid, snapId, rating.id, rating.value);
                // Reload data after update
                await openSnap();
            } catch (error) {
                const errorMessage = error instanceof Error ? error.message : 'Failed to update note';
                console.error(errorMessage);
            }
        },
        [dispatch, openSnap, state]
    );

    const closeSnap = useCallback((path: string) => {
        if (!dispatch) throw new Error('useSnapActions must be used within a SnapProvider');
        dispatch({ type: 'REMOVE', path });
    }, [dispatch]);

    return {
        openSnap,
        viewSnap,
        setCurrentBoard,
        updateRating,
        closeSnap
    };
}

/*
    Provides the Quality Control context anywhere

    Example:
    ```
    const { openSnap, setCurrentBoard, updateNote } = useSnapComplete();
    ```
*/
export function useSnapSession() {
    const state = useContext(SnapSessionContext);
    const actions = useSnapSessionActions();

    if (!state) {
        throw new Error('useSnapSession must be used within a SnapSessionProvider');
    }    
    
    const closeCurrentSnap = () => {
        actions.closeSnap(state.currentSnapPath!);
    }

    return {
        ...state,
        ...actions,
        ...state.snaps[state.currentSnapPath!],
        closeCurrentSnap
    };
}