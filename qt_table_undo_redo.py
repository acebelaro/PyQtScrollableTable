from collections.abc import Callable
from enum import Enum, auto
from typing import Any, List, NamedTuple, Optional

from qt_table_row import TableRow
from qt_table_types import (
    TableCreateAddRowParam,
    TableDeleteRowParam,
    TableSwapRowsParam,
)

_DEFAULT_MAX_UNDO_REDO = 10


class TableEventType(Enum):
    ROW_ADDED = auto()
    ROW_DELETED = auto()
    ROW_EDITED = auto()
    ROW_MOVED_UP = auto()
    ROW_MOVED_DOWN = auto()


class TableEvent(NamedTuple):
    type: TableEventType
    row_index: int
    data: Any

    def to_str(self) -> str:
        return f"{self.type.name}, {self.row_index}"


class UndoRedoActions(NamedTuple):
    # fmt: off
    create_and_add_row_at_index: Callable[[TableCreateAddRowParam], Optional[TableEvent]]
    delete_row: Callable[[TableDeleteRowParam], Optional[TableEvent]]
    swap_rows: Callable[[TableSwapRowsParam], bool]
    # fmt: on


class TableUndoRedo:

    def __init__(
        self,
        actions: UndoRedoActions,
        get_row_at_index: Callable[[int], Optional[TableRow]],
        max_count: int = _DEFAULT_MAX_UNDO_REDO,
    ):
        self._actions = actions
        self._get_row_at_index = get_row_at_index
        self._max_count = max_count
        self._undo_events: List[TableEvent] = []
        self._redo_events: List[TableEvent] = []

    def add_undo_event(self, event: TableEvent):
        self._undo_events.append(event)
        print(f"Added undo {event.to_str()}")

        if len(self._undo_events) > self._max_count:
            del self._undo_events[0]

    def add_redo_event(self, event: TableEvent):
        self._redo_events.append(event)
        print(f"Added redo {event.to_str()}")

        if len(self._redo_events) > self._max_count:
            del self._redo_events[0]

    def get_last_undo_event(self) -> Optional[TableEvent]:
        return TableUndoRedo._get_last_event_from_list(events=self._undo_events)

    def get_last_redo_event(self) -> Optional[TableEvent]:
        return TableUndoRedo._get_last_event_from_list(events=self._redo_events)

    def clear(self):
        self._undo_events = []
        self._redo_events = []

    def undo(self):
        print("~~~~~ Undo")
        """Undo the last table action."""
        last_undo_event = self.get_last_undo_event()
        if last_undo_event:
            row_event_for_redo = self._execute_revert(revert_event=last_undo_event)
            if row_event_for_redo:
                self.add_redo_event(event=row_event_for_redo)

    def redo(self):
        print("~~~~~ Redo")
        """Redo the last undone table action."""
        last_redo_event = self.get_last_redo_event()
        if last_redo_event:
            row_event_for_undo = self._execute_revert(revert_event=last_redo_event)
            if row_event_for_undo:
                self.add_undo_event(event=row_event_for_undo)

    def _execute_revert(self, revert_event: TableEvent) -> Optional[TableEvent]:
        print("_execute_revert()")
        print(revert_event)
        revert_revert_event = None
        if revert_event.type == TableEventType.ROW_ADDED:
            # delete that row
            delete_param = TableDeleteRowParam(
                row_index=revert_event.row_index,
                confirm_before_deleting=False,
                report_when_deleted=False,
            )
            revert_revert_event = self._actions.delete_row(delete_param)
        elif revert_event.type == TableEventType.ROW_DELETED:
            create_add_param = TableCreateAddRowParam(
                row_index=revert_event.row_index,
                data=revert_event.data,
                skip_select=True,
                confirm_before_adding=False,
                report_when_added=False,
            )
            revert_revert_event = self._actions.create_and_add_row_at_index(
                create_add_param
            )
        elif revert_event.type == TableEventType.ROW_EDITED:
            # update data in cell
            edit_row_index = revert_event.row_index
            current_row = self._get_row_at_index(edit_row_index)
            if current_row:
                # replace with new row to avoid on update triggers
                # that can register revert event
                is_selected = current_row.is_selected
                current_row_data = current_row.data
                delete_param = TableDeleteRowParam(
                    row_index=revert_event.row_index,
                    confirm_before_deleting=False,
                    report_when_deleted=False,
                )
                revert_revert_event = self._actions.delete_row(delete_param)
                create_add_param = TableCreateAddRowParam(
                    row_index=edit_row_index,
                    data=revert_event.data,
                    skip_select=True,
                    confirm_before_adding=False,
                    report_when_added=False,
                )
                self._actions.create_and_add_row_at_index(create_add_param)
                revert_revert_event = TableEvent(
                    type=TableEventType.ROW_EDITED,
                    row_index=edit_row_index,
                    data=current_row_data,
                )
                if is_selected:
                    edited_row = self._get_row_at_index(edit_row_index)
                    if edited_row:
                        edited_row.set_as_selected()
        elif revert_event.type == TableEventType.ROW_MOVED_UP:
            # move row down
            upper_row_index = revert_event.row_index - 1
            swap_param = TableSwapRowsParam(
                upper_row_index=upper_row_index,
                lower_row_index=revert_event.row_index,
                confirm_before_swapping=False,
                report_when_swapped=False,
            )
            is_swapped = self._actions.swap_rows(swap_param)
            if is_swapped:
                revert_revert_event = TableEvent(
                    type=TableEventType.ROW_MOVED_UP,
                    row_index=revert_event.row_index,
                    data=None,  # not used
                )
        elif revert_event.type == TableEventType.ROW_MOVED_DOWN:
            # move row up
            lower_row_index = revert_event.row_index + 1
            swap_param = TableSwapRowsParam(
                upper_row_index=revert_event.row_index,
                lower_row_index=lower_row_index,
                confirm_before_swapping=False,
                report_when_swapped=False,
            )
            is_swapped = self._actions.swap_rows(swap_param)
            if is_swapped:
                revert_revert_event = TableEvent(
                    type=TableEventType.ROW_MOVED_DOWN,
                    row_index=revert_event.row_index,
                    data=None,  # not used
                )
        return revert_revert_event

    @staticmethod
    def _get_last_event_from_list(events: List[TableEvent]) -> Optional[TableEvent]:
        event_count = len(events)
        if event_count > 0:
            last_event = events[event_count - 1]
            del events[event_count - 1]
            return last_event
        return None
