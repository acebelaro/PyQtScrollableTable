from typing import Any
from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QWidget,
    QGroupBox,
    QScrollArea,
    QVBoxLayout,
)
from qt_table_row import TableRow


class TableValueRowsDisplay:

    def __init__(
        self,
        groupbox_container: QGroupBox,
        y_pos: int,
    ):
        self._groupbox_container = groupbox_container
        self._y_pos = y_pos
        self._table_layout = self._create_scroll_area()

    def _create_scroll_area(self) -> QVBoxLayout:
        scroll_area = QScrollArea(parent=self._groupbox_container)
        scroll_area_rect = QtCore.QRect(
            0,
            self._y_pos,
            self._groupbox_container.width(),
            self._groupbox_container.height() - self._y_pos,
        )
        scroll_area.setGeometry(scroll_area_rect)
        scroll_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        scroll_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scrollAreaActionList")

        scroll_area_content = QWidget()
        scroll_area_content.setGeometry(scroll_area.rect())
        scroll_area.setWidget(scroll_area_content)

        table_layout = QVBoxLayout()
        table_layout.addStretch()
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        scroll_area_content.setLayout(table_layout)

        return table_layout

    def add_row_at_index(self, row: TableRow, row_index: int):
        self._table_layout.insertWidget(row_index, row)

    def remove_row(self, row: TableRow, delete_row_widget: bool) -> Any:
        row_data = row.data
        self._table_layout.removeWidget(row)
        if delete_row_widget:
            row.setParent(None)
            row.deleteLater()
        return row_data
