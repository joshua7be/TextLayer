from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QFont, QFontDatabase


def pick_font_for_language(lang: str) -> QFont:
    # Prefer CJK-capable fonts on Windows; fall back gracefully.
    _ensure_windows_cjk_fonts_loaded()
    candidates = {
        "zh_CN": [
            "Microsoft YaHei UI",
            "Microsoft YaHei",
            "SimHei",
            "SimSun",
            "Noto Sans CJK SC",
        ],
        "ja": [
            "Yu Gothic UI",
            "Yu Gothic",
            "Meiryo",
            "MS Gothic",
            "Noto Sans CJK JP",
        ],
        "en": [
            "Segoe UI",
            "Arial",
        ],
    }

    families = set(QFontDatabase.families())
    chosen = [name for name in candidates.get(lang, []) if name in families]
    if chosen:
        font = QFont()
        # Use a fallback family list so missing glyphs can cascade.
        font.setFamilies(chosen)
        font.setPointSize(9)
        return font

    # Last-resort fallback: let Qt pick a default font.
    return QFont()


def _ensure_windows_cjk_fonts_loaded() -> None:
    # On Windows, Qt may not enumerate some system fonts unless added explicitly.
    font_dir = Path("C:/Windows/Fonts")
    if not font_dir.exists():
        return

    font_files = [
        # Chinese
        "msyh.ttc",     # Microsoft YaHei
        "msyhbd.ttc",
        "simhei.ttf",
        "simsun.ttc",
        # Japanese
        "yugothic.ttf",
        "yugothb.ttf",
        "yugothl.ttf",
        "meiryo.ttc",
        "msgothic.ttc",
    ]
    for name in font_files:
        path = font_dir / name
        if path.exists():
            QFontDatabase.addApplicationFont(str(path))
