from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


_PROGRESS_PATTERNS = [
    re.compile(r"Page\s+(\d+)\s+of\s+(\d+)", re.IGNORECASE),
    re.compile(r"page\s+(\d+)\s+of\s+(\d+)", re.IGNORECASE),
    re.compile(r"\((\d+)\s*/\s*(\d+)\)"),
    re.compile(r"(\d+)\s*/\s*(\d+)")
]


@dataclass
class OCRTask:
    input_pdf: str
    output_pdf: str
    lang: str
    output_txt: Optional[str]
    tesseract_path: str
    redo_ocr: bool
    output_type: str
    color_strategy: str


class OCRWorker(QObject):
    progress = Signal(int, str)
    finished = Signal(bool, str, str, str)

    def __init__(self, task: OCRTask) -> None:
        super().__init__()
        self._task = task

    def run(self) -> None:
        input_pdf = self._task.input_pdf
        output_pdf = self._task.output_pdf
        lang = self._task.lang
        output_txt = self._task.output_txt
        output_type = self._task.output_type
        color_strategy = self._task.color_strategy

        # Verify external dependencies early to produce actionable UI errors.
        ocrmypdf_bin = shutil.which("ocrmypdf")
        if not ocrmypdf_bin:
            self.finished.emit(False, "Missing dependency: ocrmypdf not found.", "", "")
            return

        tesseract_bin = self._task.tesseract_path or shutil.which("tesseract")
        if not tesseract_bin:
            self.finished.emit(False, "Missing dependency: tesseract not found.", "", "")
            return

        # Inject Tesseract path into PATH for OCRmyPDF if user configured it.
        env = os.environ.copy()
        if self._task.tesseract_path:
            tesseract_dir = os.path.dirname(self._task.tesseract_path)
            env["PATH"] = tesseract_dir + os.pathsep + env.get("PATH", "")
            env["TESSERACT_CMD"] = self._task.tesseract_path

        if not _tesseract_has_lang(tesseract_bin, lang, env):
            self.finished.emit(False, f"Tesseract language '{lang}' not installed.", "", "")
            return

        cmd = [
            ocrmypdf_bin,
            "-l",
            lang,
        ]
        if self._task.redo_ocr:
            cmd.append("--redo-ocr")
        if output_type == "pdf":
            cmd.extend(["--output-type", "pdf"])
        resolved_color = _resolve_color_strategy(
            input_pdf=input_pdf,
            output_type=output_type,
            color_strategy=color_strategy,
        )
        if resolved_color:
            cmd.extend(["--color-conversion-strategy", resolved_color])
        if output_txt:
            cmd.extend(["--sidecar", output_txt])
        cmd.extend([input_pdf, output_pdf])

        logger.info("Running OCR: %s", " ".join(cmd))
        self.progress.emit(0, "Starting OCR...")

        try:
            return_code, lines = _run_ocr_process(cmd, env, self.progress)
            if return_code != 0:
                if _needs_color_conversion_retry(lines):
                    retry_cmd = cmd[:]
                    retry_cmd.insert(1, "--output-type")
                    retry_cmd.insert(2, "pdf")
                    logger.info("Retrying OCR with --output-type pdf due to color space issue")
                    return_code, lines = _run_ocr_process(retry_cmd, env, self.progress)
                if return_code != 0:
                    self.finished.emit(False, f"OCRmyPDF failed with code {return_code}", "", "")
                    return

            self.progress.emit(100, "Finished")
            self.finished.emit(True, "Conversion finished.", output_pdf, output_txt or "")
        except Exception as exc:
            logger.exception("OCR process failed")
            self.finished.emit(False, f"Conversion failed: {exc}", "", "")


# OCRmyPDF output varies by version; parse several patterns conservatively.
def _parse_progress(line: str) -> Optional[int]:
    for pattern in _PROGRESS_PATTERNS:
        match = pattern.search(line)
        if match:
            current = int(match.group(1))
            total = int(match.group(2))
            if total > 0:
                return int(current / total * 100)
    return None


def _tesseract_has_lang(tesseract_bin: str, lang: str, env: dict) -> bool:
    try:
        result = subprocess.run(
            [tesseract_bin, "--list-langs"],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        output = (result.stdout or "") + (result.stderr or "")
        langs = {line.strip() for line in output.splitlines() if line.strip()}
        return lang in langs
    except Exception:
        return True


def _run_ocr_process(cmd: list[str], env: dict, progress_signal: Signal) -> tuple[int, list[str]]:
    lines: list[str] = []
    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NO_WINDOW
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
        creationflags=creationflags,
    )
    if process.stdout is None:
        raise RuntimeError("Failed to start OCR process.")

    for line in process.stdout:
        line = line.strip()
        if not line:
            continue
        lines.append(line)
        logger.info("OCR: %s", line)
        percent = _parse_progress(line)
        if percent is not None:
            # Emit progress updates when possible.
            progress_signal.emit(percent, line)
        else:
            progress_signal.emit(-1, line)

    return_code = process.wait()
    return return_code, lines


def _needs_color_conversion_retry(lines: list[str]) -> bool:
    joined = " ".join(lines)
    return "ColorConversionNeededError" in joined or "--color-conversion-strategy" in joined


def _resolve_color_strategy(input_pdf: str, output_type: str, color_strategy: str) -> Optional[str]:
    # ocrmypdf expects specific, case-sensitive strategy names.
    if color_strategy == "rgb":
        return "RGB"
    if color_strategy == "gray":
        return "Gray"
    # Auto rules:
    # - If output is PDF/A, prefer Gray
    if output_type == "pdfa":
        return "Gray"
    # - If input is color, use RGB; if B/W, use Gray
    is_gray = _is_pdf_grayscale(input_pdf)
    if is_gray is None:
        return None
    return "Gray" if is_gray else "RGB"


def _is_pdf_grayscale(path: str) -> Optional[bool]:
    try:
        import fitz
    except Exception:
        return None
    try:
        doc = fitz.open(path)
        page_limit = min(3, doc.page_count)
        for i in range(page_limit):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2), colorspace=fitz.csRGB, alpha=False)
            # If pixel buffer has no color channels, treat as grayscale.
            if pix.n == 1:
                continue
            samples = pix.samples
            step = max(3, (pix.width * pix.height * pix.n) // 5000)
            for idx in range(0, len(samples) - 2, step):
                r = samples[idx]
                g = samples[idx + 1]
                b = samples[idx + 2]
                if r != g or g != b:
                    doc.close()
                    return False
        doc.close()
        return True
    except Exception:
        return None
