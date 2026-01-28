from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional

import pikepdf


# PyMuPDF (fitz) is optional at import time to avoid crashing the UI;
# missing dependency is reported via DetectionResult.
from textlayer.utils import format_bytes, format_dt, is_pdf_path, size_on_disk

logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    path: str
    location: str
    size: int
    size_on_disk: int
    created: str
    modified: str
    accessed: str


@dataclass
class DetectionResult:
    is_pdf: bool
    is_encrypted: bool
    is_signed: bool
    has_text: bool
    has_image: bool
    page_count: int
    decision: str
    details: str
    error: Optional[str]
    file_info: Optional[FileInfo]


def _get_file_info(path: str) -> FileInfo:
    stat = os.stat(path)
    size = stat.st_size
    return FileInfo(
        path=path,
        location=os.path.dirname(path),
        size=size,
        size_on_disk=size_on_disk(size),
        created=format_dt(stat.st_ctime),
        modified=format_dt(stat.st_mtime),
        accessed=format_dt(stat.st_atime),
    )


def _has_signature(pdf: pikepdf.Pdf) -> bool:
    try:
        root = pdf.trailer.get("/Root", {})
        acroform = root.get("/AcroForm", None)
        if acroform and "/Fields" in acroform:
            for field in acroform["/Fields"]:
                try:
                    ft = field.get("/FT", None)
                    ftype = field.get("/Type", None)
                    if str(ft) == "/Sig" or str(ftype) == "/Sig":
                        return True
                except Exception:
                    continue
        perms = root.get("/Perms", None)
        if perms and "/DocMDP" in perms:
            return True
    except Exception:
        return False
    return False


def detect_file(path: str) -> DetectionResult:
    if not os.path.exists(path):
        return DetectionResult(
            is_pdf=False,
            is_encrypted=False,
            is_signed=False,
            has_text=False,
            has_image=False,
            page_count=0,
            decision="reject_not_found",
            details="File not found.",
            error="File not found.",
            file_info=None,
        )

    # Always capture file metadata for the status panel.
    file_info = _get_file_info(path)

    if not is_pdf_path(path):
        return DetectionResult(
            is_pdf=False,
            is_encrypted=False,
            is_signed=False,
            has_text=False,
            has_image=False,
            page_count=0,
            decision="reject_not_pdf",
            details="Not a PDF. Rejected.",
            error=None,
            file_info=file_info,
        )

    # Detect encryption and signatures early to avoid destructive operations.
    try:
        with pikepdf.open(path) as pdf:
            if pdf.is_encrypted:
                return DetectionResult(
                    is_pdf=True,
                    is_encrypted=True,
                    is_signed=False,
                    has_text=False,
                    has_image=False,
                    page_count=0,
                    decision="reject_encrypted",
                    details="Encrypted or signed PDF. Rejected.",
                    error=None,
                    file_info=file_info,
                )
            if _has_signature(pdf):
                return DetectionResult(
                    is_pdf=True,
                    is_encrypted=False,
                    is_signed=True,
                    has_text=False,
                    has_image=False,
                    page_count=0,
                    decision="reject_signed",
                    details="Encrypted or signed PDF. Rejected.",
                    error=None,
                    file_info=file_info,
                )
    except pikepdf.PasswordError:
        return DetectionResult(
            is_pdf=True,
            is_encrypted=True,
            is_signed=False,
            has_text=False,
            has_image=False,
            page_count=0,
            decision="reject_encrypted",
            details="Encrypted or signed PDF. Rejected.",
            error=None,
            file_info=file_info,
        )
    except Exception as exc:
        logger.exception("Failed to open PDF with pikepdf")
        return DetectionResult(
            is_pdf=True,
            is_encrypted=False,
            is_signed=False,
            has_text=False,
            has_image=False,
            page_count=0,
            decision="reject_error",
            details="Not a PDF. Rejected.",
            error=str(exc),
            file_info=file_info,
        )

    # Detect text/image layers using PyMuPDF for OCR decisioning.
    has_text = False
    has_image = False
    page_count = 0

    try:
        try:
            import fitz
        except Exception as exc:
            return DetectionResult(
                is_pdf=True,
                is_encrypted=False,
                is_signed=False,
                has_text=False,
                has_image=False,
                page_count=0,
                decision="reject_error",
                details="Missing dependency: PyMuPDF not found.",
                error=str(exc),
                file_info=file_info,
            )

        doc = fitz.open(path)
        page_count = doc.page_count
        for page in doc:
            if not has_text:
                text = page.get_text("text")
                if text and text.strip():
                    has_text = True
            if not has_image:
                blocks = page.get_text("dict").get("blocks", [])
                for block in blocks:
                    if block.get("type") == 1:
                        has_image = True
                        break
                if not has_image and page.get_images():
                    has_image = True
            if has_text and has_image:
                break
        doc.close()
    except Exception as exc:
        logger.exception("Failed to inspect PDF with PyMuPDF")
        return DetectionResult(
            is_pdf=True,
            is_encrypted=False,
            is_signed=False,
            has_text=False,
            has_image=False,
            page_count=0,
            decision="reject_error",
            details="Not a PDF. Rejected.",
            error=str(exc),
            file_info=file_info,
        )

    if has_image and not has_text:
        decision = "ocr"
        details = "PDF with image-only pages. OCR will be applied."
    elif has_text and not has_image:
        decision = "skip_text_only"
        details = "PDF with text-only pages. No conversion."
    elif has_text and has_image:
        decision = "ask_reocr"
        details = "PDF with image + text. Re-OCR?"
    else:
        decision = "ocr"
        details = "PDF appears empty. OCR will be applied."

    return DetectionResult(
        is_pdf=True,
        is_encrypted=False,
        is_signed=False,
        has_text=has_text,
        has_image=has_image,
        page_count=page_count,
        decision=decision,
        details=details,
        error=None,
        file_info=file_info,
    )


def format_file_info(file_info: FileInfo) -> dict[str, str]:
    return {
        "Location": file_info.location,
        "Size": f"{format_bytes(file_info.size)} ({file_info.size:,} bytes)",
        "Size on disk": f"{format_bytes(file_info.size_on_disk)} ({file_info.size_on_disk:,} bytes)",
        "Created": file_info.created,
        "Modified": file_info.modified,
        "Accessed": file_info.accessed,
    }
