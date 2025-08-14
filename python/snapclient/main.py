from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineWidgets import QWebEngineSettings

from PyQt5.QtCore import QUrl, Qt
import sys
import subprocess
import time
import atexit
import PyQt5.QtWidgets as qw
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtGui import QPixmap
import os.path as op
import requests
from snapclient.titlebar import CustomTitleBar

ASSETS_PATH = op.abspath(op.join(op.dirname(__file__), "assets"))
SPLASH_PATH = op.join(ASSETS_PATH, "splash.jpg")

FRONT_PATH = op.abspath(op.join(op.dirname(__file__), "..", "..", "snapcheck-front"))
DEFAULT_PORT = 3000
DEFAULT_URL = "127.0.0.1"


class BottomBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: #333; color: #ccc; font-size: 10px;")
        self.setFixedHeight(20)

        # Create a bottom bar
        layout = qw.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(5)  # Add spacing between widgets

        # Add a "Setting" button
        config_button = qw.QPushButton("Settings")
        layout.addWidget(config_button)

        # Add a connection status label
        connection_status = qw.QLabel("Status: Connected to localhost")
        layout.addWidget(connection_status)

        # Align items to the left and use the smallest space necessary
        layout.addStretch()  # Add a stretchable space to push items to the left
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self, url: str):
        super().__init__()
        self.setWindowTitle("SnapCheck")
        self.setStyleSheet("background-color: #333; color: #ccc;")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.title_bar = CustomTitleBar(self)

        # Create a QWebEngineView to display the web page
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))

        # Change some settings to avoid CORS issues
        self.browser.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.browser.settings().setAttribute(QWebEngineSettings.DnsPrefetchEnabled, True)

        # Set the central widget
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(0)  # Remove spacing between widgets
        layout.addWidget(self.title_bar)
        layout.setStretchFactor(self.title_bar, 0)  #  Do not extend the title bar
        layout.addWidget(self.browser)
        layout.setStretchFactor(self.browser, 1)

        # # Add the bottom status bar
        # self.bottom_bar = BottomBar()
        # layout.addWidget(self.bottom_bar)
        # layout.setStretch(0, 1)

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
    splash = qw.QSplashScreen(splash_pix)

    splash.show()

    # Process events to ensure the splash screen is displayed
    # app.processEvents()
    # Start the Vite server
    process = start_vite_server(port=port)
    # Close the server when exiting the program
    atexit.register(lambda: stop_vite_server(process, port))

    # Wait for the Vite server to be ready
    for i in range(100):
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            response = None
        print('.', end='', flush=True)
        if response and response.status_code == 200:
            # Server is ready
            break
        time.sleep(0.2)
    else:
        print(f"Server dind't start in time.")
        sys.exit(1)

    window = MainWindow(url)
    splash.finish(window)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()