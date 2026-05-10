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
