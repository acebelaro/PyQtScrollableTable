"""
Module defining row action interfaces for table operations.

This module provides the `RowActions` named tuple and `TableRowAction` base class
that define the interface for performing actions on table rows. These actions
include creating, deleting, swapping, and copying rows.

The `RowActions` tuple serves as a dependency injection mechanism, allowing
different components (like undo/redo and copy/cut/paste) to perform row operations
without direct coupling to the main table implementation.

Classes:
    RowActions: A named tuple containing callable actions for row operations
    TableRowAction: Base class for components that perform row actions
"""
from typing import Any, Callable, NamedTuple, Optional
from qt_table_types import (
    RowInfo,
    TableCreateAddRowParam,
    TableDeleteRowParam,
    TableEvent,
    TableSwapRowsParam,
)


class RowActions(NamedTuple):
    # fmt: off
    selected_row_provider: Callable[[], Optional[RowInfo]]
    create_and_add_row_at_index: Callable[[TableCreateAddRowParam], Optional[TableEvent]]
    delete_row: Callable[[TableDeleteRowParam], Optional[TableEvent]]
    swap_rows: Callable[[TableSwapRowsParam], bool]
    create_row_data_copy: Callable[[RowInfo], Any]
    adjust_row_index_cells: Callable[[int],None]
    # fmt: on


class TableRowAction:

    def __init__(
        self,
        row_actions: RowActions,
    ):
        self._row_actions = row_actions
