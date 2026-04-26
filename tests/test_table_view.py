"""
Tests for the live table renderer.
"""

import io
import os

from context import mtr2mqtt
from mtr2mqtt.table_view import MeasurementTableView


def test_table_view_adds_dynamic_columns_from_measurements(monkeypatch):
    """
    Extra measurement fields become visible as new columns automatically.
    """
    stream = io.StringIO()
    view = MeasurementTableView(stream=stream)
    monkeypatch.setattr(
        "mtr2mqtt.table_view.shutil.get_terminal_size",
        lambda *args, **kwargs: os.terminal_size((160, 24)),
    )

    view.update(
        "RTR970123",
        (
            '{"id":"15006","reading":22.7,"location":"Kids room",'
            '"zone":"Indoor","custom":"value","ha":{"name":"ignored"}}'
        ),
    )

    rendered = stream.getvalue()

    assert "receiver" in rendered
    assert "custom" in rendered
    assert "RTR970123" in rendered
    assert "Kids room" in rendered
    assert "value" in rendered
    assert '"name":"ignored"' not in rendered


def test_table_view_keeps_latest_reading_for_sensor(monkeypatch):
    """
    The table redraw only shows the latest row per receiver and sensor id.
    """
    stream = io.StringIO()
    view = MeasurementTableView(stream=stream)
    monkeypatch.setattr(
        "mtr2mqtt.table_view.shutil.get_terminal_size",
        lambda *args, **kwargs: os.terminal_size((160, 24)),
    )

    view.update("RTR970123", '{"id":"15006","reading":22.7}')
    view.update("RTR970123", '{"id":"15006","reading":23.1}')

    rendered = stream.getvalue().split("\x1b[H\x1b[2J")[-1]

    assert "23.1" in rendered
    assert "22.7" not in rendered


def test_table_view_sorts_rows_by_numeric_sensor_id(monkeypatch):
    """
    Rows are ordered by sensor id rather than location or receiver name.
    """
    stream = io.StringIO()
    view = MeasurementTableView(stream=stream)
    monkeypatch.setattr(
        "mtr2mqtt.table_view.shutil.get_terminal_size",
        lambda *args, **kwargs: os.terminal_size((160, 24)),
    )

    view.update("RTR970123", '{"id":"15010","location":"B room","reading":20.0}')
    view.update("RTR970123", '{"id":"15002","location":"A room","reading":21.0}')

    rendered = stream.getvalue().split("\x1b[H\x1b[2J")[-1]
    assert rendered.index("15002") < rendered.index("15010")


def test_table_view_formats_timestamp_to_second_precision(monkeypatch):
    """
    The table timestamp view drops sub-second precision while keeping timezone.
    """
    stream = io.StringIO()
    view = MeasurementTableView(stream=stream)
    monkeypatch.setattr(
        "mtr2mqtt.table_view.shutil.get_terminal_size",
        lambda *args, **kwargs: os.terminal_size((160, 24)),
    )

    full_timestamp = "2026-04-18 19:36:09.629822+00:00"
    displayed_timestamp = "2026-04-18 19:36:09+00:00"
    view.update(
        "RTR970123",
        (
            '{"id":"15006","reading":22.7,"timestamp":"'
            + full_timestamp
            + '","location":"Kids room"}'
        ),
    )

    rendered = stream.getvalue().split("\x1b[H\x1b[2J")[-1]
    assert displayed_timestamp in rendered
    assert full_timestamp not in rendered


def test_table_view_can_colorize_headers_and_cells(monkeypatch):
    """
    Table view can apply ANSI coloring for interactive terminals.
    """
    stream = io.StringIO()
    view = MeasurementTableView(stream=stream, use_color=True)
    monkeypatch.setattr(
        "mtr2mqtt.table_view.shutil.get_terminal_size",
        lambda *args, **kwargs: os.terminal_size((160, 24)),
    )

    view.update(
        "RTR970123",
        '{"id":"15006","reading":22.7,"unit":"°C","timestamp":"2026-04-18T19:36:09+00:00"}',
    )

    rendered = stream.getvalue()
    assert "\033[1;38;5;255m" in rendered
    assert "\033[1;38;5;117m" in rendered
    assert "\033[38;5;121m" in rendered


def test_table_view_includes_status_information(monkeypatch):
    """
    Measurement rows can show textual and numeric status.
    """
    stream = io.StringIO()
    view = MeasurementTableView(stream=stream)
    monkeypatch.setattr(
        "mtr2mqtt.table_view.shutil.get_terminal_size",
        lambda *args, **kwargs: os.terminal_size((160, 24)),
    )

    view.update(
        "RTR970123",
        '{"id":"15006","reading":22.7}',
        status_payload={"status": "online", "status_code": 1},
    )

    rendered = stream.getvalue().split("\x1b[H\x1b[2J")[-1]
    assert "status" in rendered
    assert "status_code" in rendered
    assert "online" in rendered
    assert "1" in rendered


def test_table_view_reflects_offline_status_transition(monkeypatch):
    """
    Status-only updates redraw existing rows when a sensor times out.
    """
    stream = io.StringIO()
    view = MeasurementTableView(stream=stream)
    monkeypatch.setattr(
        "mtr2mqtt.table_view.shutil.get_terminal_size",
        lambda *args, **kwargs: os.terminal_size((160, 24)),
    )

    view.update(
        "RTR970123",
        '{"id":"15006","reading":22.7}',
        status_payload={"status": "online", "status_code": 1},
    )
    view.update_statuses(
        [
            {
                "entity_type": "sensor",
                "receiver": "RTR970123",
                "sensor": "15006",
                "status": "offline",
                "status_code": 0,
            }
        ]
    )

    rendered = stream.getvalue().split("\x1b[H\x1b[2J")[-1]
    assert "offline" in rendered
    assert "online" not in rendered
