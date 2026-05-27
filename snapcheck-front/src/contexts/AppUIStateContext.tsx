import { createLStateContext } from '@lepton/core/contexts/LStateContext';


const AppUIState = {
    showSidebar: true,
};

export const {
    LStateProvider: AppUIStateProvider,
    useLState: useAppUIState,
    useLStateValue: useAppUIStateValue,
    useLStateActions: useAppUIStateActions
} = createLStateContext(AppUIState);


