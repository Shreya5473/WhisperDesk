"""
Floating "recording in progress" overlay.
"""

from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont

NUM_BARS = 9
BAR_WIDTH = 4
BAR_GAP = 3
BAR_MAX_HEIGHT = 28
BAR_MIN_HEIGHT = 4
ACCENT_RED = QColor("#FF3B30")
BG_DARK = QColor(18, 18, 20, 235)


class LevelMeter(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._levels = [BAR_MIN_HEIGHT] * NUM_BARS
        self._targets = [BAR_MIN_HEIGHT] * NUM_BARS
        width = NUM_BARS * (BAR_WIDTH + BAR_GAP)
        self.setFixedSize(width, BAR_MAX_HEIGHT)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate_step)
        self._timer.start(33)

    def set_level(self, level: float) -> None:
        level = max(0.0, min(1.0, level))
        for i in range(NUM_BARS):
            center_weight = 1.0 - abs(i - NUM_BARS / 2) / (NUM_BARS / 2) * 0.5
            variation = 0.7 + 0.6 * ((i * 37 + int(level * 100)) % 7) / 7
            target = BAR_MIN_HEIGHT + level * center_weight * variation * (BAR_MAX_HEIGHT - BAR_MIN_HEIGHT)
            self._targets[i] = max(BAR_MIN_HEIGHT, min(BAR_MAX_HEIGHT, target))

    def _animate_step(self) -> None:
        changed = False
        for i in range(NUM_BARS):
            diff = self._targets[i] - self._levels[i]
            if abs(diff) > 0.5:
                self._levels[i] += diff * 0.35
                changed = True
            else:
                self._levels[i] = self._targets[i]
        if changed:
            self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(ACCENT_RED)
        for i, height in enumerate(self._levels):
            x = i * (BAR_WIDTH + BAR_GAP)
            y = (BAR_MAX_HEIGHT - height) / 2
            painter.drawRoundedRect(int(x), int(y), BAR_WIDTH, int(height), 2, 2)


class RecordingOverlay(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 12, 20, 12)
        layout.setSpacing(12)

        self.mic_label = QLabel("\u25CF")
        mic_font = QFont()
        mic_font.setPointSize(16)
        self.mic_label.setFont(mic_font)
        self.mic_label.setStyleSheet(f"color: {ACCENT_RED.name()};")

        self.meter = LevelMeter()

        self.status_label = QLabel("Listening...")
        self.status_label.setStyleSheet("color: white; font-weight: 600; font-size: 13px;")

        layout.addWidget(self.mic_label)
        layout.addWidget(self.meter)
        layout.addWidget(self.status_label)
        self.setFixedSize(240, 56)

        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._pulse)
        self._pulse_on = True

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(BG_DARK)
        painter.drawRoundedRect(self.rect(), 28, 28)

    def _pulse(self) -> None:
        self._pulse_on = not self._pulse_on
        color = ACCENT_RED.name() if self._pulse_on else "#8B1A16"
        self.mic_label.setStyleSheet(f"color: {color};")

    def show_at_bottom_center(self) -> None:
        screen = QApplication.primaryScreen().geometry()
        x = screen.center().x() - self.width() // 2
        y = screen.bottom() - 140
        self.move(x, y)
        self.status_label.setText("Listening...")
        self.mic_label.setStyleSheet(f"color: {ACCENT_RED.name()};")
        self._pulse_timer.start(450)
        self.show()
        self.raise_()
        self.activateWindow()

    def show_transcribing(self, message: str = "Transcribing...") -> None:
        self._pulse_timer.stop()
        self.status_label.setText(message)
        self.meter.set_level(0.0)

    def hide_overlay(self) -> None:
        self._pulse_timer.stop()
        self.hide()

    def update_level(self, level: float) -> None:
        self.meter.set_level(level)