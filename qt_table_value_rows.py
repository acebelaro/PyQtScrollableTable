from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional

from PyQt6 import QtCore
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import (
    QWidget,
    QGroupBox,
    QScrollArea,
    QVBoxLayout,
)
from PyQt6.QtCore import pyqtSignal

from qt_table_header_row import TableHeaderRow
from qt_table_types import (
    RowInfo,
    TableConfig,
    TableRowCellConfig,
    TableRowCellValue,
    TableRowCellValueUpdatedParam,
)
from qt_table_row import TableRow

ROW_INDEX_PLACEHOLDER_TOKEN = "%row_index%"


class TableValueRows:

    def __init__(
        self,
        groupbox_container: QGroupBox,
        y_pos: int,
        height: int,
        select_new_row_added: bool,
        confirm_row_swap: Optional[Callable[[RowInfo, RowInfo], bool]] = None,
    ):
        self._groupbox_container = groupbox_container
        self._select_new_row_added = select_new_row_added
        self._confirm_row_swap = confirm_row_swap

        # create scroll area
        self._scroll_area = QScrollArea(parent=self._groupbox_container)
        self._scroll_area.setGeometry(
            QtCore.QRect(
                0,
                y_pos,  # self._config.header_row_config.height,
                self._groupbox_container.width(),
                height,  # self._groupbox_container.height() - self._config.header_row_config.height,
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

        self._scroll_area_content = QWidget()
        self._scroll_area_content.setGeometry(self._scroll_area.rect())
        self._scroll_area.setWidget(self._scroll_area_content)

        self._table_layout = QVBoxLayout()
        self._table_layout.addStretch()
        self._table_layout.setContentsMargins(0, 0, 0, 0)
        self._table_layout.setSpacing(0)
        self._scroll_area_content.setLayout(self._table_layout)

        self._rows: List[TableRow] = []

    @property
    def rows(self) -> List[TableRow]:
        return self._rows

    @property
    def row_count(self) -> int:
        return len(self._rows)

    @property
    def selected_row(self) -> Optional[TableRow]:
        return next((b for b in self._rows if b.is_selected), None)

    @property
    def selected_row_index(self) -> int:
        selected_row = self.selected_row
        if selected_row:
            selected_row_id = selected_row.id
            return self.get_row_index_by_id(row_id=selected_row_id)
        return -1

    def is_valid_row_index(self, row_index: int) -> bool:
        if row_index >= 0 and row_index < self.row_count:
            return True
        return False

    def add_row_at_index(
        self, row_index: int, row: TableRow, skip_select: bool = False
    ):
        print(f"Adding at row {row_index}")
        self._rows.insert(row_index, row)
        self._table_layout.insertWidget(row_index, row)

        if self._select_new_row_added and not skip_select:
            selected_row = self.selected_row
            if selected_row:
                selected_row.clear_selected_state()
            row.set_as_selected()

    def delete_row_at_index(self, row_index: int) -> Optional[RowInfo]:
        deleted_row_info = None
        if self.is_valid_row_index(row_index=row_index):
            row = self._rows[row_index]
            deleted_row_info = RowInfo(
                row_index=row_index,
                data=self._rows[row_index].data,
            )
            del self._rows[row_index]
            self._table_layout.removeWidget(row)
            row.setParent(None)
            row.deleteLater()
        return deleted_row_info

    def swap_row_index(
        self,
        upper_row_index: int,
        lower_row_index: int,
    ) -> bool:
        is_swapped = False

        # fmt: off
        if self.is_valid_row_index(row_index=upper_row_index) and \
            self.is_valid_row_index(row_index=lower_row_index):
        # fmt: on

            proceed_swap = True
            upper_row = self._rows[upper_row_index]
            lower_row = self._rows[lower_row_index]

            if self._confirm_row_swap and self._confirm_row_swap:
                upper_row_info = RowInfo(
                    row_index=upper_row_index,
                    data=upper_row.data,
                )
                lower_row_info = RowInfo(
                    row_index=lower_row_index,
                    data=lower_row.data,
                )
                proceed_swap = self._confirm_row_swap(
                    upper_row_info=upper_row_info,
                    lower_row_info=lower_row_info,
                )
            if proceed_swap:
                deleted_row = self._rows[lower_row_index]
                del self._rows[lower_row_index]
                self._table_layout.removeWidget(deleted_row)

                self._rows.insert(upper_row_index, deleted_row)
                self._table_layout.insertWidget(upper_row_index, deleted_row)
                is_swapped = True

        return is_swapped

    def get_row_index_by_id(self, row_id: str) -> int:
        row_index = 0
        while row_index < self.row_count:
            if row_id == self._rows[row_index].id:
                return row_index
            row_index = row_index + 1
        return -1

    def get_selected_row_info(self) -> Optional[RowInfo]:
        selected_row = self.selected_row
        if selected_row:
            selected_row_index = self.get_row_index_by_id(row_id=selected_row.id)
            if selected_row_index != -1:
                return RowInfo(
                    row_index=selected_row_index,
                    data=selected_row.data,
                )
        return None
