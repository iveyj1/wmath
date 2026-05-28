"""Main application window for the PySide6 prototype."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtGui import QAction, QFont, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from wmath.core import (
    EvalInput,
    EvalOutput,
    evaluate,
    format_rendered_rows,
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

        self.setWindowTitle("wmath — Untitled")
        self._build_actions()
        self._build_ui()
        self._wire_signals()
        self._install_shortcuts()
        self._recalculate()

    def _build_actions(self) -> None:
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

        for action in (self.open_action, self.save_action, self.save_as_action):
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

        splitter = QSplitter(Qt.Orientation.Horizontal, root)
        splitter.setChildrenCollapsible(False)

        self.editor = QPlainTextEdit(splitter)
        self.editor.setPlaceholderText("Enter wmath source here…")
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.editor.setPlainText("length = 2 m\nwidth = 3 m\narea = length * width |")
        self.editor.setFont(self._mono_font())

        self.rendered_label = QLabel("Rendered rows will appear here.", splitter)
        self.rendered_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.rendered_label.setFont(self._mono_font())
        self.rendered_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.rendered_label.setTextFormat(Qt.TextFormat.PlainText)

        self.rendered_scroll = QScrollArea(splitter)
        self.rendered_scroll.setWidgetResizable(True)
        self.rendered_scroll.setWidget(self.rendered_label)

        splitter.addWidget(self.editor)
        splitter.addWidget(self.rendered_scroll)
        splitter.setSizes([550, 550])
        layout.addWidget(splitter, stretch=1)

        self.setCentralWidget(root)

    def _wire_signals(self) -> None:
        self.editor.textChanged.connect(self._on_text_changed)
        self.editor.cursorPositionChanged.connect(self._update_active_line)
        self.editor.verticalScrollBar().valueChanged.connect(self._sync_render_scroll)
        self.undo_action.triggered.connect(self.editor.undo)
        self.redo_action.triggered.connect(self.editor.redo)

    def _install_shortcuts(self) -> None:
        for action in (
            self.open_action,
            self.save_action,
            self.save_as_action,
            self.undo_action,
            self.redo_action,
        ):
            self.addAction(action)

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
        with QSignalBlocker(self.editor):
            self.editor.setPlainText(source)
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

    def _mono_font(self) -> QFont:
        font = QFont("monospace")
        font.setStyleHint(QFont.StyleHint.Monospace)
        point_size = self.font().pointSizeF()
        if point_size > 0:
            font.setPointSizeF(point_size)
        return font

    def _on_text_changed(self) -> None:
        self._recalculate(mark_dirty=True)

    def _recalculate(self, *, mark_dirty: bool = False) -> None:
        if mark_dirty:
            self._dirty = True
        source = self.editor.toPlainText()
        self._last_output = evaluate(
            EvalInput(source=source, file_path=self._current_file, metadata=self._metadata)
        )
        self._active_line = self.editor.textCursor().blockNumber()
        self._render_output(self._last_output)
        self._update_status()

    def _render_output(self, output: EvalOutput) -> None:
        scroll_value = self.rendered_scroll.verticalScrollBar().value()
        self.rendered_label.setText(
            format_rendered_rows(
                output,
                active_line=self._active_line + 1,
                value_column_percent=self._metadata.valueColumnPercent,
            )
        )
        self.rendered_scroll.verticalScrollBar().setValue(scroll_value)
        self._update_warning_bar(output)

    def _update_warning_bar(self, output: EvalOutput) -> None:
        warning_text = format_warning_bar(output.warnings)
        self.warning_bar.setText(warning_text)
        self.warning_bar.setVisible(bool(warning_text))

    def _sync_render_scroll(self, editor_value: int) -> None:
        editor_bar = self.editor.verticalScrollBar()
        render_bar = self.rendered_scroll.verticalScrollBar()
        if editor_bar.maximum() <= editor_bar.minimum():
            render_bar.setValue(render_bar.minimum())
            return

        ratio = (editor_value - editor_bar.minimum()) / (editor_bar.maximum() - editor_bar.minimum())
        render_value = round(render_bar.minimum() + ratio * (render_bar.maximum() - render_bar.minimum()))
        render_bar.setValue(render_value)

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
