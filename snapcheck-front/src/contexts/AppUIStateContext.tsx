import { createUIStateContext } from '@lepton/core/contexts/UIStateContext';


const AppUIState = {
    showSidebar: true,
};

export const {
    UIStateProvider: AppUIStateProvider,
    useUIState: useAppUIState,
    useUIStateValue: useAppUIStateValue,
    useUIStateActions: useAppUIStateActions
} = createUIStateContext(AppUIState);


