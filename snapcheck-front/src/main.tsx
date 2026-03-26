import { startLeptonApp } from '@lepton/core/bootstrap';
import { AppUIStateProvider } from './contexts/AppUIStateContext';
import Snapcheck from './Snapcheck.tsx'
import './index.css'



startLeptonApp(<Snapcheck />, AppUIStateProvider);
