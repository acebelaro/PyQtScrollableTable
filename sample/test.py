from pathlib import Path
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

sys.path.append(Path(__file__).parent.parent.as_posix())

from sample.sample_main import Ui_SampleMain
from sample.sample_table import SampleTable


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self._ui = Ui_SampleMain()
        self._ui.setupUi(self)

        self._table = SampleTable(
            groupbox_container=self._ui.grpTable,
        )


if __name__ == "__main__":

    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
