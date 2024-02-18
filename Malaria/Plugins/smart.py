from Malaria.Plugins import MalariaPlugin
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
            if device.name not in self.data.keys():
                data[device.name] = {}
            try:
                for attribute in device.attributes:
                    data[device.name][attribute.name] = attribute.raw
            except:
                pass
        self.report_data(data, True)
