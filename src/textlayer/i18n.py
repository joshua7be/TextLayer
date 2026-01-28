from PySide6.QtCore import QCoreApplication, QTranslator


# Note: Use ASCII-only source with Unicode escape sequences to avoid encoding corruption.
_TRANSLATIONS = {
    "zh_CN": {
        "Input": "\u8f93\u5165",
        "Drop PDF here or click 'Browse PDF' to select a file.": "\u62d6\u62fd PDF \u5230\u6b64\u5904\uff0c\u6216\u70b9\u51fb\u201c\u9009\u62e9PDF\u201d\u9009\u62e9\u6587\u4ef6\u3002",
        "Browse PDF...": "\u9009\u62e9PDF...",
        "Convert": "\u8f6c\u6362",
        "Output Directory": "\u8f93\u51fa\u76ee\u5f55",
        "Browse...": "\u6d4f\u89c8...",
        "Save As...": "\u53e6\u5b58\u4e3a...",
        "Save Text As...": "\u5bfc\u51fa\u6587\u672c...",
        "Language": "\u8bed\u8a00",
        "OCR Language": "OCR\u8bed\u8a00",
        "Output Type": "\u8f93\u51fa\u7c7b\u578b",
        "Color Strategy": "\u989c\u8272\u7b56\u7565",
        "Auto": "\u81ea\u52a8",
        "Status": "\u72b6\u6001\u6846",
        "Progress: {percent}% - {status}": "\u8fdb\u5ea6\uff1a{percent}% - {status}",
        "Idle": "\u7a7a\u95f2",
        "Ready": "\u5c31\u7eea",
        "Detecting file...": "\u6b63\u5728\u68c0\u6d4b\u6587\u4ef6...",
        "File not found.": "\u6587\u4ef6\u4e0d\u5b58\u5728\u3002",
        "Not a PDF. Rejected.": "\u4e0d\u662fPDF\uff0c\u62d2\u7edd\u6267\u884c\u3002",
        "Encrypted or signed PDF. Rejected.": "\u52a0\u5bc6\u6216\u7b7e\u540dPDF\uff0c\u62d2\u7edd\u6267\u884c\u3002",
        "PDF with image-only pages. OCR will be applied.": "\u4ec5\u56fe\u50cf\u5c42PDF\uff0c\u5c06\u6267\u884cOCR\u3002",
        "PDF with text-only pages. No conversion.": "\u4ec5\u6587\u5b57\u5c42PDF\uff0c\u4e0d\u6267\u884c\u8f6c\u6362\u3002",
        "PDF with image + text. Re-OCR?": "\u56fe\u50cf+\u6587\u5b57PDF\uff0c\u662f\u5426\u91cd\u65b0OCR\uff1f",
        "PDF appears empty. OCR will be applied.": "PDF\u5185\u5bb9\u4e3a\u7a7a\uff0c\u5c06\u6267\u884cOCR\u3002",
        "Output will be saved to: {path}": "\u8f93\u51fa\u5c06\u4fdd\u5b58\u5230\uff1a{path}",
        "Current input: {path}": "\u5f53\u524d\u8f93\u5165\uff1a{path}",
        "Pages": "\u9875\u6570",
        "Location": "\u4f4d\u7f6e",
        "Size": "\u5927\u5c0f",
        "Size on disk": "\u5360\u7528\u7a7a\u95f4",
        "Created": "\u521b\u5efa\u65f6\u95f4",
        "Modified": "\u4fee\u6539\u65f6\u95f4",
        "Accessed": "\u8bbf\u95ee\u65f6\u95f4",
        "OCR Decision": "OCR\u5224\u5b9a",
        "Output": "\u8f93\u51fa",
        "Errors": "\u9519\u8bef",
        "Select output directory": "\u9009\u62e9\u8f93\u51fa\u76ee\u5f55",
        "Select PDF": "\u9009\u62e9PDF",
        "Save output PDF as": "\u53e6\u5b58\u4e3aPDF",
        "Save OCR text as": "\u5bfc\u51faOCR\u6587\u672c",
        "Conversion finished.": "\u8f6c\u6362\u5b8c\u6210\u3002",
        "Conversion failed: {error}": "\u8f6c\u6362\u5931\u8d25\uff1a{error}",
        "Missing dependency: ocrmypdf not found.": "\u7f3a\u5c11\u4f9d\u8d56\uff1a\u672a\u68c0\u6d4b\u5230ocrmypdf\u3002",
        "Missing dependency: tesseract not found.": "\u7f3a\u5c11\u4f9d\u8d56\uff1a\u672a\u68c0\u6d4b\u5230tesseract\u3002",
        "Please install Tesseract OCR and/or OCRmyPDF.": "\u8bf7\u5b89\u88c5Tesseract OCR\u548c/\u6216OCRmyPDF\u3002",
        "Re-OCR": "\u91cd\u65b0OCR",
        "Yes": "\u662f",
        "No": "\u5426",
        "Select Tesseract executable": "\u9009\u62e9tesseract.exe",
        "Preferences": "\u8bbe\u7f6e",
        "Set Tesseract Path...": "\u8bbe\u7f6eTesseract\u8def\u5f84...",
        "Tesseract path saved.": "\u5df2\u4fdd\u5b58Tesseract\u8def\u5f84\u3002",
        "About": "\u5173\u4e8e",
        "Author: OCat": "\u4f5c\u8005\uff1aOCat",
        "AI-assisted development: Codex (GPT-5.2 Codex)": "AI\u8f85\u52a9\u5f00\u53d1\uff1aCodex (GPT-5.2 Codex)",
        "Output path must be different from input.": "\u8f93\u51fa\u8def\u5f84\u5fc5\u987b\u4e0e\u8f93\u5165\u4e0d\u540c\u3002",
        "No OCR text available. Run OCR first.": "\u6ca1\u6709OCR\u6587\u672c\uff0c\u8bf7\u5148\u6267\u884cOCR\u3002",
        "Saved text to {path}": "\u5df2\u4fdd\u5b58\u6587\u672c\u5230 {path}",
        "Tesseract language '{lang}' not installed.": "Tesseract\u8bed\u8a00\u5305\u672a\u5b89\u88c5\uff1a{lang}",
    },
    "ja": {
        "Input": "\u5165\u529b",
        "Drop PDF here or click 'Browse PDF' to select a file.": "PDF\u3092\u3053\u3053\u306b\u30c9\u30ed\u30c3\u30d7\u3059\u308b\u304b\u3001\u300cPDF\u3092\u9078\u629e\u300d\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u304f\u3060\u3055\u3044\u3002",
        "Browse PDF...": "PDF\u3092\u9078\u629e...",
        "Convert": "\u5909\u63db",
        "Output Directory": "\u51fa\u529b\u30d5\u30a9\u30eb\u30c0\u30fc",
        "Browse...": "\u53c2\u7167...",
        "Save As...": "\u540d\u524d\u3092\u4ed8\u3051\u3066\u4fdd\u5b58...",
        "Save Text As...": "\u30c6\u30ad\u30b9\u30c8\u3092\u4fdd\u5b58...",
        "Language": "\u8a00\u8a9e",
        "OCR Language": "OCR\u8a00\u8a9e",
        "Output Type": "\u51fa\u529b\u5f62\u5f0f",
        "Color Strategy": "\u8272\u5909\u63db\u65b9\u6cd5",
        "Auto": "\u81ea\u52d5",
        "Status": "\u30b9\u30c6\u30fc\u30bf\u30b9",
        "Progress: {percent}% - {status}": "\u9032\u6357\uff1a{percent}% - {status}",
        "Idle": "\u5f85\u6a5f\u4e2d",
        "Ready": "\u6e96\u5099\u5b8c\u4e86",
        "Detecting file...": "\u30d5\u30a1\u30a4\u30eb\u3092\u691c\u51fa\u4e2d...",
        "File not found.": "\u30d5\u30a1\u30a4\u30eb\u304c\u898b\u3064\u304b\u308a\u307e\u305b\u3093\u3002",
        "Not a PDF. Rejected.": "PDF\u3067\u306f\u3042\u308a\u307e\u305b\u3093\u3002\u62d2\u5426\u3057\u307e\u3059\u3002",
        "Encrypted or signed PDF. Rejected.": "\u6697\u53f7\u5316\u307e\u305f\u306f\u7f72\u540d\u4ed8\u304dPDF\u3002\u62d2\u5426\u3057\u307e\u3059\u3002",
        "PDF with image-only pages. OCR will be applied.": "\u753b\u50cf\u306e\u307f\u306ePDF\u3002OCR\u3092\u5b9f\u884c\u3057\u307e\u3059\u3002",
        "PDF with text-only pages. No conversion.": "\u30c6\u30ad\u30b9\u30c8\u306e\u307f\u306ePDF\u3002\u5909\u63db\u3057\u307e\u305b\u3093\u3002",
        "PDF with image + text. Re-OCR?": "\u753b\u50cf+\u30c6\u30ad\u30b9\u30c8\u306ePDF\u3002\u518dOCR\u3057\u307e\u3059\u304b\uff1f",
        "PDF appears empty. OCR will be applied.": "PDF\u304c\u7a7a\u306e\u305f\u3081OCR\u3092\u5b9f\u884c\u3057\u307e\u3059\u3002",
        "Output will be saved to: {path}": "\u51fa\u529b\u5148\uff1a{path}",
        "Current input: {path}": "\u5165\u529b\uff1a{path}",
        "Pages": "\u30da\u30fc\u30b8\u6570",
        "Location": "\u5834\u6240",
        "Size": "\u30b5\u30a4\u30ba",
        "Size on disk": "\u30c7\u30a3\u30b9\u30af\u4e0a\u306e\u30b5\u30a4\u30ba",
        "Created": "\u4f5c\u6210\u65e5\u6642",
        "Modified": "\u66f4\u65b0\u65e5\u6642",
        "Accessed": "\u30a2\u30af\u30bb\u30b9\u65e5\u6642",
        "OCR Decision": "OCR\u5224\u5b9a",
        "Output": "\u51fa\u529b",
        "Errors": "\u30a8\u30e9\u30fc",
        "Select output directory": "\u51fa\u529b\u30d5\u30a9\u30eb\u30c0\u30fc\u3092\u9078\u629e",
        "Select PDF": "PDF\u3092\u9078\u629e",
        "Save output PDF as": "PDF\u3068\u3057\u3066\u4fdd\u5b58",
        "Save OCR text as": "OCR\u30c6\u30ad\u30b9\u30c8\u3092\u4fdd\u5b58",
        "Conversion finished.": "\u5909\u63db\u304c\u5b8c\u4e86\u3057\u307e\u3057\u305f\u3002",
        "Conversion failed: {error}": "\u5909\u63db\u306b\u5931\u6557\u3057\u307e\u3057\u305f\uff1a{error}",
        "Missing dependency: ocrmypdf not found.": "\u4f9d\u5b58\u95a2\u4fc2\u4e0d\u8db3\uff1aocrmypdf\u304c\u898b\u3064\u304b\u308a\u307e\u305b\u3093\u3002",
        "Missing dependency: tesseract not found.": "\u4f9d\u5b58\u95a2\u4fc2\u4e0d\u8db3\uff1atesseract\u304c\u898b\u3064\u304b\u308a\u307e\u305b\u3093\u3002",
        "Please install Tesseract OCR and/or OCRmyPDF.": "Tesseract OCR \u3068 OCRmyPDF \u3092\u30a4\u30f3\u30b9\u30c8\u30fc\u30eb\u3057\u3066\u304f\u3060\u3055\u3044\u3002",
        "Re-OCR": "\u518dOCR",
        "Yes": "\u306f\u3044",
        "No": "\u3044\u3044\u3048",
        "Select Tesseract executable": "tesseract.exe\u3092\u9078\u629e",
        "Preferences": "\u8a2d\u5b9a",
        "Set Tesseract Path...": "Tesseract\u30d1\u30b9\u3092\u8a2d\u5b9a...",
        "Tesseract path saved.": "Tesseract\u30d1\u30b9\u3092\u4fdd\u5b58\u3057\u307e\u3057\u305f\u3002",
        "About": "\u60c5\u5831",
        "Author: OCat": "\u4f5c\u6210\u8005\uff1aOCat",
        "AI-assisted development: Codex (GPT-5.2 Codex)": "AI\u88dc\u52a9\u958b\u767a\uff1aCodex (GPT-5.2 Codex)",
        "Output path must be different from input.": "\u51fa\u529b\u30d1\u30b9\u306f\u5165\u529b\u3068\u7570\u306a\u308b\u5fc5\u8981\u304c\u3042\u308a\u307e\u3059\u3002",
        "No OCR text available. Run OCR first.": "OCR\u30c6\u30ad\u30b9\u30c8\u304c\u3042\u308a\u307e\u305b\u3093\u3002\u5148\u306bOCR\u3092\u5b9f\u884c\u3057\u3066\u304f\u3060\u3055\u3044\u3002",
        "Saved text to {path}": "\u30c6\u30ad\u30b9\u30c8\u3092\u4fdd\u5b58\u3057\u307e\u3057\u305f: {path}",
        "Tesseract language '{lang}' not installed.": "Tesseract\u8a00\u8a9e\u30d1\u30c3\u30af\u304c\u672a\u30a4\u30f3\u30b9\u30c8\u30fc\u30eb\u3067\u3059: {lang}",
    },
}


class DictTranslator(QTranslator):
    def __init__(self, lang: str) -> None:
        super().__init__()
        self._lang = lang

    def translate(self, context: str, sourceText: str, disambiguation: str | None = None, n: int = -1) -> str:
        mapping = _TRANSLATIONS.get(self._lang, {})
        return mapping.get(sourceText, sourceText)


class I18nManager:
    def __init__(self) -> None:
        self._translator: DictTranslator | None = None

    def set_language(self, lang: str) -> None:
        if self._translator is not None:
            QCoreApplication.removeTranslator(self._translator)
        self._translator = DictTranslator(lang)
        QCoreApplication.installTranslator(self._translator)

    def available_languages(self) -> list[tuple[str, str]]:
        return [
            ("en", "English"),
            ("ja", "\u65e5\u672c\u8a9e"),
            ("zh_CN", "\u7b80\u4f53\u4e2d\u6587"),
        ]
