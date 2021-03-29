from Malaria.Plugins import MalariaPlugin
import subprocess
import re
from nesteddictionary import NestedDict


class NVidia(MalariaPlugin):
    def __init__(self, malaria, **kwargs):
        super(NVidia, self).__init__(malaria, **kwargs)
        self.kv_parse = re.compile('^(\s+)(.*?)\s\s+:\s+(.*)')
        self.h_parse = re.compile('^(\s+)(.*)')

    def update(self):
        sp = subprocess.Popen(['nvidia-smi', '-q'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf8')
        data = self.parse(sp.communicate()[0])
        self.report_data(data)

    def parse(self, smistr):
        lines = smistr.split('\n')
        kv_parse = re.compile('^(\s+)(.*?)\s\s+:\s+(.*)')
        h_parse = re.compile('^(\s+)(.*)')
        accumulator = {}
        path = ['root']
        # Parse the lines shifting the path as we go
        for line in lines:
            line = '    ' + line
            try:
                (i_str, key, value) = kv_parse.findall(line)[0]
                if (len(i_str) / 4) < len(path):
                    path = path[:-1]
                accumulator['/'.join(path) + '/' + key] = value
            except:
                try:
                    (i_str, header) = h_parse.findall(line)[0]
                    if (len(i_str) / 4) < len(path):
                        path = path[:-1]
                    if len(header.strip()) > 0:
                        path.append(header)
                except:
                    continue
        # Convert the paths into a nested dictionary for reporting
        n = NestedDict({'root': {}})
        for k, v in accumulator.items():
            if v == 'N/A': continue
            n.insert(k.split('/'), v)

        return n.unnest()
