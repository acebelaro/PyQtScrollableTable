from enum import Enum, auto
from typing import Any, List, NamedTuple, Optional


class TableEventType(Enum):
    ROW_ADDED = auto()
    ROW_DELETED = auto()
    ROW_EDITED = auto()
    ROW_MOVED_UP = auto()


class TableEvent(NamedTuple):
    type: TableEventType
    row_index: int
    data: Any


class TableEventCollection:

    def __init__(self):
        self._undo_events: List[TableEvent] = []
        self._redo_events: List[TableEvent] = []

    def add_undo_event(self, event: TableEvent):
        self._undo_events.append(event)

    def add_redo_event(self, event: TableEvent):
        self._redo_events.append(event)

    def get_last_undo_event(self) -> Optional[TableEvent]:
        return TableEventCollection._get_last_event_from_list(events=self._undo_events)

    def get_last_redo_event(self) -> Optional[TableEvent]:
        return TableEventCollection._get_last_event_from_list(events=self._redo_events)

    def clear(self):
        self._undo_events = []
        self._redo_events = []

    @staticmethod
    def _get_last_event_from_list(events: List[TableEvent]) -> Optional[TableEvent]:
        event_count = len(events)
        if event_count > 0:
            last_event = events[event_count - 1]
            del events[event_count - 1]
            return last_event
        return None
