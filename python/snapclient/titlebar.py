from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtSvg import QSvgRenderer
import os.path as op
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
from snapclient.constants import ASSETS_PATH, CLOSE_ICON, ICON_COLOR, MAXIMIZE_ICON, MINIMIZE_ICON, NORMAL_ICON
# from snapclient.constants import CLOSE_ICON, RESTORE_ICON, MINIMIZE_ICON

def svg_icon_with_color(svg_path: str, color: str, size=(24, 24)) -> QIcon:
    """Load an SVG file and color it with the specified color."""
    renderer = QSvgRenderer(svg_path)
    pixmap = QPixmap(size[0], size[1])
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_Source)
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return QIcon(pixmap)


class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)
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
        min_icon = svg_icon_with_color(MINIMIZE_ICON, ICON_COLOR)
        self.min_button.setIcon(min_icon)
        self.min_button.clicked.connect(self.window().showMinimized)

        # Max button
        self.max_button = QToolButton(self)
        max_icon = svg_icon_with_color(MAXIMIZE_ICON, ICON_COLOR)
        self.max_button.setIcon(max_icon)
        self.max_button.clicked.connect(self.window().showMaximized)

        # Close button
        self.close_button = QToolButton(self)
        close_icon = svg_icon_with_color(CLOSE_ICON, ICON_COLOR)
        self.close_button.setIcon(close_icon)
        self.close_button.clicked.connect(self.window().close)

        # Normal button
        self.normal_button = QToolButton(self)
        normal_icon = svg_icon_with_color(NORMAL_ICON, ICON_COLOR)
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
        # Window manual resizing
        window = self.window()
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if click is in bottom-right corner (resize zone)
            margin = 12
            rect = self.rect()
            if event.pos().x() >= rect.width() - margin and event.pos().y() >= rect.height() - margin and not window.isMaximized():
                self.resizing = True
                self.resize_start_pos = event.globalPos()
                self.resize_start_size = window.size()
                event.accept()
                return
            self.initial_pos = event.globalPos() - window.frameGeometry().topLeft()
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.initial_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.window().move(event.globalPos() - self.initial_pos)
 

    def mouseReleaseEvent(self, event):
        self.initial_pos = None
        event.accept()

        # Window manual resizing
        # self.initial_pos = None
        # if hasattr(self, 'resizing'):
        #     self.resizing = False
        # event.accept()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            window = self.window()
            if window.isMaximized():
                window.showNormal()
            else:
                window.showMaximized()
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
                    # Correction: Commented out problematic block to prevent infinite loop
                    # if not self.window().isMaximized() and abs(geo.top() - screen_geo.top()) <= margin:
                    #     window.showMaximized()
                    # elif window.isMaximized():
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

