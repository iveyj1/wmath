"""Main application window for the PySide6 prototype."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtGui import QAction, QFont, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from wmath.app.config import load_app_config
from wmath.app.plot_widget import PlotWidget
from wmath.core import (
    EvalInput,
    EvalOutput,
    evaluate,
    format_rendered_row,
    format_warning_bar,
)
from wmath.storage import (
    SheetMetadata,
    load_metadata,
    load_mru,
    read_sheet,
    save_metadata,
    save_mru,
    update_mru,
    write_sheet,
)


class MainWindow(QMainWindow):
    """Prototype shell with source and rendered panes."""

    def __init__(self) -> None:
        super().__init__()
        self._current_file: Path | None = None
        self._dirty = False
        self._metadata = SheetMetadata()
        self._mru_files = load_mru()
        self._last_output: EvalOutput | None = None
        self._active_line = 0
        self._syncing_scroll = False
        self._rendered_row_widgets: list[QWidget] = []
        self._app_config = load_app_config()

        self._saved_source = ""

        self.setWindowTitle("wmath — Untitled")
        self._build_actions()
        self._build_ui()
        self._wire_signals()
        self._install_shortcuts()
        self._recalculate()

    def _build_actions(self) -> None:
        self.new_action = QAction("New", self)
        self.new_action.setShortcut(QKeySequence.New)
        self.new_action.triggered.connect(self.new_file)

        self.open_action = QAction("Open", self)
        self.open_action.setShortcut(QKeySequence.Open)
        self.open_action.triggered.connect(self.open_file)

        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.triggered.connect(self.save_file)

        self.save_as_action = QAction("Save As", self)
        self.save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.save_as_action.triggered.connect(self.save_file_as)

        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.Undo)

        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcuts([QKeySequence.Redo, QKeySequence("Ctrl+Shift+Z")])

    def _build_ui(self) -> None:
        root = QWidget(self)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        header = QWidget(root)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.filename_label = QLabel("Untitled", header)
        self.filename_label.setObjectName("filenameLabel")
        self.filename_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header_layout.addWidget(self.filename_label)

        self.status_label = QLabel("0 lines · ok · saved", header)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(self.status_label)

        self.show_all_values = QCheckBox("All values", header)
        self.show_all_values.setToolTip("Show all evaluated values, ignoring `|` display markers")
        self.show_all_values.toggled.connect(self._on_metadata_controls_changed)
        header_layout.addWidget(self.show_all_values)

        header_layout.addWidget(QLabel("Value %", header))
        self.value_column_percent = QSpinBox(header)
        self.value_column_percent.setRange(40, 90)
        self.value_column_percent.setSingleStep(5)
        self.value_column_percent.setToolTip("Approximate value column position in rendered pane")
        self.value_column_percent.valueChanged.connect(self._on_metadata_controls_changed)
        header_layout.addWidget(self.value_column_percent)

        header_layout.addWidget(QLabel("Sig", header))
        self.significant_figures = QSpinBox(header)
        self.significant_figures.setRange(3, 15)
        self.significant_figures.setToolTip("Rendered number significant figures")
        self.significant_figures.valueChanged.connect(self._on_metadata_controls_changed)
        header_layout.addWidget(self.significant_figures)

        header_layout.addWidget(QLabel("Sci", header))
        self.scientific_magnitude = QSpinBox(header)
        self.scientific_magnitude.setRange(3, 12)
        self.scientific_magnitude.setToolTip("Use scientific notation outside 10^±this magnitude")
        self.scientific_magnitude.valueChanged.connect(self._on_metadata_controls_changed)
        header_layout.addWidget(self.scientific_magnitude)

        header_layout.addWidget(QLabel("Font", header))
        self.font_point_size = QDoubleSpinBox(header)
        self.font_point_size.setRange(6.0, 36.0)
        self.font_point_size.setSingleStep(0.5)
        self.font_point_size.setToolTip("Rendered font size; editor is about 8% smaller")
        self.font_point_size.valueChanged.connect(self._on_metadata_controls_changed)
        header_layout.addWidget(self.font_point_size)
        self._sync_metadata_controls()

        for action in (self.new_action, self.open_action, self.save_action, self.save_as_action):
            button = QToolButton(header)
            button.setDefaultAction(action)
            header_layout.addWidget(button)

        layout.addWidget(header)

        self.mru_bar = QWidget(root)
        self.mru_bar.setObjectName("mruBar")
        self.mru_layout = QHBoxLayout(self.mru_bar)
        self.mru_layout.setContentsMargins(0, 0, 0, 0)
        self.mru_layout.setSpacing(4)
        layout.addWidget(self.mru_bar)
        self._refresh_mru_bar()

        self.warning_bar = QLabel("", root)
        self.warning_bar.setObjectName("warningBar")
        self.warning_bar.setWordWrap(True)
        self.warning_bar.setStyleSheet("QLabel#warningBar { padding: 4px; background: #fff3cd; }")
        self.warning_bar.setVisible(False)
        layout.addWidget(self.warning_bar)

        self.splitter = QSplitter(Qt.Orientation.Horizontal, root)
        self.splitter.setChildrenCollapsible(False)

        self.editor = QPlainTextEdit(self.splitter)
        self.editor.setPlaceholderText("Enter wmath source here…")
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.editor.setPlainText("length = 2 m\nwidth = 3 m\narea = length * width |")
        self.editor.setFont(self._editor_font())
        self.editor.document().setDocumentMargin(self._app_config.editorDocumentMargin)

        self.rendered_content = QWidget(self.splitter)
        self.rendered_content.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        self.rendered_layout = QVBoxLayout(self.rendered_content)
        self.rendered_layout.setContentsMargins(0, 0, 0, 0)
        self.rendered_layout.setSpacing(self._app_config.renderedLayoutSpacing)

        self.rendered_scroll = QScrollArea(self.splitter)
        self.rendered_scroll.setWidgetResizable(True)
        self.rendered_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.rendered_scroll.setWidget(self.rendered_content)

        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.rendered_scroll)
        self.splitter.setSizes([550, 550])
        layout.addWidget(self.splitter, stretch=1)

        self.setCentralWidget(root)

    def _wire_signals(self) -> None:
        self.editor.textChanged.connect(self._on_text_changed)
        self.editor.cursorPositionChanged.connect(self._update_active_line)
        self.editor.verticalScrollBar().valueChanged.connect(self._sync_render_scroll)
        self.rendered_scroll.verticalScrollBar().valueChanged.connect(self._sync_editor_scroll)
        self.splitter.splitterMoved.connect(lambda _pos, _index: self._rerender_current_output())
        self.undo_action.triggered.connect(self.editor.undo)
        self.redo_action.triggered.connect(self.editor.redo)

    def _install_shortcuts(self) -> None:
        for action in (
            self.new_action,
            self.open_action,
            self.save_action,
            self.save_as_action,
            self.undo_action,
            self.redo_action,
        ):
            self.addAction(action)

    def new_file(self) -> None:
        if not self._confirm_discard_dirty():
            return
        with QSignalBlocker(self.editor):
            self.editor.clear()
        self._current_file = None
        self._saved_source = ""
        self._dirty = False
        self._metadata = SheetMetadata()
        self._sync_metadata_controls()
        self._recalculate(mark_dirty=False)

    def open_file(self) -> None:
        if not self._confirm_discard_dirty():
            return

        path_text, _ = QFileDialog.getOpenFileName(
            self,
            "Open wmath file",
            str(self._current_file.parent if self._current_file else Path.home()),
            "wmath files (*.wmath);;All files (*)",
        )
        if path_text:
            self._load_file(Path(path_text))

    def save_file(self) -> None:
        if self._current_file is None:
            self.save_file_as()
            return
        self._save_to_path(self._current_file)

    def save_file_as(self) -> None:
        path_text, _ = QFileDialog.getSaveFileName(
            self,
            "Save wmath file",
            str(self._current_file or Path.home() / "untitled.wmath"),
            "wmath files (*.wmath);;All files (*)",
        )
        if not path_text:
            return

        path = Path(path_text)
        if path.suffix == "":
            path = path.with_suffix(".wmath")
        self._save_to_path(path)

    def _load_file(self, path: Path) -> None:
        try:
            source = read_sheet(path)
        except OSError as exc:
            QMessageBox.critical(self, "Open failed", f"Could not open {path}:\n{exc}")
            return

        self._current_file = path.expanduser().resolve()
        self._metadata = load_metadata(self._current_file)
        self._sync_metadata_controls()
        with QSignalBlocker(self.editor):
            self.editor.setPlainText(source)
        self._saved_source = source
        self._dirty = False
        self._mru_files = update_mru(self._mru_files, self._current_file)
        save_mru(self._mru_files)
        self._refresh_mru_bar()
        self._recalculate(mark_dirty=False)

    def _save_to_path(self, path: Path) -> None:
        path = path.expanduser().resolve()
        try:
            write_sheet(path, self.editor.toPlainText())
            save_metadata(path, self._metadata)
        except OSError as exc:
            QMessageBox.critical(self, "Save failed", f"Could not save {path}:\n{exc}")
            return

        self._current_file = path
        self._saved_source = self.editor.toPlainText()
        self._dirty = False
        self._mru_files = update_mru(self._mru_files, path)
        save_mru(self._mru_files)
        self._refresh_mru_bar()
        self._update_status()

    def _confirm_discard_dirty(self) -> bool:
        if not self._dirty:
            return True

        choice = QMessageBox.question(
            self,
            "Discard unsaved changes?",
            "The current document has unsaved changes. Discard them?",
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        return choice == QMessageBox.StandardButton.Discard

    def _refresh_mru_bar(self) -> None:
        while self.mru_layout.count():
            item = self.mru_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        label = QLabel("Recent files:", self.mru_bar)
        self.mru_layout.addWidget(label)

        if not self._mru_files:
            none_label = QLabel("none", self.mru_bar)
            self.mru_layout.addWidget(none_label)
        else:
            for path in self._mru_files:
                button = QPushButton(path.name, self.mru_bar)
                button.setToolTip(str(path))
                button.clicked.connect(lambda _checked=False, p=path: self._open_mru_file(p))
                self.mru_layout.addWidget(button)

        self.mru_layout.addStretch(1)

    def _open_mru_file(self, path: Path) -> None:
        if not self._confirm_discard_dirty():
            return
        self._load_file(path)

    def _sync_metadata_controls(self) -> None:
        if not hasattr(self, "show_all_values"):
            return
        with (
            QSignalBlocker(self.show_all_values),
            QSignalBlocker(self.value_column_percent),
            QSignalBlocker(self.significant_figures),
            QSignalBlocker(self.scientific_magnitude),
            QSignalBlocker(self.font_point_size),
        ):
            self.show_all_values.setChecked(self._metadata.showValuesMode == "all_assignments")
            self.value_column_percent.setValue(round(self._metadata.valueColumnPercent))
            self.significant_figures.setValue(self._metadata.significantFigures)
            self.scientific_magnitude.setValue(self._metadata.scientificMagnitude)
            self.font_point_size.setValue(self._effective_font_point_size())
        self._apply_editor_font()

    def _on_metadata_controls_changed(self) -> None:
        mode = "all_assignments" if self.show_all_values.isChecked() else "explicit"
        self._metadata = SheetMetadata(
            showValuesMode=mode,
            valueColumnPercent=float(self.value_column_percent.value()),
            significantFigures=int(self.significant_figures.value()),
            scientificMagnitude=int(self.scientific_magnitude.value()),
            fontPointSize=float(self.font_point_size.value()),
        )
        if self._current_file is not None:
            try:
                save_metadata(self._current_file, self._metadata)
            except OSError as exc:
                QMessageBox.warning(self, "Metadata save failed", f"Could not save metadata:\n{exc}")
        self._apply_editor_font()
        self._recalculate(mark_dirty=False)

    def _effective_font_point_size(self) -> float:
        return self._metadata.fontPointSize or max(10.0, self.font().pointSizeF())

    def _mono_font(self, scale: float = 1.0) -> QFont:
        font = QFont(self._app_config.fontFamily)
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSizeF(self._effective_font_point_size() * scale)
        font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, self._app_config.fontLetterSpacingPercent)
        return font

    def _editor_font(self) -> QFont:
        return self._mono_font(self._app_config.editorFontScale)

    def _render_font(self) -> QFont:
        return self._mono_font(self._app_config.renderedFontScale)

    def _apply_editor_font(self) -> None:
        if hasattr(self, "editor"):
            self.editor.setFont(self._editor_font())

    def _on_text_changed(self) -> None:
        self._recalculate(mark_dirty=True)

    def _recalculate(self, *, mark_dirty: bool = False) -> None:
        source = self.editor.toPlainText()
        if mark_dirty:
            self._dirty = source != self._saved_source
        self._last_output = evaluate(
            EvalInput(source=source, file_path=self._current_file, metadata=self._metadata)
        )
        self._active_line = self.editor.textCursor().blockNumber()
        self._render_output(self._last_output)
        self._update_status()

    def _render_output(self, output: EvalOutput) -> None:
        scroll_value = self.rendered_scroll.verticalScrollBar().value()
        self._clear_rendered_layout()
        line_width = self._rendered_line_width()
        self._rendered_row_widgets = []
        for row in output.rows:
            row_label = QLabel(self.rendered_content)
            row_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            row_label.setMinimumWidth(0)
            row_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
            row_label.setFont(self._render_font())
            row_label.setFixedHeight(
                round(row_label.fontMetrics().height() * self._app_config.renderedRowHeightScale)
            )
            row_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            row_label.setTextFormat(Qt.TextFormat.PlainText)
            row_label.setText(
                format_rendered_row(
                    row,
                    active_line=self._active_line + 1,
                    value_column_percent=self._metadata.valueColumnPercent,
                    line_width=line_width,
                )
            )
            self.rendered_layout.addWidget(row_label)
            self._rendered_row_widgets.append(row_label)
            if row.artifact is not None:
                self.rendered_layout.addWidget(PlotWidget(row.artifact, self._app_config, self.rendered_content))
        self.rendered_layout.addStretch(1)
        self.rendered_scroll.verticalScrollBar().setValue(scroll_value)
        self._update_warning_bar(output)

    def _clear_rendered_layout(self) -> None:
        self._rendered_row_widgets = []
        while self.rendered_layout.count():
            item = self.rendered_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _rendered_line_width(self) -> int:
        char_width = max(1, self.editor.fontMetrics().horizontalAdvance("0"))
        viewport_width = max(1, self.rendered_scroll.viewport().width() - 12)
        return max(40, viewport_width // char_width)

    def _rerender_current_output(self) -> None:
        if self._last_output is not None:
            self._render_output(self._last_output)

    def _update_warning_bar(self, output: EvalOutput) -> None:
        warning_text = format_warning_bar(output.warnings)
        self.warning_bar.setText(warning_text)
        self.warning_bar.setVisible(bool(warning_text))

    def _sync_render_scroll(self, _editor_value: int) -> None:
        if self._syncing_scroll:
            return
        row_index = self.editor.firstVisibleBlock().blockNumber()
        if row_index < 0 or row_index >= len(self._rendered_row_widgets):
            return
        target_value = self._rendered_row_widgets[row_index].y()
        self._syncing_scroll = True
        try:
            self.rendered_scroll.verticalScrollBar().setValue(target_value)
        finally:
            self._syncing_scroll = False

    def _sync_editor_scroll(self, render_value: int) -> None:
        if self._syncing_scroll or not self._rendered_row_widgets:
            return
        row_index = self._rendered_row_index_at(render_value)
        self._syncing_scroll = True
        try:
            self.editor.verticalScrollBar().setValue(row_index)
        finally:
            self._syncing_scroll = False

    def _rendered_row_index_at(self, render_value: int) -> int:
        best_index = 0
        for index, widget in enumerate(self._rendered_row_widgets):
            if widget.y() <= render_value:
                best_index = index
            else:
                break
        return best_index

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._rerender_current_output()

    def closeEvent(self, event) -> None:  # noqa: N802
        if not self._dirty:
            event.accept()
            return
        choice = QMessageBox.question(
            self,
            "Save changes?",
            "The current document has unsaved changes. Save before quitting?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if choice == QMessageBox.StandardButton.Cancel:
            event.ignore()
            return
        if choice == QMessageBox.StandardButton.Discard:
            event.accept()
            return
        self.save_file()
        if self._dirty:
            event.ignore()
        else:
            event.accept()

    def _update_status(self) -> None:
        line_count = len(self.editor.toPlainText().splitlines()) or 1
        dirty_text = "dirty" if self._dirty else "saved"
        eval_text = self._evaluation_status_text()
        self.status_label.setText(f"{line_count} lines · {eval_text} · {dirty_text}")
        filename = str(self._current_file) if self._current_file else "Untitled"
        self.filename_label.setText(filename)
        dirty_mark = "*" if self._dirty else ""
        self.setWindowTitle(f"wmath — {filename}{dirty_mark}")

    def _evaluation_status_text(self) -> str:
        if self._last_output is None:
            return "not evaluated"
        errors = sum(
            1
            for row in self._last_output.rows
            for diagnostic in row.diagnostics
            if diagnostic.severity == "error"
        )
        warnings = len(self._last_output.warnings) + sum(
            1
            for row in self._last_output.rows
            for diagnostic in row.diagnostics
            if diagnostic.severity == "warning"
        )
        if errors:
            return f"{errors} error" + ("s" if errors != 1 else "")
        if warnings:
            return f"{warnings} warning" + ("s" if warnings != 1 else "")
        return "ok"

    def _update_active_line(self) -> None:
        new_active_line = self.editor.textCursor().blockNumber()
        if new_active_line == self._active_line:
            return
        self._active_line = new_active_line
        if self._last_output is not None:
            self._render_output(self._last_output)
