from enum import Enum
from typing import Optional
from qt_table_row_actions import RowActions, TableRowAction
from qt_table_types import (
    RowInfo,
    TableCreateAddRowParam,
    TableDeleteRowParam,
    TableEvent,
    TableEventType,
)
from qt_table_undo_redo import TableUndoRedo


class CopyType(Enum):
    NONE = 0
    COPY = 1
    CUT = 2


class TableCopyCutPaste(TableRowAction):

    def __init__(
        self,
        row_actions: RowActions,
        undo_redo: TableUndoRedo,
    ):
        super().__init__(row_actions=row_actions)
        self._undo_redo = undo_redo
        self._copy_type = CopyType.NONE
        self._copy_row: Optional[RowInfo] = None

    def set_copy(self):
        selected_row = self._row_actions.selected_row_provider()
        self._copy_row = selected_row
        if selected_row:
            self._copy_type = CopyType.COPY
            print(f"Set copy {selected_row.row_index}")

    def set_cut(self):
        selected_row = self._row_actions.selected_row_provider()
        self._copy_row = selected_row
        if selected_row:
            self._copy_type = CopyType.CUT
            print(f"Set cut {selected_row.row_index}")

    def execute_paste(self):
        if self._copy_row and self._copy_type != CopyType.NONE:
            add_event = None
            destination_row = self._row_actions.selected_row_provider()
            if destination_row:
                data_copy = self._row_actions.create_row_data_copy(self._copy_row)
                print(f"Created copy of data of row {self._copy_row.row_index}.")
                destination_row_index = destination_row.row_index + 1
                create_add_param = TableCreateAddRowParam(
                    row_index=destination_row_index,
                    data=data_copy,
                    skip_select=False,
                    confirm_before_adding=False,
                    report_when_added=False,
                )
                add_event = self._row_actions.create_and_add_row_at_index(
                    create_add_param
                )
                self._row_actions.adjust_row_index_cells(destination_row.row_index)
                if self._copy_type == CopyType.CUT:
                    delete_row_index = self._copy_row.row_index
                    if destination_row.row_index < delete_row_index:
                        delete_row_index = delete_row_index + 1
                    delete_param = TableDeleteRowParam(
                        row_index=delete_row_index,
                        confirm_before_deleting=False,
                        report_when_deleted=False,
                    )
                    delete_event = self._row_actions.delete_row(delete_param)
                    if delete_event:
                        # create cut event
                        cut_event = TableEvent(
                            type=TableEventType.ROW_CUT,
                            row_index=destination_row_index,
                            data=self._copy_row.data,
                            delete_row_index=delete_row_index,
                        )
                        self._undo_redo.add_undo_event(event=cut_event)
                    self.reset()
                else:
                    # register add event for revert
                    if add_event:
                        self._undo_redo.add_undo_event(event=add_event)

    def reset(self):
        self._copy_type = CopyType.NONE
        self._copy_row: Optional[RowInfo] = None
