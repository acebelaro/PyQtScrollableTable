from abc import ABC, abstractmethod
from typing import Any, Callable, Optional
from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QGroupBox,
    QLabel,
    QCheckBox,
    QLineEdit,
)

from qt_table_types import (
    TableCellUiType,
)

_TABLE_ROW_VALUE_CELL_TEXTBOX_GROUPBOX_NAME = "QtTableRowCellEditTextbox"


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
