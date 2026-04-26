from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, List, NamedTuple, Optional
from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QWidget,
    QGroupBox,
    QScrollArea,
    QLabel,
    QVBoxLayout,
    QCheckBox,
    QLineEdit,
    QPushButton,
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QMouseEvent
import uuid

ROW_INDEX_PLACEHOLDER_TOKEN = "%row_index%"

_TABLE_HEADER_CELL_GROUPBOX_NAME = "QtTableHeaderCellGroupBox"
_TABLE_ROW_GROUPBOX_NAME = "QtTableRowGroupBox"
_TABLE_ROW_VALUE_CELL_GROUPBOX_NAME = "QtTableRowValueCellGroupBox"
_TABLE_ROW_VALUE_CELL_TEXTBOX_GROUPBOX_NAME = "QtTableRowCellEditTextbox"
_TABLE_ROW_SELECTED_CLASS_VALUE = "selected-row"


class TableCellUiType(Enum):
    ROW_INDEX_CELL = 0
    EDITABLE_TEXT = 1
    READONLY_TEXT = 2
    CHECKBOX = 3


class TableColumnConfig(NamedTuple):
    ui_type: TableCellUiType
    text: str
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


class TableRowCellConfig(NamedTuple):
    ui_type: TableCellUiType
    cell_index: int
    width: int


class TableRowCellValueWidget(ABC):

    def __init__(
        self,
        ui_type: TableCellUiType,
        cell_index: int,
        on_value_updated: Optional[Callable[[int, Any], None]],
    ):
        super().__init__()
        self._ui_type = ui_type
        self._cell_index = cell_index
        self._on_value_updated = on_value_updated

    @property
    def ui_type(self) -> TableCellUiType:
        return self._ui_type

    @property
    def cell_index(self) -> int:
        return self._cell_index

    @abstractmethod
    def set_value(self, value: Any):
        raise NotImplementedError()

    @abstractmethod
    def get_value(self) -> Any:
        raise NotImplementedError()


class TableRowCellTextbox(TableRowCellValueWidget):

    def __init__(
        self,
        parent: QGroupBox,
        cell_index: int,
        width: int,
        value: bool,
        on_value_updated: Optional[Callable[[int, str], None]],
    ):
        super().__init__(
            ui_type=TableCellUiType.EDITABLE_TEXT,
            cell_index=cell_index,
            on_value_updated=on_value_updated,
        )
        self._line_edit = QLineEdit(parent=parent)
        self._line_edit.setObjectName(_TABLE_ROW_VALUE_CELL_TEXTBOX_GROUPBOX_NAME)
        self._line_edit.setStyleSheet(
            f"QLineEdit#{_TABLE_ROW_VALUE_CELL_TEXTBOX_GROUPBOX_NAME} {{ border: none; }}"
        )
        self._line_edit.setGeometry(
            QtCore.QRect(
                10,
                10,
                width - 20,
                20,
            )
        )
        self._line_edit.textChanged.connect(self._text_updated)
        self.set_value(value=value)

    def set_value(self, value: str):
        self._line_edit.setText(value)

    def get_value(self) -> str:
        return self._line_edit.text()

    def _text_updated(self):
        self._on_value_updated(self._cell_index, self._line_edit.text())


class TableRowCellCheckbox(TableRowCellValueWidget):

    def __init__(
        self,
        parent: QGroupBox,
        cell_index: int,
        width: int,
        value: bool,
        on_value_updated: Optional[Callable[[int, bool], None]],
    ):
        super().__init__(
            ui_type=TableCellUiType.CHECKBOX,
            cell_index=cell_index,
            on_value_updated=on_value_updated,
        )
        self._check_box = QCheckBox(parent=parent)
        self._check_box.setGeometry(
            QtCore.QRect(
                10,
                10,
                width - 20,
                20,
            )
        )
        self._check_box.checkStateChanged.connect(self._checked_updated)
        self.set_value(value=value)

    def set_value(self, value: str):
        self._check_box.setChecked(value)

    def get_value(self) -> bool:
        return self._check_box.isChecked()

    def _checked_updated(self):
        self._on_value_updated(self._cell_index, self._check_box.isChecked())


class TableRowCellLabel(TableRowCellValueWidget):

    def __init__(
        self,
        ui_type: TableCellUiType,
        parent: QGroupBox,
        cell_index: int,
        width: int,
        text: bool,
    ):
        super().__init__(
            ui_type=ui_type,
            cell_index=cell_index,
            on_value_updated=None,
        )
        self._label = QLabel(parent=parent)
        self._label.setGeometry(
            QtCore.QRect(
                10,
                10,
                width - 20,
                20,
            )
        )
        self.set_value(value=text)

    def set_value(self, value: str):
        self._label.setText(value)

    def get_value(self) -> str:
        return self._label.text()


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


class TableRow(QWidget):

    on_value_cell_updated = pyqtSignal(str, int, FieldValue)
    on_row_selected_state_updated = pyqtSignal(str, bool)
    on_row_double_clicked = pyqtSignal(str)

    _on_update_selected_state = pyqtSignal()

    def __init__(
        self,
        config: TableRowConfig,
        cell_configs: List[TableRowCellConfig],
        id: str = "",
        data: Optional[Any] = None,
    ):
        super().__init__()
        self._config = config
        self._cell_configs = cell_configs
        self._id = id
        self._data = data
        self._cell_widgets: List[TableRowCellValueWidget] = []
        self._is_selected = False

        if self._id == "":
            self._id = str(uuid.uuid4())

        self._row_group_box = QGroupBox(parent=self)
        self._row_group_box.setGeometry(QtCore.QRect(0, 0, config.width, config.height))
        self._row_group_box.setTitle("")
        self._update_property_due_to_selected_state()

        self._create_row_fields_ui(row_group_box=self._row_group_box)

        self.setFixedHeight(config.height)

        self._on_update_selected_state.connect(
            self._update_property_due_to_selected_state
        )

    @property
    def id(self) -> str:
        return self._id

    @property
    def row_index_str(self) -> str:
        row_index_cell_widget = self._get_row_index_cell_widget()
        if row_index_cell_widget:
            return row_index_cell_widget.get_value()
        return ""

    @property
    def data(self) -> Optional[Any]:
        return self._data

    @property
    def is_selected(self) -> bool:
        return self._is_selected

    def clear_selected_state(self):
        self._is_selected = False
        self._update_property_due_to_selected_state()

    def mousePressEvent(self, event: QMouseEvent):
        self._is_selected = not self._is_selected
        self._on_update_selected_state.emit()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.on_row_double_clicked.emit(self._id)

    def set_row_index_cell_value(self, row_index_cell_value: str):
        row_index_cell_widget = self._get_row_index_cell_widget()
        if row_index_cell_widget:
            row_index_cell_widget.set_value(value=row_index_cell_value)

    def set_cell_values(self, cell_values: List[TableRowCellValue]):
        for cell_widget in self._cell_widgets:
            cell_info = next(
                (c for c in cell_values if c.cell_index == cell_widget.cell_index),
                None,
            )
            if cell_info:
                cell_widget.set_value(cell_info.value)
            else:
                raise ValueError(
                    f"Cannot find value for cell widget index '{cell_widget.cell_index}'"
                )

    @abstractmethod
    def _create_ui(self, row_group_box: QGroupBox) -> None:
        raise NotImplementedError()

    def _get_row_index_cell_widget(self) -> Optional[TableRowCellValueWidget]:
        return next(
            (
                c
                for c in self._cell_widgets
                if c.ui_type == TableCellUiType.ROW_INDEX_CELL
            ),
            None,
        )

    def _create_row_fields_ui(self, row_group_box: QGroupBox):
        row_cell_x_pos = 0
        cell_index = 0
        for cell_config in self._cell_configs:
            self._create_row_cell_groupbox(
                row_group_box=row_group_box,
                cell_index=cell_index,
                cell_config=cell_config,
                x_pos=row_cell_x_pos,
            )
            row_cell_x_pos = row_cell_x_pos + cell_config.width
            cell_index = cell_index + 1

    def _create_row_cell_groupbox(
        self,
        row_group_box: QGroupBox,
        cell_index: int,
        cell_config: TableRowCellConfig,
        x_pos: int,
    ) -> QGroupBox:
        row_cell_group_box = QGroupBox(parent=row_group_box)
        row_cell_group_box.setGeometry(
            QtCore.QRect(
                x_pos,
                0,
                cell_config.width,
                self._config.height - 1,
            )
        )
        row_cell_group_box.setObjectName(_TABLE_ROW_VALUE_CELL_GROUPBOX_NAME)
        row_cell_group_box.setStyleSheet(
            f"QGroupBox#{_TABLE_ROW_VALUE_CELL_GROUPBOX_NAME}{{ border: 1px solid lightgray; }}"
        )
        row_cell_value_widget = self._create_row_cell_value_widget(
            row_cell_group_box=row_cell_group_box,
            cell_index=cell_index,
            cell_config=cell_config,
        )
        if row_cell_value_widget:
            self._cell_widgets.append(row_cell_value_widget)
        return row_cell_group_box

    def _create_row_cell_value_widget(
        self,
        row_cell_group_box: QGroupBox,
        cell_index: int,
        cell_config: TableRowCellConfig,
    ) -> TableRowCellValueWidget:
        row_cell_widget = None
        if cell_config.ui_type == TableCellUiType.CHECKBOX:
            row_cell_widget = TableRowCellCheckbox(
                parent=row_cell_group_box,
                cell_index=cell_index,
                width=cell_config.width,
                value=False,
                on_value_updated=self._checkbox_cell_checked_updated,
            )
        elif (
            cell_config.ui_type == TableCellUiType.READONLY_TEXT
            or cell_config.ui_type == TableCellUiType.ROW_INDEX_CELL
        ):
            row_cell_widget = TableRowCellLabel(
                ui_type=cell_config.ui_type,
                parent=row_cell_group_box,
                cell_index=cell_config.cell_index,
                width=cell_config.width,
                text="",
            )
        elif cell_config.ui_type == TableCellUiType.EDITABLE_TEXT:
            row_cell_widget = TableRowCellTextbox(
                parent=row_cell_group_box,
                cell_index=cell_index,
                width=cell_config.width,
                value="",
                on_value_updated=self._textbox_cell_text_updated,
            )
        else:
            raise ValueError(f"Unsupported ui type {cell_config.ui_type.name}")
        return row_cell_widget

    def _checkbox_cell_checked_updated(self, cell_index: int, checked: bool):
        field_value = FieldValue(
            row_data=self.data,
            value=checked,
        )
        self.on_value_cell_updated.emit(
            self._id,
            cell_index,
            field_value,
        )

    def _textbox_cell_text_updated(self, cell_index: int, text: str):
        field_value = FieldValue(
            row_data=self.data,
            value=text,
        )
        self.on_value_cell_updated.emit(
            self._id,
            cell_index,
            field_value,
        )

    def _update_property_due_to_selected_state(self):
        current_class_value = self._row_group_box.property("class")
        new_class_value = ""
        if self._is_selected:
            new_class_value = _TABLE_ROW_SELECTED_CLASS_VALUE
        else:
            new_class_value = ""

        if current_class_value != new_class_value:
            self._row_group_box.setProperty("class", new_class_value)
            css_style_text = (
                f"QGroupBox#{_TABLE_ROW_GROUPBOX_NAME}{{ border: 1px solid black; }}"
            )
            self._row_group_box.setStyleSheet(css_style_text)
            self._row_group_box.setObjectName(_TABLE_ROW_GROUPBOX_NAME)
            css_style_text = f"""QGroupBox#{_TABLE_ROW_GROUPBOX_NAME}{{
        border: 1px solid black;
    }}
    .selected-row {{
        background-color: {self._config.selected_row_color_css_value};
    }}"""
            self._row_group_box.setStyleSheet(css_style_text)
            self.on_row_selected_state_updated.emit(self._id, self._is_selected)


class TableRowInfo(NamedTuple):
    row: TableRow
    row_index: int


class Table(ABC):

    on_rows_swapped = pyqtSignal(int, int)

    def __init__(
        self,
        name: str,
        groupbox_container: QGroupBox,
        table_config: TableConfig,
    ):
        super().__init__()
        self._name = name
        self._groupbox_container = groupbox_container
        self._table_config = table_config

        self._row_width = 0
        self._columng_group_boxes: List[QGroupBox] = self._create_header_row()

        # create scroll area
        self._scroll_area = QScrollArea(parent=self._groupbox_container)
        self._scroll_area.setGeometry(
            QtCore.QRect(
                0,
                self._table_config.header_row_height,
                self._groupbox_container.width(),
                self._groupbox_container.height()
                - self._table_config.header_row_height,
            )
        )
        self._scroll_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self._scroll_area.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setObjectName("scrollAreaActionList")

        self._scroll_area_content = QWidget()
        self._scroll_area_content.setGeometry(self._scroll_area.rect())
        self._scroll_area.setWidget(self._scroll_area_content)

        self._table_layout = QVBoxLayout()
        self._table_layout.addStretch()
        self._table_layout.setContentsMargins(0, 0, 0, 0)
        self._table_layout.setSpacing(0)
        self._scroll_area_content.setLayout(self._table_layout)

        if table_config.button_controls:
            button_control = table_config.button_controls
            if button_control.delete_selected:
                button_control.delete_selected.clicked.connect(self._delete_selected)
            if button_control.move_up_selected:
                button_control.move_up_selected.clicked.connect(self._move_up_selected)
            if button_control.move_down_selected:
                button_control.move_down_selected.clicked.connect(
                    self._move_down_selected
                )

        self._rows: List[TableRow] = []

    @property
    def rows(self) -> List[TableRow]:
        return self._rows

    @property
    def row_count(self) -> int:
        return len(self._rows)

    @property
    def selected_row(self) -> Optional[TableRow]:
        return next((b for b in self._rows if b.is_selected), None)

    def add_new_row(self, data: Any):
        """Create and add new row at the bottom."""
        row_index = self.row_count
        new_row = self._create_row(row_index=row_index, data=data)
        self.add_row_at_index(row_index=row_index, row=new_row)

    def add_row_at_index(self, row_index: int, row: TableRow):
        print(f"Adding at row {row_index}")
        self._rows.insert(row_index, row)
        self._table_layout.insertWidget(row_index, row)

        row.on_value_cell_updated.connect(self._on_value_cell_updated)
        row.on_row_selected_state_updated.connect(self._on_row_selected_state_updated)
        row.on_row_double_clicked.connect(self._on_row_double_clicked)

    def update_row_at_index(self, row_index: int, data: Any):
        if row_index < self.row_count:
            cell_values = self._create_row_cell_values(row_index=row_index, data=data)
            self._rows[row_index].set_cell_values(cell_values=cell_values)

    def _create_header_row(self) -> List[QGroupBox]:
        columng_group_boxes: List[QGroupBox] = []
        self._row_width = 0
        table_column_config_count = len(self._table_config.column_configs)
        for index in range(table_column_config_count):
            table_column_config = self._table_config.column_configs[index]
            is_last_column = False
            if index != (table_column_config_count - 1):
                is_last_column = True
            columng_group_box = self._create_header_cell_group_box(
                table_column_config=table_column_config,
                x_pos=self._row_width,
                is_last_column=is_last_column,
            )
            self._row_width = self._row_width + table_column_config.width
            columng_group_boxes.append(columng_group_box)
        if self._row_width > self._groupbox_container.width():
            raise ValueError(
                f"Table '{self._name}' column header total width exceeds given group box container width!"
            )
        return columng_group_boxes

    def _create_header_cell_group_box(
        self,
        table_column_config: TableColumnConfig,
        x_pos: int,
        is_last_column: bool,
    ) -> QGroupBox:

        columng_group_box = QGroupBox(parent=self._groupbox_container)
        columng_group_box.setGeometry(
            QtCore.QRect(
                x_pos,
                0,
                table_column_config.width,
                self._table_config.header_row_height,
            )
        )
        css_style_text = "; ".join(self._table_config.header_cell_css_styles)
        css_style_text = f"{css_style_text}; border: 1px solid black;"
        if is_last_column:
            css_style_text = f"{css_style_text} border-right: none;"
        css_style_text = (
            f"QGroupBox#{_TABLE_HEADER_CELL_GROUPBOX_NAME}{{ {css_style_text} }}"
        )
        columng_group_box.setObjectName(_TABLE_HEADER_CELL_GROUPBOX_NAME)
        columng_group_box.setStyleSheet(css_style_text)
        columng_group_box.setTitle("")

        column_text_label = QLabel(parent=columng_group_box)
        column_text_label.setGeometry(
            QtCore.QRect(
                0,
                0,
                table_column_config.width,
                self._table_config.header_row_height,
            )
        )
        column_text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        column_text_label.setText(table_column_config.text)

    def _create_empty_table_row_field_configs(self) -> 1:
        row_field_config_list: List[TableRowCellConfig] = []
        cell_index = 0
        for column_config in self._table_config.column_configs:
            row_field_config_list.append(
                TableRowCellConfig(
                    ui_type=column_config.ui_type,
                    cell_index=cell_index,
                    width=column_config.width,
                )
            )
            cell_index = cell_index + 1
        return row_field_config_list

    def _create_row_index_cell_value(self, row_index: int) -> str:
        row_index_str = f"{row_index+1}"
        if self._table_config.row_number_cell_format != "":
            return self._table_config.row_number_cell_format.replace(
                ROW_INDEX_PLACEHOLDER_TOKEN, row_index_str
            )
        return row_index_str

    def _on_value_cell_updated(self, id: str, cell_index: int, value: FieldValue):
        print("In table _on_value_cell_updated:")
        print(id, cell_index, value)

    def _on_row_selected_state_updated(self, id: str, is_selected: bool):
        print("In table _on_row_selected_state_updated:")
        print(id, is_selected)

        if is_selected:
            for row in self._rows:
                if row.id != id:
                    row.clear_selected_state()

    def _on_row_double_clicked(self, id: str):
        print("In table _on_row_double_clicked:")
        print(id)

    def _get_row_index(self, row: TableRow) -> int:
        row_index = 0
        while row_index < self.row_count:
            if row.id == self._rows[row_index].id:
                return row_index
            row_index = row_index + 1
        return -1

    def _adjust_row_index_cells(self, start_row_index: int = 0):
        row_count = self.row_count
        row_index = start_row_index
        while row_index < row_count:
            row_index_cell_value = self._create_row_index_cell_value(
                row_index=row_index
            )
            self._rows[row_index].set_row_index_cell_value(
                row_index_cell_value=row_index_cell_value
            )
            row_index = row_index + 1

    def _get_selected_row_info(self) -> Optional[TableRowInfo]:
        selected_row = self.selected_row
        if selected_row:
            selected_row_index = self._get_row_index(row=selected_row)
            if selected_row_index != -1:
                return TableRowInfo(
                    row=selected_row,
                    row_index=selected_row_index,
                )
        return None

    def _swap_row_index(
        self,
        upper_row_info: TableRowInfo,
        lower_row_info: TableRowInfo,
    ):
        print(
            f"Swapping {upper_row_info.row.row_index_str} <-> {lower_row_info.row.row_index_str}..."
        )

        deleted_row = self._rows[lower_row_info.row_index]
        del self._rows[lower_row_info.row_index]
        self._table_layout.removeWidget(lower_row_info.row)

        self._rows.insert(upper_row_info.row_index, deleted_row)
        self._table_layout.insertWidget(upper_row_info.row_index, deleted_row)

        lower_row_index_cell_value = self._create_row_index_cell_value(
            row_index=lower_row_info.row_index
        )
        upper_row_index_cell_value = self._create_row_index_cell_value(
            row_index=upper_row_info.row_index
        )

        self._rows[lower_row_info.row_index].set_row_index_cell_value(
            row_index_cell_value=lower_row_index_cell_value
        )
        self._rows[upper_row_info.row_index].set_row_index_cell_value(
            row_index_cell_value=upper_row_index_cell_value
        )

        print("Updated rows")
        for row in self._rows:
            print(f"  {row.row_index_str}")

        self._on_rows_swapped(
            lower_row_index=lower_row_info.row_index,
            upper_row_index=upper_row_info.row_index,
        )

    def _delete_selected(self):
        selected_row_info = self._get_selected_row_info()
        if selected_row_info:
            selected_row = selected_row_info.row
            selected_row_index = selected_row_info.row_index
            data = self._rows[selected_row_index].data
            del self._rows[selected_row_index]
            self._table_layout.removeWidget(selected_row)
            selected_row.setParent(None)
            selected_row.deleteLater()

            self._adjust_row_index_cells(start_row_index=selected_row_index)

            self._on_row_deleted(row_index=selected_row_index, data=data)
        else:
            print("No selected row index.")

    def _move_up_selected(self):
        selected_row_info = self._get_selected_row_info()
        if selected_row_info:
            upper_row_index = selected_row_info.row_index - 1
            if upper_row_index >= 0:
                upper_row_info = TableRowInfo(
                    row=self._rows[upper_row_index],
                    row_index=upper_row_index,
                )
                self._swap_row_index(
                    upper_row_info=upper_row_info,
                    lower_row_info=selected_row_info,
                )
            else:
                print("Nowhere to move up")

    def _move_down_selected(self):
        selected_row_info = self._get_selected_row_info()
        if selected_row_info:
            lower_row_index = selected_row_info.row_index + 1
            if lower_row_index < self.row_count:
                lower_row_info = TableRowInfo(
                    row=self._rows[lower_row_index],
                    row_index=lower_row_index,
                )
                self._swap_row_index(
                    upper_row_info=selected_row_info,
                    lower_row_info=lower_row_info,
                )
            else:
                print("Nowhere to move down")

    @abstractmethod
    def _on_rows_swapped(
        self,
        lower_row_index: int,
        upper_row_index: int,
    ):
        raise NotImplementedError()

    def _create_row(self, row_index: int, data: int) -> TableRow:
        print(f"Creating new row with data {data}")

        cell_info_list: List[TableRowCellConfig] = (
            self._create_empty_table_row_field_configs()
        )

        row = TableRow(
            config=TableRowConfig(
                width=self._row_width,
                height=self._table_config.value_row_height,
                selected_row_color_css_value=self._table_config.selected_row_color_css_value,
            ),
            cell_configs=cell_info_list,
            data=data,
        )

        row_cell_values = self._create_row_cell_values(row_index=row_index, data=data)
        row.set_cell_values(cell_values=row_cell_values)

        return row

    @abstractmethod
    def _create_row_cell_values(
        self,
        row_index: int,
        data: Any,
    ) -> List[TableRowCellValue]:
        raise NotImplementedError()

    @abstractmethod
    def _on_row_deleted(self, row_index: int, data: Any) -> None:
        raise NotImplementedError()
