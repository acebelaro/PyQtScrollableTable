from typing import List
from PyQt6.QtWidgets import QGroupBox

from qt_table import (
    ROW_INDEX_PLACEHOLDER_TOKEN,
    Table,
    TableButtonControls,
    TableCellUiType,
    TableColumnConfig,
    TableConfig,
    TableRow,
    TableCellConfig,
)


class SampleTableRow(TableRow):

    def __init__(
        self,
        data: int,
        field_configs: List[TableCellConfig],
    ):
        super().__init__(
            width=830,
            height=40,
            cell_configs=field_configs,
            id="",
            data=data,
        )


class SampleTable(Table):

    def __init__(
        self,
        groupbox_container: QGroupBox,
        button_controls: TableButtonControls,
    ):
        super().__init__(
            name="Sample",
            groupbox_container=groupbox_container,
            table_config=TableConfig(
                column_configs=[
                    TableColumnConfig(
                        ui_type=TableCellUiType.ROW_INDEX_CELL,
                        text="#",
                        width=65,
                    ),
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
                row_number_cell_format=f"Step {ROW_INDEX_PLACEHOLDER_TOKEN}",
                button_controls=button_controls,
            ),
        )

    def _create_row(self, row_index: int, data: int) -> TableRow:
        print(f"Creating new row with data {data}")

        field_configs: List[TableCellConfig] = (
            self._create_empty_table_row_field_configs()
        )

        field_configs[0].value = self._create_row_index_cell_value(row_index=row_index)
        field_configs[1].value = True
        field_configs[2].value = f"Test Name for {data}"
        field_configs[3].value = f"{data}"
        field_configs[4].value = ""

        return SampleTableRow(
            field_configs=field_configs,
            data=data,
        )

    def _on_row_deleted(self, row_index: int, data: int) -> None:
        print(f"Deleted row index {row_index} with data {data}")
