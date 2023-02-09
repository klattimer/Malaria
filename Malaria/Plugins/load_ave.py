from Malaria.Plugins import MalariaPlugin
import os


class LoadAvereage(MalariaPlugin):
    def __init__(self, malaria, **kwargs):
        super(LoadAvereage, self).__init__(malaria, **kwargs)
        self.malaria.register_homeassistant_sensor(
            'LoadAverage/1',
            None,
            'CPU Load (1 min)',
            '%',
            'float',
            'mdi:chip'
        )
        self.malaria.register_homeassistant_sensor(
            'LoadAverage/5',
            None,
            'CPU Load (5 min)',
            '%',
            'float',
            'mdi:chip'
        )
        self.malaria.register_homeassistant_sensor(
            'LoadAverage/15',
            None,
            'CPU Load (15 min)',
            '%',
            'float',
            'mdi:chip'
        )

    def update(self):
        self.report_data(dict(zip([1, 5, 15], os.getloadavg())), True)
