import { startLeptonApp } from '@lepton/core/bootstrap';
import { AppUIStateProvider } from './contexts/AppUIStateContext';
import Snapcheck from './Snapcheck.tsx'
import './index.css'
import { ModalProvider } from './lepton/contexts/ModalContext.tsx';



startLeptonApp(<ModalProvider><Snapcheck /></ModalProvider>, AppUIStateProvider);
