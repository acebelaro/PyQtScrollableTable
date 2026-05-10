from enum import Enum
from typing import Any, Callable, Optional
from qt_table_types import TableCreateAddRowParam, TableDeleteRowParam
from qt_table_undo_redo import TableEvent, TableUndoRedo
from qt_table_value_rows import TableValueRowInfo


class CopyType(Enum):
    NONE = 0
    COPY = 1
    CUT = 2


class TableCopyCutPaste:

    def __init__(
        self,
        # fmt: off
        selected_row_provider: Callable[[],Optional[TableValueRowInfo]],
        create_and_add_row_at_index: Callable[[TableCreateAddRowParam], Optional[TableEvent]],
        delete_row: Callable[[TableDeleteRowParam], Optional[TableEvent]],
        create_row_data_copy: Callable[[TableValueRowInfo],Any],
        adjust_row_index_cells: Callable[[int],None],
        undo_redo: TableUndoRedo,
        # fmt: on
    ):
        self._selected_row_provider = selected_row_provider
        self._create_and_add_row_at_index = create_and_add_row_at_index
        self._delete_row = delete_row
        self._create_row_data_copy = create_row_data_copy
        self._adjust_row_index_cells = adjust_row_index_cells
        self._undo_redo = undo_redo
        self._copy_type = CopyType.NONE
        self._copy_row: Optional[TableValueRowInfo] = None

    def set_copy(self):
        selected_row = self._selected_row_provider()
        self._copy_row = selected_row
        if selected_row:
            self._copy_type = CopyType.COPY
            print(f"Set copy {selected_row.row_index}")

    def set_cut(self):
        selected_row = self._selected_row_provider()
        self._copy_row = selected_row
        if selected_row:
            self._copy_type = CopyType.CUT
            print(f"Set cut {selected_row.row_index}")

    def execute_paste(self):
        if self._copy_row and self._copy_type != CopyType.NONE:
            selected_row = self._selected_row_provider()
            if selected_row:
                data_copy = self._create_row_data_copy(self._copy_row)
                create_add_param = TableCreateAddRowParam(
                    row_index=selected_row.row_index,
                    data=data_copy,
                    skip_select=True,
                    confirm_before_adding=False,
                    report_when_added=False,
                )
                add_event = self._create_and_add_row_at_index(create_add_param)
                if add_event:
                    self._undo_redo.add_undo_event(event=add_event)

                self._adjust_row_index_cells(selected_row.row_index)

                if self._copy_type == CopyType.CUT:
                    delete_param = TableDeleteRowParam(
                        row_index=self._copy_row.row_index,
                        confirm_before_deleting=False,
                        report_when_deleted=False,
                    )
                    delete_event = self._delete_row(delete_param)
                    if delete_event:
                        self._undo_redo.add_undo_event(event=add_event)
                    self.reset()

    def reset(self):
        self._copy_type = CopyType.NONE
        self._copy_row: Optional[TableValueRowInfo] = None
