import { createContext, useCallback, useContext, useReducer } from 'react';
import type { DefaultProps } from '../core/types';
import { QcService, type BoardModel, type QualityControlModel } from '../api';

type QCState = {
    qc: QualityControlModel | null;
    currentBoardIndex: number;
    currentBoard: BoardModel | null;
    loading: boolean;
    error: string | null;
};

const defaultQCState: QCState = {
    qc: null,
    currentBoardIndex: -1,
    currentBoard: null,
    loading: false,
    error: null,
};

/*
    The reducer is in charge to modify the QCState based on an action type and its args
    This modify only the state, it doesn't do any async work by itself (like loading data)
*/
type QCAction =
    | { type: 'LOAD'; path: string }
    | { type: 'SUCCESS'; payload: QualityControlModel }
    | { type: 'ERROR'; error: string }
    | { type: 'SET_BOARD'; boardIndex: number }
    | { type: 'RESET'; };

function qcReducer(state: QCState, action: QCAction): QCState {
    const qc = state.qc;

    switch (action.type) {
        case 'RESET':
            return defaultQCState;
        case 'LOAD':
            return { ...state, loading: true, error: null };
        case 'SUCCESS':
            return { ...state, loading: false, qc: action.payload };
        case 'ERROR':
            return { ...state, loading: false, error: action.error };
        case 'SET_BOARD':
            if (!qc) return { ...state, error: 'No QC available' };
            if (action.boardIndex < 0) {
                return { ...state, currentBoardIndex: -1, currentBoard: null };
            }
            if (!qc.boards) return { ...state, error: 'No boards available in QC' };
            const idx = Math.min(action.boardIndex, qc.boards.length!);
            return {
                ...state,
                currentBoardIndex: action.boardIndex,
                currentBoard: qc.boards[idx] || null
            };
        default:
            return state;
    }
}

const QCContext = createContext<QCState | undefined>(undefined);
export const QCDispatchContext = createContext<React.Dispatch<QCAction> | null>(null);

export function QCProvider(props: DefaultProps) {
    const [state, dispatch] = useReducer(qcReducer, defaultQCState);

    return (
        <QCContext.Provider value={state}>
            <QCDispatchContext.Provider value={dispatch}>
                {props.children}
            </QCDispatchContext.Provider>
        </QCContext.Provider>
    );
}

/*
    Use this function to manage the QC
    This centralizes all the actions here
    It perfoms all async works and dispatches the actions
*/
export function useQCActions() {
    const dispatch = useContext(QCDispatchContext);

    const loadQC = useCallback(async (path?: string) => {
        if (!dispatch) throw new Error('useQCActions must be used within a QCProvider');

        dispatch({ type: 'LOAD', path: path || '' });

        try {
            const qc = await QcService.qcGetFullQc();
            dispatch({ type: 'SUCCESS', payload: qc });
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to load QC';
            dispatch({ type: 'ERROR', error: errorMessage });
        }
    }, [dispatch]);

    const setCurrentBoard = useCallback((boardIndex: number) => {
        if (!dispatch) throw new Error('useQCActions must be used within a QCProvider');
        dispatch({ type: 'SET_BOARD', boardIndex });
    }, [dispatch]);

    const updateNote = useCallback(async (note: any) => {
        if (!dispatch) throw new Error('useQCActions must be used within a QCProvider');

        try {
            await QcService.qcUpdateNote(note);
            // Reload data after update
            await loadQC();
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Failed to update note';
            dispatch({ type: 'ERROR', error: errorMessage });
        }
    }, [dispatch, loadQC]);

    return {
        loadQC,
        setCurrentBoard,
        updateNote,
    };
}

/*
    Provides the Quality Control context anywhere

    Example:
    ```
    const { loadQC, setCurrentBoard, updateNote } = useQCComplete();
    ```
*/
export function useQC() {
    const state = useContext(QCContext);
    const actions = useQCActions();

    if (!state) {
        throw new Error('useQC must be used within a QCProvider');
    }

    return {
        ...state,
        ...actions,
    };
}