from Malaria.Plugins import MalariaPlugin
import psutil
import time
import os


class Network(MalariaPlugin):
    def __init__(self, malaria, **kwargs):
        super(Network, self).__init__(malaria, **kwargs)
        self._last_timestamp = None
        self._last_in = 0
        self._last_out = 0

    def update(self):
        psutil.net_io_counters(pernic=True)
        data = {
            "addresses": psutil.net_if_addrs(),
            "io": psutil.net_io_counters(pernic=True, nowrap=True),
            "stats": psutil.net_if_stats(),
            "online": True if os.system("ping -c 1 8.8.4.4") is 0 else False
        }
        now = time.time()
        bytes_in = 0
        bytes_out = 0
        for d in data['io'].keys():
            if d == 'lo': continue
            bytes_in += data['io'][d].bytes_recv
            bytes_out += data['io'][d].bytes_sent

        if self._last_timestamp is not None:
            duration = now - self._last_timestamp
            bps_in = (bytes_in - self._last_in) / duration
            bps_out = (bytes_out - self._last_out) / duration
            data['io']['download_speed'] = bps_in
            data['io']['upload_speed'] = bps_out

            self.malaria.register_homeassistant_sensor(
                'Network/io/download_speed',
                None,
                'Total Download Speed',
                "bps",
                "int",
                "mdi:download-network"
            )
            self.malaria.register_homeassistant_sensor(
                'Network/io/upload_speed',
                None,
                'Total Upload Speed',
                "bps",
                "int",
                "mdi:upload-network"
            )

        self._last_in = bytes_in
        self._last_out = bytes_out
        self._last_timestamp = now
        self.report_data(data)
