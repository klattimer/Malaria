from Malaria.Plugins import MalariaPlugin
import logging
try:
    from pySMART import DeviceList
    from pySMART import Device
except:
    pass

class Smart(MalariaPlugin):
    def __init__(self, malaria, **kwargs):
        super(Smart, self).__init__(malaria, **kwargs)
        self._devices = DeviceList()

    def update(self):
        data = {}
        for device in self._devices:
            if device.name not in data.keys():
                data[device.name] = {}
            try:
                for attribute in device.attributes:
                    if attribute is None: continue 
                    data[device.name][attribute.name] = attribute.raw
            except Exception as e:
                logging.exception("Attribute error: " + device.name)
        self.report_data(data)
