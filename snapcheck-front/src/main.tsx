import { startLeptonApp } from '@lepton/core/bootstrap';
import { OpenAPI } from '@lepton/api-client';
import { AppUIStateProvider } from './contexts/AppUIStateContext';
import Snapcheck from './Snapcheck.tsx'
import './index.css'
import { ModalProvider } from './lepton/contexts/ModalContext.tsx';


// Backend URL given at startup (see snapclient/launcher.py), overrides the one set when building the API
if (import.meta.env.VITE_API_URL) {
    OpenAPI.BASE = import.meta.env.VITE_API_URL;
}

startLeptonApp(<ModalProvider><Snapcheck /></ModalProvider>, AppUIStateProvider);
