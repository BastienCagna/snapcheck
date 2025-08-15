declare global {
    interface Window {
        qt: any;
        QWebChannel: any;
        pybridge: any;
    }
}

class PyBridgeService {
    private bridge: any = null;
    private isInitialized: boolean = false;

    async initialize(): Promise<void> {
        return new Promise((resolve, reject) => {
            if (typeof window.QWebChannel === 'undefined') {
                // Pas dans l'environnement Qt, simuler pour le développement
                console.log('QWebChannel not available, using mock');
                this.bridge = this.createMockBridge();
                this.isInitialized = true;
                resolve();
                return;
            }

            new window.QWebChannel(window.qt.webChannelTransport, (channel: any) => {
                console.log('QWebChannel initialized');
                this.bridge = channel.objects.pybridge;
                this.isInitialized = true;
                resolve();
            });

            // Timeout de sécurité
            setTimeout(() => {
                if (!this.isInitialized) {
                    reject(new Error('Failed to initialize PyBridge'));
                }
            }, 5000);
        });
    }

    private createMockBridge() {
        return {
            closeApplication: () => console.log('Mock closeApplication'),
        };
    }

    closeApplication(): void {
        if (this.bridge) {
            this.bridge.closeApplication();
        }
    }
}

export const pyBridgeService = new PyBridgeService();