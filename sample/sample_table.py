from typing import List
from PyQt6.QtWidgets import QGroupBox

from qt_table_types import (
    BeforeUpdateConfirmers,
    RowClassNameDeciderParam,
    RowInfo,
    TableButtonControls,
    TableCellUiType,
    TableElemClassStyle,
    TableHeaderRowConfig,
    TableValueRowConfig,
)
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
        column_configs = [
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
        ]

        header_row_config = TableHeaderRowConfig(
            height=40,
            header_cell_css_styles=[
                "background-color: rgb(199, 199, 199)",
            ],
        )

        def row_class_name_decider(param: RowClassNameDeciderParam) -> str:
            if param.is_selected:
                return "selected"
            else:
                # no class
                pass
            return ""

        value_row_config = TableValueRowConfig(
            height=40,
            class_styles=[
                TableElemClassStyle(
                    class_name="selected",
                    styles=[
                        "background-color: #0ec0e8",
                    ],
                )
            ],
            row_class_name_decider=row_class_name_decider,
        )

        super().__init__(
            name="Sample",
            groupbox_container=groupbox_container,
            table_config=TableConfig(
                header_row_config=header_row_config,
                column_configs=column_configs,
                value_row_config=value_row_config,
                # selected_row_color_css_value="#0ec0e8",
                row_number_cell_format=f"Step {ROW_INDEX_PLACEHOLDER_TOKEN}",
                button_controls=button_controls,
                before_update_confirmers=BeforeUpdateConfirmers(
                    confirm_row_addition=self._confirm_row_addition,
                    confirm_row_deletion=self._confirm_row_deletion,
                    confirm_row_swap=self._confirm_row_swap,
                ),
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

    def _confirm_row_addition(self, row_info: RowInfo) -> bool:
        print("Just add...")
        return True

    def _confirm_row_deletion(self, row_info: RowInfo) -> bool:
        print("Just delete...")
        return True

    def _confirm_row_swap(
        self, upper_row_info: RowInfo, lower_row_info: RowInfo
    ) -> bool:
        print("Just swap...")
        return True
