from collections.abc import Callable
from enum import Enum, auto
from typing import Any, List, NamedTuple, Optional

from qt_table_row import TableRow

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
    create_row: Callable[[int, Any], TableRow]
    add_row_at_index: Callable[[int, TableRow, bool], None]
    delete_row_at_index: Callable[[int], None]
    swap_rows: Callable[[int, int], bool]


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
            print("Reverting add...")
            # delete that row
            revert_revert_event = self._actions.delete_row_at_index(
                revert_event.row_index
            )
            # revert_revert_event = self._delete_row_at_index(
            #     row_index=revert_event.row_index
            # )
        elif revert_event.type == TableEventType.ROW_DELETED:
            # add in row index
            new_row = self._actions.create_row(
                revert_event.row_index,
                revert_event.data,
            )
            # new_row = self._create_row(
            #     row_index=revert_event.row_index, data=revert_event.data
            # )
            revert_revert_event = self._actions.add_row_at_index(
                revert_event.row_index,
                new_row,
                False,
            )
            # revert_revert_event = self._add_row_at_index(
            #     row_index=revert_event.row_index,
            #     row=new_row,
            #     skip_select=True,
            # )
        elif revert_event.type == TableEventType.ROW_EDITED:
            # update data in cell
            edit_row_index = revert_event.row_index
            # current_row = self._value_rows.get_row_at_index(row_index=edit_row_index)
            current_row = self._get_row_at_index(edit_row_index)
            if current_row:
                # replace with new row to avoid on update triggers
                # that can register revert event
                is_selected = current_row.is_selected
                current_row_data = current_row.data
                self._actions.delete_row_at_index(edit_row_index)
                # self._delete_row_at_index(row_index=edit_row_index)
                new_row = self._actions.create_row(edit_row_index, revert_event.data)
                # new_row = self._create_row(
                #     row_index=edit_row_index, data=revert_event.data
                # )
                self._actions.add_row_at_index(
                    edit_row_index,
                    new_row,
                    False,
                )
                # self._add_row_at_index(
                #     row_index=edit_row_index,
                #     row=new_row,
                #     skip_select=True,
                # )
                revert_revert_event = TableEvent(
                    type=TableEventType.ROW_EDITED,
                    row_index=edit_row_index,
                    data=current_row_data,
                )
                if is_selected:
                    new_row.set_as_selected()
        elif revert_event.type == TableEventType.ROW_MOVED_UP:
            # move row down
            upper_row_index = revert_event.row_index - 1
            is_swapped = self._actions.swap_rows(
                upper_row_index,
                revert_event.row_index,
            )
            if is_swapped:
                revert_revert_event = TableEvent(
                    type=TableEventType.ROW_MOVED_UP,
                    row_index=revert_event.row_index,
                    data=None,  # not used
                )
        elif revert_event.type == TableEventType.ROW_MOVED_DOWN:
            # move row up
            lower_row_index = revert_event.row_index + 1
            is_swapped = self._actions.swap_rows(
                revert_event.row_index,
                lower_row_index,
            )
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
