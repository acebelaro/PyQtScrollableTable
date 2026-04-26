from PyQt6.QtWidgets import QGroupBox

from qt_table import Table, TableCellUiType, TableColumnConfig, TableConfig


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
