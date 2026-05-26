import sys
import subprocess
import time
import atexit
import requests
import argparse
import os.path as op

import PyQt5.QtWidgets as qw
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt, QTimer, QObject, pyqtSlot
from PyQt5.QtGui import QPixmap, QCursor, QIcon
from PyQt5.QtWebChannel import QWebChannel

from snapclient.constants import APP_ICON, FRONT_PATH, DEFAULT_PORT, DEFAULT_URL, SPLASH_PATH


class BottomBar(qw.QWidget):
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


class Bridge(QObject):
    _threshold_ms = 25.0
    _multiplier = 1.5
    _last_move_time = None

    def __init__(self, win, jwt: str = None):
        super().__init__()
        self.win = win
        self.jwt = jwt

    @pyqtSlot(result=str)
    def getJWT(self):
        """Return the JWT token for authentication."""
        return self.jwt if self.jwt else ""

    @pyqtSlot()
    def close(self):
        qw.QApplication.instance().quit()

    @pyqtSlot()
    def minimize(self):
        self.win.showMinimized()

    @pyqtSlot()
    def restore(self):
        self.win.showNormal()

    @pyqtSlot()
    def toggleWindowSize(self):
        if self.win.isMaximized():
            self.win.showNormal()
        else:
            self.win.showMaximized()

    @pyqtSlot()
    def maximize(self):
        self.win.showMaximized()

    @pyqtSlot(int, int)
    def moveWindowTo(self, x, y):
        self.win.moveWindowTo(x, y)

    @pyqtSlot()
    def startWindowDrag(self):
        self.win.startWindowDrag()

    @pyqtSlot()
    def stopWindowDrag(self):
        self.win.stopWindowDrag()


class MainWindow(qw.QMainWindow):
    url: str
    jwt: str

    def __init__(self, url: str, jwt: str = None):
        """
        Url: The URL to load in the web view.
        JWT: Authentification token to be sent to the server.
        """
        super().__init__()
        self.url = url
        self.jwt = jwt

        self.setWindowTitle("SnapCheck")
        self.setStyleSheet("background-color: #333; color: #ccc")

        # Remove the title bar and window frame (make it a frameless window)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        if op.exists(APP_ICON):
            self.setWindowIcon(QIcon(APP_ICON))

        # Create a QWebEngineView to display the web page
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))

        # Change some settings to avoid CORS issues
        self.browser.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.browser.settings().setAttribute(QWebEngineSettings.DnsPrefetchEnabled, True)

        # Set the central widget
        central_widget = qw.QWidget()
        m = 4
        central_widget.setContentsMargins(m, m, m, m)
        layout = qw.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(0)  # Remove spacing between widgets
        layout.addWidget(self.browser)
        layout.setStretchFactor(self.browser, 1)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.resizing = None
        self.setMouseTracking(True)
        central_widget.setMouseTracking(True)
        self.browser.setMouseTracking(True)

        self.showMaximized()

        self.channel = QWebChannel()
        self.bridge = Bridge(self, jwt=jwt)
        self.channel.registerObject("bridge", self.bridge)
        self.browser.page().setWebChannel(self.channel)

        # Variables for window dragging
        self.dragging = False
        self.drag_position = None

        # µUse a timer to periodically verify mouse position during drag
        self.drag_timer = QTimer()
        self.drag_timer.timeout.connect(self.checkMousePosition)
        self.drag_timer.setInterval(16)  # ~60fps

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        # Handle window dragging if enabled
        if self.dragging and self.drag_position is not None:
            from PyQt5.QtGui import QCursor

            print(f"🐛 DEBUG: mouseMoveEvent - dragging mode active")
            new_pos = QCursor.pos() - self.drag_position
            print(f"🐛 DEBUG: moving window to {new_pos}")
            self.move(new_pos)
            return

        w = 3  # half border width
        x, y = event.globalPos().x(), event.globalPos().y()
        geo = self.geometry()
        dist_to_top = abs(y - geo.top())
        dist_to_left = abs(x - geo.left())
        dist_to_right = abs(x - geo.right())
        dist_to_bottom = abs(y - geo.bottom())
        if dist_to_top <= w:
            if dist_to_left <= w:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                self.resizing = "top-left"
            elif dist_to_right <= w:
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
                self.resizing = "top-right"
            else:
                self.setCursor(Qt.CursorShape.SizeVerCursor)
                self.resizing = "top"
        elif dist_to_bottom <= w:
            if dist_to_left <= w:
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
                self.resizing = "bottom-left"
            elif dist_to_right <= w:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                self.resizing = "bottom-right"
            else:
                self.setCursor(Qt.CursorShape.SizeVerCursor)
                self.resizing = "bottom"
        elif dist_to_left <= w:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
            self.resizing = "left"
        elif dist_to_right <= w:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
            self.resizing = "right"
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.resizing = None
        # print(f"Curseur déplacé : x={x}, y={y}", self.resizing, dist_to_top, dist_to_left, dist_to_right, dist_to_bottom)
        # Store the last resizing direction and position when mouse is pressed
        if not hasattr(self, "_resize_active"):
            self._resize_active = False
            self._resize_start_pos = None

        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.resizing and not self._resize_active:
                # Start resizing
                self._resize_active = True
                self._resize_start_pos = event.globalPos()
                self._resize_start_geo = self.geometry()
                self._resize_direction = self.resizing

            if self._resize_active:
                # Continue resizing even if cursor leaves the border
                new_geo = self._resize_start_geo
                factor = 0.5
                dx = int(factor * (event.globalPos().x() - self._resize_start_pos.x()))
                dy = int(factor * (event.globalPos().y() - self._resize_start_pos.y()))
                geo = new_geo
            else:
                return

            if "left" in self._resize_direction:
                geo.setLeft(geo.left() + dx)
            if "right" in self._resize_direction:
                geo.setRight(geo.right() + dx)
            if "top" in self._resize_direction:
                geo.setTop(geo.top() + dy)
            if "bottom" in self._resize_direction:
                geo.setBottom(geo.bottom() + dy)

            min_width = self.minimumWidth()
            min_height = self.minimumHeight()
            if geo.width() < min_width:
                if "left" in self._resize_direction:
                    geo.setLeft(geo.right() - min_width)
                else:
                    geo.setRight(geo.left() + min_width)
            if geo.height() < min_height:
                if "top" in self._resize_direction:
                    geo.setTop(geo.bottom() - min_height)
                else:
                    geo.setBottom(geo.top() + min_height)
            self.setGeometry(geo)
            event.accept()
        else:
            self._resize_active = False

    def showMaximized(self):
        super().showMaximized()

    def showNormal(self):
        super().showNormal()

    def showMinimized(self):
        super().showMinimized()

    def startWindowDrag(self):
        """Start window drag mode - will be handled by timer."""
        self.drag_position = QCursor.pos() - self.pos()
        self.dragging = True
        self.drag_timer.start()

    def stopWindowDrag(self):
        """Stop window drag mode."""
        self.dragging = False
        self.drag_timer.stop()

    def checkMousePosition(self):
        """Check mouse position and move window if dragging."""
        if self.dragging and self.drag_position is not None:
            new_pos = QCursor.pos() - self.drag_position
            self.move(new_pos)


def vite_commandline(port):
    """Return the command line to start the Vite development server."""
    return f"npm run dev -- --port {str(port)}"


def start_vite_server(port) -> subprocess.Popen:
    """Start the Vite development server."""
    try:
        return subprocess.Popen(vite_commandline(port).split(" "), cwd=FRONT_PATH)
    except Exception as e:
        print(f"Failed to start Vite server: {e}")


def stop_vite_server(process: subprocess.Popen, port: int):
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

    parser = argparse.ArgumentParser(description="SnapClient Application")
    parser.add_argument("--jwt", type=str, default=None, help="Authentification token.")
    args = parser.parse_args()

    # Launch the PyQt application
    app = qw.QApplication(sys.argv)

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
        print(".", end="", flush=True)
        if response and response.status_code == 200:
            # Server is ready
            break
        time.sleep(0.2)
    else:
        print(f"Server dind't start in time.")
        sys.exit(1)

    window = MainWindow(url, jwt=args.jwt)
    splash.finish(window)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
