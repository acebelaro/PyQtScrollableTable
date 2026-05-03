from typing import List
from PyQt6.QtWidgets import QGroupBox

from qt_table_types import TableButtonControls, TableCellUiType
from qt_table import (
    ROW_INDEX_PLACEHOLDER_TOKEN,
    Table,
    TableColumnConfig,
    TableConfig,
    TableRowCellValue,
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
                ],
                header_row_height=40,
                value_row_height=40,
                header_cell_css_styles=[
                    "background-color: rgb(199, 199, 199)",
                ],
                selected_row_color_css_value="#0ec0e8",
                row_number_cell_format=f"Step {ROW_INDEX_PLACEHOLDER_TOKEN}",
                button_controls=button_controls,
            ),
        )

    def _create_row_cell_values(
        self,
        row_index: int,
        data: int,
    ) -> List[TableRowCellValue]:
        return [
            TableRowCellValue(
                cell_index=0,
                value=self._create_row_index_cell_value(row_index=row_index),
            ),
            TableRowCellValue(
                cell_index=1,
                value=True,
            ),
            TableRowCellValue(
                cell_index=2,
                value=f"Test Name for {data}",
            ),
            TableRowCellValue(
                cell_index=3,
                value=f"{data}",
            ),
        ]

    def _on_row_deleted(self, row_index: int, data: int) -> None:
        print(f"Deleted row index {row_index} with data {data}")

    def _on_rows_swapped(
        self,
        lower_row_index: int,
        upper_row_index: int,
    ):
        print(f"Swapped {lower_row_index} <-> {upper_row_index}")
