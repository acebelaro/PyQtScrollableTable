from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QWidget,
    QGroupBox,
    QScrollArea,
    QVBoxLayout,
)
from qt_table_row import TableRow


class TableValueRowsScrollArea:

    def __init__(
        self,
        groupbox_container: QGroupBox,
        y_pos: int,
    ):
        # create scroll area
        self._scroll_area = QScrollArea(parent=groupbox_container)
        self._scroll_area.setGeometry(
            QtCore.QRect(
                0,
                y_pos,
                groupbox_container.width(),
                groupbox_container.height() - y_pos,
            )
        )
        self._scroll_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self._scroll_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setObjectName("scrollAreaActionList")

        # self._scroll_area = scroll_area
        self._scroll_area_content = QWidget()
        self._scroll_area_content.setGeometry(self._scroll_area.rect())
        self._scroll_area.setWidget(self._scroll_area_content)

        self._table_layout = QVBoxLayout()
        self._table_layout.addStretch()
        self._table_layout.setContentsMargins(0, 0, 0, 0)
        self._table_layout.setSpacing(0)
        self._scroll_area_content.setLayout(self._table_layout)

    def add_row_at_widget_index(self, row: TableRow, widget_index: int):
        if widget_index != -1:
            self._table_layout.insertWidget(widget_index, row)
        else:
            self._table_layout.addWidget(row)

    def remove_row(self, row: TableRow):
        self._table_layout.removeWidget(row)

    def get_widget_index_of_row(self, row_id: str) -> int:
        row_count = self._table_layout.count()
        for widget_index in range(row_count):
            widget_at_index = self._table_layout.itemAt(widget_index)
            row = widget_at_index.widget()
            if isinstance(row, TableRow):
                if row.id == row_id:
                    return widget_at_index
        return -1
