from PySide6.QtCore import QLocale, QSettings


class SettingsManager:
    def __init__(self) -> None:
        self._settings = QSettings()

    def get_language(self) -> str:
        lang = self._settings.value("ui/language", "")
        if lang:
            return lang
        # Default to system locale when no setting is stored.
        sys_locale = QLocale.system().name()
        if sys_locale.startswith("zh"):
            return "zh_CN"
        if sys_locale.startswith("ja"):
            return "ja"
        return "en"

    def set_language(self, lang: str) -> None:
        self._settings.setValue("ui/language", lang)

    def get_output_dir(self) -> str:
        return self._settings.value("output/last_dir", "")

    def set_output_dir(self, path: str) -> None:
        self._settings.setValue("output/last_dir", path)

    def get_tesseract_path(self) -> str:
        return self._settings.value("ocr/tesseract_path", "")

    def set_tesseract_path(self, path: str) -> None:
        self._settings.setValue("ocr/tesseract_path", path)

    def get_ocr_language(self) -> str:
        lang = self._settings.value("ocr/language", "")
        if lang:
            return lang
        # Default OCR language is Simplified Chinese unless user changes it.
        return "chi_sim"

    def set_ocr_language(self, lang: str) -> None:
        self._settings.setValue("ocr/language", lang)

    def get_output_type(self) -> str:
        # "pdfa" (default) or "pdf"
        return self._settings.value("output/type", "pdfa")

    def set_output_type(self, value: str) -> None:
        self._settings.setValue("output/type", value)

    def get_color_strategy(self) -> str:
        # "auto", "rgb", or "gray"
        return self._settings.value("output/color_strategy", "auto")

    def set_color_strategy(self, value: str) -> None:
        self._settings.setValue("output/color_strategy", value)
