import { createContext, useContext, useReducer } from 'react';
import type { DefaultProps } from '../core/types';
import { useEffect } from 'react';
import { AppdataService, type AppDataModel } from '../api';

type AppDataState = {
    loading: boolean;
    data: AppDataModel | null;
};

const defaultAppDataState: AppDataState = {
    loading: false,
    data: null
};


type AppDataAction =
    | { type: "IS_LOADING"; }
    | { type: 'SET_DATA'; data: AppDataModel }

function modalReducer(state: AppDataState, action: AppDataAction): AppDataState {
    switch (action.type) {
        case 'IS_LOADING':
            return {...defaultAppDataState, loading: true};
        case 'SET_DATA':
            return { ...state, data: action.data, loading: false };
        default:
            return state;
    }
}

const AppDataContext = createContext<AppDataState | undefined>(undefined);
export const AppDataDispatchContext = createContext<React.Dispatch<AppDataAction> | null>(null);

export function AppDataProvider(props: DefaultProps) {
    const [state, dispatch] = useReducer(modalReducer, defaultAppDataState);

    useEffect(() => {
        dispatch({ type: 'IS_LOADING' });
        AppdataService.getAll().then((data) => {
            dispatch({ type: 'SET_DATA', data });
        });
    }, []);
    
    return (
        <AppDataContext.Provider value={state}>
            <AppDataDispatchContext.Provider value={dispatch}>
                {props.children}
            </AppDataDispatchContext.Provider>
        </AppDataContext.Provider>
    );
}


export function useAppDataActions() {
    const dispatch = useContext(AppDataDispatchContext);

    const loadAppData = () => {
        if (!dispatch) throw new Error('useAppDataActions must be used within a AppDataProvider');
        dispatch({ type: 'IS_LOADING' });
        AppdataService.getAll().then((data) => {
            dispatch({ type: 'SET_DATA', data });
        });
    }

    return {
        loadAppData
    };
}

/*
    Provides the Quality Control context anywhere

    Example:
    ```
    const { openQC, setCurrentBoard, updateNote } = useQCComplete();
    ```
*/
export function useAppData() {
    const state = useContext(AppDataContext);
    const actions = useAppDataActions();

    if (!state) {
        throw new Error('useAppData must be used within a AppDataProvider');
    }

    return {
        loading: state.loading,
        ...state.data,
        ...actions,
    };
}