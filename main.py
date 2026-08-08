"""
WhisperDesk entry point.
"""

import sys
import signal
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QTimer

from src.whisperdesk.frontend.recording_overlay import RecordingOverlay
from src.whisperdesk.frontend.controller import AppController
from src.whisperdesk.frontend.settings_window import SettingsWindow


def make_tray_icon() -> QIcon:
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
    app.setQuitOnLastWindowClosed(False)

    signal.signal(signal.SIGINT, lambda *args: app.quit())
    signal_timer = QTimer()
    signal_timer.timeout.connect(lambda: None)
    signal_timer.start(200)

    overlay = RecordingOverlay()
    controller = AppController()

    # Dictation flow
    controller.recording_started.connect(overlay.show_at_bottom_center)
    controller.level_changed.connect(overlay.update_level)
    controller.recording_stopped.connect(lambda: overlay.show_transcribing("Transcribing..."))
    controller.transcript_ready.connect(lambda text: overlay.hide_overlay())

    # Voice query (RAG) flow -- reuses the same overlay, different labels
    controller.query_started.connect(overlay.show_at_bottom_center)
    controller.query_thinking.connect(lambda: overlay.show_transcribing("Thinking..."))
    controller.query_answered.connect(lambda answer: overlay.hide_overlay())

    tray = QSystemTrayIcon(make_tray_icon())
    tray.setToolTip("WhisperDesk")
    tray.setVisible(True)

    settings_window_ref = {"window": None}

    def open_settings():
        # Keep a reference so the window isn't garbage-collected
        # immediately after opening (a common PyQt gotcha).
        settings_window_ref["window"] = SettingsWindow(controller.settings_manager)
        settings_window_ref["window"].show()

    menu = QMenu()
    settings_action = menu.addAction("Settings...")
    settings_action.triggered.connect(open_settings)
    menu.addSeparator()
    quit_action = menu.addAction("Quit WhisperDesk")
    quit_action.triggered.connect(app.quit)
    tray.setContextMenu(menu)
    tray.show()

    controller.start()
    print("WhisperDesk running.")
    print("  Hold Cmd+Shift+Space to dictate.")
    print("  Hold Cmd+Shift+A to ask a question about your notes.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()