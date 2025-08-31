import { createContext, useContext, useReducer } from 'react';
import type { DefaultProps } from '../core/types';

type ModalState = {
    content: React.ReactNode | null;
};

const defaultModalState: ModalState = {
    content: null
};


type ModalAction =
    | { type: 'HIDE'; }
    | { type: 'SHOW'; content: React.ReactNode };

function modalReducer(state: ModalState, action: ModalAction): ModalState {
    switch (action.type) {
        case 'HIDE':
            return defaultModalState;
        case 'SHOW':
            return { ...state, content: action.content };
        default:
            return state;
    }
}

const ModalContext = createContext<ModalState | undefined>(undefined);
export const ModalDispatchContext = createContext<React.Dispatch<ModalAction> | null>(null);

export function ModalProvider(props: DefaultProps) {
    const [state, dispatch] = useReducer(modalReducer, defaultModalState);

    return (
        <ModalContext.Provider value={state}>
            <ModalDispatchContext.Provider value={dispatch}>
                {props.children}
            </ModalDispatchContext.Provider>
        </ModalContext.Provider>
    );
}


export function useModalActions() {
    const dispatch = useContext(ModalDispatchContext);

    const showModal = (content: React.ReactNode) => {
        if (!dispatch) throw new Error('useModalActions must be used within a ModalProvider');
        dispatch({ type: 'SHOW', content });
    }

    const hideModal = () => {
        if (!dispatch) throw new Error('useModalActions must be used within a ModalProvider');
        dispatch({ type: 'HIDE' });
    }

    return {
        showModal,
        hideModal
    };
}

/*
    Provides the Quality Control context anywhere

    Example:
    ```
    const { openQC, setCurrentBoard, updateNote } = useQCComplete();
    ```
*/
export function useModal() {
    const state = useContext(ModalContext);
    const actions = useModalActions();

    if (!state) {
        throw new Error('useModal must be used within a ModalProvider');
    }

    return {
        ...state,
        ...actions,
    };
}