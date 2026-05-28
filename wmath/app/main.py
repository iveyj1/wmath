"""Application entry point."""

from __future__ import annotations

import os
import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from wmath.app.main_window import MainWindow


def _quiet_known_qt_warnings() -> None:
    """Suppress noisy platform warnings that do not affect the prototype."""

    rule = "qt.accessibility.atspi.warning=false"
    current = os.environ.get("QT_LOGGING_RULES", "")
    if rule not in current.split(";"):
        os.environ["QT_LOGGING_RULES"] = f"{current};{rule}" if current else rule


def _scale_app_font(app: QApplication, factor: float = 1.5) -> None:
    """Increase default UI font size for prototype readability."""

    font = QFont(app.font())
    point_size = font.pointSizeF()
    if point_size <= 0:
        point_size = 10.0
    font.setPointSizeF(point_size * factor)
    app.setFont(font)


def main(argv: list[str] | None = None) -> int:
    """Run the desktop prototype."""

    _quiet_known_qt_warnings()

    app = QApplication(sys.argv if argv is None else argv)
    _scale_app_font(app)
    app.setApplicationName("wmath")
    app.setOrganizationName("wmath")

    window = MainWindow()
    window.resize(1100, 760)
    window.show()

    return app.exec()
