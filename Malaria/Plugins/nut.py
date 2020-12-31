from Malaria.Plugins import MalariaPlugin
import subprocess
import re


class NUT(MalariaPlugin):
    __topic__ = "UPS"

    def __init__(self, malaria, **kwargs):
        super(NUT, self).__init__(malaria, **kwargs)
        self.__keyvalue = re.compile(r'(.*?): (.*)')

    def update(self):
        ups_list = subprocess.Popen(["upsc", "-l"], stdout=subprocess.PIPE).communicate()[0]
        ups_list = ups_list.decode("utf-8")
        for ups in ups_list.split('\n'):
            if len(ups) == 0: continue
            o = subprocess.Popen(["upsc", ups], stdout=subprocess.PIPE).communicate()[0]
            o = o.decode("utf-8")
            for line in o.split('\n'):
                if ':' in line:
                    (key, value) = self.__keyvalue.findall(line)[0]
                    key = key.replace('.', '/')
                    key = ups + '/' + key
                    self.report_reading(key, value)
