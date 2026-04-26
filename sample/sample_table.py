from PyQt6.QtWidgets import QGroupBox
from PyQt6 import QtCore, QtGui, QtWidgets

from qt_table import Table, TableCellUiType, TableColumnConfig, TableConfig, TableRow


class SampleTableRow(TableRow):

    def __init__(
        self,
        data: int,
    ):
        super().__init__(
            id="",
            data=data,
        )

        self.setFixedHeight(40)
        self.setContentsMargins(0, 0, 0, 0)

    def _create_ui(self):
        # # raise NotImplementedError
        # self.setGeometry(QtCore.QRect(0, 0, 731, 41))
        # # self.setTitle("")
        # self.setObjectName("grpActionRow")

        # self.labelDescription = QtWidgets.QLabel(parent=self)
        # self.labelDescription.setGeometry(QtCore.QRect(10, 10, 361, 16))
        # self.labelDescription.setObjectName("labelDescription")
        # self.labelDescription.setText(f"{self.data}")
        print("...")
        ActionRow = self
        self.grpActionRow = QtWidgets.QGroupBox(parent=ActionRow)
        self.grpActionRow.setGeometry(QtCore.QRect(0, 0, 731, 41))
        self.grpActionRow.setTitle("")
        self.grpActionRow.setObjectName("grpActionRow")
        self.grpColEnable = QtWidgets.QGroupBox(parent=self.grpActionRow)
        self.grpColEnable.setGeometry(QtCore.QRect(0, 0, 71, 41))
        self.grpColEnable.setTitle("")
        self.grpColEnable.setObjectName("grpColEnable")
        self.checkEnable = QtWidgets.QCheckBox(parent=self.grpColEnable)
        self.checkEnable.setGeometry(QtCore.QRect(30, 10, 30, 20))
        self.checkEnable.setText("")
        self.checkEnable.setObjectName("checkEnable")
        self.grpColDescription = QtWidgets.QGroupBox(parent=self.grpActionRow)
        self.grpColDescription.setGeometry(QtCore.QRect(70, 0, 381, 41))
        self.grpColDescription.setTitle("")
        self.grpColDescription.setObjectName("grpColDescription")
        self.labelDescription = QtWidgets.QLabel(parent=self.grpColDescription)
        self.labelDescription.setGeometry(QtCore.QRect(10, 10, 361, 16))
        self.labelDescription.setObjectName("labelDescription")
        self.grpColButtons = QtWidgets.QGroupBox(parent=self.grpActionRow)
        self.grpColButtons.setGeometry(QtCore.QRect(560, 0, 171, 41))
        self.grpColButtons.setTitle("")
        self.grpColButtons.setObjectName("grpColButtons")
        self.btnDelete = QtWidgets.QPushButton(parent=self.grpColButtons)
        self.btnDelete.setGeometry(QtCore.QRect(100, 10, 61, 24))
        self.btnDelete.setObjectName("btnDelete")
        self.btnEdit = QtWidgets.QPushButton(parent=self.grpColButtons)
        self.btnEdit.setGeometry(QtCore.QRect(70, 10, 31, 24))
        self.btnEdit.setObjectName("btnEdit")
        self.btnMoveUp = QtWidgets.QPushButton(parent=self.grpColButtons)
        self.btnMoveUp.setGeometry(QtCore.QRect(40, 10, 31, 24))
        self.btnMoveUp.setObjectName("btnMoveUp")
        self.btnMoveDown = QtWidgets.QPushButton(parent=self.grpColButtons)
        self.btnMoveDown.setGeometry(QtCore.QRect(10, 10, 31, 24))
        self.btnMoveDown.setObjectName("btnMoveDown")
        self.grpColDelay = QtWidgets.QGroupBox(parent=self.grpActionRow)
        self.grpColDelay.setGeometry(QtCore.QRect(450, 0, 111, 41))
        self.grpColDelay.setTitle("")
        self.grpColDelay.setObjectName("grpColDelay")
        self.labelDelay = QtWidgets.QLabel(parent=self.grpColDelay)
        self.labelDelay.setGeometry(QtCore.QRect(10, 10, 71, 20))
        self.labelDelay.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.labelDelay.setObjectName("labelDelay")


class SampleTable(Table):

    def __init__(self, groupbox_container: QGroupBox):
        super().__init__(
            name="Sample",
            groupbox_container=groupbox_container,
            table_config=TableConfig(
                column_configs=[
                    TableColumnConfig(
                        ui_type=TableCellUiType.CHECKBOX,
                        text="Check",
                        width=70,
                        object_name="grpCheckCol",
                    ),
                    TableColumnConfig(
                        ui_type=TableCellUiType.READONLY_TEXT,
                        text="Name",
                        width=380,
                        object_name="grpNameCol",
                    ),
                    TableColumnConfig(
                        ui_type=TableCellUiType.READONLY_TEXT,
                        text="Value",
                        width=110,
                        object_name="grpValueCol",
                    ),
                    TableColumnConfig(
                        ui_type=TableCellUiType.CUSTOM,
                        text="",
                        width=190,
                        object_name="grpControlsCol",
                    ),
                ],
                header_row_height=40,
                header_cell_css_styles=[
                    "background-color: rgb(199, 199, 199)",
                ],
            ),
        )

    def _create_row(self, data: int) -> TableRow:
        print(f"Creating new row with data {data}")
        return SampleTableRow(
            data=data,
        )
