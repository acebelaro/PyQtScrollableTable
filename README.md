# PyQtScrollableTable

A customizable, scrollable table component for PyQt6 applications with support for row operations, undo/redo, copy/cut/paste, and more.

## Features

- **Scrollable Table**: Embeddable table component that integrates with PyQt6's QGroupBox container
- **Row Management**: Add, delete, and swap rows with ease
- **Undo/Redo**: Full undo/redo support for all row operations (Ctrl+Z, Ctrl+Y)
- **Copy/Cut/Paste**: Copy, cut, and paste row data (Ctrl+C, Ctrl+X, Ctrl+V)
- **Multiple Cell Types**: Support for editable text, readonly text, checkboxes, and row index cells
- **Customizable Styling**: CSS-based styling with support for dynamic row class names
- **Button Controls**: Optional button controls for delete, move up, and move down operations
- **Confirmation Callbacks**: Optional confirmation dialogs before row operations
- **Event Reporting**: Callbacks for row added, deleted, and swapped events
- **Keyboard Shortcuts**: Configurable keyboard shortcuts for common operations

## Requirements

- Python 3.10+
- PyQt6 >= 6.11.0

## Installation

```bash
pip install PyQt6>=6.11.0 pyqt6-tools
```

Or simply:

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Define Your Data Structure

```python
from typing import NamedTuple

class MyData(NamedTuple):
    enabled: bool
    name: str
    value: int
```

### 2. Create a Table Subclass

Subclass the `Table` class and implement the required abstract methods:

```python
from typing import List
from PyQt6.QtWidgets import QGroupBox

from qt_table import Table, TableConfig, TableRowCellValue
from qt_table_types import (
    TableColumnConfig, TableCellUiType, TableHeaderRowConfig,
    TableValueRowConfig, BeforeUpdateConfirmers, TableShortcutKeys,
)

class MyTable(Table):

    def __init__(self, groupbox_container: QGroupBox):
        # Define column configurations
        column_configs = [
            TableColumnConfig(ui_type=TableCellUiType.ROW_INDEX_CELL, text="#", width=65),
            TableColumnConfig(ui_type=TableCellUiType.CHECKBOX, text="Enabled", width=70),
            TableColumnConfig(ui_type=TableCellUiType.EDITABLE_TEXT, text="Name", width=200),
            TableColumnConfig(ui_type=TableCellUiType.READONLY_TEXT, text="Value", width=100),
        ]

        # Configure header row
        header_row_config = TableHeaderRowConfig(
            height=40,
            header_cell_css_styles=["background-color: rgb(199, 199, 199)"],
        )

        # Configure value rows
        value_row_config = TableValueRowConfig(
            height=40,
        )

        # Initialize the table
        super().__init__(
            name="My Table",
            groupbox_container=groupbox_container,
            table_config=TableConfig(
                header_row_config=header_row_config,
                column_configs=column_configs,
                value_row_config=value_row_config,
                shortcut_keys=TableShortcutKeys(
                    ctrl_z_y_undo_redo=True,
                    ctrl_c_x_v_copy_cut_paste=True,
                ),
            ),
        )

    def _create_row_index_cell_value(self, row_index: int) -> str:
        """Return the display value for the row index cell."""
        return f"Row {row_index + 1}"

    def _create_row_cell_values(self, row_index: int, data: MyData) -> List[TableRowCellValue]:
        """Convert row data into cell values for display."""
        return [
            TableRowCellValue(cell_index=0, value=self._create_row_index_cell_value(row_index)),
            TableRowCellValue(cell_index=1, value=data.enabled),
            TableRowCellValue(cell_index=2, value=data.name),
            TableRowCellValue(cell_index=3, value=str(data.value)),
        ]

    def _create_data_from_row_cell_values(self, cell_values: List[TableRowCellValue]) -> MyData:
        """Reconstruct data from cell values (used when editing)."""
        return MyData(
            enabled=cell_values[1].value,
            name=cell_values[2].value,
            value=int(cell_values[3].value),
        )

    def _on_row_added(self, row_index: int, data: MyData) -> None:
        """Called when a row is added."""
        print(f"Row added at index {row_index}")

    def _on_row_deleted(self, row_index: int, data: MyData) -> None:
        """Called when a row is deleted."""
        print(f"Row deleted at index {row_index}")

    def _on_rows_swapped(self, upper_row_info, lower_row_info) -> None:
        """Called when rows are swapped."""
        print(f"Rows swapped: {upper_row_info.row_index} <-> {lower_row_info.row_index}")

    def _create_row_data_copy(self, row_info) -> MyData:
        """Create a copy of row data (used for copy/paste operations)."""
        return row_info.data
```

### 3. Use the Table in Your Application

```python
from PyQt6.QtWidgets import QApplication, QMainWindow, QGroupBox, QVBoxLayout, QWidget

app = QApplication([])
window = QMainWindow()
container = QGroupBox(window)
container.setGeometry(10, 10, 500, 400)

table = MyTable(container)

# Add some initial data
table.add_new_row_data(MyData(enabled=True, name="Item 1", value=100))
table.add_new_row_data(MyData(enabled=False, name="Item 2", value=200))

window.show()
app.exec()
```

## Configuration Options

### Cell UI Types

| Type | Description |
|------|-------------|
| `ROW_INDEX_CELL` | Auto-numbered row index |
| `EDITABLE_TEXT` | Editable text input |
| `READONLY_TEXT` | Read-only text display |
| `CHECKBOX` | Boolean checkbox |

### TableConfig Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `header_row_config` | `TableHeaderRowConfig` | Configuration for the header row |
| `column_configs` | `List[TableColumnConfig]` | List of column configurations |
| `value_row_config` | `TableValueRowConfig` | Configuration for data rows |
| `button_controls` | `TableButtonControls` | Optional button controls |
| `before_update_confirmers` | `BeforeUpdateConfirmers` | Optional confirmation callbacks |
| `select_new_row_added` | `bool` | Auto-select newly added rows (default: True) |
| `select_next_row_after_row_deletion` | `bool` | Auto-select next row after deletion (default: True) |
| `shortcut_keys` | `TableShortcutKeys` | Keyboard shortcut configuration |

### Styling

You can customize the appearance using CSS styles:

```python
value_row_config = TableValueRowConfig(
    height=40,
    class_styles=[
        TableElemClassStyle(
            class_name="selected",
            styles=["background-color: #0ec0e8"],
        ),
        TableElemClassStyle(
            class_name="even",
            styles=["background-color: #cceeff"],
        ),
    ],
    row_class_name_decider=lambda param: "even" if param.data.value % 2 == 0 else "odd",
)
```

### Button Controls

```python
from PyQt6.QtWidgets import QPushButton

button_controls = TableButtonControls(
    delete_selected=QPushButton("Delete"),
    move_up_selected=QPushButton("Move Up"),
    move_down_selected=QPushButton("Move Down"),
)
```

### Confirmation Callbacks

```python
def confirm_row_addition(row_info: RowInfo) -> bool:
    # Return True to proceed, False to cancel
    return QMessageBox.question(None, "Confirm", "Add row?") == QMessageBox.Yes

before_update_confirmers = BeforeUpdateConfirmers(
    confirm_row_addition=confirm_row_addition,
    confirm_row_deletion=confirm_row_deletion,
    confirm_row_swap=confirm_row_swap,
)
```

## API Reference

### Table Class Methods

| Method | Description |
|--------|-------------|
| `add_new_row_data(data)` | Add a new row at the bottom |
| `add_new_row_data_at_index(row_index, data)` | Add a new row at a specific index |
| `update_row_at_index(row_index, data)` | Update the data of an existing row |

### Table Class Properties

| Property | Type | Description |
|----------|------|-------------|
| `rows` | `List[TableRow]` | List of all row objects |
| `row_count` | `int` | Total number of rows |
| `selected_row` | `Optional[TableRow]` | Currently selected row |
| `selected_row_index` | `int` | Index of the selected row (-1 if none) |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+C` | Copy selected row |
| `Ctrl+X` | Cut selected row |
| `Ctrl+V` | Paste row |

## Project Structure

```
PyQtScrollableTable/
├── qt_table.py                 # Main Table class
├── qt_table_types.py           # Type definitions and configurations
├── qt_table_row.py             # TableRow implementation
├── qt_table_row_cell.py        # Cell implementation
├── qt_table_header_rows.py     # Header row implementation
├── qt_table_value_rows.py      # Value rows management
├── qt_table_value_rows_display.py  # Value rows display/scrolling
├── qt_table_undo_redo.py       # Undo/redo functionality
├── qt_table_copy_cut_paste.py  # Copy/cut/paste functionality
├── qt_table_row_actions.py     # Row action operations
├── sample/                     # Sample application
│   ├── sample_main.py
│   ├── sample_main.ui
│   └── sample_table.py
└── README.md
```

## License

MIT License