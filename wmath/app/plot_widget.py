"""Lightweight Qt plot widget for core plot artifacts."""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from wmath.app.config import AppConfig
from wmath.core.models import PlotArtifact


class PlotWidget(QWidget):
    """Draw a simple line/point plot for a core PlotArtifact."""

    def __init__(
        self,
        artifact: PlotArtifact,
        config: AppConfig | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.artifact = artifact
        self.config = config or AppConfig()
        requested_height = artifact.requested_size[1] if artifact.requested_size is not None else self.config.plotDefaultHeight
        self.setMinimumWidth(0)
        self.setMinimumHeight(max(self.config.plotMinHeight, min(self.config.plotMaxHeight, requested_height)))
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        outer = self.config.plotOuterMargin
        available = QRectF(self.rect().adjusted(outer, outer, -outer, -outer))
        requested_width = self.artifact.requested_size[0] if self.artifact.requested_size is not None else None
        full_width = available.width()
        if requested_width is not None:
            full_width = min(full_width, max(80.0, float(requested_width)))
        full = QRectF(available.left(), available.top(), full_width, available.height())
        painter.fillRect(full, QColor("white"))
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawRect(full)

        plot_rect = QRectF(
            full.adjusted(
                self.config.plotLeftGutter,
                self.config.plotTopGutter,
                -self.config.plotRightGutter,
                -self.config.plotBottomGutter,
            )
        )
        if plot_rect.width() <= 0 or plot_rect.height() <= 0:
            return

        painter.setPen(QPen(QColor("#666666"), 1))
        painter.drawLine(plot_rect.bottomLeft(), plot_rect.bottomRight())
        painter.drawLine(plot_rect.bottomLeft(), plot_rect.topLeft())

        mapped = [self._map_point(x, y, plot_rect) for x, y in self.artifact.points]
        painter.save()
        try:
            painter.setClipRect(plot_rect)
            if len(mapped) >= 2:
                path = QPainterPath(mapped[0])
                for point in mapped[1:]:
                    path.lineTo(point)
                painter.setPen(QPen(QColor("#1f77b4"), 2))
                painter.drawPath(path)

            painter.setPen(QPen(QColor("#1f77b4"), 1))
            painter.setBrush(QColor("#1f77b4"))
            for point in mapped:
                painter.drawEllipse(point, 3.0, 3.0)
        finally:
            painter.restore()

        painter.setPen(QPen(QColor("#333333"), 1))
        x_min, x_max = self.artifact.x_range
        y_min, y_max = self.artifact.y_range
        painter.drawText(full.left() + 4, round(plot_rect.bottom()), _format_number(y_min))
        painter.drawText(full.left() + 4, round(plot_rect.top() + 8), _format_number(y_max))
        painter.drawText(round(plot_rect.left()), full.bottom() - 4, _format_number(x_min))
        painter.drawText(round(plot_rect.right()) - 40, full.bottom() - 4, _format_number(x_max))

    def _map_point(self, x: float, y: float, rect: QRectF) -> QPointF:
        x_min, x_max = self.artifact.x_range
        y_min, y_max = self.artifact.y_range
        x_ratio = (x - x_min) / (x_max - x_min)
        y_ratio = (y - y_min) / (y_max - y_min)
        x_pos = rect.left() + x_ratio * rect.width()
        y_pos = rect.bottom() - y_ratio * rect.height()
        return QPointF(x_pos, y_pos)


def _format_number(value: float) -> str:
    if abs(value - round(value)) < 1e-12:
        return str(int(round(value)))
    return f"{value:.6g}"
