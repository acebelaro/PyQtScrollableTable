from typing import List
from PyQt6.QtWidgets import QGroupBox

from qt_table import (
    Table,
    TableCellUiType,
    TableColumnConfig,
    TableConfig,
    TableRow,
    TableRowFieldConfig,
)


class SampleTableRow(TableRow):

    def __init__(
        self,
        data: int,
        field_configs: List[TableRowFieldConfig],
    ):
        super().__init__(
            width=730,
            height=40,
            field_configs=field_configs,
            id="",
            data=data,
        )

    def _create_ui(self, row_group_box: QGroupBox):
        # TODO: create UI here
        pass


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
                    ),
                    TableColumnConfig(
                        ui_type=TableCellUiType.EDITABLE_TEXT,
                        text="Name",
                        width=380,
                    ),
                    TableColumnConfig(
                        ui_type=TableCellUiType.READONLY_TEXT,
                        text="Value",
                        width=110,
                    ),
                    TableColumnConfig(
                        ui_type=TableCellUiType.CUSTOM,
                        text="",
                        width=190,
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

        field_configs: List[TableRowFieldConfig] = (
            self._create_empty_table_row_field_configs()
        )

        # populate values
        field_configs[0].value = True
        field_configs[1].value = f"Test Name for {data}"
        field_configs[2].value = f"{data}"
        field_configs[3].value = ""

        return SampleTableRow(
            field_configs=field_configs,
            data=data,
        )
