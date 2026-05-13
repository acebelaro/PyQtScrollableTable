"""
Module for managing the collection of value rows in the table.

This module provides the `TableValueRows` class that manages the data layer
of the table, handling the storage, retrieval, and manipulation of table rows.
It serves as the interface between the visual display and the underlying row data.

Key responsibilities:
- Storing and managing the list of TableRow objects
- Providing row lookup by index, ID, or condition
- Managing row selection state
- Creating cell values from row data using provided callbacks
- Maintaining row index cell values (e.g., row numbers)

The class uses callback functions to create row index values and cell values,
allowing the table implementation to define how data is displayed in cells.

Classes:
    TableValueRows: Manages the collection and state of table value rows
"""
from typing import Any, Callable, List, Optional

from PyQt6.QtCore import pyqtSignal

from qt_table_types import RowInfo, TableRowCellValue
from qt_table_row import TableRow


class TableValueRows:

    on_rows_swapped = pyqtSignal(int, int)

    def __init__(
        self,
        row_index_cell_value_creator: Callable[[int], str],
        row_cell_values_creator: Callable[[int, Any], List[TableRowCellValue]],
    ):
        super().__init__()
        self._rows: List[TableRow] = []
        self._row_index_cell_value_creator = row_index_cell_value_creator
        self._row_cell_values_creator = row_cell_values_creator

    @property
    def rows(self) -> List[TableRow]:
        return self._rows

    @property
    def row_count(self) -> int:
        return len(self._rows)

    @property
    def selected_row(self) -> Optional[TableRow]:
        return next((b for b in self._rows if b.is_selected), None)

    def is_valid_row_index(self, row_index: int) -> bool:
        if row_index >= 0 and row_index < self.row_count:
            return True
        return False

    def get_row_at_index(self, row_index: int) -> Optional[TableRow]:
        if self.is_valid_row_index(row_index=row_index):
            return self._rows[row_index]
        return None

    def add_row(self, row: TableRow, row_index: int):
        self._rows.insert(row_index, row)

    def delete_row_at_index(self, row_index: int) -> Optional[TableRow]:
        deleted_row = None
        if self.is_valid_row_index(row_index=row_index):
            deleted_row = self._rows[row_index]
            del self._rows[row_index]
        return deleted_row

    def get_row_by_id(self, row_id: str) -> Optional[RowInfo]:
        def is_row_id_match(row: TableRow) -> bool:
            if row.id == row_id:
                return True
            return False

        return self._get_row_based_on_condition(condition=is_row_id_match)

    def clear_other_rows_selected_state(self, except_row_id: str):
        for row in self._rows:
            if row.id != except_row_id and row.is_selected:
                row.clear_selected_state()

    def get_selected_row_info(self) -> Optional[RowInfo]:
        def is_selected_row(row: TableRow) -> bool:
            return row.is_selected

        return self._get_row_based_on_condition(condition=is_selected_row)

    def set_row_as_selected(self, row_index: int):
        if self.is_valid_row_index(row_index=row_index):
            self._rows[row_index].set_as_selected()

    def set_data_of_row(self, row_index: int, data: Any):
        if self.is_valid_row_index(row_index=row_index):
            self._rows[row_index].set_data(data=data)
            cell_values = self._row_cell_values_creator(row_index, data)
            self._rows[row_index].set_cell_values(cell_values=cell_values)

    def adjust_row_index_cells(self, start_row_index: int = 0):
        row_count = self.row_count
        row_index = start_row_index
        while row_index < row_count:
            row_index_cell_value = self._row_index_cell_value_creator(row_index)
            self._rows[row_index].set_row_index_cell_value(
                row_index_cell_value=row_index_cell_value
            )
            row_index = row_index + 1

    def _get_row_based_on_condition(
        self, condition: Callable[[TableRow], bool]
    ) -> Optional[RowInfo]:
        row_index = 0
        while row_index < self.row_count:
            current_row = self._rows[row_index]
            if condition(current_row):
                return RowInfo(
                    row_index=row_index,
                    data=current_row.data,
                )
            row_index = row_index + 1
        return None
