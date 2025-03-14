# mtr2mqtt

A CLI tool for reading Nokeval MTR wireless receivers and forwarding readings as JSON objects to MQTT topics. This allows integration with home automation systems, data logging platforms, and visualization tools.

## Overview

mtr2mqtt connects to Nokeval MTR series wireless receivers (such as RTR970, FTR980, etc.) via serial connection, reads the measurements from wireless transmitters, and publishes the data to MQTT topics in a structured JSON format.

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
$ mtr2mqtt -f metadata.yml
```

Or define the serial port and mqtt host as parameters:
```sh
$ mtr2mqtt --serial-port /dev/ttyUSB12345 --mqtt-host 192.168.1.2
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
:
```sh
$ docker run --rm -it -v /dev/ttyUSB12345:/dev/ttyUSB12345 tvallas/mtr2mqtt:latest --serial-port /dev/ttyUSB12345 --mqtt-host 192.168.1.2
```

Note: On macOS, Docker cannot access the serial port because it runs in a virtual machine. You will need to run the tool natively on macOS or use a Linux-based system for Docker.

## Using Docker Compose

You can also use Docker Compose to run the application along with an MQTT broker.

1. Create a docker-compose.yml file:

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
The metadata.yml file is used to provide additional configuration for the mtr2mqtt tool. This file allows you to define the structure and details of the data being read from the Nokeval MTR wireless receivers.

### Structure of metadata.yml
The metadata.yml file should be structured as follows:

```yaml
sensors:
- id: 12345
  location: 'Living room'
  description: 'Ambient air temperature'
  unit: '°C'
  quantity: 'Temperature'
- id: 54321
  location: 'Living room'
  unit: '%'
  description: 'Ambient air humidity'
  quantity: 'Humidity'
```
Each sensor entry should include:

- `id`: A unique identifier for the sensor.
- `name`: A descriptive name for the sensor.
- `unit`: The unit of measurement for the sensor's readings.

**Note:** Other metadata fields can be freely added and those are added to the json object.

### Using the metadata file
To use the metadata file with mtr2mqtt, pass the file path as an argument:
```sh
$ mtr2mqtt -f metadata.yml
```
### MQTT Topics and message format
The messages are published to the MQTT broker in a structured JSON format. The structure of the topics and message format is as follows:

### Topic Structure

The MQTT topics are structured based on the receiver serial number and sensor ID. For example:
```
measurements/<receiver_serial_number>/<sensor_id>
```
Where `<receiver_serial_number>` is the serial number of the receiver and `<sensor_id>` is the unique identifier for the sensor.

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

## Preparing the Development


1. Ensure `pip` and `pipenv` are installed.
2. Clone the repository:
```sh
git clone git@github.com:tvallas/mtr2mqtt
```
3. Change into the repository directory:
```sh
cd mtr2mqtt
```
4. Fetch development dependencies:
```sh
make install
```
5. Activate the virtual environment:
```sh
pipenv shell
```
6. Running
```sh
pipenv run python -m mtr2mqtt.cli 
```


### Running tests

```sh
make test
```

### Linting
```sh
make lint
```