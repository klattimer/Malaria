from Malaria.Plugins import MalariaPlugin
import os


class LoadAvereage(MalariaPlugin):
    def __init__(self, malaria, **kwargs):
        super(LoadAvereage, self).__init__(malaria, **kwargs)

    def update(self):
        self.report_data(dict(zip([1, 5, 15], os.getloadavg())), True)
