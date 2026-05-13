import argparse
from pathlib import Path
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

sys.path.append(Path(__file__).parent.parent.as_posix())

from qt_table_types import TableButtonControls
from sample.sample_main import Ui_SampleMain
from sample.sample_table import SampleData, SampleTable


class MainWindow(QMainWindow):

    def __init__(
        self,
        use_confirmers: bool,
        report_events: bool,
    ):
        super().__init__()

        self._data_index = 1

        self._ui = Ui_SampleMain()
        self._ui.setupUi(self)

        button_controls = TableButtonControls(
            delete_selected=self._ui.btnDelete,
            move_up_selected=self._ui.btnMoveUp,
            move_down_selected=self._ui.btnMoveDown,
        )
        self._table = SampleTable(
            groupbox_container=self._ui.grpTable,
            button_controls=button_controls,
            use_confirmers=use_confirmers,
            report_events=report_events,
        )
        self._btn_add_row = self._ui.btnAddRow
        self._btn_add_child_row = self._ui.btnAddChildRow

        self._btn_add_row.clicked.connect(self._add_row)
        self._btn_add_child_row.clicked.connect(self._add_child_row)

    def _add_row(self):
        data = SampleData(
            enabled=True,
            name=f"Test for {self._data_index}",
            value=self._data_index,
        )
        selected_row_index = self._table.selected_row_index
        if selected_row_index == -1:
            self._table.add_new_row_data(data=data)
        else:
            self._table.add_new_row_data_at_index(
                row_index=selected_row_index + 1, data=data
            )
        self._data_index = self._data_index + 1

    def _add_child_row(self):
        selected_row_index = self._table.selected_row_index
        if selected_row_index != -1:
            data = SampleData(
                enabled=True,
                name=f"Test for {self._data_index}",
                value=self._data_index,
            )
            self._table.add_child_row(row_index=selected_row_index, data=data)
            # selected_row_index = self._table.selected_row_index
            # if selected_row_index == -1:
            #     self._table.add_new_row(data=data)
            # else:
            #     self._table.add_row_at_index(row_index=selected_row_index + 1, data=data)
            self._data_index = self._data_index + 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--use-confirmers",
        "-c",
        action="store_true",
        default=False,
        help="Enable user confirmers",
    )
    parser.add_argument(
        "--report-events",
        "-r",
        action="store_true",
        default=False,
        help="Enable event reporting",
    )
    args = parser.parse_args()

    app = QApplication([])
    window = MainWindow(
        use_confirmers=args.use_confirmers,
        report_events=args.report_events,
    )
    window.show()
    sys.exit(app.exec())
