from Malaria.Plugins import MalariaPlugin
import psutil


class Thermal(MalariaPlugin):
    def __init__(self, malaria, **kwargs):
        super(Thermal, self).__init__(malaria, **kwargs)

    def update(self):
        data = {}
        t = psutil.sensors_fans()
        for k in t.keys():
            for i, x in enumerate(t[k]):
                t[k][i] = dict(x._asdict())
        data['fans'] = t

        t = psutil.sensors_temperatures()
        for k in t.keys():
            for i, x in enumerate(t[k]):
                t[k][i] = dict(x._asdict())
        data['temperatures'] = t
        self.report_data(data, True)
