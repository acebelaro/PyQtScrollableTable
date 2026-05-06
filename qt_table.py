from abc import ABC, abstractmethod
from typing import Any, List, Optional

from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import (
    QGroupBox,
)
from PyQt6.QtCore import pyqtSignal

from qt_table_header_row import TableHeaderRow
from qt_table_types import (
    RowInfo,
    TableConfig,
    TableRowCellConfig,
    TableRowCellValue,
    TableRowCellValueUpdatedParam,
)
from qt_table_row import TableRow
from qt_table_event import TableEvent, TableEventCollection, TableEventType
from qt_table_value_rows import TableValueRows

ROW_INDEX_PLACEHOLDER_TOKEN = "%row_index%"


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
        self._row_number_cell_value_creator = table_config.row_number_cell_value_creator
        self._before_update_confirmers = table_config.before_update_confirmers

        self._header_row = TableHeaderRow(
            name=name,
            header_row_config=table_config.header_row_config,
            column_configs=table_config.column_configs,
            groupbox_container=groupbox_container,
        )
        self._calculated_row_width_from_header_row = self._header_row.create()

        self._table_value_rows = TableValueRows(
            groupbox_container=groupbox_container,
            y_pos=self._config.header_row_config.height,
            select_new_row_added=self._config.select_new_row_added,
        )

        self._event_collection = TableEventCollection()
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

    @property
    def row_count(self) -> int:
        return self._table_value_rows.row_count

    @property
    def selected_row(self) -> Optional[TableRow]:
        return self._table_value_rows.selected_row

    @property
    def selected_row_index(self) -> int:
        return self._table_value_rows.selected_row_index

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
            self._table_value_rows.add_row_at_index(row_index=row_index, row=new_row)
            row_added_event = TableEvent(
                type=TableEventType.ROW_ADDED,
                row_index=row_index,
                data=data,
            )
            if row_added_event:
                self._event_collection.add_undo_event(event=row_added_event)

    def add_child_row(self, row_index: int, data: Any):
        pass

    def update_row_at_index(self, row_index: int, data: Any) -> TableRow:
        # replace with new row to avoid on update triggers
        # that can register revert event
        self._delete_row_at_index(row_index=row_index)
        new_row = self._create_row(row_index=row_index, data=data)
        self._table_value_rows.add_row_at_index(
            row_index=row_index,
            row=new_row,
            skip_select=True,
        )
        return new_row

    def _create_row_cell_configs(self) -> List[TableRowCellConfig]:
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
        row_number = row_index + 1
        if self._row_number_cell_value_creator:
            return self._row_number_cell_value_creator(row_number)
        return f"{row_number}"

    def _on_value_cell_updated(
        self, row_cell_value_updated_param: TableRowCellValueUpdatedParam
    ):
        updated_row = self._table_value_rows.get_row_by_id(
            row_id=row_cell_value_updated_param.row_id
        )
        if updated_row:
            new_data = self._create_data_from_row_cell_values(
                cell_values=row_cell_value_updated_param.new_cell_values
            )
            row_index = self._table_value_rows.get_row_index_by_id(
                row_id=row_cell_value_updated_param.row_id
            )
            if row_index != -1:
                revert_edit = TableEvent(
                    type=TableEventType.ROW_EDITED,
                    row_index=row_index,
                    data=row_cell_value_updated_param.current_row_data,
                )
                self._event_collection.add_undo_event(event=revert_edit)
            updated_row.set_data(data=new_data)

    def _on_row_selected_state_updated(self, id: str, is_selected: bool):
        self._table_value_rows.update_rows_selected_states_due_to_toggled_row(
            toggled_row_id=id, is_selected=is_selected
        )

    def _on_row_double_clicked(self, id: str):
        pass

    def _adjust_row_index_cells(self, start_row_index: int = 0):
        row_count = self.row_count
        row_index = start_row_index
        while row_index < row_count:
            row_index_cell_value = self._create_row_index_cell_value(
                row_index=row_index
            )
            self._table_value_rows.set_row_index_cell_value(
                row_index=row_index,
                row_index_cell_value=row_index_cell_value,
            )
            row_index = row_index + 1

    def _swap_row_index(
        self,
        upper_row_index: int,
        lower_row_index: int,
    ) -> bool:
        proceed_swap = True

        if (
            self._before_update_confirmers
            and self._before_update_confirmers.confirm_row_swap
        ):
            upper_row = self._table_value_rows.get_row_at_index(upper_row_index)
            lower_row = self._table_value_rows.get_row_at_index(lower_row_index)

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
            self._table_value_rows.swap_row_index(
                upper_row_index=upper_row_index,
                lower_row_index=lower_row_index,
            )

            self._adjust_row_index_cells(start_row_index=upper_row_index)

            self._on_rows_swapped(
                lower_row_index=lower_row_index,
                upper_row_index=upper_row_index,
            )
        return proceed_swap

    def _delete_selected(self):
        selected_row_info = self._table_value_rows.get_selected_row_info()
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
                            self._table_value_rows.set_selected_row(
                                row_index=new_selected_row_index
                            )
        else:
            print("No selected row index.")

    def _move_up_selected(self):
        selected_row_info = self._table_value_rows.get_selected_row_info()
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
                    self._event_collection.add_undo_event(event=revert_swap)
            else:
                print("Nowhere to move up")

    def _move_down_selected(self):
        selected_row_info = self._table_value_rows.get_selected_row_info()
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
                    self._event_collection.add_undo_event(event=revert_swap)
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
        deleted_row_info = self._table_value_rows.delete_row_at_index(
            row_index=row_index
        )
        if deleted_row_info:
            table_event = TableEvent(
                type=TableEventType.ROW_DELETED,
                row_index=row_index,
                data=deleted_row_info.data,
            )
            self._adjust_row_index_cells(start_row_index=row_index)
            self._on_row_deleted(row_index=row_index, data=deleted_row_info.data)
        return table_event

    def _undo(self):
        """Undo the last table action."""
        last_undo_event = self._event_collection.get_last_undo_event()
        if last_undo_event:
            row_event_for_redo = self._execute_revert(revert_event=last_undo_event)
            if row_event_for_redo:
                self._event_collection.add_redo_event(event=row_event_for_redo)

    def _redo(self):
        """Redo the last undone table action."""
        last_redo_event = self._event_collection.get_last_redo_event()
        if last_redo_event:
            row_event_for_undo = self._execute_revert(revert_event=last_redo_event)
            if row_event_for_undo:
                self._event_collection.add_undo_event(event=row_event_for_undo)

    def _execute_revert(self, revert_event: TableEvent) -> Optional[TableEvent]:
        revert_revert_event = None
        event_row_index = revert_event.row_index

        if revert_event.type == TableEventType.ROW_ADDED:
            # delete that row
            revert_revert_event = self._delete_row_at_index(row_index=event_row_index)
        elif revert_event.type == TableEventType.ROW_DELETED:
            # add in row index
            new_row = self._create_row(
                row_index=event_row_index, data=revert_event.data
            )
            self._table_value_rows.add_row_at_index(
                row_index=event_row_index,
                row=new_row,
                skip_select=True,
            )
            self._adjust_row_index_cells(start_row_index=event_row_index)
            revert_revert_event = TableEvent(
                type=TableEventType.ROW_ADDED,
                row_index=event_row_index,
                data=new_row.data,
            )
        elif revert_event.type == TableEventType.ROW_EDITED:
            # update data in cell
            if self._table_value_rows.is_valid_row_index(row_index=event_row_index):
                current_row = self._table_value_rows.get_row_at_index(
                    row_index=event_row_index
                )
                is_selected = current_row.is_selected
                current_row_data = current_row.data
                new_row = self.update_row_at_index(
                    row_index=event_row_index, data=revert_event.data
                )
                revert_revert_event = TableEvent(
                    type=TableEventType.ROW_EDITED,
                    row_index=event_row_index,
                    data=current_row_data,
                )
                if is_selected:
                    new_row.set_as_selected()
        elif revert_event.type == TableEventType.ROW_MOVED_UP:
            # move row down
            upper_row_index = event_row_index - 1
            if upper_row_index >= 0:
                self._swap_row_index(
                    upper_row_index=upper_row_index,
                    lower_row_index=event_row_index,
                )
                revert_revert_event = TableEvent(
                    type=TableEventType.ROW_MOVED_UP,
                    row_index=event_row_index,
                    data=None,  # not used
                )
        elif revert_event.type == TableEventType.ROW_MOVED_DOWN:
            # move row up
            lower_row_index = event_row_index + 1
            if lower_row_index < self.row_count:
                self._swap_row_index(
                    upper_row_index=event_row_index,
                    lower_row_index=lower_row_index,
                )
                revert_revert_event = TableEvent(
                    type=TableEventType.ROW_MOVED_DOWN,
                    row_index=event_row_index,
                    data=None,  # not used
                )
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
