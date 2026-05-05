from typing import List

from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QGroupBox,
    QLabel,
)

from qt_table_types import (
    TableColumnConfig,
    TableHeaderRowConfig,
)

_TABLE_HEADER_CELL_GROUPBOX_NAME = "QtTableHeaderCellGroupBox"


class TableHeaderRow:

    def __init__(
        self,
        name: str,
        header_row_config: TableHeaderRowConfig,
        column_configs: List[TableColumnConfig],
        groupbox_container: QGroupBox,
    ):
        self._name = name
        self._header_row_config = header_row_config
        self._column_configs = column_configs
        self._groupbox_container = groupbox_container

    def create(self) -> int:
        calculated_row_width_from_header_row = 0
        table_column_config_count = len(self._column_configs)
        for index in range(table_column_config_count):
            table_column_config = self._column_configs[index]
            is_last_column = False
            if index != (table_column_config_count - 1):
                is_last_column = True
            self._create_header_cell_group_box(
                table_column_config=table_column_config,
                x_pos=calculated_row_width_from_header_row,
                is_last_column=is_last_column,
            )
            calculated_row_width_from_header_row = (
                calculated_row_width_from_header_row + table_column_config.width
            )
        if calculated_row_width_from_header_row > self._groupbox_container.width():
            raise ValueError(
                f"Table '{self._name}' column header total width exceeds given group box container width!"
            )
        return calculated_row_width_from_header_row

    def _create_header_cell_group_box(
        self,
        table_column_config: TableColumnConfig,
        x_pos: int,
        is_last_column: bool,
    ) -> None:
        columng_group_box = QGroupBox(parent=self._groupbox_container)
        columng_group_box.setGeometry(
            QtCore.QRect(
                x_pos,
                0,
                table_column_config.width,
                self._header_row_config.height,
            )
        )
        css_style_text = "; ".join(self._header_row_config.header_cell_css_styles)
        css_style_text = f"{css_style_text}; border: 1px solid black;"
        if is_last_column:
            css_style_text = f"{css_style_text} border-right: none;"
        css_style_text = (
            f"QGroupBox#{_TABLE_HEADER_CELL_GROUPBOX_NAME}{{ {css_style_text} }}"
        )
        columng_group_box.setObjectName(_TABLE_HEADER_CELL_GROUPBOX_NAME)
        columng_group_box.setStyleSheet(css_style_text)
        columng_group_box.setTitle("")

        column_text_label = QLabel(parent=columng_group_box)
        column_text_label.setGeometry(
            QtCore.QRect(
                0,
                0,
                table_column_config.width,
                self._header_row_config.height,
            )
        )
        column_text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        column_text_label.setText(table_column_config.text)
