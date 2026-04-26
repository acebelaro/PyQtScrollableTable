from abc import ABC, ABCMeta, abstractmethod
from enum import Enum
from typing import Any, List, NamedTuple, Optional
from PyQt6 import QtCore
from PyQt6.QtWidgets import QWidget, QGroupBox, QScrollArea, QLabel, QVBoxLayout
import uuid


class TableCellUiType(Enum):
    EDITABLE_TEXT = 0
    READONLY_TEXT = 1
    CHECKBOX = 2
    CUSTOM = 3


class TableColumnConfig(NamedTuple):
    ui_type: TableCellUiType
    text: str
    width: int
    object_name: str


class TableConfig(NamedTuple):
    column_configs: List[TableColumnConfig]
    header_row_height: int
    header_cell_css_styles: List[str]


# Custom metaclass to resolve conflict between QWidget's metaclass and ABCMeta
class _TableRowMeta(type(QWidget), ABCMeta):
    pass


class TableRow(QWidget):

    def __init__(
        self,
        id: str = "",
        data: Optional[Any] = None,
    ):
        super().__init__()

        self._id = id
        self._data = data
        if self._id == "":
            self._id = str(uuid.uuid4())
            # print(f"ID generated: {self._id}")

        self._create_ui()

    @property
    def id(self) -> str:
        return self._id

    @property
    def data(self) -> Optional[Any]:
        return self._data

    @abstractmethod
    def _create_ui(self) -> None:
        raise NotImplementedError()


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
        self._scroll_area_content.setObjectName("scrollAreaWidgetContents")
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

    # def create_row(self, row_field_value:List[Any], row_data:Any)->

    def add_row(self, row_index: int, row: TableRow):
        print(f"Adding at row {row_index}")
        self._rows.insert(row_index, row)
        self._table_layout.insertWidget(row_index, row)

    def _create_header_row(self) -> List[QGroupBox]:
        columng_group_boxes: List[QGroupBox] = []
        group_box_y_pos = 0
        table_column_config_count = len(self._table_config.column_configs)
        for index in range(table_column_config_count):
            table_column_config = self._table_config.column_configs[index]
            columng_group_box = QGroupBox(parent=self._groupbox_container)
            columng_group_box.setGeometry(
                QtCore.QRect(
                    group_box_y_pos,
                    0,
                    table_column_config.width,
                    self._table_config.header_row_height,
                )
            )
            css_style_text = "; ".join(self._table_config.header_cell_css_styles)
            css_style_text = f"{css_style_text}; border: 1px solid black;"
            if index != (table_column_config_count - 1):
                css_style_text = f"{css_style_text} border-right: none;"

            columng_group_box.setStyleSheet(css_style_text)
            columng_group_box.setTitle("")
            columng_group_box.setObjectName(table_column_config.object_name)

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
            column_text_label.setObjectName(f"label_{table_column_config.object_name}")
            column_text_label.setText(table_column_config.text)

            group_box_y_pos = group_box_y_pos + table_column_config.width
            columng_group_boxes.append(columng_group_box)
        if group_box_y_pos > self._groupbox_container.width():
            raise ValueError(
                f"Table '{self._name}' column header total width exceeds given group box container width!"
            )
        return columng_group_boxes

    # @staticmethod
    # def

    @abstractmethod
    def _create_row(self, data: Any) -> TableRow:
        raise NotImplementedError()

    # raos
