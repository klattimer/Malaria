# Malaria

Malaria is a pluggable system for gathering current system data points and publishing them to an MQTT service. The
intention is to provide a basic shim project that people can add python code snippets to, and have that data
reported to a mosquitto server for other systems to subscribe to.

The idea is to keep this simple and small but very easy to extend with new features. Plugins can be added in a few
lines of boiler plate plus whatever you want to monitor. Malaria works best for users when it's running on every
system they use, reporting to a centralised (and/or replicated) Mosquitto server, then the events generated in the
mosquitto server can be tied into other processes which act on them accordingly.

Malaria is intended to generate dense amounts of sometimes changing data, some of these data points are useful for
charting and general monitoring, where as others provide structure which can be used as metadata. There are some
limitations to this kind of monitoring. For instance we don't want to generate huge amounts of fast changing data
which is useless like the kind of data we might see for system processes or incoming network connections. These
types of data collection would have gaps, and hit performance un-necessarily.

## Features

 - Monitor NUT UPSMON
 - Monitor CPU temperature and usage
 - Monitor disk usage and io
 - Monitor Waveshare UPS backpack for Raspberry Pi
 - Monitor Raspberry Pi internal temperature
 - Monitor online/offline and network connections
 - Monitor system load average
 - Monitor system users
 - Monitor data on docker containers
 - Monitor nvidia graphics data
 - [Home Assistant](http://www.home-assistant.io) sensor/binary sensor/trigger auto-configuration.

## Documentation

- [Architecture](docs/Architecture.md)
- [Writing Plugins](docs/WritingPlugins.md)
- [Code of Conduct](docs/code_of_conduct.md)
- [License](docs/License.md)

## Installation

```bash
sudo apt install smartmontools
sudo python3 setup.py install
sudo malaria_setup

# Make any appropriate changes to /etc/malaria/config.json
sudo service malaria start
```

## Configuration

The configuration file is a simple JSON document to allow easy validation
and editing in modern editors. Once installed it can be found in ```/etc/malaria/config.json```

The basic required configuration looks like this.
```json
{
    "log_file": "/var/log/malaria.log",
    "update_interval": 10,
    "mosquitto": {
        "host": "192.168.1.3",
        "port": 1883,
        "username": "blaster",
        "password": "blasted",
        "base_topic": "Malaria"
    },
    "plugins": {
    }
}
```

### Plugin configuration

Plugins can be designed to take in extra configuration parameters on initialisation
these are passed to the init function, and can also have default values associated with
them. Required values which are omitted will prevent the plugin from initialising and
will generate an exception in the logs.

Here's an example using the INA219 backpack from waveshare on an old Raspberry Pi 1,
which used i2c_bus 0 rather than 1 like the newer Pis.

```json
"INA219": {
    "enabled": true,
    "addr": 66,
    "i2c_bus": 0
}
```

All contributions will be considered, useful ones which are clear and concise will likely
get accepted quickly.

