"""
Tests for runtime module.
"""

from types import SimpleNamespace

import pytest
from context import mtr2mqtt
from mtr2mqtt import runtime


def test_open_mqtt_connection_uses_callback_api_v2(monkeypatch):
    """
    MQTT client initialization opts in to the non-deprecated callback API.
    """
    captured = {}

    class FakeClient:
        def __init__(self, **kwargs):
            captured["kwargs"] = kwargs
            self.connected_flag = False

        def enable_logger(self):
            captured["enable_logger"] = True

        def reconnect_delay_set(self, min_delay, max_delay):
            captured["reconnect_delay_set"] = (min_delay, max_delay)

        def loop_start(self):
            captured["loop_start"] = True

        def connect(self, host, port):
            captured["connect"] = (host, port)
            self.connected_flag = True

    monkeypatch.setattr(runtime.mqtt, "Client", FakeClient)
    monkeypatch.setattr(
        runtime.mqtt,
        "CallbackAPIVersion",
        SimpleNamespace(VERSION2="version2"),
    )
    monkeypatch.setattr(runtime.time, "sleep", lambda _: None)

    args = SimpleNamespace(mqtt_host="mqtt.example", mqtt_port=1884)

    client = runtime.open_mqtt_connection(args)

    assert captured["kwargs"]["callback_api_version"] == "version2"
    assert captured["kwargs"]["client_id"] == "mtr2mqtt"
    assert captured["kwargs"]["protocol"] == runtime.mqtt.MQTTv311
    assert captured["kwargs"]["transport"] == "tcp"
    assert captured["connect"] == ("mqtt.example", 1884)
    assert captured["reconnect_delay_set"] == (1, 30)
    assert captured["enable_logger"] is True
    assert captured["loop_start"] is True
    assert client.on_connect is runtime.on_connect
    assert client.on_disconnect is runtime.on_disconnect


def test_open_mqtt_connection_raises_mqtt_error_on_connect_failure(monkeypatch):
    """
    MQTT startup failures are surfaced as runtime exceptions instead of exits.
    """

    class FakeClient:
        def __init__(self, **kwargs):
            self.connected_flag = False

        def enable_logger(self):
            return None

        def reconnect_delay_set(self, min_delay, max_delay):
            return None

        def loop_start(self):
            return None

        def loop_stop(self):
            return None

        def connect(self, host, port):
            raise runtime.mqtt.socket.error("boom")

    monkeypatch.setattr(runtime.mqtt, "Client", FakeClient)
    monkeypatch.setattr(runtime.time, "sleep", lambda _: None)

    args = SimpleNamespace(mqtt_host="mqtt.example", mqtt_port=1884)

    try:
        runtime.open_mqtt_connection(args)
    except runtime.MqttConnectionError as error:
        assert "Unable to connect to MQTT host mqtt.example:1884" == str(error)
    else:
        raise AssertionError("MqttConnectionError was not raised")


def test_open_mqtt_connection_raises_on_broker_rejection(monkeypatch):
    """
    MQTT broker rejections fail startup instead of hanging indefinitely.
    """

    class FakeClient:
        def __init__(self, **kwargs):
            self.connected_flag = False
            self.connect_error = None

        def enable_logger(self):
            return None

        def reconnect_delay_set(self, min_delay, max_delay):
            return None

        def loop_start(self):
            return None

        def loop_stop(self):
            return None

        def connect(self, host, port):
            runtime.on_connect(self, None, None, 5, None)

    monkeypatch.setattr(runtime.mqtt, "Client", FakeClient)
    monkeypatch.setattr(runtime.time, "sleep", lambda _: None)

    args = SimpleNamespace(mqtt_host="mqtt.example", mqtt_port=1884)

    with pytest.raises(runtime.MqttConnectionError) as error:
        runtime.open_mqtt_connection(args)

    assert "reason code 5" in str(error.value)


def test_open_mqtt_connection_raises_on_timeout(monkeypatch):
    """
    MQTT startup times out when the callback never reports success or failure.
    """
    monotonic_values = iter([0, 10, 20, 31])

    class FakeClient:
        def __init__(self, **kwargs):
            self.connected_flag = False
            self.connect_error = None

        def enable_logger(self):
            return None

        def reconnect_delay_set(self, min_delay, max_delay):
            return None

        def loop_start(self):
            return None

        def loop_stop(self):
            return None

        def connect(self, host, port):
            return None

    monkeypatch.setattr(runtime.mqtt, "Client", FakeClient)
    monkeypatch.setattr(runtime.time, "sleep", lambda _: None)
    monkeypatch.setattr(runtime.time, "monotonic", lambda: next(monotonic_values))

    args = SimpleNamespace(mqtt_host="mqtt.example", mqtt_port=1884)

    with pytest.raises(runtime.MqttConnectionError) as error:
        runtime.open_mqtt_connection(args)

    assert "Timed out waiting" in str(error.value)


def test_on_connect_logs_reason_code_objects_without_crashing(caplog):
    """
    Successful MQTT connects must tolerate ReasonCode-like callback objects.
    """

    class FakeReasonCode:
        def __eq__(self, other):
            return other == 0

        def __str__(self):
            return "Success"

    client = SimpleNamespace(connected_flag=False, connect_error="previous")

    with caplog.at_level("INFO"):
        runtime.on_connect(client, None, None, FakeReasonCode(), None)

    assert client.connected_flag is True
    assert client.connect_error is None
    assert caplog.records[0].event == "mqtt_connected"
    assert caplog.records[0].mqtt_reason_code == "Success"


def test_open_receiver_connection_rejects_incompatible_explicit_port(monkeypatch):
    """
    Explicit ports must still validate as compatible receivers.
    """

    class FakeSerial:
        def __init__(self):
            self.closed = False
            self.name = "/dev/cu.usbserial-test"

        def close(self):
            self.closed = True

    fake_serial = FakeSerial()
    args = SimpleNamespace(
        serial_port="/dev/cu.usbserial-test",
        baudrate=9600,
        bytesize=8,
        parity="N",
        stopbits=1,
        serial_timeout=1,
        scl_address=126,
    )

    monkeypatch.setattr(runtime, "_create_serial_handle", lambda *_args: fake_serial)
    monkeypatch.setattr(runtime.scl, "get_receiver_type", lambda *_args: None)

    receiver = runtime.open_receiver_connection(args)

    assert receiver is None
    assert fake_serial.closed is True


def test_open_receiver_connection_raises_receiver_error_for_open_failure(monkeypatch):
    """
    Explicit-port failures are surfaced as runtime exceptions instead of exits.
    """
    args = SimpleNamespace(
        serial_port="/dev/cu.usbserial-test",
        baudrate=9600,
        bytesize=8,
        parity="N",
        stopbits=1,
        serial_timeout=1,
        scl_address=126,
    )

    def raise_serial_error(*_args):
        raise runtime.serial.serialutil.SerialException("boom")

    monkeypatch.setattr(runtime, "_create_serial_handle", raise_serial_error)

    try:
        runtime.open_receiver_connection(args)
    except runtime.ReceiverConnectionError as error:
        assert "Unable to open serial port /dev/cu.usbserial-test" == str(error)
    else:
        raise AssertionError("ReceiverConnectionError was not raised")


def test_recover_receiver_connection_rediscovery_finds_replugged_receiver(monkeypatch):
    """
    Autodetect mode rescans for a receiver when reopening the old port fails.
    """

    class ExistingSerial:
        def __init__(self):
            self.port = "/dev/cu.usbserial-old"
            self.closed = False

        def close(self):
            self.closed = True

    class ReopenAttempt:
        def __init__(self):
            self.port = None

        def apply_settings(self, _settings):
            pass

        def open(self):
            raise FileNotFoundError("device disappeared")

    rediscovered_receiver = runtime.ReceiverConnection(
        serial_handle=SimpleNamespace(port="/dev/cu.usbserial-new"),
        device_type="RTR970",
        receiver_serial_number="RTR970456",
        serial_config={"baudrate": 9600},
    )
    current_receiver = runtime.ReceiverConnection(
        serial_handle=ExistingSerial(),
        device_type="RTR970",
        receiver_serial_number="RTR970123",
        serial_config={"baudrate": 9600},
    )

    monkeypatch.setattr(runtime.serial, "Serial", ReopenAttempt)
    monkeypatch.setattr(
        runtime,
        "open_receiver_connection",
        lambda _args: rediscovered_receiver,
    )

    recovered = runtime.recover_receiver_connection(
        current_receiver,
        SimpleNamespace(serial_port=None, scl_address=126),
    )

    assert current_receiver.serial_handle.closed is True
    assert recovered is rediscovered_receiver


def test_publish_measurement_skips_while_mqtt_is_disconnected():
    """
    Measurements are skipped cleanly when MQTT is temporarily disconnected.
    """
    client = SimpleNamespace(connected_flag=False)

    result, mid = runtime.publish_measurement(
        client,
        "RTR970123",
        '{"id": "15006", "reading": 22.9}',
    )

    assert result == runtime.mqtt.MQTT_ERR_NO_CONN
    assert mid is None


def test_publish_measurement_publishes_discovery_first():
    """
    Measurement publishing keeps the normal state topic and publishes discovery first.
    """

    class FakeClient:
        def __init__(self):
            self.calls = []

        def publish(self, topic, **kwargs):
            self.calls.append((topic, kwargs))
            return (0, len(self.calls))

    client = FakeClient()
    publisher = runtime.homeassistant.DiscoveryPublisher("homeassistant", retain=True)
    measurement_json = (
        '{"id":"15006","type":"FT10","reading":22.9,"battery":2.6,"rsl":-69}'
    )

    result, mid = runtime.publish_measurement(
        client,
        "RTR970123",
        measurement_json,
        ha_discovery_publisher=publisher,
    )

    assert result == 0
    assert mid == 2
    assert client.calls[0][0] == "homeassistant/device/15006/config"
    assert client.calls[0][1]["qos"] == 1
    assert client.calls[0][1]["retain"] is True
    assert client.calls[1][0] == "measurements/RTR970123/15006"
    assert client.calls[1][1]["payload"] == measurement_json
    assert client.calls[1][1]["retain"] is False


def test_publish_measurement_rejects_invalid_json_payload():
    """
    Invalid measurement payloads are skipped instead of raising.
    """
    client = SimpleNamespace(connected_flag=True)

    result, mid = runtime.publish_measurement(client, "RTR970123", "{")

    assert result == runtime.mqtt.MQTT_ERR_INVAL
    assert mid is None


def test_publish_measurement_handles_publish_exceptions():
    """
    MQTT publish exceptions are converted to a failed publish result.
    """

    class FakeClient:
        connected_flag = True

        def publish(self, *args, **kwargs):
            raise RuntimeError("boom")

    result, mid = runtime.publish_measurement(
        FakeClient(),
        "RTR970123",
        '{"id": "15006", "reading": 22.9}',
    )

    assert result == runtime.mqtt.MQTT_ERR_NO_CONN
    assert mid is None


def test_publish_measurement_without_discovery_keeps_normal_publish_behavior():
    """
    Measurement publishing still works unchanged when discovery is disabled.
    """

    class FakeClient:
        def __init__(self):
            self.calls = []

        def publish(self, topic, **kwargs):
            self.calls.append((topic, kwargs))
            return (0, 1)

    client = FakeClient()
    measurement_json = (
        '{"id":"15006","type":"FT10","reading":22.9,"battery":2.6,"rsl":-69}'
    )

    result, mid = runtime.publish_measurement(
        client,
        "RTR970123",
        measurement_json,
        ha_discovery_publisher=None,
    )

    assert result == 0
    assert mid == 1
    assert client.calls == [
        (
            "measurements/RTR970123/15006",
            {"payload": measurement_json, "qos": 1, "retain": False},
        )
    ]


def test_log_measurement_adds_structured_measurement_payload(caplog):
    """
    Measurement logs carry the parsed payload as structured data.
    """
    with caplog.at_level("INFO"):
        runtime.log_measurement('{"id":"15006","reading":22.9,"location":"Kids room"}')

    assert caplog.records[0].event == "measurement_received"
    assert caplog.records[0].measurement["id"] == "15006"
    assert caplog.records[0].measurement["location"] == "Kids room"


def test_build_receiver_connection_logs_structured_receiver_details(monkeypatch, caplog):
    """
    Receiver connection logs expose the device and serial identity as fields.
    """

    class FakeSerial:
        name = "/dev/cu.usbserial-test"

        def get_settings(self):
            return {"baudrate": 9600}

    monkeypatch.setattr(runtime, "_read_receiver_serial_number", lambda *_args: "A118636")

    with caplog.at_level("INFO"):
        receiver = runtime._build_receiver_connection(
            FakeSerial(),
            SimpleNamespace(scl_address=126),
            "RTR970 V3.0",
        )

    assert receiver.receiver_serial_number == "A118636"
    assert caplog.records[0].event == "receiver_connected"
    assert caplog.records[0].device_type == "RTR970 V3.0"
    assert caplog.records[0].serial_port == "/dev/cu.usbserial-test"


def test_bridge_recovers_and_uses_refreshed_receiver_serial_number(monkeypatch):
    """
    After serial recovery, publishes use the refreshed receiver serial number.
    """

    class BrokenSerial:
        port = "/dev/cu.usbserial-old"
        name = port

        def write(self, _command):
            raise OSError("Device not configured")

        def close(self):
            pass

    old_receiver = runtime.ReceiverConnection(
        serial_handle=BrokenSerial(),
        device_type="RTR970",
        receiver_serial_number="RTR970123",
        serial_config={"baudrate": 9600},
    )
    new_receiver = runtime.ReceiverConnection(
        serial_handle=SimpleNamespace(name="/dev/cu.usbserial-new"),
        device_type="RTR970",
        receiver_serial_number="RTR970456",
        serial_config={"baudrate": 9600},
    )
    args = SimpleNamespace(scl_address=126, serial_port="/dev/cu.usbserial-old")
    bridge = runtime.MtrBridge(args)
    bridge.receiver = old_receiver
    bridge.mqtt_client = object()

    captured = {}

    monkeypatch.setattr(runtime.time, "sleep", lambda _: None)
    monkeypatch.setattr(
        runtime,
        "recover_receiver_connection",
        lambda receiver, _args: new_receiver,
    )
    monkeypatch.setattr(
        runtime,
        "publish_measurement",
        lambda _client, receiver_serial_number, _json, ha_discovery_publisher=None: (
            captured.setdefault("receiver_serial_number", receiver_serial_number),
            None,
        ),
    )

    result = bridge.poll_once()

    assert result.state is runtime.BridgeState.RECOVERING
    assert result.measurement_json is None
    assert bridge.receiver is new_receiver
    assert bridge.state is runtime.BridgeState.READY

    bridge.publish_measurement('{"id":"15006","reading":22.9}')

    assert captured["receiver_serial_number"] == "RTR970456"


def test_poll_once_returns_waiting_state_when_no_receiver_is_available(monkeypatch):
    """
    Polling exposes the no-receiver case explicitly.
    """
    args = SimpleNamespace(scl_address=126, serial_port=None)
    bridge = runtime.MtrBridge(args)

    monkeypatch.setattr(runtime, "open_receiver_connection", lambda _args: None)

    result = bridge.poll_once()

    assert result.state is runtime.BridgeState.WAITING_FOR_RECEIVER
    assert result.measurement_json is None
    assert bridge.state is runtime.BridgeState.WAITING_FOR_RECEIVER


def test_poll_once_returns_idle_for_empty_ring_buffer(monkeypatch):
    """
    Polling exposes an empty receiver buffer as an idle cycle.
    """

    class FakeSerial:
        name = "/dev/cu.usbserial-test"

        def write(self, _command):
            return None

        def read_until(self, _end):
            return b"\x80#\x03"

        def read(self, _size):
            return runtime.scl.calc_bcc(b"\x80#\x03")

    args = SimpleNamespace(scl_address=126)
    bridge = runtime.MtrBridge(args)
    bridge.receiver = runtime.ReceiverConnection(
        serial_handle=FakeSerial(),
        device_type="RTR970",
        receiver_serial_number="RTR970123",
        serial_config={"baudrate": 9600},
    )

    result = bridge.poll_once()

    assert result.state is runtime.BridgeState.IDLE
    assert result.measurement_json is None
    assert bridge.state is runtime.BridgeState.IDLE


def test_poll_once_returns_measurement_payload_when_data_is_available(monkeypatch):
    """
    Polling exposes parsed measurements explicitly instead of overloading None.
    """

    class FakeSerial:
        name = "/dev/cu.usbserial-test"

        def write(self, _command):
            return None

        def read_until(self, _end):
            return b"\x800 90 58 15006 145 11\x03"

        def read(self, _size):
            return runtime.scl.calc_bcc(b"\x800 90 58 15006 145 11\x03")

    args = SimpleNamespace(scl_address=126)
    bridge = runtime.MtrBridge(args)
    bridge.receiver = runtime.ReceiverConnection(
        serial_handle=FakeSerial(),
        device_type="RTR970",
        receiver_serial_number="RTR970123",
        serial_config={"baudrate": 9600},
    )

    result = bridge.poll_once()

    assert result.state is runtime.BridgeState.READY
    assert result.measurement_json is not None
    assert '"id": "15006"' in result.measurement_json
    assert bridge.state is runtime.BridgeState.READY


def test_bridge_start_raises_receiver_error_when_no_receiver_is_found(monkeypatch):
    """
    Bridge startup reports missing receivers as a runtime exception.
    """
    args = SimpleNamespace(scl_address=126)
    bridge = runtime.MtrBridge(args)

    monkeypatch.setattr(runtime, "open_receiver_connection", lambda _args: None)

    try:
        bridge.start()
    except runtime.ReceiverConnectionError as error:
        assert "Unable to find MTR receivers" == str(error)
    else:
        raise AssertionError("ReceiverConnectionError was not raised")
