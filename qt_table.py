from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, NamedTuple, Optional
from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QWidget,
    QGroupBox,
    QScrollArea,
    QLabel,
    QVBoxLayout,
    QCheckBox,
    QLineEdit,
)
from PyQt6.QtCore import pyqtSignal
import uuid

_TABLE_HEADER_CELL_GROUPBOX_NAME = "QtTableHeaderCellGroupBox"
_TABLE_ROW_GROUPBOX_NAME = "QtTableRowGroupBox"
_TABLE_ROW_VALUE_CELL_GROUPBOX_NAME = "QtTableRowValueCellGroupBox"
_TABLE_ROW_VALUE_CELL_TEXTBOX_GROUPBOX_NAME = "QtTableRowCellEditTextbox"


class TableCellUiType(Enum):
    EDITABLE_TEXT = 0
    READONLY_TEXT = 1
    CHECKBOX = 2
    CUSTOM = 3


class TableColumnConfig(NamedTuple):
    ui_type: TableCellUiType
    text: str
    width: int


class TableConfig(NamedTuple):
    column_configs: List[TableColumnConfig]
    header_row_height: int
    header_cell_css_styles: List[str]


class TableRowFieldConfig:

    on_ = pyqtSignal()

    def __init__(
        self,
        ui_type: TableCellUiType,
        width: int,
    ):
        self._ui_type = ui_type
        self._width = width
        self._value: Optional[str | Any] = None

    @property
    def ui_type(self) -> TableCellUiType:
        return self._ui_type

    @property
    def width(self) -> int:
        return self._width

    @property
    def value(self) -> Optional[str | bool]:
        return self._value

    @value.setter
    def value(self, v: Optional[str | bool]):
        self._value = v


class TableRowCellCheckbox(QCheckBox):

    on_checked_updated = pyqtSignal(int, bool)

    def __init__(
        self,
        parent: QGroupBox,
        cell_index: int,
        width: int,
    ):
        super().__init__(parent=parent)
        self._field_index = cell_index
        self.checkStateChanged.connect(self._check_update)

        self.setGeometry(
            QtCore.QRect(
                10,
                10,
                width - 20,
                20,
            )
        )

    def _check_update(self):
        self.on_checked_updated.emit(self._field_index, self.isChecked())


class TableRowCellLabel(QLabel):

    on_text_updated = pyqtSignal(int, str)

    def __init__(
        self,
        parent: QGroupBox,
        width: int,
        text: str,
    ):
        super().__init__(parent=parent)
        self.setText(text)
        self.setGeometry(
            QtCore.QRect(
                10,
                10,
                width - 20,
                20,
            )
        )


class TableRowCellTextbox(QLineEdit):

    on_text_updated = pyqtSignal(int, str)

    def __init__(
        self,
        parent: QGroupBox,
        cell_index: int,
        width: int,
        text: str,
    ):
        super().__init__(parent=parent)
        self._field_index = cell_index
        self.textChanged.connect(self._text_updated)
        self.setText(text)

        self.setObjectName(_TABLE_ROW_VALUE_CELL_TEXTBOX_GROUPBOX_NAME)
        self.setStyleSheet(
            f"QLineEdit#{_TABLE_ROW_VALUE_CELL_TEXTBOX_GROUPBOX_NAME} {{ border: none; }}"
        )
        self.setGeometry(
            QtCore.QRect(
                10,
                10,
                width - 20,
                20,
            )
        )

    def _text_updated(self):
        self.on_text_updated.emit(self._field_index, self.text())


class FieldValue(NamedTuple):
    row_data: Any
    value: str | bool


class TableRow(QWidget):

    on_value_cell_updated = pyqtSignal(str, int, FieldValue)

    def __init__(
        self,
        width: int,
        height: int,
        field_configs: List[TableRowFieldConfig],
        id: str = "",
        data: Optional[Any] = None,
    ):
        super().__init__()
        self._width = width
        self._height = height
        self._object_name = "TableRow"
        self._field_configs = field_configs
        self._id = id
        self._data = data
        self._ui_widgets: List[QWidget] = []

        if self._id == "":
            self._id = str(uuid.uuid4())

        row_group_box = QGroupBox(parent=self)
        row_group_box.setGeometry(QtCore.QRect(0, 0, width, height))
        row_group_box.setTitle("")
        row_group_box.setObjectName(_TABLE_ROW_GROUPBOX_NAME)
        css_style_text = (
            f"QGroupBox#{_TABLE_ROW_GROUPBOX_NAME}{{ border: 1px solid black; }}"
        )
        row_group_box.setStyleSheet(css_style_text)

        self._create_row_fields_ui(row_group_box=row_group_box)

        self.setFixedHeight(height)

    @staticmethod
    @property
    def id(self) -> str:
        return self._id

    @property
    def data(self) -> Optional[Any]:
        return self._data

    @abstractmethod
    def _create_ui(self, row_group_box: QGroupBox) -> None:
        raise NotImplementedError()

    def _create_row_fields_ui(self, row_group_box: QGroupBox):
        row_cell_x_pos = 0
        cell_index = 0
        for field_config in self._field_configs:
            self._create_row_cell_groupbox(
                row_group_box=row_group_box,
                cell_index=cell_index,
                field_config=field_config,
                x_pos=row_cell_x_pos,
            )
            row_cell_x_pos = row_cell_x_pos + field_config.width
            cell_index = cell_index + 1

    def _create_row_cell_groupbox(
        self,
        row_group_box: QGroupBox,
        cell_index: int,
        field_config: TableRowFieldConfig,
        x_pos: int,
    ) -> QGroupBox:
        row_cell_group_box = QGroupBox(parent=row_group_box)
        row_cell_group_box.setGeometry(
            QtCore.QRect(
                x_pos,
                0,
                field_config.width,
                self._height - 1,
            )
        )
        row_cell_group_box.setObjectName(_TABLE_ROW_VALUE_CELL_GROUPBOX_NAME)
        row_cell_group_box.setStyleSheet(
            f"QGroupBox#{_TABLE_ROW_VALUE_CELL_GROUPBOX_NAME}{{ border: 2px solid lightgray; }}"
        )
        row_cell_value_widget = self._create_row_cell_value_widget(
            row_cell_group_box=row_cell_group_box,
            cell_index=cell_index,
            field_config=field_config,
        )
        if row_cell_value_widget:
            self._ui_widgets.append(row_cell_value_widget)
        return row_cell_group_box

    def _create_row_cell_value_widget(
        self,
        row_cell_group_box: QGroupBox,
        cell_index: int,
        field_config: TableRowFieldConfig,
    ) -> QWidget:
        row_cell_widget = None
        if field_config.ui_type == TableCellUiType.CHECKBOX:
            row_cell_widget = TableRowCellCheckbox(
                parent=row_cell_group_box,
                cell_index=cell_index,
                width=field_config.width,
            )
            row_cell_widget.on_checked_updated.connect(
                self._checkbox_cell_checked_updated
            )
        elif field_config.ui_type == TableCellUiType.READONLY_TEXT:
            row_cell_widget = TableRowCellLabel(
                parent=row_cell_group_box,
                width=field_config.width,
                text=field_config.value,
            )
        elif field_config.ui_type == TableCellUiType.EDITABLE_TEXT:
            row_cell_widget = TableRowCellTextbox(
                parent=row_cell_group_box,
                cell_index=cell_index,
                width=field_config.width,
                text=field_config.value,
            )
            row_cell_widget.on_text_updated.connect(self._textbox_cell_text_updated)
        elif field_config.ui_type == TableCellUiType.CUSTOM:
            pass
        else:
            raise ValueError(f"Unsupported ui type {field_config.ui_type.name}")
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


class Table(ABC):

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

        self._rows: List[TableRow] = []

    @property
    def rows(self) -> List[TableRow]:
        return self._rows

    @property
    def row_count(self) -> int:
        return len(self._rows)

    def add_new_row(self, data: Any):
        """Create and add new row at the bottom."""
        new_row = self._create_row(data=data)
        index = self.row_count
        self.add_row(row_index=index, row=new_row)

    def add_row(self, row_index: int, row: TableRow):
        print(f"Adding at row {row_index}")
        self._rows.insert(row_index, row)
        self._table_layout.insertWidget(row_index, row)

        row.on_value_cell_updated.connect(self._on_value_cell_updated)

    def _create_header_row(self) -> List[QGroupBox]:
        columng_group_boxes: List[QGroupBox] = []
        group_box_x_pos = 0
        table_column_config_count = len(self._table_config.column_configs)
        for index in range(table_column_config_count):
            table_column_config = self._table_config.column_configs[index]
            is_last_column = False
            if index != (table_column_config_count - 1):
                is_last_column = True
            columng_group_box = self._create_header_cell_group_box(
                table_column_config=table_column_config,
                x_pos=group_box_x_pos,
                is_last_column=is_last_column,
            )
            group_box_x_pos = group_box_x_pos + table_column_config.width
            columng_group_boxes.append(columng_group_box)
        if group_box_x_pos > self._groupbox_container.width():
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

    def _create_empty_table_row_field_configs(self) -> List[TableRowFieldConfig]:
        return [
            TableRowFieldConfig(
                ui_type=b.ui_type,
                width=b.width,
            )
            for b in self._table_config.column_configs
        ]

    def _on_value_cell_updated(self, id: str, cell_index: int, value: FieldValue):
        print(id, cell_index, value)

    @abstractmethod
    def _create_row(self, data: Any) -> TableRow:
        raise NotImplementedError()

    # raos
