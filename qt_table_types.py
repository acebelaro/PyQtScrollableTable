from enum import Enum
from typing import Any, Callable, List, NamedTuple, Optional

from PyQt6.QtWidgets import QPushButton


class TableCellUiType(Enum):
    ROW_INDEX_CELL = 0
    EDITABLE_TEXT = 1
    READONLY_TEXT = 2
    CHECKBOX = 3


class TableRowCellConfig(NamedTuple):
    ui_type: TableCellUiType
    width: int
    cell_index: int


class TableButtonControls(NamedTuple):
    delete_selected: Optional[QPushButton] = None
    move_up_selected: Optional[QPushButton] = None
    move_down_selected: Optional[QPushButton] = None


class RowCellValue(NamedTuple):
    row_data: Any
    value: str | bool | int


class RowInfo(NamedTuple):
    row_index: int
    data: Any


class TableRowCellValue(NamedTuple):
    cell_index: int
    value: str | bool | int


class BeforeUpdateConfirmers(NamedTuple):
    confirm_row_addition: Optional[Callable[[RowInfo], bool]] = None
    confirm_row_deletion: Optional[Callable[[RowInfo], bool]] = None
    confirm_row_swap: Optional[Callable[[RowInfo, RowInfo], bool]] = None


class TableColumnConfig(NamedTuple):
    ui_type: TableCellUiType
    text: str
    width: int


class TableHeaderRowConfig(NamedTuple):
    height: int
    header_cell_css_styles: List[str]


class TableElemClassStyle(NamedTuple):
    class_name: str
    styles: List[str]


class RowClassNameDeciderParam(NamedTuple):
    data: Any
    is_selected: bool


class TableValueRowConfig(NamedTuple):
    height: int
    class_styles: Optional[List[TableElemClassStyle]] = None
    row_class_name_decider: Optional[Callable[[RowClassNameDeciderParam], str]] = None


class TableShortcutKeys(NamedTuple):
    ctrl_z_y_undo_redo: Optional[bool] = False
    ctrl_c_x_v_copy_cut_paste: Optional[bool] = True


class TableCreateAddRowParam(NamedTuple):
    row_index: int
    data: Any
    skip_select: Optional[bool] = False
    confirm_before_adding: Optional[bool] = False
    report_when_added: Optional[bool] = True


class TableDeleteRowParam(NamedTuple):
    row_index: int
    confirm_before_deleting: Optional[bool] = False
    report_when_deleted: Optional[bool] = True


class TableSwapRowsParam(NamedTuple):
    upper_row_index: int
    lower_row_index: int
    confirm_before_swapping: Optional[bool] = False
    report_when_swapped: Optional[bool] = True


class TableConfig(NamedTuple):
    header_row_config: TableHeaderRowConfig
    column_configs: List[TableColumnConfig]
    value_row_config: TableValueRowConfig
    button_controls: Optional[TableButtonControls] = None
    before_update_confirmers: Optional[BeforeUpdateConfirmers] = None
    select_new_row_added: bool = True
    select_next_row_after_row_deletion: bool = True
    shortcut_keys: Optional[TableShortcutKeys] = None


class TableRowCellValueUpdatedParam(NamedTuple):
    row_id: str
    current_row_data: Any
    updated_cell_index: int
    new_cell_values: List[TableRowCellValue]
