from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineWidgets import QWebEngineSettings

from PyQt5.QtCore import QUrl
import sys
import subprocess
import time
import atexit
from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPixmap
import os.path as op

ASSETS_PATH = op.abspath(op.join(op.dirname(__file__), "assets"))
SPLASH_PATH = op.join(ASSETS_PATH, "splash.jpg")

FRONT_PATH = op.abspath(op.join(op.dirname(__file__), "..", "..", "snapcheck-front"))
DEFAULT_PORT = 3000
DEFAULT_URL = "127.0.0.1"

class MainWindow(QMainWindow):
    def __init__(self, url: str):
        super().__init__()
        self.setWindowTitle("SnapCheck")

        # Create a QWebEngineView to display the web page
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))

        self.browser.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        # self.browser.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True) # Already set by default
        self.browser.settings().setAttribute(QWebEngineSettings.DnsPrefetchEnabled, True)

        # Set the central widget
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(0)  # Remove spacing between widgets
        layout.addWidget(self.browser)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


def vite_commandline(port):
    """Return the command line to start the Vite development server."""
    return f"npm run dev -- --port {str(port)}"

def start_vite_server(port) -> subprocess.Popen:
    """Start the Vite development server."""
    try:
        return subprocess.Popen(vite_commandline(port).split(" "), cwd=FRONT_PATH)
    except Exception as e:
        print(f"Failed to start Vite server: {e}")

def stop_vite_server(process:subprocess.Popen, port: int):
    """Stop the Vite development server."""
    try:
        process.terminate()
        process.wait()
        # Kill Vite server instance
        cmd = ["pkill", "-f", f"node {op.join(FRONT_PATH, 'node_modules', '.bin', 'vite')} --port {port}"]
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"Failed to stop Vite server: {e}")


def main():
    port = DEFAULT_PORT
    url = f"http://{DEFAULT_URL}:{port}"

    # Launch the PyQt application
    app = QApplication(sys.argv)

    # Create a splash screen
    splash_pix = QPixmap(SPLASH_PATH)  # Replace with your splash image path
    splash = QSplashScreen(splash_pix)

    splash.show()

    # Process events to ensure the splash screen is displayed
    # app.processEvents()
    # Start the Vite server
    process = start_vite_server(port=port)
    # Close the server when exiting the program
    atexit.register(lambda: stop_vite_server(process, port))

    time.sleep(0.4) # Waiting 250ms seems to be enough for the server to start
    # Wait for the Vite server to be ready
    # print('Waiting for the Vite server to start', end="")
    # for _ in range(100):
    #     try:
    #         response = requests.get(url)
    #     except requests.exceptions.ConnectionError:
    #         response = None
    #     print('.', end='', flush=True)
    #     if response and response.status_code == 200:
    #         # Server is ready
    #         break
    #     time.sleep(0.25)
    # else:
    #     print(f"Server dind't start in time.")
    #     sys.exit(1)

    window = MainWindow(url)
    splash.finish(window)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()