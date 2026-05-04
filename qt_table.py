from abc import ABC, abstractmethod
from typing import Any, List, NamedTuple, Optional
from PyQt6 import QtCore
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import (
    QWidget,
    QGroupBox,
    QScrollArea,
    QLabel,
    QVBoxLayout,
)
from PyQt6.QtCore import pyqtSignal

from qt_table_types import (
    RowInfo,
    TableColumnConfig,
    TableConfig,
    TableRowCellConfig,
    TableRowCellValue,
    TableRowCellValueUpdatedParam,
)
from qt_table_row import TableRow
from qt_table_event import TableEvent, TableEventCollection, TableEventType

ROW_INDEX_PLACEHOLDER_TOKEN = "%row_index%"

_TABLE_HEADER_CELL_GROUPBOX_NAME = "QtTableHeaderCellGroupBox"


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
        self._config = table_config
        self._before_update_confirmers = table_config.before_update_confirmers

        self._calculated_row_width_from_header_row = 0
        self._columng_group_boxes: List[QGroupBox] = self._create_header_row()
        self._event_collection = TableEventCollection()
        self._row_cell_configs: List[TableRowCellConfig] = (
            self._create_row_cell_configs()
        )

        # create scroll area
        self._scroll_area = QScrollArea(parent=self._groupbox_container)
        self._scroll_area.setGeometry(
            QtCore.QRect(
                0,
                self._config.header_row_config.height,
                self._groupbox_container.width(),
                self._groupbox_container.height()
                - self._config.header_row_config.height,
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

        if table_config.shortcut_keys:
            if table_config.shortcut_keys.ctrl_z_y_undo_redo:
                undo_shortcut = QShortcut(
                    QKeySequence("Ctrl+Z"), self._groupbox_container
                )
                undo_shortcut.activated.connect(self._undo)
                redo_shortcut = QShortcut(
                    QKeySequence("Ctrl+Y"), self._groupbox_container
                )
                redo_shortcut.activated.connect(self._redo)

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

    @property
    def selected_row_index(self) -> int:
        selected_row_info = self._get_selected_row_info()
        if selected_row_info:
            return selected_row_info.row_index
        return -1

    def add_new_row(self, data: Any):
        """Create and add new row at the bottom."""
        row_index = self.row_count
        self.add_row_at_index(row_index=row_index, data=data)

    def add_row_at_index(self, row_index: int, data: Any):
        proceed_to_add = True
        if self._before_update_confirmers:
            confirm_row_addition = self._before_update_confirmers.confirm_row_addition
            if confirm_row_addition:
                proceed_to_add = confirm_row_addition(
                    RowInfo(
                        row_index=row_index,
                        data=data,
                    )
                )
        if proceed_to_add:
            new_row = self._create_row(row_index=row_index, data=data)
            row_added_event = self._add_row_at_index(row_index=row_index, row=new_row)
            if row_added_event:
                self._event_collection.add_undo_event(event=row_added_event)

    def update_row_at_index(self, row_index: int, data: Any):
        if row_index < self.row_count:
            self._rows[row_index].set_data(data=data)
            cell_values = self._create_row_cell_values(row_index=row_index, data=data)
            self._rows[row_index].set_cell_values(cell_values=cell_values)

    def _add_row_at_index(self, row_index: int, row: TableRow) -> Optional[TableEvent]:
        print(f"Adding at row {row_index}")
        self._rows.insert(row_index, row)
        self._table_layout.insertWidget(row_index, row)

        if self._config.select_new_row_added:
            selected_row = self.selected_row
            if selected_row:
                selected_row.clear_selected_state()
            row.set_as_selected()

        row_added_event = TableEvent(
            type=TableEventType.ROW_ADDED,
            row_index=row_index,
            data=row.data,
        )
        return row_added_event

    def _create_header_row(self) -> List[QGroupBox]:
        columng_group_boxes: List[QGroupBox] = []
        self._calculated_row_width_from_header_row = 0
        table_column_config_count = len(self._config.column_configs)
        for index in range(table_column_config_count):
            table_column_config = self._config.column_configs[index]
            is_last_column = False
            if index != (table_column_config_count - 1):
                is_last_column = True
            columng_group_box = self._create_header_cell_group_box(
                table_column_config=table_column_config,
                x_pos=self._calculated_row_width_from_header_row,
                is_last_column=is_last_column,
            )
            self._calculated_row_width_from_header_row = (
                self._calculated_row_width_from_header_row + table_column_config.width
            )
            columng_group_boxes.append(columng_group_box)
        if (
            self._calculated_row_width_from_header_row
            > self._groupbox_container.width()
        ):
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
                self._config.header_row_config.height,
            )
        )
        css_style_text = "; ".join(
            self._config.header_row_config.header_cell_css_styles
        )
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
                self._config.header_row_config.height,
            )
        )
        column_text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        column_text_label.setText(table_column_config.text)

    def _create_row_cell_configs(self) -> 1:
        row_cell_configs: List[TableRowCellConfig] = []
        cell_index = 0
        for column_config in self._config.column_configs:
            row_cell_configs.append(
                TableRowCellConfig(
                    ui_type=column_config.ui_type,
                    width=column_config.width,
                    cell_index=cell_index,
                )
            )
            cell_index = cell_index + 1
        return row_cell_configs

    def _create_row_index_cell_value(self, row_index: int) -> str:
        row_index_str = f"{row_index+1}"
        if self._config.row_number_cell_format != "":
            return self._config.row_number_cell_format.replace(
                ROW_INDEX_PLACEHOLDER_TOKEN, row_index_str
            )
        return row_index_str

    def _on_value_cell_updated(
        self, row_cell_value_updated_param: TableRowCellValueUpdatedParam
    ):
        updated_row = next(
            (r for r in self._rows if r.id == row_cell_value_updated_param.row_id), None
        )
        if updated_row:
            new_data = self._create_data_from_row_cell_values(
                cell_values=row_cell_value_updated_param.new_cell_values
            )
            print("Created new data")
            print(new_data)

            row_index = self._get_row_index_by_id(
                id=row_cell_value_updated_param.row_id
            )
            if row_index != -1:
                revert_edit = TableEvent(
                    type=TableEventType.ROW_EDITED,
                    row_index=row_index,
                    data=row_cell_value_updated_param.current_row_data,
                )
                self._event_collection.add_undo_event(event=revert_edit)
                print("[_on_value_cell_updated] Added undo event")
                print(revert_edit)
            updated_row.set_data(data=new_data)

    def _on_row_selected_state_updated(self, id: str, is_selected: bool):
        if is_selected:
            for row in self._rows:
                if row.id != id:
                    row.clear_selected_state()

    def _on_row_double_clicked(self, id: str):
        pass

    def _get_row_index_by_id(self, id: str) -> int:
        row_index = 0
        while row_index < self.row_count:
            if id == self._rows[row_index].id:
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
            selected_row_index = self._get_row_index_by_id(id=selected_row.id)
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

        confirm_row_swap = self._config.before_update_confirmers.confirm_row_swap
        if confirm_row_swap:
            proceed_swap = confirm_row_swap(
                upper_row_info=RowInfo(
                    row_index=upper_row_info.row_index,
                    data=upper_row_info.row.data,
                ),
                lower_row_info=RowInfo(
                    row_index=lower_row_info.row_index,
                    data=lower_row_info.row.data,
                ),
            )
            if not proceed_swap:
                return

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
            proceed_to_delete = True
            confirm_row_deletion = self._before_update_confirmers.confirm_row_deletion
            if confirm_row_deletion:
                proceed_to_delete = confirm_row_deletion(
                    RowInfo(
                        row_index=selected_row_info.row_index,
                        data=selected_row_info.row.data,
                    )
                )
            if proceed_to_delete:
                row_delete_event = self._delete_row_at_index(
                    row_index=selected_row_info.row_index,
                )
                if row_delete_event:
                    self._event_collection.add_undo_event(event=row_delete_event)
                    if self._config.select_next_row_after_row_deletion:
                        new_selected_row_index = selected_row_info.row_index
                        row_count = self.row_count
                        if new_selected_row_index == row_count:
                            new_selected_row_index = row_count - 1

                        if (
                            new_selected_row_index >= 0
                            and new_selected_row_index < row_count
                        ):
                            self._rows[new_selected_row_index].set_as_selected()
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

    def _create_row(self, row_index: int, data: int) -> TableRow:
        print(f"Creating new row with data {data}")
        row = TableRow(
            width=self._calculated_row_width_from_header_row,
            config=self._config.value_row_config,
            cell_configs=self._row_cell_configs,
            data=data,
        )

        row.on_value_cell_updated.connect(self._on_value_cell_updated)
        row.on_row_selected_state_updated.connect(self._on_row_selected_state_updated)
        row.on_row_double_clicked.connect(self._on_row_double_clicked)

        row_cell_values = self._create_row_cell_values(row_index=row_index, data=data)
        row.set_cell_values(cell_values=row_cell_values)
        return row

    def _delete_row_at_index(self, row_index: int) -> Optional[TableEvent]:
        table_event: Optional[TableEvent] = None
        if row_index >= 0 and row_index < self.row_count:
            row = self._rows[row_index]
            data = self._rows[row_index].data
            del self._rows[row_index]
            self._table_layout.removeWidget(row)
            row.setParent(None)
            row.deleteLater()

            table_event = TableEvent(
                type=TableEventType.ROW_DELETED,
                row_index=row_index,
                data=row.data,
            )
            self._adjust_row_index_cells(start_row_index=row_index)
            self._on_row_deleted(row_index=row_index, data=data)
        return table_event

    def _undo(self):
        """Undo the last table action."""
        print("UNDOING...")
        last_undo_event = self._event_collection.get_last_undo_event()
        if last_undo_event:
            row_event_for_redo = self._execute_revert(revert_event=last_undo_event)
            if row_event_for_redo:
                self._event_collection.add_redo_event(event=row_event_for_redo)

    def _redo(self):
        """Redo the last undone table action."""
        print("REDOING...")
        last_redo_event = self._event_collection.get_last_redo_event()
        if last_redo_event:
            row_event_for_undo = self._execute_revert(revert_event=last_redo_event)
            if row_event_for_undo:
                self._event_collection.add_undo_event(event=row_event_for_undo)

    def _execute_revert(self, revert_event: TableEvent) -> Optional[TableEvent]:
        print(revert_event)
        revert_revert_event = None
        if revert_event.type == TableEventType.ROW_ADDED:
            # delete that row
            revert_revert_event = self._delete_row_at_index(
                row_index=revert_event.row_index
            )
        elif revert_event.type == TableEventType.ROW_DELETED:
            # add in row index
            new_row = self._create_row(
                row_index=revert_event.row_index, data=revert_event.data
            )
            revert_revert_event = self._add_row_at_index(
                row_index=revert_event.row_index,
                row=new_row,
            )
        elif revert_event.type == TableEventType.ROW_EDITED:
            # update data in cell
            edit_row_index = revert_event.row_index
            if edit_row_index >= 0 and edit_row_index < self.row_count:
                old_row_data = self._rows[edit_row_index].data
                print(old_row_data)
                self.update_row_at_index(
                    row_index=edit_row_index, data=revert_event.data
                )
                revert_event = TableEvent(
                    type=TableEventType.ROW_EDITED,
                    row_index=edit_row_index,
                    data=old_row_data,
                )
        elif revert_event.type == TableEventType.ROW_MOVED_UP:
            # TODO:
            pass
        return revert_revert_event

    @abstractmethod
    def _create_row_cell_values(
        self,
        row_index: int,
        data: Any,
    ) -> List[TableRowCellValue]:
        raise NotImplementedError()

    @abstractmethod
    def _create_data_from_row_cell_values(
        self,
        cell_values: List[TableRowCellValue],
    ) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def _on_row_deleted(self, row_index: int, data: Any) -> None:
        raise NotImplementedError()

    @abstractmethod
    def _on_rows_swapped(
        self,
        lower_row_index: int,
        upper_row_index: int,
    ):
        raise NotImplementedError()
