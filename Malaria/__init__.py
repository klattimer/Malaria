import os
import importlib
import logging
import inspect
import paho.mqtt.client as mqtt
import time
import json
import sys
import threading
import shutil
from queue import Queue
from .Plugins import MalariaPlugin

MALARIA_VERSION = '0.1'


class Malaria:
    def __init__(self, **kwargs):
        logging.basicConfig(level=logging.DEBUG)
        logging.info("Starting Malaria")
        self.config = {}
        try:
            with open("/etc/malaria/config.json") as f:
                self.config = json.loads(f.read())
        except:
            if kwargs['testing'] is not True:
                logging.Error("/etc/malaria/config.json not present or broken, run malaria_setup to complete installation")
                sys.exit(1)

        self.config.update(kwargs)

        self.base_topic = self.config['mosquitto']['base_topic']
        if self.base_topic.startswith('/'):
            self.base_topic = self.base_topic[1:]
        if self.base_topic.endswith('/'):
            self.base_topic = self.base_topic[:-1]
        self.host = self.config['mosquitto']['host']
        self.port = self.config['mosquitto']['port']
        self.username = self.config['mosquitto'].get('username')
        self.password = self.config['mosquitto'].get('password')

        self.plugin_classes = {}
        self.plugins = []
        self.report_queue = Queue()
        self.running = True

        p = os.path.dirname(os.path.abspath(__file__))
        p = os.path.join(p, "Plugins")
        files = os.listdir(p)
        for f in files:
            if f.startswith("__"): continue
            if not f.endswith(".py"): continue
            m = f.replace('.py', '')
            try:
                module = importlib.import_module('.' + m, 'Malaria.Plugins')
            except:
                logging.exception("Module import failed: " + m)
                continue

            for name, obj in inspect.getmembers(module):
                try:
                    if not inspect.isclass(obj):
                        continue

                    if not issubclass(obj, MalariaPlugin):
                        continue

                    if name == "MalariaPlugin":
                        continue

                    plugin = getattr(module, name)

                    if name in self.plugin_classes.keys():
                        logging.warning("Plugin already registered %s" % name)
                        continue

                    self.plugin_classes[name] = plugin
                    logging.info("Plugin loaded \"%s\"" % name)
                except:
                    logging.exception("Plugin failed to load: \"%s\"" % name)

    def run(self):
        for p, pkwargs in self.config['plugins'].items():
            if pkwargs['enabled'] is not True:
                continue
            try:
                self.plugins.append(self.plugin_classes[p](self, **pkwargs))
            except:
                logging.exception("Failed to start plugin: " + p)

        self.client = mqtt.Client()
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()

        while self.running is True:
            self.update()
            time.sleep(self.config['update_interval'])
            self.drain()

    def report_reading(self, subtopic, value):
        subtopic = subtopic.replace('//', '/')
        if subtopic.startswith('/'):
            subtopic = subtopic[1:]
        if subtopic.endswith('/'):
            subtopic = subtopic[:-1]

        topics = subtopic.split('/')
        if topics[-1] == "temperature" or (topics[-2] == "temperature" and topics[-1] == "current"):
            key = topics[topics.index("temperature") - 1] + ' temperature'
            self.register_homeassistant_sensor(subtopic, "temperature", key, "\u00b0C", "float")
        self.report_queue.put((self.base_topic + '/' + subtopic, value))

    def drain(self):
        while self.report_queue.empty() is not True:
            (topic, value) = self.report_queue.get()
            logging.debug("> %s = %s" % (topic, str(value)))
            try:
                self.client.publish(topic, value)
            except:
                self.client.publish(topic, str(value))

            self.report_queue.task_done()
        self.report_queue.join()

    def register_homeassistant_sensor(self, topic, device_class, name, units, value_type):
        if value_type == "float":
            value_template = "{{ value|float|round(2) }}"
        elif value_type == "int":
            value_template = "{{ value|int }}"
        else:
            value_template = "{{ value }}"

        ha_sensor = {
            "device": {
                "identifiers": ["malaria-" + MALARIA_VERSION + '-' + self.config['name']],
                "manufacturer": 'malaria',
                "model": 'malaria-' + MALARIA_VERSION,
                "name": "malaria-" + MALARIA_VERSION + '-' + self.config['name']
            },
            "device_class": device_class,
            "name": name,
            "state_topic": self.base_topic + '/' + topic,
            "unique_id": "malaria-" + MALARIA_VERSION + '-' + self.config['name'] + '-' + name,
            "unit_of_measurement": units,
            "value_template": value_template,
            "platform": "mqtt"
        }

        ha_topic = "homeassistant/sensor/%s/%s/config" % (ha_sensor['device']['name'], ha_sensor['unique_id'])
        self.client.publish(ha_topic, json.dumps(ha_sensor))

    def register_homeassistant_trigger(self, topic, device_class, name, units, value_type):
        ha_trigger = {
            "automation_type": "trigger",
            "topic": self.base_topic + '/' + topic,
            "type": "button_short_release",
            "subtype": "button_1",
            "payload": "Button0",
            "device": {
                "identifiers": ["malaria-" + MALARIA_VERSION + '-' + self.config['name']],
                "manufacturer": 'malaria',
                "model": 'malaria-' + MALARIA_VERSION,
                "name": "malaria-" + MALARIA_VERSION + '-' + self.config['name']
            },
            "platform": "mqtt"
        }
        ha_topic = "homeassistant/device_automation/%s/%s/config" % (ha_trigger['device']['name'], ha_trigger['unique_id'])
        self.client.publish(ha_topic, json.dumps(ha_trigger))

    def register_homeassistant_binary_sensor(self, topic, device_class, name, units, value_type):
        ha_binary_sensor = {
            "device": {
                "identifiers": ["malaria-" + MALARIA_VERSION + '-' + self.config['name']],
                "manufacturer": 'malaria',
                "model": 'malaria-' + MALARIA_VERSION,
                "name": "malaria-" + MALARIA_VERSION + '-' + self.config['name']
            },
            "device_class": device_class,
            "name": name,
            "state_topic": self.base_topic + '/' + topic,
            "unique_id": "malaria-" + MALARIA_VERSION + '-' + self.config['name'] + '-' + name,
            "platform": "mqtt"
        }
        ha_topic = "homeassistant/binary_sensor/%s/%s/config" % (ha_binary_sensor['device']['name'], ha_binary_sensor['unique_id'])

        self.client.publish(ha_topic, json.dumps(ha_binary_sensor))

    def update(self):
        for plugin in self.plugins:
            threading.Thread(target=plugin.update).start()


def main():
    m = Malaria()
    m.run()


def setup():
    # Install the data/malaria.service to systemd
    path = os.path.dirname(os.path.abspath(__file__))

    shutil.copy(os.path.join(path, 'data/malaria.service'), '/etc/systemd/system/')

    # Install the config.json /etc/malaria/
    with open(os.path.join(path, 'data/config.json')) as f:
        config = json.loads(f.read())

    config['mosquitto']['host'] = input("MQTT Server address: ")
    config['mosquitto']['port'] = input("MQTT Server port (1883):")
    config['mosquitto']['username'] = input("MQTT username (None):")
    if config['mosquitto']['username']:
        config['mosquitto']['password'] = input("MQTT Password:")
    config['mosquitto']['base_topic'] = input("MQTT base topic (Malaria/<hostname>):")

    # Detect if this is a raspberry pi and if so enable the RaspberryPi plugin

    with open('/etc/malaria/config.json', 'wt') as f:
        f.write(json.dumps(config, indent=4, sortkeys=True))

if __name__ == '__main__':
    main()
