from __future__ import annotations

import json
import logging
import os
import shutil
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QFileDialog,
    QVBoxLayout,
    QWidget,
)

from textlayer.i18n import I18nManager
from textlayer.font_utils import pick_font_for_language
from textlayer.settings import SettingsManager
from textlayer.services.detection import detect_file, format_file_info
from textlayer.services.ocr_service import OCRTask, OCRWorker

logger = logging.getLogger(__name__)


class DropArea(QFrame):
    def __init__(self, label: QLabel, path_label: QLabel) -> None:
        super().__init__()
        self._label = label
        self._path_label = path_label
        self.setAcceptDrops(True)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        if path:
            self._path_label.setText(path)
            window = self.window()
            if hasattr(window, "set_input_file"):
                window.set_input_file(path)


class MainWindow(QMainWindow):
    def __init__(self, settings: SettingsManager, i18n: I18nManager) -> None:
        super().__init__()
        self.settings = settings
        self.i18n = i18n

        self.current_input_path = ""
        self.current_output_dir = settings.get_output_dir()
        self.custom_output_path = ""
        self.last_text_path = ""
        self.current_detection = None

        self.worker_thread: QThread | None = None
        self.worker: OCRWorker | None = None

        self.setWindowTitle("TextLayer")
        self.resize(1100, 650)

        self._build_ui()
        self._load_settings()
        self._wire_events()
        self._update_progress(0, self.tr("Idle"))

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)

        top_bar = QHBoxLayout()
        top_bar.addStretch(1)
        self.language_label = QLabel(self.tr("Language"))
        self.language_combo = QComboBox()
        for code, name in self.i18n.available_languages():
            self.language_combo.addItem(name, code)
        top_bar.addWidget(self.language_label)
        top_bar.addWidget(self.language_combo)
        left_layout.addLayout(top_bar)

        self.input_group = QGroupBox(self.tr("Input"))
        self.input_group.setMinimumHeight(260)
        input_layout = QVBoxLayout(self.input_group)

        self.input_hint = QLabel(self.tr("Drop PDF here or click 'Browse PDF' to select a file."))
        self.input_hint.setWordWrap(True)
        self.input_path_label = QLabel("-")
        self.input_path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.drop_area = DropArea(self.input_hint, self.input_path_label)
        self.drop_area.setMinimumHeight(220)
        drop_layout = QVBoxLayout(self.drop_area)
        drop_layout.addWidget(self.input_hint)
        drop_layout.addWidget(self.input_path_label)
        input_layout.addWidget(self.drop_area)

        self.browse_btn = QPushButton(self.tr("Browse PDF..."))
        input_layout.addWidget(self.browse_btn)
        left_layout.addWidget(self.input_group)

        self.convert_btn = QPushButton(self.tr("Convert"))
        self.convert_btn.setFixedHeight(48)
        left_layout.addWidget(self.convert_btn, alignment=Qt.AlignHCenter)

        output_frame = QFrame()
        output_layout = QVBoxLayout(output_frame)
        self.output_label = QLabel(self.tr("Output Directory"))
        output_layout.addWidget(self.output_label)

        ocr_lang_row = QHBoxLayout()
        self.ocr_language_label = QLabel(self.tr("OCR Language"))
        self.ocr_language_combo = QComboBox()
        self.ocr_language_combo.addItem("English", "eng")
        self.ocr_language_combo.addItem("简体中文", "chi_sim")
        self.ocr_language_combo.addItem("繁體中文", "chi_tra")
        self.ocr_language_combo.addItem("日本語", "jpn")
        ocr_lang_row.addWidget(self.ocr_language_label)
        ocr_lang_row.addWidget(self.ocr_language_combo)
        output_layout.addLayout(ocr_lang_row)

        output_type_row = QHBoxLayout()
        self.output_type_label = QLabel(self.tr("Output Type"))
        self.output_type_combo = QComboBox()
        self.output_type_combo.addItem("PDF/A (default)", "pdfa")
        self.output_type_combo.addItem("PDF", "pdf")
        output_type_row.addWidget(self.output_type_label)
        output_type_row.addWidget(self.output_type_combo)
        output_layout.addLayout(output_type_row)

        color_row = QHBoxLayout()
        self.color_strategy_label = QLabel(self.tr("Color Strategy"))
        self.color_strategy_combo = QComboBox()
        self.color_strategy_combo.addItem(self.tr("Auto"), "auto")
        self.color_strategy_combo.addItem("RGB", "rgb")
        self.color_strategy_combo.addItem("Gray", "gray")
        color_row.addWidget(self.color_strategy_label)
        color_row.addWidget(self.color_strategy_combo)
        output_layout.addLayout(color_row)

        output_row = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setReadOnly(True)
        self.output_dir_btn = QPushButton(self.tr("Browse..."))
        self.output_save_as_btn = QPushButton(self.tr("Save As..."))
        output_row.addWidget(self.output_dir_edit, 1)
        output_row.addWidget(self.output_dir_btn)
        output_row.addWidget(self.output_save_as_btn)
        output_layout.addLayout(output_row)

        self.save_text_btn = QPushButton(self.tr("Save Text As..."))
        self.save_text_btn.setEnabled(False)
        output_layout.addWidget(self.save_text_btn)

        left_layout.addWidget(output_frame)

        self.progress_label = QLabel()
        left_layout.addWidget(self.progress_label, alignment=Qt.AlignLeft)

        self.status_group = QGroupBox(self.tr("Status"))
        self.status_group.setMinimumWidth(320)
        status_layout = QVBoxLayout(self.status_group)

        self.location_label = QLabel(self.tr("Location"))
        self.size_label = QLabel(self.tr("Size"))
        self.disk_label = QLabel(self.tr("Size on disk"))
        self.created_label = QLabel(self.tr("Created"))
        self.modified_label = QLabel(self.tr("Modified"))
        self.accessed_label = QLabel(self.tr("Accessed"))
        self.pages_label = QLabel(self.tr("Pages"))
        self.ocr_label = QLabel(self.tr("OCR Decision"))
        self.output_label_right = QLabel(self.tr("Output"))

        self.location_value = QLabel("-")
        self.size_value = QLabel("-")
        self.disk_value = QLabel("-")
        self.created_value = QLabel("-")
        self.modified_value = QLabel("-")
        self.accessed_value = QLabel("-")
        self.pages_value = QLabel("-")
        self.ocr_value = QLabel("-")
        self.output_value = QLabel("-")

        status_layout.addWidget(self._row(self.location_label, self.location_value))
        status_layout.addWidget(self._row(self.size_label, self.size_value))
        status_layout.addWidget(self._row(self.disk_label, self.disk_value))
        status_layout.addWidget(self._row(self.created_label, self.created_value))
        status_layout.addWidget(self._row(self.modified_label, self.modified_value))
        status_layout.addWidget(self._row(self.accessed_label, self.accessed_value))
        status_layout.addWidget(self._row(self.pages_label, self.pages_value))
        status_layout.addWidget(self._row(self.ocr_label, self.ocr_value))
        status_layout.addWidget(self._row(self.output_label_right, self.output_value))

        self.status_log = QPlainTextEdit()
        self.status_log.setReadOnly(True)
        status_layout.addWidget(self.status_log)

        right_layout.addWidget(self.status_group)

        menu = self.menuBar().addMenu(self.tr("Preferences"))
        self.set_tesseract_action = menu.addAction(self.tr("Set Tesseract Path..."))
        help_menu = self.menuBar().addMenu("?")
        self.about_action = help_menu.addAction(self.tr("About"))

    def _row(self, title_label: QLabel, value: QLabel) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        title_label.setFixedWidth(120)
        value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(title_label)
        layout.addWidget(value, 1)
        return container

    def _load_settings(self) -> None:
        if self.current_output_dir:
            self.output_dir_edit.setText(self.current_output_dir)
        lang = self.settings.get_language()
        index = self.language_combo.findData(lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        ocr_lang = self.settings.get_ocr_language()
        ocr_index = self.ocr_language_combo.findData(ocr_lang)
        if ocr_index >= 0:
            self.ocr_language_combo.setCurrentIndex(ocr_index)
        output_type = self.settings.get_output_type()
        output_type_index = self.output_type_combo.findData(output_type)
        if output_type_index >= 0:
            self.output_type_combo.setCurrentIndex(output_type_index)
        color_strategy = self.settings.get_color_strategy()
        color_index = self.color_strategy_combo.findData(color_strategy)
        if color_index >= 0:
            self.color_strategy_combo.setCurrentIndex(color_index)

    def _wire_events(self) -> None:
        self.browse_btn.clicked.connect(self._on_browse_pdf)
        self.convert_btn.clicked.connect(self._on_convert)
        self.output_dir_btn.clicked.connect(self._on_choose_output_dir)
        self.output_save_as_btn.clicked.connect(self._on_save_as)
        self.save_text_btn.clicked.connect(self._on_save_text_as)
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        self.ocr_language_combo.currentIndexChanged.connect(self._on_ocr_language_changed)
        self.output_type_combo.currentIndexChanged.connect(self._on_output_type_changed)
        self.color_strategy_combo.currentIndexChanged.connect(self._on_color_strategy_changed)
        self.set_tesseract_action.triggered.connect(self._on_set_tesseract_path)
        self.about_action.triggered.connect(self._on_about)

    def _on_language_changed(self) -> None:
        lang = self.language_combo.currentData()
        if not lang:
            return
        self.i18n.set_language(lang)
        self.settings.set_language(lang)
        self._apply_language_font(lang)
        self._retranslate_ui()

    def _on_ocr_language_changed(self) -> None:
        ocr_lang = self.ocr_language_combo.currentData()
        if ocr_lang:
            self.settings.set_ocr_language(ocr_lang)

    def _on_output_type_changed(self) -> None:
        value = self.output_type_combo.currentData()
        if value:
            self.settings.set_output_type(value)

    def _on_color_strategy_changed(self) -> None:
        value = self.color_strategy_combo.currentData()
        if value:
            self.settings.set_color_strategy(value)

    def _retranslate_ui(self) -> None:
        self.setWindowTitle("TextLayer")
        self.input_group.setTitle(self.tr("Input"))
        self.input_hint.setText(self.tr("Drop PDF here or click 'Browse PDF' to select a file."))
        self.browse_btn.setText(self.tr("Browse PDF..."))
        self.convert_btn.setText(self.tr("Convert"))
        self.output_label.setText(self.tr("Output Directory"))
        self.ocr_language_label.setText(self.tr("OCR Language"))
        self.output_type_label.setText(self.tr("Output Type"))
        self.color_strategy_label.setText(self.tr("Color Strategy"))
        self.output_dir_btn.setText(self.tr("Browse..."))
        self.output_save_as_btn.setText(self.tr("Save As..."))
        self.save_text_btn.setText(self.tr("Save Text As..."))
        self.language_label.setText(self.tr("Language"))
        self.status_group.setTitle(self.tr("Status"))
        self.location_label.setText(self.tr("Location"))
        self.size_label.setText(self.tr("Size"))
        self.disk_label.setText(self.tr("Size on disk"))
        self.created_label.setText(self.tr("Created"))
        self.modified_label.setText(self.tr("Modified"))
        self.accessed_label.setText(self.tr("Accessed"))
        self.pages_label.setText(self.tr("Pages"))
        self.ocr_label.setText(self.tr("OCR Decision"))
        self.output_label_right.setText(self.tr("Output"))
        self.set_tesseract_action.setText(self.tr("Set Tesseract Path..."))
        self.menuBar().clear()
        menu = self.menuBar().addMenu(self.tr("Preferences"))
        menu.addAction(self.set_tesseract_action)
        help_menu = self.menuBar().addMenu("?")
        help_menu.addAction(self.about_action)
        self._update_progress(0, self.tr("Idle"))

    def _apply_language_font(self, lang: str) -> None:
        # Apply a font that supports the selected language to avoid tofu.
        app = QApplication.instance()
        if app is not None:
            app.setFont(pick_font_for_language(lang))

    def set_input_file(self, path: str) -> None:
        self.current_input_path = path
        self.input_path_label.setText(path)
        if path:
            # Only set default output directory if user has not chosen one yet.
            if not self.current_output_dir:
                self.current_output_dir = os.path.dirname(path)
                self.output_dir_edit.setText(self.current_output_dir)
                self.settings.set_output_dir(self.current_output_dir)
        self.custom_output_path = ""
        self._detect_and_update()

    def _detect_and_update(self) -> None:
        self._append_status(self.tr("Detecting file..."))
        self.current_detection = detect_file(self.current_input_path)
        result = self.current_detection

        if result.file_info:
            info = format_file_info(result.file_info)
            self.location_value.setText(info.get("Location", "-"))
            self.size_value.setText(info.get("Size", "-"))
            self.disk_value.setText(info.get("Size on disk", "-"))
            self.created_value.setText(info.get("Created", "-"))
            self.modified_value.setText(info.get("Modified", "-"))
            self.accessed_value.setText(info.get("Accessed", "-"))
        else:
            self.location_value.setText("-")
            self.size_value.setText("-")
            self.disk_value.setText("-")
            self.created_value.setText("-")
            self.modified_value.setText("-")
            self.accessed_value.setText("-")

        self.pages_value.setText(str(result.page_count or "-"))
        self.ocr_value.setText(self.tr(result.details))
        output_path = self._get_output_path() if self.current_input_path else "-"
        self.output_value.setText(output_path)

        self._append_status(self.tr(result.details))

    def _on_browse_pdf(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select PDF"),
            self.current_output_dir or "",
            "PDF Files (*.pdf);;All Files (*.*)",
        )
        if file_path:
            self.set_input_file(file_path)

    def _on_choose_output_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select output directory"),
            self.current_output_dir or "",
        )
        if directory:
            self.current_output_dir = directory
            self.output_dir_edit.setText(directory)
            self.settings.set_output_dir(directory)
            self.custom_output_path = ""
            self.output_value.setText(self._get_output_path())

    def _on_save_as(self) -> None:
        if not self.current_input_path:
            return
        default_name = self._default_output_name()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Save output PDF as"),
            str(Path(self.current_output_dir) / default_name),
            "PDF Files (*.pdf)",
        )
        if file_path:
            self.custom_output_path = file_path
            self.output_value.setText(file_path)

    def _on_save_text_as(self) -> None:
        if not self.last_text_path or not os.path.exists(self.last_text_path):
            QMessageBox.information(self, "TextLayer", self.tr("No OCR text available. Run OCR first."))
            return
        default_name = Path(self.current_input_path).stem + "_ocr.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Save OCR text as"),
            str(Path(self.current_output_dir) / default_name),
            "Text Files (*.txt)",
        )
        if file_path:
            shutil.copyfile(self.last_text_path, file_path)
            self._append_status(self.tr("Saved text to {path}").format(path=file_path))

    def _on_set_tesseract_path(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Tesseract executable"),
            "",
            "Executable Files (*.exe);;All Files (*.*)",
        )
        if file_path:
            self.settings.set_tesseract_path(file_path)
            self._append_status(self.tr("Tesseract path saved."))

    def _on_about(self) -> None:
        text = self._load_about_text()
        QMessageBox.information(self, "TextLayer", text)

    def _load_about_text(self) -> str:
        # Load About text from assets/about.json for easy customization.
        try:
            # Prefer runtime directory (next to exe) if available.
            if getattr(sys, "frozen", False):
                exe_dir = Path(sys.executable).resolve().parent
                # PyInstaller one-folder places data under _internal.
                candidates = [
                    exe_dir / "assets" / "about.json",
                    exe_dir / "_internal" / "assets" / "about.json",
                ]
                # PyInstaller one-file extracts to sys._MEIPASS.
                meipass = Path(getattr(sys, "_MEIPASS", "")) if getattr(sys, "_MEIPASS", None) else None
                if meipass:
                    candidates.append(meipass / "assets" / "about.json")
            else:
                root = Path(__file__).resolve().parents[3]
                candidates = [root / "assets" / "about.json"]
            for about_path in candidates:
                if about_path.exists():
                    data = json.loads(about_path.read_text(encoding="utf-8"))
                    value = data.get("text", "").strip()
                    if value:
                        return value
        except Exception:
            pass
        return "Version:0.1.7   Author: OCat  AI-assisted development: Codex (GPT-5.2 Codex)"

    def _on_convert(self) -> None:
        if not self.current_input_path:
            QMessageBox.warning(self, "TextLayer", self.tr("File not found."))
            return

        # Re-run detection at conversion time to ensure up-to-date decisions.
        result = detect_file(self.current_input_path)
        self.current_detection = result

        if result.decision in ("reject_not_pdf", "reject_encrypted", "reject_signed", "reject_error"):
            self._append_status(self.tr(result.details))
            QMessageBox.warning(self, "TextLayer", self.tr(result.details))
            return
        if result.decision == "skip_text_only":
            self._append_status(self.tr(result.details))
            QMessageBox.information(self, "TextLayer", self.tr(result.details))
            return

        redo_ocr = False
        # Mixed text+image PDFs require explicit user confirmation to rebuild text.
        if result.decision == "ask_reocr":
            answer = QMessageBox.question(
                self,
                self.tr("Re-OCR"),
                self.tr("PDF with image + text. Re-OCR?"),
                QMessageBox.Yes | QMessageBox.No,
            )
            if answer != QMessageBox.Yes:
                self._append_status(self.tr("PDF with text-only pages. No conversion."))
                return
            redo_ocr = True

        output_path = self._get_output_path()
        if not output_path:
            return
        if os.path.abspath(output_path) == os.path.abspath(self.current_input_path):
            QMessageBox.warning(self, "TextLayer", self.tr("Output path must be different from input."))
            return

        lang = self.ocr_language_combo.currentData() or self.settings.get_ocr_language()
        output_type = self.output_type_combo.currentData() or self.settings.get_output_type()
        color_strategy = self.color_strategy_combo.currentData() or self.settings.get_color_strategy()

        output_txt = str(Path(self.current_output_dir) / (Path(self.current_input_path).stem + "_ocr.txt"))

        task = OCRTask(
            input_pdf=self.current_input_path,
            output_pdf=output_path,
            lang=lang,
            output_txt=output_txt,
            tesseract_path=self.settings.get_tesseract_path(),
            redo_ocr=redo_ocr,
            output_type=output_type,
            color_strategy=color_strategy,
        )

        self._set_busy(True)
        self._append_status(self.tr("Output will be saved to: {path}").format(path=output_path))
        self._start_worker(task)

    def _start_worker(self, task: OCRTask) -> None:
        self.worker_thread = QThread()
        self.worker = OCRWorker(task)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    def _on_progress(self, percent: int, status: str) -> None:
        if percent < 0:
            current = self.progress_label.text()
            if current:
                self._append_status(status)
            return
        self._update_progress(percent, status)

    def _on_finished(self, success: bool, message: str, output_pdf: str, output_txt: str) -> None:
        self._set_busy(False)
        display_message = self._format_worker_message(message)
        self._append_status(display_message)
        if success:
            self._update_progress(100, self.tr("Ready"))
            self.last_text_path = output_txt
            self.save_text_btn.setEnabled(bool(output_txt))
            QMessageBox.information(self, "TextLayer", self.tr("Conversion finished."))
        else:
            QMessageBox.critical(self, "TextLayer", display_message)

    def _set_busy(self, busy: bool) -> None:
        self.convert_btn.setEnabled(not busy)
        self.browse_btn.setEnabled(not busy)
        self.output_dir_btn.setEnabled(not busy)
        self.output_save_as_btn.setEnabled(not busy)
        self.language_combo.setEnabled(not busy)

    def _update_progress(self, percent: int, status: str) -> None:
        self.progress_label.setText(self.tr("Progress: {percent}% - {status}").format(
            percent=percent,
            status=status,
        ))

    def _append_status(self, text: str) -> None:
        self.status_log.appendPlainText(text)

    def _format_worker_message(self, message: str) -> str:
        if message.startswith("Tesseract language '") and message.endswith("not installed."):
            lang = message.split("'")[1]
            template = self.tr("Tesseract language '{lang}' not installed.")
            return template.format(lang=lang)
        return self.tr(message)

    def _default_output_name(self) -> str:
        stem = Path(self.current_input_path).stem
        return f"{stem}_textlayer.pdf"

    def _get_output_path(self) -> str:
        if self.custom_output_path:
            return self.custom_output_path
        if not self.current_input_path:
            return ""
        directory = self.current_output_dir or os.path.dirname(self.current_input_path)
        return str(Path(directory) / self._default_output_name())
