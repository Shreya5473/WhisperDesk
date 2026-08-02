"""
WhisperDesk entry point.

Sets up the Qt application, system tray icon, and the recording
overlay, then wires everything together via AppController's signals.
"""

import sys
import signal
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QTimer

from src.whisperdesk.frontend.recording_overlay import RecordingOverlay
from src.whisperdesk.frontend.controller import AppController


def make_tray_icon() -> QIcon:
    """Draws a simple red circle icon in code, so we don't need an
    external image file for the tray/menu bar icon."""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#FF3B30"))
    painter.drawEllipse(8, 8, 48, 48)
    painter.end()
    return QIcon(pixmap)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # keep running with no windows open (tray-only app)

    signal.signal(signal.SIGINT, lambda *args: app.quit())

    # Qt's event loop doesn't check for OS signals on its own -- this
    # timer forces Python to "wake up" every 200ms and notice the
    # signal was received.
    signal_timer = QTimer()
    signal_timer.timeout.connect(lambda: None)
    signal_timer.start(200)

    overlay = RecordingOverlay()
    controller = AppController()

    # Wiring: connect controller signals (safe, main-thread) to overlay methods.
    controller.recording_started.connect(overlay.show_at_bottom_center)
    controller.level_changed.connect(overlay.update_level)
    controller.recording_stopped.connect(overlay.show_transcribing)
    controller.transcript_ready.connect(lambda text: overlay.hide_overlay())

    tray = QSystemTrayIcon(make_tray_icon())
    tray.setToolTip("WhisperDesk")
    tray.setVisible(True)

    menu = QMenu()
    quit_action = menu.addAction("Quit WhisperDesk")
    quit_action.triggered.connect(app.quit)
    tray.setContextMenu(menu)
    tray.show()

    controller.start()
    print("WhisperDesk running in the background. Hold Cmd+Shift+Space to dictate.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()