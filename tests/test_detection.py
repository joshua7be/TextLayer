from pathlib import Path

import fitz
import pikepdf

from textlayer.services.detection import detect_file


def _make_text_pdf(path: Path) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello")
    doc.save(path)
    doc.close()


def _make_image_pdf(path: Path) -> None:
    doc = fitz.open()
    page = doc.new_page()
    pix = fitz.Pixmap(fitz.csRGB, (0, 0, 100, 100), 0)
    img_bytes = pix.tobytes("png")
    page.insert_image(page.rect, stream=img_bytes)
    doc.save(path)
    doc.close()


def _make_mixed_pdf(path: Path) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello")
    pix = fitz.Pixmap(fitz.csRGB, (0, 0, 100, 100), 0)
    img_bytes = pix.tobytes("png")
    page.insert_image(page.rect, stream=img_bytes)
    doc.save(path)
    doc.close()


def test_detect_non_pdf(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("hi", encoding="utf-8")
    result = detect_file(str(file_path))
    assert result.decision == "reject_not_pdf"


def test_detect_text_only(tmp_path: Path) -> None:
    file_path = tmp_path / "text.pdf"
    _make_text_pdf(file_path)
    result = detect_file(str(file_path))
    assert result.decision == "skip_text_only"


def test_detect_image_only(tmp_path: Path) -> None:
    file_path = tmp_path / "image.pdf"
    _make_image_pdf(file_path)
    result = detect_file(str(file_path))
    assert result.decision == "ocr"


def test_detect_mixed(tmp_path: Path) -> None:
    file_path = tmp_path / "mixed.pdf"
    _make_mixed_pdf(file_path)
    result = detect_file(str(file_path))
    assert result.decision == "ask_reocr"


def test_detect_encrypted(tmp_path: Path) -> None:
    file_path = tmp_path / "plain.pdf"
    _make_text_pdf(file_path)
    encrypted_path = tmp_path / "encrypted.pdf"
    with pikepdf.open(file_path) as pdf:
        pdf.save(encrypted_path, encryption=pikepdf.Encryption(owner="owner", user="user"))
    result = detect_file(str(encrypted_path))
    assert result.decision == "reject_encrypted"
