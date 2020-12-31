from Malaria.Plugins import MalariaPlugin
import subprocess
import re


class RaspberryPi(MalariaPlugin):
    def __init__(self, malaria, **kwargs):
        super(RaspberryPi, self).__init__(malaria, **kwargs)
        self.__justnumbers = re.compile(r'[^\d.]+')

    def update(self):
        o = subprocess.Popen(["vcgencmd", "measure_temp"], stdout=subprocess.PIPE).communicate()[0]
        temperature = float(self.__justnumbers.sub('', o.decode('UTF-8')))
        self.report_reading('VideoCore/temperature', temperature)

        o = subprocess.Popen(["vcgencmd", "measure_volts"], stdout=subprocess.PIPE).communicate()[0]
        volts = float(self.__justnumbers.sub('', o.decode('UTF-8')))
        self.report_reading('VideoCore/voltage', volts)

        o = subprocess.Popen(["vcgencmd", "get_throttled"], stdout=subprocess.PIPE).communicate()[0]
        throttled = int(self.__justnumbers.sub('', o.decode('UTF-8')), 16)
        self.report_reading('VideoCore/throttled', throttled)

        o = subprocess.Popen(["rpi3-gpiovirtbuf", "g", "135"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[1]
        low_power = True
        if int(re.findall("Get state of 135 as (\d)", o.decode('UTF-8'))[0]) == 1:
            low_power = False
        self.report_reading('low_power', low_power)
