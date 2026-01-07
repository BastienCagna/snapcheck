import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { SnapSessionProvider } from './contexts/SnapSessionContext';
import { ModalProvider } from './contexts/ModalContext';
import { SettingsProvider } from './contexts/SettingsContext';
import { AppDataProvider } from './contexts/AppDataContext';
import { OpenAPI } from './api/core/OpenAPI';
import './index.css'
import App from './App.tsx'


// Initialize JWT from Qt bridge if available
const initializeJWT = async () => {
  if ((window as any).qt?.webChannelTransport) {
    return new Promise<void>((resolve) => {
      // @ts-ignore
      // new (window as any).qt.webChannelTransport.QWebChannel((window as any).qt.webChannelTransport, (channel: any) => {
      //   const bridge = channel.objects.bridge;
      //   bridge.getJWT((jwt: string) => {
      //     if (jwt) {
      //       OpenAPI.TOKEN = jwt;
      //       console.log('JWT initialized from Qt bridge');
      //     }
      //     resolve();
      //   });
      // });
        new QWebChannel((window as any).qt.webChannelTransport, function (channel: any) {
              (window as any).bridge = channel.objects.bridge;
              (window as any).bridge.getJWT((jwt: string) => {
                if (jwt) {
                  OpenAPI.TOKEN = jwt;
                  OpenAPI.HEADERS = { Authorization: `Bearer ${jwt}` };
                  console.error('JWT initialized from Qt bridge to', jwt);
                }
                else {
                  console.error('No JWT received from Qt bridge');
                }
                resolve();
          });
        });
    });
  } else {
    // For web-only testing, check localStorage or environment
    const token = localStorage.getItem('jwt');
    if (token) {
      OpenAPI.TOKEN = token;
      OpenAPI.HEADERS = { Authorization: `Bearer ${token}` };
    }
    console.log("local JWT initialized to ", token);
  }
};

// Initialize before rendering
initializeJWT().then(() => {
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
});

