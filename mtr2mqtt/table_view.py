"""
Live table rendering for human-facing terminal output.
"""

from __future__ import annotations

from datetime import datetime
import json
import shutil
import sys


CORE_COLUMNS = [
    "receiver",
    "id",
    "status",
    "status_code",
    "location",
    "quantity",
    "reading",
    "unit",
    "battery",
    "rsl",
    "timestamp",
]
OPTIONAL_COLUMNS = [
    "type",
    "description",
    "zone",
    "calibrated",
    "message",
    "utility",
]
HIDDEN_COLUMNS = {"ha"}
HEADER_COLOR = "\033[1;38;5;255m"
TITLE_COLOR = "\033[1;38;5;81m"
COUNT_COLOR = "\033[38;5;250m"
SEPARATOR_COLOR = "\033[38;5;240m"
ID_COLOR = "\033[1;38;5;117m"
READING_COLOR = "\033[38;5;121m"
STATUS_COLOR = "\033[38;5;222m"
TIMESTAMP_COLOR = "\033[38;5;250m"
RESET = "\033[0m"
PREFERRED_WIDTHS = {
    "id": 8,
    "status": 7,
    "status_code": 11,
    "reading": 10,
    "battery": 7,
    "rsl": 6,
    "timestamp": 25,
}
MAX_WIDTHS = {
    "receiver": 16,
    "id": 8,
    "status": 7,
    "status_code": 11,
    "location": 20,
    "quantity": 16,
    "reading": 10,
    "unit": 8,
    "battery": 7,
    "rsl": 6,
    "timestamp": 25,
    "type": 12,
    "description": 24,
    "zone": 18,
    "calibrated": 12,
    "message": 24,
    "utility": 24,
}


def _display_value(value):
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _format_timestamp(value):
    rendered = _display_value(value)
    normalized = rendered.replace("Z", "+00:00")
    try:
        timestamp = datetime.fromisoformat(normalized)
    except ValueError:
        return rendered
    return timestamp.isoformat(sep=" ", timespec="seconds")


class MeasurementTableView:
    """
    Maintain the latest measurement per sensor and redraw a terminal table.
    """

    def __init__(self, stream=None, use_color=None):
        self.stream = stream or sys.stdout
        self.rows = {}
        self.dynamic_columns = []
        self.use_color = (
            hasattr(self.stream, "isatty") and self.stream.isatty()
            if use_color is None
            else use_color
        )

    def update(self, receiver_serial_number, measurement_json, status_payload=None):
        """
        Merge a measurement into the latest-state table and redraw it.
        """
        measurement = json.loads(measurement_json)
        row = {
            key: value
            for key, value in measurement.items()
            if key not in HIDDEN_COLUMNS
        }
        receiver_serial_number = str(receiver_serial_number)
        row["receiver"] = receiver_serial_number
        sensor_id = str(row.get("id", "unknown"))
        row_key = (receiver_serial_number, sensor_id)
        if status_payload:
            row["status"] = status_payload.get("status")
            row["status_code"] = status_payload.get("status_code")
        self.rows[row_key] = row

        known_columns = set(CORE_COLUMNS + OPTIONAL_COLUMNS + self.dynamic_columns)
        for key in sorted(row):
            if key not in known_columns:
                self.dynamic_columns.append(key)
                known_columns.add(key)

        self.render()

    def update_statuses(self, status_payloads):
        """
        Merge status-only updates into existing sensor rows and redraw if changed.
        """
        changed = False
        for status_payload in status_payloads:
            if status_payload.get("entity_type") != "sensor":
                continue
            row_key = (
                str(status_payload.get("receiver")),
                str(status_payload.get("sensor")),
            )
            if row_key not in self.rows:
                continue
            row = self.rows[row_key]
            for column in ("status", "status_code"):
                if row.get(column) != status_payload.get(column):
                    row[column] = status_payload.get(column)
                    changed = True
        if changed:
            self.render()

    def render(self):
        """
        Draw the full table for the current latest sensor state.
        """
        columns = self._columns()
        rows = self._sorted_rows()
        terminal_width = shutil.get_terminal_size((120, 24)).columns

        lines = [
            self._colorize("mtr2mqtt live table", TITLE_COLOR),
            self._colorize(f"Sensors: {len(rows)}", COUNT_COLOR),
            "",
            self._render_header(columns, terminal_width),
            self._render_separator(columns, terminal_width),
        ]
        for row in rows:
            lines.append(self._render_row(columns, row, terminal_width))

        self.stream.write("\x1b[H\x1b[2J")
        self.stream.write("\n".join(lines))
        self.stream.write("\n")
        self.stream.flush()

    def _columns(self):
        columns = []
        for name in CORE_COLUMNS + OPTIONAL_COLUMNS + self.dynamic_columns:
            if any(name in row for row in self.rows.values()) and name not in columns:
                columns.append(name)
        return columns

    def _sorted_rows(self):
        return [
            self.rows[key]
            for key in sorted(
                self.rows,
                key=lambda item: (
                    self._sort_id(item[1]),
                    str(item[1]),
                    str(item[0]),
                ),
            )
        ]

    def _sort_id(self, sensor_id):
        return int(sensor_id) if str(sensor_id).isdigit() else float("inf")

    def _render_separator(self, columns, terminal_width):
        widths = self._column_widths(columns, terminal_width)
        separator = "-+-".join("-" * widths[column] for column in columns)
        return self._colorize(separator, SEPARATOR_COLOR)

    def _render_header(self, columns, terminal_width):
        widths = self._column_widths(columns, terminal_width)
        cells = [
            self._colorize(column.ljust(widths[column]), HEADER_COLOR)
            for column in columns
        ]
        return " | ".join(cells)

    def _render_row(self, columns, values, terminal_width):
        widths = self._column_widths(columns, terminal_width)
        rendered_cells = []
        for column in columns:
            value = self._cell_value(column, values).replace("\n", " ")
            fitted = self._fit(value, widths[column])
            rendered_cells.append(self._colorize_cell(column, fitted))
        return " | ".join(rendered_cells)

    def _column_widths(self, columns, terminal_width):
        min_widths = {column: self._min_width(column) for column in columns}
        rows = self._sorted_rows()
        widths = {
            column: self._desired_width(column, rows, min_widths[column])
            for column in columns
        }

        table_width = sum(widths.values()) + max(0, len(columns) - 1) * 3
        while (
            table_width > terminal_width
            and any(width > min_widths[column] for column, width in widths.items())
        ):
            widest_column = self._widest_shrinkable_column(
                columns,
                widths,
                min_widths,
            )
            if widths[widest_column] <= min_widths[widest_column]:
                break
            widths[widest_column] -= 1
            table_width -= 1
        return widths

    def _min_width(self, column):
        return max(len(column), min(6, PREFERRED_WIDTHS.get(column, 6)))

    def _desired_width(self, column, rows, min_width):
        sample_values = [_display_value(row.get(column, "")) for row in rows]
        value_lengths = [len(value) for value in sample_values]
        widest = max([len(column), *value_lengths], default=len(column))
        preferred = PREFERRED_WIDTHS.get(column, widest)
        max_width = MAX_WIDTHS.get(column, 24)
        return min(max(min_width, widest, preferred), max_width)

    def _widest_shrinkable_column(self, columns, widths, min_widths):
        shrinkable_columns = [
            column for column in columns if widths[column] > min_widths[column]
        ]
        preferred_columns = [
            column for column in shrinkable_columns if column != "timestamp"
        ]
        candidate_columns = preferred_columns or shrinkable_columns
        return max(candidate_columns, key=lambda column: widths[column])

    def _cell_value(self, column, values):
        if column == "timestamp":
            return _format_timestamp(values.get(column, ""))
        return _display_value(values.get(column, ""))

    def _fit(self, value, width):
        if len(value) <= width:
            return value.ljust(width)
        if width <= 1:
            return value[:width]
        return value[: width - 1] + "…"

    def _colorize(self, text, color):
        if not self.use_color:
            return text
        return f"{color}{text}{RESET}"

    def _colorize_cell(self, column, text):
        color = None
        if column == "id":
            color = ID_COLOR
        elif column in {"reading", "unit"}:
            color = READING_COLOR
        elif column in {"battery", "rsl", "type", "status", "status_code"}:
            color = STATUS_COLOR
        elif column == "timestamp":
            color = TIMESTAMP_COLOR
        return self._colorize(text, color) if color else text
