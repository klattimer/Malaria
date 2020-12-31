from Malaria.Plugins import MalariaPlugin
from uptime import boottime


class Uptime(MalariaPlugin):
    __topic__ = ""

    def __init__(self, malaria, **kwargs):
        super(Uptime, self).__init__(malaria, **kwargs)

    def update(self):
        self.report_data({"system_start_time": boottime().isoformat()})
