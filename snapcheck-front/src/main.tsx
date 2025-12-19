import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { SnapSessionProvider } from './contexts/SnapSessionContext';
import { ModalProvider } from './contexts/ModalContext';
import { SettingsProvider } from './contexts/SettingsContext';
import { AppDataProvider } from './contexts/AppDataContext';
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SettingsProvider>
        <AppDataProvider>
            <SnapSessionProvider>
                <ModalProvider>
                    <App />
                </ModalProvider>
            </SnapSessionProvider>
        </AppDataProvider>
    </SettingsProvider>
  </StrictMode>
)
