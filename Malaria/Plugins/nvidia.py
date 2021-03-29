from Malaria.Plugins import MalariaPlugin
import subprocess
import re
from nesteddictionary import NestedDict

units = {
    '%': '%',
    'MiB': 'MiB',
    'MHz': 'Mhz',
    ' C': "\u00b0C",
    'KB/s': 'KB/s'
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
        path = ['root']
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
                for unit in units.keys():
                    if value.endswith(unit):
                        key += ' (' + units[unit] + ')'
                        value = value.replace(unit, '').strip()
                        with_units[key] = {
                            'path': p,
                            'unit': units[unit]
                        }
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
        n = NestedDict({'root': {}})
        for k, v in accumulator.items():
            if v == 'N/A': continue
            n.insert(k.split('/'), v)

        data = n.unnest()['root']
        for k in with_units.keys():
            self.malaria.register_homeassistant_sensor(
                with_units[k]['path'],
                None,
                k.replace('(', '').replace(')', ''),
                with_units[k]['unit'],
                'float',
                'mdi:gpu'
            )
        return data
