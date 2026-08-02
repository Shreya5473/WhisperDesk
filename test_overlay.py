import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from src.whisperdesk.frontend.recording_overlay import RecordingOverlay

app = QApplication(sys.argv)

overlay = RecordingOverlay()

print("Showing overlay NOW...")
overlay.show_at_bottom_center()

# Keep it on screen for 8 full seconds, no hotkey needed
QTimer.singleShot(8000, app.quit)

sys.exit(app.exec())