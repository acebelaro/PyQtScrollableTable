from typing import Any, List, Optional
from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QWidget,
    QGroupBox,
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QMouseEvent
import uuid

from qt_table_row_cell import (
    TableRowCellCheckbox,
    TableRowCellLabel,
    TableRowCellTextbox,
    TableRowCellValueWidget,
)
from qt_table_types import (
    RowCellValue,
    RowClassNameDeciderParam,
    TableCellUiType,
    TableRowCellConfig,
    TableRowCellValue,
    TableRowCellValueUpdatedParam,
    TableValueRowConfig,
)

_TABLE_ROW_VALUE_CELL_GROUPBOX_NAME = "QtTableRowValueCellGroupBox"


class TableRow(QWidget):

    on_value_cell_updated = pyqtSignal(TableRowCellValueUpdatedParam)
    on_row_selected_state_updated = pyqtSignal(str, bool)
    on_row_double_clicked = pyqtSignal(str)

    _on_update_selected_state = pyqtSignal()

    def __init__(
        self,
        width: int,
        # height: int,
        config: TableValueRowConfig,
        cell_configs: List[TableRowCellConfig],
        id: str = "",
        data: Optional[Any] = None,
    ):
        super().__init__()
        self._config = config
        self._row_class_name_decider = self._config.row_class_name_decider
        self._cell_configs = cell_configs
        self._id = id
        self._data = data
        self._cell_widgets: List[TableRowCellValueWidget] = []
        self._is_selected = False

        if self._id == "":
            self._id = str(uuid.uuid4())

        self._row_css_style_text = self._create_css_style_text()
        self._row_group_box = QGroupBox(parent=self)
        self._row_group_box.setGeometry(QtCore.QRect(0, 0, width, self._config.height))
        self._row_group_box.setTitle("")
        self._update_property_due_to_selected_state()

        self._create_row_fields_ui(row_group_box=self._row_group_box)

        self.setFixedHeight(self._config.height)

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

    def set_data(self, data: Any):
        self._data = data

    def set_as_selected(self):
        self._is_selected = True
        self._update_property_due_to_selected_state()

    def clear_selected_state(self):
        self._is_selected = False
        self._update_property_due_to_selected_state()

    def mousePressEvent(self, event: QMouseEvent):
        self._is_selected = not self._is_selected
        self.on_row_selected_state_updated.emit(self._id, self._is_selected)
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
        self._update_property_due_to_selected_state()

    def _create_css_style_text(self) -> str:
        row_css_style_text = ""
        class_styles = self._config.class_styles
        if class_styles and len(class_styles) > 0:
            for class_style in class_styles:
                css_style_text = ""
                for style in class_style.styles:
                    css_style_text = f"""{css_style_text}
    {style}
"""
                row_css_style_text = f"""{row_css_style_text}QGroupBox.{class_style.class_name} {{
{css_style_text}
}}
    """
        return row_css_style_text

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
        cell_value = RowCellValue(
            row_data=self.data,
            value=checked,
        )
        self.on_value_cell_updated.emit(
            TableRowCellValueUpdatedParam(
                row_id=self._id,
                cell_index=cell_index,
                cell_value=cell_value,
            )
        )

    def _textbox_cell_text_updated(self, cell_index: int, text: str):
        cell_value = RowCellValue(
            row_data=self.data,
            value=text,
        )
        self.on_value_cell_updated.emit(
            TableRowCellValueUpdatedParam(
                row_id=self._id,
                cell_index=cell_index,
                cell_value=cell_value,
            )
        )

    def _update_property_due_to_selected_state(self):
        current_class_value = self._row_group_box.property("class")
        new_class_value = ""

        if self._row_class_name_decider:
            row_class_name_decider_param = RowClassNameDeciderParam(
                data=self._data,
                is_selected=self._is_selected,
            )
            new_class_value = self._row_class_name_decider(row_class_name_decider_param)

        if current_class_value != new_class_value:
            self._row_group_box.setProperty("class", new_class_value)
            self._row_group_box.setStyleSheet(self._row_css_style_text)
