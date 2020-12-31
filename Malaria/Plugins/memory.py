from Malaria.Plugins import MalariaPlugin
import psutil


class Memory(MalariaPlugin):
    def __init__(self, malaria, **kwargs):
        super(Memory, self).__init__(malaria, **kwargs)

    def update(self):
        self.report_data({
            "memory": psutil.virtual_memory()._asdict(),
            "swap": psutil.swap_memory()._asdict()
        }, True)
