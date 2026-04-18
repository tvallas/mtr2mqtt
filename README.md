# mtr2mqtt

A CLI tool for reading Nokeval MTR wireless receivers and forwarding readings as JSON objects to MQTT topics. This allows integration with home automation systems, data logging platforms, and visualization tools.

## Overview

mtr2mqtt connects to Nokeval MTR series wireless receivers (such as RTR970, FTR980, etc.) via serial connection, reads the measurements from wireless transmitters, and publishes the data to MQTT topics in a structured JSON format.

It can also publish Home Assistant MQTT Discovery messages so that each detected transmitter appears automatically as a Home Assistant device with `reading`, `battery`, and `rsl` sensor entities.

## Installation

### Using pip

The simplest way to install mtr2mqtt:

```sh
pip install mtr2mqtt
```

#### Basic Command Line Usage

Pass in serial port settings and MQTT server address. If not provided, serial port autodetection is used and localhost is used for MQTT.

Example with metadata file:

```sh
mtr2mqtt -f metadata.yml
```

Or define the serial port and mqtt host as parameters:

```sh
mtr2mqtt --serial-port /dev/ttyUSB12345 --mqtt-host 192.168.1.2
```

By default, runtime logs are emitted as one JSON object per line. When running in an interactive terminal, JSON keys and values are syntax colored, with standard fields such as `timestamp`, `level`, `logger`, and `message` highlighted consistently. When output is redirected or piped, ANSI color is suppressed so the log stream remains valid JSON.

Enable Home Assistant discovery:

```sh
mtr2mqtt -f metadata.yml --ha-discovery
```

Use a custom discovery prefix or node id:

```sh
mtr2mqtt --ha-discovery --ha-discovery-prefix ha --ha-discovery-node-id mtr-bridge-1
```

### Using Docker

You can use the pre-built Docker images from Docker Hub. Specify the latest or a specific version.

1. Pull the latest Docker image:

```sh
docker pull tvallas/mtr2mqtt:latest
```

Or pull a specific version:

```sh
docker pull tvallas/mtr2mqtt:0.5.4
```

Run the Docker container:

```sh
docker run --rm -it -v /dev/ttyUSB12345:/dev/ttyUSB12345 tvallas/mtr2mqtt:latest --serial-port /dev/ttyUSB12345 --mqtt-host 192.168.1.2
```

Note: On macOS, Docker cannot access the serial port because it runs in a virtual machine. You will need to run the tool natively on macOS or use a Linux-based system for Docker.

## Using Docker Compose

You can also use Docker Compose to run the application along with an MQTT broker.

1. Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  mosquitto:
    image: eclipse-mosquitto:latest
    container_name: mosquitto
    restart: always
    ports:
      - "1883:1883"
    command: mosquitto -c /mosquitto-no-auth.conf
  mtr2mqtt:
    image: tvallas/mtr2mqtt:latest
    container_name: mtr2mqtt
    restart: always
    depends_on:
      - mosquitto
    volumes:
      - type: bind
        source: ./metadata.yml
        target: /tmp/metadata.yml
    environment:
      MTR2MQTT_MQTT_HOST: mosquitto
      MTR2MQTT_METADATA_FILE: /tmp/metadata.yml
      MTR2MQTT_QUIET: "true"
    devices:
      - "/dev/ttyUSB0:/dev/ttyUSB0"
```

2. Run Docker Compose:

```sh
docker-compose up -d
```

## Metadata

The `metadata.yml` file is used to provide additional configuration for the `mtr2mqtt` tool. This file allows you to define the structure and details of the data being read from the Nokeval MTR wireless receivers.

### Structure of `metadata.yml`

The `metadata.yml` file should be structured as follows:

```yaml
- id: 12345
  location: "Living room"
  description: "Ambient air temperature"
  unit: "°C"
  quantity: "Temperature"
  ha:
    name: "Ambient"
    device_class: "temperature"
    state_class: "measurement"
    suggested_display_precision: 1
    icon: "mdi:thermometer"
- id: 54321
  location: "Living room"
  unit: "%"
  description: "Ambient air humidity"
  quantity: "Humidity"
```

Each sensor entry should include:

- `id`: A unique identifier for the sensor.
- `description`: A descriptive label for the sensor.
- `unit`: The unit of measurement for the sensor's readings.

**Note:** Other metadata fields can be freely added and those are added to the JSON object.

The optional `ha:` block is used only for Home Assistant discovery customization. It can override the main reading entity metadata with fields such as `name`, `device_class`, `state_class`, `suggested_display_precision`, and `icon`. Existing metadata files continue to work unchanged.

### Using the metadata file

To use the metadata file with `mtr2mqtt`, pass the file path as an argument:

```sh
mtr2mqtt -f metadata.yml
```

### MQTT Topics and message format

The messages are published to the MQTT broker in a structured JSON format. The structure of the topics and message format is as follows:

### Topic Structure

The MQTT topics are structured based on the receiver serial number and sensor ID. For example:

```text
measurements/<receiver_serial_number>/<sensor_id>
```

Where `<receiver_serial_number>` is the serial number of the receiver and `<sensor_id>` is the unique identifier for the sensor.

This measurement topic structure remains unchanged even when Home Assistant discovery is enabled.

### Home Assistant MQTT Discovery

When `--ha-discovery` is enabled, mtr2mqtt publishes retained Home Assistant device discovery messages the first time it sees a real measurement for a transmitter. One Home Assistant device is created per physical transmitter, using the transmitter id as the Home Assistant device identifier and entity unique id base. The MQTT state topic itself remains unchanged and still includes the receiver serial number.

Discovery creates these entities for each transmitter:

- `reading`: the primary sensor entity
- `battery`: a diagnostic battery voltage sensor
- `rsl`: a diagnostic signal sensor

Discovery topics use Home Assistant device discovery:

```text
<discovery_prefix>/device/<object_id>/config
<discovery_prefix>/device/<node_id>/<object_id>/config
```

For example:

```text
homeassistant/device/15006/config
measurements/RTR970123/15006
```

The discovery payload points each entity to the existing measurement topic, so measurement payloads continue to be published as non-retained JSON messages.

The primary reading entity also exposes the measurement JSON as Home Assistant attributes using `json_attributes_topic`, which means metadata fields such as `location`, `description`, `quantity`, and `zone` are visible in Home Assistant automatically.

#### Home Assistant discovery configuration

CLI flags:

- `--ha-discovery`: enable Home Assistant discovery
- `--ha-discovery-prefix`: set the discovery prefix, default `homeassistant`
- `--ha-discovery-retain` and `--no-ha-discovery-retain`: control retained discovery messages, default retained
- `--ha-discovery-node-id`: add an optional node id segment to the discovery topic

Environment variables:

- `MTR2MQTT_HA_DISCOVERY`
- `MTR2MQTT_HA_DISCOVERY_PREFIX`
- `MTR2MQTT_HA_DISCOVERY_RETAIN`
- `MTR2MQTT_HA_DISCOVERY_NODE_ID`

The reading entity infers conservative Home Assistant metadata from the existing metadata file when possible. For example, `quantity: Temperature` or `unit: °C` maps to `device_class: temperature`, humidity-like metadata maps to `device_class: humidity`, and pressure-like metadata maps to `device_class: pressure`.

To align better with typical Home Assistant sensor setups, the primary reading entity also publishes:

- `expire_after: 900`
- `suggested_area` from metadata `location`
- a default icon inferred from the measurement type, unless overridden in metadata `ha:`

### Message Format

```json
{
  "battery": 2.8,
  "type": "FT10",
  "rsl": -69,
  "id": "15006",
  "reading": 21.2,
  "timestamp": "2025-03-14 20:57:49.152063+00:00"
}
```

#### Fields Explanation

- `battery`: The battery voltage of the sensor.
- `type`: The type of the sensor.
- `rsl`: The received signal level (RSL) of the sensor.
- `id`: The unique identifier for the sensor.
- `reading`: The current reading from the sensor.
- `timestamp`: The timestamp of the reading in ISO 8601 format.

**Note:** Other metadata fields can be freely added and those are added to the JSON object.

## Preparing the Development Environment

1. Install `uv`.
2. Clone the repository:

```sh
git clone git@github.com:tvallas/mtr2mqtt
```

3. Change into the repository directory:

```sh
cd mtr2mqtt
```

4. Create or update the virtual environment and install runtime and development dependencies:

```sh
uv sync --group dev
```

5. Run the CLI locally:

```sh
uv run python -m mtr2mqtt.cli
```

### Running tests

```sh
uv run pytest -v
```

### Linting

```sh
uv run pylint $(find mtr2mqtt -name "*.py" -type f)
```

### Building distributions

```sh
uv build
```
