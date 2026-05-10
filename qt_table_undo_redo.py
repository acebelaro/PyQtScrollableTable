from typing import Any, Dict, List, Optional, Callable

from qt_table_types import (
    TableCreateAddRowParam,
    TableDeleteRowParam,
    TableEvent,
    TableEventType,
    TableRowAddEventData,
    TableRowCutEventData,
    TableRowDeleteEventData,
    TableRowEditEventData,
    TableRowMovedEventData,
    TableSwapRowsParam,
)
from qt_table_row import TableRow
from qt_table_row_actions import RowActions, TableRowAction

_DEFAULT_MAX_UNDO_REDO = 10


class TableUndoRedo(TableRowAction):

    def __init__(
        self,
        row_actions: RowActions,
        get_row_at_index: Callable[[int], Optional[TableRow]],
        max_count: int = _DEFAULT_MAX_UNDO_REDO,
    ):
        super().__init__(row_actions=row_actions)
        self._get_row_at_index = get_row_at_index
        self._max_count = max_count
        self._undo_events: List[Any] = []
        self._redo_events: List[Any] = []

        self._revert_functions_map: Dict[
            TableEventType,
            Callable[
                [
                    TableRowAddEventData
                    | TableRowEditEventData
                    | TableRowDeleteEventData
                    | TableRowMovedEventData
                    | TableRowCutEventData
                ],
                Optional[TableEvent],
            ],
        ] = {}

        # fmt: off
        self._revert_functions_map[TableEventType.ROW_ADDED] = self._revert_row_add
        self._revert_functions_map[TableEventType.ROW_DELETED] = self._revert_row_delete
        self._revert_functions_map[TableEventType.ROW_EDITED] = self._revert_row_edit
        self._revert_functions_map[TableEventType.ROW_MOVED_UP] = self._revert_row_move_up
        self._revert_functions_map[TableEventType.ROW_MOVED_DOWN] = self._revert_row_move_down
        self._revert_functions_map[TableEventType.ROW_CUT] = self._revert_row_cut
        # fmt: on

    def add_undo_event(self, event: Any):
        self._undo_events.append(event)
        if len(self._undo_events) > self._max_count:
            del self._undo_events[0]

    def add_redo_event(self, event: Any):
        self._redo_events.append(event)
        if len(self._redo_events) > self._max_count:
            del self._redo_events[0]

    def get_last_undo_event(self) -> Optional[Any]:
        return TableUndoRedo._get_last_event_from_list(events=self._undo_events)

    def get_last_redo_event(self) -> Optional[Any]:
        return TableUndoRedo._get_last_event_from_list(events=self._redo_events)

    def clear(self):
        self._undo_events = []
        self._redo_events = []

    def undo(self):
        """Undo the last table action."""
        last_undo_event = self.get_last_undo_event()
        if last_undo_event:
            row_event_for_redo = self._execute_revert(revert_event=last_undo_event)
            if row_event_for_redo:
                self.add_redo_event(event=row_event_for_redo)

    def redo(self):
        """Redo the last undone table action."""
        last_redo_event = self.get_last_redo_event()
        if last_redo_event:
            row_event_for_undo = self._execute_revert(revert_event=last_redo_event)
            if row_event_for_undo:
                self.add_undo_event(event=row_event_for_undo)

    def _execute_revert(self, revert_event: TableEvent) -> Optional[TableEvent]:
        revert_revert_event = None
        if revert_event.type in self._revert_functions_map:
            revert_revert_event = self._revert_functions_map[revert_event.type](
                revert_event.event_data
            )
        return revert_revert_event

    def _revert_row_add(
        self,
        add_event_data: TableRowAddEventData,
    ) -> TableEvent:
        delete_param = TableDeleteRowParam(
            row_index=add_event_data.row_index,
            confirm_before_deleting=False,
            report_when_deleted=False,
        )
        revert_add = self._row_actions.delete_row(delete_param)
        return revert_add

    def _revert_row_delete(
        self, delete_event_data: TableRowDeleteEventData
    ) -> TableEvent:
        create_add_param = TableCreateAddRowParam(
            row_index=delete_event_data.row_index,
            data=delete_event_data.row_data,
            skip_select=True,
            confirm_before_adding=False,
            report_when_added=False,
        )
        revert_delete = self._row_actions.create_and_add_row_at_index(create_add_param)
        return revert_delete

    def _revert_row_edit(self, edit_event_data: TableRowEditEventData) -> TableEvent:
        revert_edit = None
        edit_row_index = edit_event_data.row_index
        current_row = self._get_row_at_index(edit_row_index)
        if current_row:
            # replace with new row to avoid on update triggers
            # that can register revert event
            is_selected = current_row.is_selected
            current_row_data = current_row.data
            delete_param = TableDeleteRowParam(
                row_index=edit_row_index,
                confirm_before_deleting=False,
                report_when_deleted=False,
            )
            self._row_actions.delete_row(delete_param)
            create_add_param = TableCreateAddRowParam(
                row_index=edit_row_index,
                data=edit_event_data.row_data,
                skip_select=True,
                confirm_before_adding=False,
                report_when_added=False,
            )
            self._row_actions.create_and_add_row_at_index(create_add_param)
            revert_edit = TableEvent(
                type=TableEventType.ROW_EDITED,
                event_data=TableRowEditEventData(
                    row_index=edit_row_index,
                    row_data=current_row_data,
                ),
            )
            if is_selected:
                edited_row = self._get_row_at_index(edit_row_index)
                if edited_row:
                    edited_row.set_as_selected()
        return revert_edit

    def _revert_row_move_up(
        self,
        moved_event_data: TableRowMovedEventData,
    ) -> TableEvent:
        revert_swap = None
        upper_row_index = moved_event_data.row_index - 1
        swap_param = TableSwapRowsParam(
            upper_row_index=upper_row_index,
            lower_row_index=moved_event_data.row_index,
            confirm_before_swapping=False,
            report_when_swapped=False,
        )
        is_swapped = self._row_actions.swap_rows(swap_param)
        if is_swapped:
            revert_swap = TableEvent(
                type=TableEventType.ROW_MOVED_UP,
                event_data=TableRowMovedEventData(
                    row_index=moved_event_data.row_index,
                ),
            )
        return revert_swap

    def _revert_row_cut(
        self,
        cut_event_data: TableRowCutEventData,
    ) -> TableEvent:
        revert_row_cut = None
        # re-add deleted row
        create_add_param = TableCreateAddRowParam(
            row_index=cut_event_data.deleted_row_index,
            data=cut_event_data.data,
            skip_select=True,
            confirm_before_adding=False,
            report_when_added=False,
        )
        self._row_actions.create_and_add_row_at_index(create_add_param)

        # delete added row
        delete_param = TableDeleteRowParam(
            row_index=cut_event_data.added_row_index,
            confirm_before_deleting=False,
            report_when_deleted=False,
        )
        self._row_actions.delete_row(delete_param)
        revert_row_cut = TableEvent(
            type=TableEventType.ROW_CUT,
            event_data=TableRowCutEventData(
                deleted_row_index=cut_event_data.added_row_index,
                added_row_index=cut_event_data.deleted_row_index,
                data=cut_event_data.data,
            ),
        )
        return revert_row_cut

    def _revert_row_move_down(
        self,
        moved_event_data: TableRowMovedEventData,
    ) -> TableEvent:
        revert_swap = None
        lower_row_index = moved_event_data.row_index + 1
        swap_param = TableSwapRowsParam(
            upper_row_index=moved_event_data.row_index,
            lower_row_index=lower_row_index,
            confirm_before_swapping=False,
            report_when_swapped=False,
        )
        is_swapped = self._row_actions.swap_rows(swap_param)
        if is_swapped:
            revert_swap = TableEvent(
                type=TableEventType.ROW_MOVED_DOWN,
                event_data=TableRowMovedEventData(
                    row_index=moved_event_data.row_index,
                ),
            )
        return revert_swap

    @staticmethod
    def _get_last_event_from_list(events: List[Any]) -> Optional[Any]:
        event_count = len(events)
        if event_count > 0:
            last_event = events[event_count - 1]
            del events[event_count - 1]
            return last_event
        return None
