from PyQt6.QtWidgets import QApplication

from model.app_config import AppConfig
from view.view import CrAAnVisView


class CRAAnVis:
    """ Main class of CRAAnVis."""

    def __init__(self, headless_mode=False):
        self.app_config = AppConfig()
        self.app_config.headless_mode = headless_mode

        self.app = QApplication([])
        self.app.setApplicationName("CrAAnVis")
        self.app.setOrganizationName("Jan-Martin Romberg")

        self.view = CrAAnVisView(self.app_config)

        if not headless_mode:
            self.view.show_firsttime()
            self.app.exec()
        else:
            self.app.quit()

if __name__ == '__main__':
    cv = CRAAnVis()


