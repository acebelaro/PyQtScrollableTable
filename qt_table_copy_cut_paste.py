from enum import Enum
from typing import Any, Optional
from qt_table_row_actions import RowActions, TableRowAction
from qt_table_types import (
    RowInfo,
    TableCreateAddRowParam,
    TableDeleteRowParam,
    TableEvent,
    TableEventType,
    TableRowCutEventData,
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
            selected_row = self._row_actions.selected_row_provider()
            if selected_row:
                self._copy_paste_row(
                    source_row=self._copy_row,
                    selected_row=selected_row,
                )

    def reset(self):
        self._copy_type = CopyType.NONE
        self._copy_row: Optional[RowInfo] = None

    def _copy_paste_row(
        self,
        source_row: RowInfo,
        selected_row: RowInfo,
    ):
        adjust_row_index_start = -1
        destination_row_index = selected_row.row_index + 1
        data_copy = self._row_actions.create_row_data_copy(source_row)
        add_event = self._add_new_row_for_paste(
            destination_row_index=destination_row_index,
            data_copy=data_copy,
        )
        adjust_row_index_start = destination_row_index
        if self._copy_type == CopyType.CUT:
            delete_row_index = source_row.row_index
            if selected_row.row_index < delete_row_index:
                delete_row_index = delete_row_index + 1
            delete_event = self._delete_cut_row(delete_row_index=delete_row_index)
            if delete_event:
                # create cut event
                cut_event = TableEvent(
                    type=TableEventType.ROW_CUT,
                    event_data=TableRowCutEventData(
                        deleted_row_index=delete_row_index,
                        added_row_index=destination_row_index,
                        data=source_row.data,
                    ),
                )
                self._undo_redo.add_undo_event(event=cut_event)
                if delete_row_index < adjust_row_index_start:
                    adjust_row_index_start = delete_row_index
            self.reset()
        else:
            # register add event for revert
            if add_event:
                self._undo_redo.add_undo_event(event=add_event)

        if adjust_row_index_start != -1:
            self._row_actions.adjust_row_index_cells(adjust_row_index_start)

    def _add_new_row_for_paste(
        self,
        destination_row_index: int,
        data_copy: Any,
    ) -> TableEvent:
        create_add_param = TableCreateAddRowParam(
            row_index=destination_row_index,
            data=data_copy,
            skip_select=False,
            confirm_before_adding=False,
            report_when_added=False,
        )
        add_event = self._row_actions.create_and_add_row_at_index(create_add_param)
        return add_event

    def _delete_cut_row(self, delete_row_index: int) -> TableEvent:
        delete_param = TableDeleteRowParam(
            row_index=delete_row_index,
            confirm_before_deleting=False,
            report_when_deleted=False,
        )
        delete_event = self._row_actions.delete_row(delete_param)
        return delete_event
