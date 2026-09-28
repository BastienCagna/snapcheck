import { startLeptonApp } from '@lepton/core/bootstrap';
import { OpenAPI } from '@lepton/api-client';
import { AppUIStateProvider } from './contexts/AppUIStateContext';
import Snapcheck from './Snapcheck.tsx'
import './index.css'
import { ModalProvider } from './lepton/contexts/ModalContext.tsx';


// Backend URL given at startup with ?api=<url> (see snapclient/launcher.py),
// overrides the one set when building the API
const apiUrl = new URLSearchParams(window.location.search).get('api');
if (apiUrl) {
    OpenAPI.BASE = apiUrl;
}

startLeptonApp(<ModalProvider><Snapcheck /></ModalProvider>, AppUIStateProvider);
