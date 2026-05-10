from typing import List, NamedTuple
from PyQt6.QtWidgets import QGroupBox, QMessageBox

from qt_table_types import (
    BeforeUpdateConfirmers,
    RowClassNameDeciderParam,
    RowInfo,
    TableButtonControls,
    TableCellUiType,
    TableColumnConfig,
    TableElemClassStyle,
    TableHeaderRowConfig,
    TableShortcutKeys,
    TableValueRowConfig,
)
from qt_table import (
    Table,
    TableConfig,
    TableRowCellValue,
)
from qt_table_value_rows import TableValueRowInfo


class SampleData(NamedTuple):
    enabled: bool
    name: str
    value: int


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
                button_controls=button_controls,
                before_update_confirmers=BeforeUpdateConfirmers(
                    confirm_row_addition=self._confirm_row_addition,
                    confirm_row_deletion=self._confirm_row_deletion,
                    confirm_row_swap=self._confirm_row_swap,
                ),
                shortcut_keys=TableShortcutKeys(
                    ctrl_z_y_undo_redo=True,
                ),
            ),
        )

    def _create_row_index_cell_value(self, row_index: int) -> str:
        return f"Step {row_index+1}"

    def _create_row_cell_values(
        self,
        row_index: int,
        data: SampleData,
    ) -> List[TableRowCellValue]:
        return [
            TableRowCellValue(
                cell_index=0,
                value=self._create_row_index_cell_value(row_index=row_index),
            ),
            TableRowCellValue(
                cell_index=1,
                value=data.enabled,
            ),
            TableRowCellValue(
                cell_index=2,
                value=data.name,
            ),
            TableRowCellValue(
                cell_index=3,
                value=f"{data.value}",
            ),
        ]

    def _create_data_from_row_cell_values(
        self,
        cell_values: List[TableRowCellValue],
    ) -> SampleData:
        return SampleData(
            enabled=cell_values[1].value,
            name=cell_values[2].value,
            value=cell_values[3].value,
        )

    def _on_row_added(self, row_index: int, data: int) -> None:
        msg_box = QMessageBox(
            QMessageBox.Icon.Information,
            "Row Added",
            f"Added row {row_index}",
            QMessageBox.StandardButton.Yes,
        )
        msg_box.exec()

    def _on_row_deleted(self, row_index: int, data: int) -> None:
        msg_box = QMessageBox(
            QMessageBox.Icon.Information,
            "Row Deleted",
            f"Deleted row {row_index}",
            QMessageBox.StandardButton.Yes,
        )
        msg_box.exec()

    def _on_rows_swapped(
        self,
        lower_row_index: int,
        upper_row_index: int,
    ):
        msg_box = QMessageBox(
            QMessageBox.Icon.Information,
            "Rows Swapped",
            f"Swapped rows {lower_row_index} and {upper_row_index}",
            QMessageBox.StandardButton.Yes,
        )
        msg_box.exec()

    def _confirm_row_addition(self, row_info: RowInfo) -> bool:
        msg_box = QMessageBox(
            QMessageBox.Icon.Question,
            "Confirm Add",
            "Confirm Add?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        return msg_box.exec() == QMessageBox.StandardButton.Yes

    def _confirm_row_deletion(self, row_info: RowInfo) -> bool:
        msg_box = QMessageBox(
            QMessageBox.Icon.Question,
            "Confirm Delete",
            "Confirm Delete?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        return msg_box.exec() == QMessageBox.StandardButton.Yes

    def _confirm_row_swap(
        self, upper_row_info: RowInfo, lower_row_info: RowInfo
    ) -> bool:
        msg_box = QMessageBox(
            QMessageBox.Icon.Question,
            "Confirm Swap",
            "Confirm Swap?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        return msg_box.exec() == QMessageBox.StandardButton.Yes

    def _create_row_data_copy(self, row_info: TableValueRowInfo) -> SampleData:
        data: SampleData = row_info.row.data
        return SampleData(
            enabled=data.enabled,
            name=data.name,
            value=data.value,
        )
