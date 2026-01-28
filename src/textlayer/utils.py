import os
from datetime import datetime


def format_bytes(size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024.0:
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} PB"


def format_dt(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d, %H:%M:%S")


def size_on_disk(size: int, cluster: int = 4096) -> int:
    if size == 0:
        return 0
    return ((size + cluster - 1) // cluster) * cluster


def is_pdf_path(path: str) -> bool:
    return os.path.splitext(path)[1].lower() == ".pdf"
