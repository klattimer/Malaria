from Malaria.Plugins import MalariaPlugin
import psutil
import os


class Network(MalariaPlugin):
    def __init__(self, malaria, **kwargs):
        super(Network, self).__init__(malaria, **kwargs)

    def update(self):
        psutil.net_io_counters(pernic=True)
        self.report_data({
            "addresses": psutil.net_if_addrs(),
            "io": psutil.net_io_counters(pernic=True, nowrap=True),
            "stats": psutil.net_if_stats(),
            "online": True if os.system("ping -c 1 8.8.4.4") is 0 else False
        })
