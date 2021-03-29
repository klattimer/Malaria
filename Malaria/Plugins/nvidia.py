from Malaria.Plugins import MalariaPlugin
import subprocess
import re
from nesteddictionary import NestedDict

units = {
    '%': {
        'display': '%',
        'icon': 'mdi:chip'
    },
    'MiB':  {
        'display': 'MiB',
        'icon': 'mdi:memory'
    },
    'MHz': {
        'display': 'Mhz',
        'icon': 'mdi:speedometer'
    },
    ' C': {
        'display': "\u00b0C",
        'icon': 'mdi:thermometer'
    },
    'KB/s': {
        'display': 'KB/s',
        'icon': 'mdi:speedometer'
    }
}


class NVidia(MalariaPlugin):
    def __init__(self, malaria, **kwargs):
        super(NVidia, self).__init__(malaria, **kwargs)
        self.kv_parse = re.compile('^(\s+)(.*?)\s\s+:\s+(.*)')
        self.h_parse = re.compile('^(\s+)(.*)')

    def update(self):
        sp = subprocess.Popen(['nvidia-smi', '-q'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf8')
        data = self.parse(sp.communicate()[0])
        self.report_data(data, True)

    def parse(self, smistr):
        lines = smistr.split('\n')
        kv_parse = re.compile('^(\s+)(.*?)\s\s+:\s+(.*)')
        h_parse = re.compile('^(\s+)(.*)')
        accumulator = {}
        with_units = {}
        path = [self.__class__.__name__]
        # Parse the lines shifting the path as we go
        for line in lines:
            line = '    ' + line
            try:
                (i_str, key, value) = kv_parse.findall(line)[0]
                if key == 'Process ID':
                    raise Exception('Process ID is a header')
                if (len(i_str) / 4) < len(path):
                    path = path[:-1]
                p = '/'.join(path) + '/' + key

                # Move units into the key name
                for unit, unitspec in units.items():
                    if value.endswith(unit):
                        value = value.replace(unit, '').strip()
                        with_units[key] = {
                            'path': p,
                            'unit': unitspec
                        }
                        key += ' (' + unitspec['display'] + ')'
                accumulator[p] = value
            except:
                try:
                    (i_str, header) = h_parse.findall(line)[0]
                    if (len(i_str) / 4) < len(path):
                        path = path[:-1]

                    if header.startswith('GPU') and path[-1] != 'GPUs':
                        header = 'GPUs/' + header

                    if header.startswith('Process ID') and path[-1] != 'Processes':
                        k, v = header.split(':')
                        header = 'Processes/' + v.strip()

                    if len(header.strip()) > 0:
                        path.append(header)
                except:
                    continue
        # Convert the paths into a nested dictionary for reporting
        n = NestedDict({self.__class__.__name__: {}})
        for k, v in accumulator.items():
            if v == 'N/A': continue
            n.insert(k.split('/'), v)

        data = n.unnest()[self.__class__.__name__]
        for k in with_units.keys():
            self.malaria.register_homeassistant_sensor(
                with_units[k]['path'],
                None,
                k,
                with_units[k]['unit']['display'],
                'float',
                with_units[k]['unit']['icon']
            )
        return data
