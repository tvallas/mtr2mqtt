import json
import logging
import paho.mqtt.client as mqtt

client = mqtt.Client()

def connect(host, port):
    client.enable_logger()
    client.on_connect = _on_connect
    client.on_publish = _on_publish
    return client.connect(host=host,port=port)


def _on_connect():
    logging.info("Connected to MQTT host")

def _on_publish(topic, payload):
    logging.info("Connected to MQTT host")
    client.publish(topic==topic, payload=payload)