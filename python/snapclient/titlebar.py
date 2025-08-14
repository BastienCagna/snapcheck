from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStyle,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.initial_pos = None
        title_bar_layout = QHBoxLayout(self)
        title_bar_layout.setContentsMargins(1, 1, 1, 1)
        title_bar_layout.setSpacing(2)
        self.title = QLabel(f"{self.__class__.__name__}", self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet(
            """
        QLabel { text-transform: uppercase; font-size: 10pt; margin-left: 48px; }
        """
        )

        if title := parent.windowTitle():
            self.title.setText(title)
        title_bar_layout.addWidget(self.title)
        # Min button
        self.min_button = QToolButton(self)
        min_icon = QIcon()
        min_icon.addFile("min.svg")
        self.min_button.setIcon(min_icon)
        self.min_button.clicked.connect(self.window().showMinimized)

        # Max button
        self.max_button = QToolButton(self)
        max_icon = QIcon()
        max_icon.addFile("max.svg")
        self.max_button.setIcon(max_icon)
        self.max_button.clicked.connect(self.window().showMaximized)

        # Close button
        self.close_button = QToolButton(self)
        close_icon = QIcon()
        close_icon.addFile("close.svg")  # Close has only a single state.
        self.close_button.setIcon(close_icon)
        self.close_button.clicked.connect(self.window().close)

        # Normal button
        self.normal_button = QToolButton(self)
        normal_icon = QIcon()
        normal_icon.addFile("normal.svg")
        self.normal_button.setIcon(normal_icon)
        self.normal_button.clicked.connect(self.window().showNormal)
        self.normal_button.setVisible(False)
        # Add buttons
        buttons = [
            self.min_button,
            self.normal_button,
            self.max_button,
            self.close_button,
        ]
        for button in buttons:
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(16, 16))
            button.setStyleSheet(
                """QToolButton {
                    border: 1px solid gray;
                    padding: 2px;
                }
                """
            )
            title_bar_layout.addWidget(button)

        self.initial_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.initial_pos = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.initial_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.window().move(event.globalPos() - self.initial_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.initial_pos = None
        event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            window = self.window()
            if window.isFullScreen():
                window.showNormal()
            else:
                window.showFullScreen()
            event.accept()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.WindowStateChange:
            state = self.window().windowState()
            self.window_state_changed(state)
        elif event.type() == QEvent.Type.Move:
            if self.window().isMinimized():
                return False
            window = self.window()
            screen = window.screen()
            if screen:
                geo = window.geometry()
                screen_geo = screen.availableGeometry()
                margin = 30  # pixels tolerance
                if not self.window().isFullScreen() and abs(geo.top() - screen_geo.top()) <= margin:
                    window.showFullScreen()
                # elif window.isFullScreen():
                #     window.showNormal()
                #     # Move window slightly down to avoid snapping back to fullscreen
                #     offset = 30
                #     window.move(window.x(), screen_geo.top() + offset)
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        self.window().installEventFilter(self)
        super().showEvent(event)

    def window_state_changed(self, state):
        if state == Qt.WindowState.WindowMaximized:
            self.normal_button.setVisible(True)
            self.max_button.setVisible(False)
        else:
            self.normal_button.setVisible(False)
            self.max_button.setVisible(True)