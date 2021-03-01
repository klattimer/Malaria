from Malaria.Plugins import MalariaPlugin
import psutil


class Memory(MalariaPlugin):
    def __init__(self, malaria, **kwargs):
        super(Memory, self).__init__(malaria, **kwargs)
        self.malaria.register_homeassistant_sensor(
            'Memory/memory/percent',
            None,
            'Memory Usage',
            "%",
            "float",
            "mdi:memory"
        )
        self.malaria.register_homeassistant_sensor(
            'Memory/swap/percent',
            None,
            'Swap Usage',
            "%",
            "float",
            "mdi:memory"
        )

    def update(self):
        self.report_data({
            "memory": psutil.virtual_memory()._asdict(),
            "swap": psutil.swap_memory()._asdict()
        }, True)
