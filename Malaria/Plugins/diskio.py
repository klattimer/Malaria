from Malaria.Plugins import MalariaPlugin
import psutil
import logging


class DiskIO(MalariaPlugin):
    __topic__ = "Disks"

    def __init__(self, malaria, **kwargs):
        super(DiskIO, self).__init__(malaria, **kwargs)

    def resolve_partition(self, partition):
        device = partition.device.replace('/dev/', '')
        if device == 'root':
            with open('/proc/cmdline') as cmdline:
                cmdline_text = cmdline.read()

            cmdline_args = {}
            for arg in cmdline_text.split(' '):
                try:
                    (k, v) = arg.split('=')
                except:
                    pass
                cmdline_args[k] = v
            try:
                device = cmdline_args['root']
                device = device.replace('/dev/', '')
            except:
                pass
        return device

    def update(self):
        partitions = psutil.disk_partitions(all=False)
        try:
            diskrw = psutil.disk_io_counters(perdisk=True)
        except:
            diskrw = {}

        diskrw_data = {
            "read_bytes": 0,
            "write_bytes": 0,
        }

        io_disks = [self.resolve_partition(p) for p in partitions if 'loop' not in p.device]

        try:
            diskrw = {k: diskrw[k] for k in io_disks if k in diskrw.keys()}

            for k in diskrw.keys():
                diskrw_data['read_bytes'] += diskrw[k].read_bytes
                diskrw_data['write_bytes'] += diskrw[k].write_bytes
        except:
            logging.exception("Disk IO issue")

        data = {
            "io": diskrw,
            "total_io": diskrw_data
        }
        self.report_data(data)
