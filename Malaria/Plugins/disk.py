from Malaria.Plugins import MalariaPlugin
import subprocess
import mdstat
import platform
import psutil
import re
import json
import logging


class Disks(MalariaPlugin):
    def __init__(self, malaria, **kwargs):
        super(Disks, self).__init__(malaria, **kwargs)
        self.last_report = {}

    def get_hdd_temp(self, hdd):
        try:
            for line in subprocess.Popen([b'sudo', b'smartctl', b'-a', bytes('/dev/' + hdd, encoding='utf8')], stdout=subprocess.PIPE).stdout.read().split(b'\n'):
                if (b'Temperature_Celsius' in line.split()) or (b'Temperature_Internal' in line.split()):
                    return int(line.split()[9])
        except:
            logging.warning("Couldn't get disk temperature")

    def get_blk_info(self):
        j = subprocess.Popen([b'lsblk', b'-fmJb'], stdout=subprocess.PIPE).stdout.read()
        return json.loads(j)

    def update(self):
        partitions = psutil.disk_partitions(all=False)
        diskusage = {}
        disks = []
        for partition in partitions:
            if 'loop' in partition.device: continue
            diskusage[partition.mountpoint] = psutil.disk_usage(partition.mountpoint)
            if 'md' in partition.device: continue
            disk = partition.device.replace('/dev/', '')
            if platform.uname()[0] == "Darwin":
                disk = re.sub(r's\d+', '', disk)
            else:
                disk = ''.join(i for i in disk if not i.isdigit())
            disks.append(disk)

        try:
            md = mdstat.parse()
            for array in md['devices'].keys():
                for disk in md['devices'][array]['disks'].keys():
                    disks.append(''.join(i for i in disk if not i.isdigit()))
        except:
            md = {}

        disks = list(set(disks))
        disks.sort()
        temperatures = {'/dev/' + k: self.get_hdd_temp(k) for k in disks}

        def collect(devices):
            out = []
            for dev in devices:
                if 'children' in dev.keys():
                    out += collect(dev['children'])
                else:
                    out += [dev]
            return out

        try:
            blk_info = self.get_blk_info()
            devices = collect(blk_info['blockdevices'])
        except:
            devices = []

        try:
            drives = {'/dev/' + dev['name']: dev for dev in blk_info['blockdevices'] if dev['name'] in disks}
        except:
            drives = {}
        for d in drives.keys():
            if d in temperatures.keys():
                drives[d]['temperature'] = temperatures[d]

        devices = {'/dev/' + dev['name']: dev for dev in devices}
        partitions = {partition.device: dev for dev in partitions}

        for d in devices.keys():
            if d in partitions.keys():
                partition_data = partitions[d]._asdict()
                devices[d].update(partition_data)
            if devices[d]['mountpoint'] in diskusage.keys():
                mp = devices[d]['mountpoint']
                u = diskusage[mp]
                devices[d].update(u._asdict())
                ha_topic = '/'.join([
                    self.__class__.__name__,
                    'partitions',
                    d[1:],
                    'percent'
                ])
                self.malaria.register_homeassistant_sensor(
                    ha_topic,
                    None,
                    devices[d]['mountpoint'] + ' used',
                    "%",
                    "float",
                    "mdi:chart-pie"
                )
            devices[d]['size'] = int(devices[d]['size'])


        data = {
            "partitions": devices,
            "drives": drives,
            'mdstat': md
        }
        self.report_data(data)
