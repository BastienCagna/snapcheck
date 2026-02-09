import { createContext, useContext, useReducer } from 'react';
import type { DefaultProps } from '../core/types';
import { SettingsService, type SettingsGroupModel } from '@lepton/api-client';
import { useEffect } from 'react';

type SettingsState = {
    loading: boolean;
    settings: SettingsGroupModel[];
};

const defaultSettingsState: SettingsState = {
    loading: false,
    settings: []
};


type SettingsAction =
    | { type: "IS_LOADING"; }
    | { type: 'SET_SETTINGS'; settings: SettingsGroupModel[] }

function modalReducer(state: SettingsState, action: SettingsAction): SettingsState {
    switch (action.type) {
        case 'IS_LOADING':
            return {...defaultSettingsState, loading: true};
        case 'SET_SETTINGS':
            return { ...state, settings: action.settings, loading: false };
        default:
            return state;
    }
}

const SettingsContext = createContext<SettingsState | undefined>(undefined);
export const SettingsDispatchContext = createContext<React.Dispatch<SettingsAction> | null>(null);

export function SettingsProvider(props: DefaultProps) {
    const [state, dispatch] = useReducer(modalReducer, defaultSettingsState);

    useEffect(() => {
        dispatch({ type: 'IS_LOADING' });
        SettingsService.getAllSettings().then((settings) => {
            dispatch({ type: 'SET_SETTINGS', settings });
        });
    }, []);
    
    return (
        <SettingsContext.Provider value={state}>
            <SettingsDispatchContext.Provider value={dispatch}>
                {props.children}
            </SettingsDispatchContext.Provider>
        </SettingsContext.Provider>
    );
}


export function useSettingsActions() {
    const dispatch = useContext(SettingsDispatchContext);

    const loadSettings = () => {
        if (!dispatch) throw new Error('useSettingsActions must be used within a SettingsProvider');
        dispatch({ type: 'IS_LOADING' });
        SettingsService.getAllSettings().then((settings) => {
            dispatch({ type: 'SET_SETTINGS', settings });
        });
    }

    return {
        loadSettings
    };
}

/*
    Provides the Quality Control context anywhere

    Example:
    ```
    const { openQC, setCurrentBoard, updateNote } = useQCComplete();
    ```
*/
export function useSettings() {
    const state = useContext(SettingsContext);
    const actions = useSettingsActions();

    if (!state) {
        throw new Error('useSettings must be used within a SettingsProvider');
    }

    return {
        ...state,
        ...actions,
    };
}