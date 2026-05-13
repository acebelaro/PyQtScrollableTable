from abc import ABC, abstractmethod
from typing import Any, List, Optional

from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import QGroupBox
from PyQt6.QtCore import pyqtSignal

from qt_table_copy_cut_paste import TableCopyCutPaste
from qt_table_header_rows import TableHeaderRows
from qt_table_row_actions import RowActions
from qt_table_types import (
    RowInfo,
    TableCreateAddRowParam,
    TableConfig,
    TableDeleteRowParam,
    TableEvent,
    TableEventType,
    TableRowAddEventData,
    TableRowCellConfig,
    TableRowCellValue,
    TableRowCellValueUpdatedParam,
    TableRowDeleteEventData,
    TableRowEditEventData,
    TableRowMovedEventData,
    TableShortcutKeys,
    TableSwapRowsParam,
)
from qt_table_row import TableRow
from qt_table_undo_redo import TableUndoRedo
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
        row_actions = RowActions(
            selected_row_provider=self._selected_row_provider,
            create_and_add_row_at_index=self._create_and_add_row_at_index,
            delete_row=self._delete_row,
            swap_rows=self._swap_rows,
            create_row_data_copy=self._create_row_data_copy,
            adjust_row_index_cells=self._value_rows.adjust_row_index_cells,
        )
        self._undo_redo = TableUndoRedo(
            row_actions=row_actions,
            get_row_at_index=self._value_rows.get_row_at_index,
        )
        self._copy_cut_paste = TableCopyCutPaste(
            row_actions=row_actions,
            undo_redo=self._undo_redo,
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

        shortcut_keys = table_config.shortcut_keys
        if shortcut_keys:
            self._setup_shortcut_keys(shortcut_keys=shortcut_keys)

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

    def add_new_row_data(self, data: Any):
        """Create and add new row at the bottom."""
        row_index = self.row_count
        self.add_new_row_data_at_index(
            row_index=row_index,
            data=data,
        )

    def add_new_row_data_at_index(self, row_index: int, data: Any):
        create_add_param = TableCreateAddRowParam(
            row_index=row_index,
            data=data,
            skip_select=False,
            confirm_before_adding=True,
            report_when_added=True,
        )
        row_added_event = self._create_and_add_row_at_index(
            create_add_param=create_add_param
        )
        if row_added_event:
            self._undo_redo.add_undo_event(event=row_added_event)

    def update_row_at_index(self, row_index: int, data: Any):
        self._value_rows.set_data_of_row(row_index=row_index, data=data)

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

    def _setup_shortcut_keys(self, shortcut_keys: TableShortcutKeys):
        if shortcut_keys.ctrl_z_y_undo_redo:
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
        if shortcut_keys.ctrl_c_x_v_copy_cut_paste:
            copy_shortcut = QShortcut(
                QKeySequence("Ctrl+C"),
                self._groupbox_container,
            )
            copy_shortcut.activated.connect(self._copy_cut_paste.set_copy)

            redo_shortcut = QShortcut(
                QKeySequence("Ctrl+X"),
                self._groupbox_container,
            )
            redo_shortcut.activated.connect(self._copy_cut_paste.set_cut)

            redo_shortcut = QShortcut(
                QKeySequence("Ctrl+V"),
                self._groupbox_container,
            )
            redo_shortcut.activated.connect(self._copy_cut_paste.execute_paste)

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
            revert_edit = TableEvent(
                type=TableEventType.ROW_EDITED,
                event_data=TableRowEditEventData(
                    row_index=updated_row_info.row_index,
                    row_data=row_cell_value_updated_param.current_row_data,
                ),
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

    def _delete_selected(self):
        selected_row_info = self._value_rows.get_selected_row_info()
        if selected_row_info:
            delete_param = TableDeleteRowParam(
                row_index=selected_row_info.row_index,
                confirm_before_deleting=True,
                report_when_deleted=True,
            )
            row_delete_event = self._delete_row(delete_param=delete_param)
            if row_delete_event:
                self._undo_redo.add_undo_event(event=row_delete_event)

    def _move_up_selected(self):
        selected_row_info = self._value_rows.get_selected_row_info()
        if selected_row_info:
            upper_row_index = selected_row_info.row_index - 1
            if upper_row_index >= 0:
                swap_param = TableSwapRowsParam(
                    upper_row_index=upper_row_index,
                    lower_row_index=selected_row_info.row_index,
                    confirm_before_swapping=True,
                    report_when_swapped=True,
                )
                is_swapped = self._swap_rows(
                    swap_param=swap_param,
                )
                if is_swapped:
                    revert_swap = TableEvent(
                        type=TableEventType.ROW_MOVED_UP,
                        event_data=TableRowMovedEventData(
                            row_index=selected_row_info.row_index,
                        ),
                    )
                    self._undo_redo.add_undo_event(event=revert_swap)
            else:
                print("Nowhere to move up")

    def _move_down_selected(self):
        selected_row_info = self._value_rows.get_selected_row_info()
        if selected_row_info:
            lower_row_index = selected_row_info.row_index + 1
            if lower_row_index < self.row_count:
                swap_param = TableSwapRowsParam(
                    upper_row_index=selected_row_info.row_index,
                    lower_row_index=lower_row_index,
                    confirm_before_swapping=True,
                    report_when_swapped=True,
                )
                is_swapped = self._swap_rows(
                    swap_param=swap_param,
                )
                if is_swapped:
                    revert_swap = TableEvent(
                        type=TableEventType.ROW_MOVED_DOWN,
                        event_data=TableRowMovedEventData(
                            row_index=selected_row_info.row_index,
                        ),
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

    def _confirm_create_and_add_row(
        self,
        create_add_param: TableCreateAddRowParam,
    ) -> bool:
        proceed_to_add = True
        if (
            self._config.before_update_confirmers
            and self._config.before_update_confirmers.confirm_row_addition
        ):
            proceed_to_add = self._config.before_update_confirmers.confirm_row_addition(
                RowInfo(
                    row_index=create_add_param.row_index,
                    data=create_add_param.data,
                )
            )
        return proceed_to_add

    def _create_and_add_row_at_index(
        self,
        create_add_param: TableCreateAddRowParam,
    ) -> Optional[TableEvent]:
        row_added_event = None
        proceed_to_add = True
        if create_add_param.confirm_before_adding:
            proceed_to_add = self._confirm_create_and_add_row(
                create_add_param=create_add_param
            )
        if proceed_to_add:
            new_row = self._create_row(
                row_index=create_add_param.row_index, data=create_add_param.data
            )
            self._value_rows.add_row(row=new_row, row_index=create_add_param.row_index)
            self._value_rows_display.add_row_at_index(
                row=new_row, row_index=create_add_param.row_index
            )
            if self._config.select_new_row_added and not create_add_param.skip_select:
                selected_row = self.selected_row
                if selected_row:
                    selected_row.clear_selected_state()
                new_row.set_as_selected()
            row_added_event = TableEvent(
                type=TableEventType.ROW_ADDED,
                event_data=TableRowAddEventData(
                    row_index=create_add_param.row_index,
                ),
            )
            if create_add_param.report_when_added:
                self._on_row_added(
                    row_index=create_add_param.row_index, data=new_row.data
                )
        return row_added_event

    def _confirm_delete_row(
        self, delete_param: TableDeleteRowParam, row_to_delete: RowInfo
    ) -> bool:
        proceed_to_delete = True
        if (
            self._before_update_confirmers
            and self._before_update_confirmers.confirm_row_deletion
        ):
            proceed_to_delete = self._before_update_confirmers.confirm_row_deletion(
                RowInfo(
                    row_index=delete_param.row_index,
                    data=row_to_delete.data,
                )
            )
        return proceed_to_delete

    def _adjust_selected_row_due_to_deletion_of_selected_row(
        self, deleted_row_index: int
    ):
        new_selected_row_index = deleted_row_index
        row_count = self.row_count
        if new_selected_row_index == row_count:
            new_selected_row_index = row_count - 1
        self._value_rows.set_row_as_selected(row_index=new_selected_row_index)

    def _delete_row(self, delete_param: TableDeleteRowParam) -> Optional[TableEvent]:
        table_event: Optional[TableEvent] = None
        row_to_delete = self._value_rows.get_row_at_index(
            row_index=delete_param.row_index
        )
        if row_to_delete:
            proceed_to_delete = True
            if delete_param.confirm_before_deleting:
                proceed_to_delete = self._confirm_delete_row(
                    delete_param=delete_param, row_to_delete=row_to_delete
                )
            if proceed_to_delete:
                is_deleted_row_selected = row_to_delete.is_selected
                deleted_row = self._value_rows.delete_row_at_index(
                    row_index=delete_param.row_index
                )
                if deleted_row:
                    data_of_deleted_row = deleted_row.data
                    self._value_rows_display.remove_row(
                        row=deleted_row, delete_row_widget=True
                    )
                    self._value_rows.adjust_row_index_cells(
                        start_row_index=delete_param.row_index
                    )
                    table_event = TableEvent(
                        type=TableEventType.ROW_DELETED,
                        event_data=TableRowDeleteEventData(
                            row_index=delete_param.row_index,
                            row_data=data_of_deleted_row,
                        ),
                    )
                    if (
                        is_deleted_row_selected
                        and self._config.select_next_row_after_row_deletion
                    ):
                        self._adjust_selected_row_due_to_deletion_of_selected_row(
                            deleted_row_index=delete_param.row_index
                        )
                    if delete_param.report_when_deleted:
                        self._on_row_deleted(
                            row_index=delete_param.row_index, data=data_of_deleted_row
                        )
        return table_event

    def _confirm_swap_rows(self, upper_row: RowInfo, lower_row: RowInfo) -> bool:
        proceed_to_swap = True
        if (
            self._before_update_confirmers
            and self._before_update_confirmers.confirm_row_swap
        ):
            proceed_to_swap = self._before_update_confirmers.confirm_row_swap(
                upper_row,
                lower_row,
            )
        return proceed_to_swap

    def _swap_rows(self, swap_param: TableSwapRowsParam) -> bool:
        is_swapped = False
        upper_row_index = swap_param.upper_row_index
        lower_row_index = swap_param.lower_row_index
        upper_row = self._value_rows.get_row_at_index(row_index=upper_row_index)
        lower_row = self._value_rows.get_row_at_index(row_index=lower_row_index)
        if upper_row and lower_row:
            proceed_to_swap = True
            if swap_param.confirm_before_swapping:
                proceed_to_swap = self._confirm_swap_rows(
                    upper_row=RowInfo(
                        row_index=upper_row_index,
                        data=upper_row.data,
                    ),
                    lower_row=RowInfo(
                        row_index=lower_row_index,
                        data=lower_row.data,
                    ),
                )
            if proceed_to_swap:
                deleted_row = self._value_rows.delete_row_at_index(
                    row_index=lower_row_index
                )
                self._value_rows_display.remove_row(
                    row=deleted_row,
                    delete_row_widget=False,
                )

                self._value_rows.add_row(row=deleted_row, row_index=upper_row_index)
                self._value_rows_display.add_row_at_index(
                    row=deleted_row, row_index=upper_row_index
                )
                self._value_rows.adjust_row_index_cells(start_row_index=upper_row_index)
                if swap_param.report_when_swapped:
                    self._on_rows_swapped(
                        lower_row_index=lower_row_index,
                        upper_row_index=upper_row_index,
                    )
                is_swapped = True
        return is_swapped

    def _selected_row_provider(self) -> Optional[RowInfo]:
        return self._value_rows.get_selected_row_info()

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

    @abstractmethod
    def _create_row_data_copy(self, row_info: RowInfo) -> Any:
        raise NotImplementedError()
