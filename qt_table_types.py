from enum import Enum
from typing import Any, List, NamedTuple, Optional

from PyQt6.QtWidgets import QPushButton


class TableCellUiType(Enum):
    ROW_INDEX_CELL = 0
    EDITABLE_TEXT = 1
    READONLY_TEXT = 2
    CHECKBOX = 3


class TableColumnConfig(NamedTuple):
    ui_type: TableCellUiType
    text: str
    width: int


class TableRowCellConfig(NamedTuple):
    ui_type: TableCellUiType
    cell_index: int
    width: int


class TableButtonControls(NamedTuple):
    delete_selected: Optional[QPushButton] = None
    move_up_selected: Optional[QPushButton] = None
    move_down_selected: Optional[QPushButton] = None


class TableConfig(NamedTuple):
    column_configs: List[TableColumnConfig]
    header_row_height: int
    value_row_height: int
    header_cell_css_styles: List[str]
    selected_row_color_css_value: str
    row_number_cell_format: str = ""
    button_controls: Optional[TableButtonControls] = None


class FieldValue(NamedTuple):
    row_data: Any
    value: str | bool


class TableRowConfig(NamedTuple):
    width: int
    height: int
    selected_row_color_css_value: str


class TableRowCellValue(NamedTuple):
    cell_index: int
    value: str | bool
