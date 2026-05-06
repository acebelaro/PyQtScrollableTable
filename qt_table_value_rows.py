from typing import List, Optional

from PyQt6.QtWidgets import QGroupBox

from qt_table_rows_scroll_area import TableValueRowsScrollArea
from qt_table_types import (
    RowInfo,
)
from qt_table_row import TableRow

ROW_INDEX_PLACEHOLDER_TOKEN = "%row_index%"


class TableValueRows:

    def __init__(
        self,
        groupbox_container: QGroupBox,
        y_pos: int,
        select_new_row_added: bool,
    ):
        self._groupbox_container = groupbox_container
        self._select_new_row_added = select_new_row_added
        self._rows_scroll_area = TableValueRowsScrollArea(
            groupbox_container=self._groupbox_container,
            y_pos=y_pos,
        )
        self._rows: List[TableRow] = []

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
        self._rows_scroll_area.add_row_at_widget_index(row=row, widget_index=row_index)

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
            self._rows_scroll_area.remove_row(row=row)
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

            deleted_row = self._rows[lower_row_index]
            del self._rows[lower_row_index]
            self._rows_scroll_area.remove_row(deleted_row)

            self._rows.insert(upper_row_index, deleted_row)
            self._rows_scroll_area.add_row_at_widget_index(row=deleted_row,widget_index=upper_row_index)
            is_swapped = True

        return is_swapped

    def get_row_by_id(self, row_id) -> Optional[TableRow]:
        return next((r for r in self._rows if r.id == row_id), None)

    def get_row_index_by_id(self, row_id: str) -> int:
        row_index = 0
        while row_index < self.row_count:
            if row_id == self._rows[row_index].id:
                return row_index
            row_index = row_index + 1
        return -1

    def get_row_at_index(self, row_index: int) -> Optional[TableRow]:
        if self.is_valid_row_index(row_index=row_index):
            return self._rows[row_index]
        return None

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

    def set_selected_row(self, row_index: int):
        if self.is_valid_row_index(row_index=row_index):
            self._rows[row_index].set_as_selected()

    def update_rows_selected_states_due_to_toggled_row(
        self, toggled_row_id: str, is_selected: bool
    ):
        if is_selected:
            for row in self._rows:
                if row.id != toggled_row_id:
                    row.clear_selected_state()

    def set_row_index_cell_value(self, row_index: int, row_index_cell_value: str):
        self._rows[row_index].set_row_index_cell_value(
            row_index_cell_value=row_index_cell_value
        )
