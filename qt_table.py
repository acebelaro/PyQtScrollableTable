from abc import ABC, abstractmethod
from typing import Any, List, Optional

from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import QGroupBox
from PyQt6.QtCore import pyqtSignal

from qt_table_header_rows import TableHeaderRows
from qt_table_types import (
    RowInfo,
    TableConfig,
    TableRowCellConfig,
    TableRowCellValue,
    TableRowCellValueUpdatedParam,
)
from qt_table_row import TableRow

from qt_table_undo_redo import (
    TableEvent,
    TableEventType,
    TableUndoRedo,
    UndoRedoActions,
)
from qt_table_value_rows import TableValueRows
from qt_table_value_rows_display import TableValueRowsDisplay


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

        self._header_rows = TableHeaderRows(
            name=name,
            groupbox_container=groupbox_container,
            config=table_config.header_row_config,
            column_configs=table_config.column_configs,
        )
        self._calculated_row_width_from_header_row = self._header_rows.create()
        self._value_rows_display = TableValueRowsDisplay(
            groupbox_container=self._groupbox_container,
            y_pos=self._config.header_row_config.height,
        )
        self._value_rows = TableValueRows(
            row_index_cell_value_creator=self._create_row_index_cell_value,
            row_cell_values_creator=self._create_row_cell_values,
        )
        self._undo_redo = TableUndoRedo(
            actions=UndoRedoActions(
                create_row=self._create_row,
                add_row_at_index=self._add_row_at_index,
                delete_row_at_index=self._delete_row_at_index,
                swap_rows=self._swap_row_index,
            ),
            get_row_at_index=self._value_rows.get_row_at_index,
        )

        self._row_cell_configs: List[TableRowCellConfig] = (
            self._create_row_cell_configs()
        )

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

        if table_config.shortcut_keys and table_config.shortcut_keys.ctrl_z_y_undo_redo:
            undo_shortcut = QShortcut(
                QKeySequence("Ctrl+Z"),
                self._groupbox_container,
            )
            undo_shortcut.activated.connect(self._undo_redo.undo)

            redo_shortcut = QShortcut(
                QKeySequence("Ctrl+Y"),
                self._groupbox_container,
            )
            redo_shortcut.activated.connect(self._undo_redo.redo)

    @property
    def rows(self) -> List[TableRow]:
        return self._value_rows.rows

    @property
    def row_count(self) -> int:
        return self._value_rows.row_count

    @property
    def selected_row(self) -> Optional[TableRow]:
        return self._value_rows.selected_row

    @property
    def selected_row_index(self) -> int:
        selected_row_info = self._value_rows.get_selected_row_info()
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
                self._undo_redo.add_undo_event(event=row_added_event)

    def update_row_at_index(self, row_index: int, data: Any):
        self._value_rows.set_data_of_row(row_index=row_index, data=data)

    def _add_row_at_index(
        self, row_index: int, row: TableRow, skip_select: bool = False
    ) -> Optional[TableEvent]:
        print(f"Adding at row {row_index}")
        self._value_rows.add_row(row=row, row_index=row_index)
        self._value_rows_display.add_row_at_index(row=row, row_index=row_index)
        self._on_row_added(row_index=row_index, data=row.data)

        if self._config.select_new_row_added and not skip_select:
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

    def _on_value_cell_updated(
        self, row_cell_value_updated_param: TableRowCellValueUpdatedParam
    ):
        updated_row_info = self._value_rows.get_row_by_id(
            row_id=row_cell_value_updated_param.row_id
        )
        if updated_row_info:
            new_data = self._create_data_from_row_cell_values(
                cell_values=row_cell_value_updated_param.new_cell_values
            )
            self._value_rows.get_row_by_id(row_id=row_cell_value_updated_param.row_id)
            revert_edit = TableEvent(
                type=TableEventType.ROW_EDITED,
                row_index=updated_row_info.row_index,
                data=row_cell_value_updated_param.current_row_data,
            )
            self._undo_redo.add_undo_event(event=revert_edit)
            self._value_rows.set_data_of_row(
                row_index=updated_row_info.row_index, data=new_data
            )

    def _on_row_selected_state_updated(self, id: str, is_selected: bool):
        if is_selected:
            self._value_rows.clear_other_rows_selected_state(except_row_id=id)

    def _on_row_double_clicked(self, id: str):
        pass

    def _swap_row_index(
        self,
        upper_row_index: int,
        lower_row_index: int,
    ) -> bool:
        proceed_swap = True

        upper_row = self._value_rows.get_row_at_index(row_index=upper_row_index)
        lower_row = self._value_rows.get_row_at_index(row_index=lower_row_index)

        if (
            self._before_update_confirmers
            and self._before_update_confirmers.confirm_row_swap
        ):
            upper_row_info = RowInfo(
                row_index=upper_row_index,
                data=upper_row.data,
            )
            lower_row_info = RowInfo(
                row_index=lower_row_index,
                data=lower_row.data,
            )
            proceed_swap = self._before_update_confirmers.confirm_row_swap(
                upper_row_info=upper_row_info,
                lower_row_info=lower_row_info,
            )
        if proceed_swap:
            deleted_row = self._value_rows.delete_row_at_index(
                row_index=lower_row_index
            )
            self._value_rows_display.remove_row(row=deleted_row)

            self._value_rows.add_row(row=deleted_row, row_index=upper_row_index)
            self._value_rows_display.add_row_at_index(
                row=deleted_row, row_index=upper_row_index
            )

            self._value_rows.adjust_row_index_cells(start_row_index=upper_row_index)
            self._on_rows_swapped(
                lower_row_index=lower_row_index,
                upper_row_index=upper_row_index,
            )
        return proceed_swap

    def _delete_selected(self):
        selected_row_info = self._value_rows.get_selected_row_info()
        if selected_row_info:
            proceed_to_delete = True
            confirm_row_deletion = self._before_update_confirmers.confirm_row_deletion
            if confirm_row_deletion:
                proceed_to_delete = confirm_row_deletion(selected_row_info)
            if proceed_to_delete:
                row_delete_event = self._delete_row_at_index(
                    row_index=selected_row_info.row_index,
                )
                if row_delete_event:
                    self._undo_redo.add_undo_event(event=row_delete_event)
                    if self._config.select_next_row_after_row_deletion:
                        new_selected_row_index = selected_row_info.row_index
                        row_count = self.row_count
                        if new_selected_row_index == row_count:
                            new_selected_row_index = row_count - 1

                        self._value_rows.set_row_as_selected(
                            row_index=new_selected_row_index
                        )
        else:
            print("No selected row index.")

    def _move_up_selected(self):
        selected_row_info = self._value_rows.get_selected_row_info()
        if selected_row_info:
            upper_row_index = selected_row_info.row_index - 1
            if upper_row_index >= 0:
                is_swapped = self._swap_row_index(
                    upper_row_index=upper_row_index,
                    lower_row_index=selected_row_info.row_index,
                )
                if is_swapped:
                    revert_swap = TableEvent(
                        type=TableEventType.ROW_MOVED_UP,
                        row_index=selected_row_info.row_index,
                        data=None,  # not used
                    )
                    self._undo_redo.add_undo_event(event=revert_swap)
            else:
                print("Nowhere to move up")

    def _move_down_selected(self):
        selected_row_info = self._value_rows.get_selected_row_info()
        if selected_row_info:
            lower_row_index = selected_row_info.row_index + 1
            if lower_row_index < self.row_count:
                is_swapped = self._swap_row_index(
                    upper_row_index=selected_row_info.row_index,
                    lower_row_index=lower_row_index,
                )
                if is_swapped:
                    revert_swap = TableEvent(
                        type=TableEventType.ROW_MOVED_DOWN,
                        row_index=selected_row_info.row_index,
                        data=None,  # not used
                    )
                    self._undo_redo.add_undo_event(event=revert_swap)
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
        deleted_row = self._value_rows.delete_row_at_index(row_index=row_index)
        if deleted_row:
            data_of_deleted_row = deleted_row.data
            self._value_rows_display.remove_row(row=deleted_row)
            deleted_row.setParent(None)
            deleted_row.deleteLater()
            self._value_rows.adjust_row_index_cells(start_row_index=row_index)
            self._on_row_deleted(row_index=row_index, data=data_of_deleted_row)
            table_event = TableEvent(
                type=TableEventType.ROW_DELETED,
                row_index=row_index,
                data=data_of_deleted_row,
            )
        return table_event

    @abstractmethod
    def _create_row_index_cell_value(
        self,
        row_index: int,
    ) -> str:
        raise NotImplementedError()

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
    def _on_row_added(self, row_index: int, data: int) -> None:
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
