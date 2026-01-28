import sys
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from textlayer.font_utils import pick_font_for_language
from textlayer.i18n import I18nManager
from textlayer.logging_config import setup_logging
from textlayer.settings import SettingsManager
from textlayer.ui.main_window import MainWindow


def run_app() -> None:
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("TextLayer")
    QCoreApplication.setApplicationName("TextLayer")

    setup_logging()
    settings = SettingsManager()

    i18n = I18nManager()
    lang = settings.get_language()
    i18n.set_language(lang)
    app.setFont(pick_font_for_language(lang))

    window = MainWindow(settings=settings, i18n=i18n)
    window.show()

    sys.exit(app.exec())
