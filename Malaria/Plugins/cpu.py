from Malaria.Plugins import MalariaPlugin
import psutil


class CPU(MalariaPlugin):
    def __init__(self, malaria, **kwargs):
        super(CPU, self).__init__(malaria, **kwargs)

    def update(self):
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        cpu_frequency = [i._asdict() for i in psutil.cpu_freq(percpu=True)]

        if len(cpu_frequency) < len(cpu_percent):
            filename = "/sys/devices/system/cpu/present"
            with open(filename) as f:
                num_cores = int(f.read().split('-')[1])

            cpu_frequency = []
            for core in range(num_cores + 1):
                filename = "/sys/devices/system/cpu/cpu%d/cpufreq/scaling_cur_freq" % core
                with open(filename) as f:
                    freq = int(f.read())
                    cpu_frequency.append(float(freq))

        t = psutil.sensors_temperatures()
        if 'coretemp' in t.keys():
            for i, x in enumerate(t['coretemp']):
                t['coretemp'][i] = dict(x._asdict()) if t['coretemp'][i].label.startswith('Core') else None

            temperatures = [v for v in t['coretemp'] if v is not None]
        elif 'cpu_thermal' in t.keys():
            temperatures = [t['cpu_thermal'][0].current for x in range(len(cpu_percent))]

        # elif len(temperatures) < range(len(cpu_percent)):
            # Probably other cases where there's half the sensors as num cores
        else:
            temperatures = [-1 for x in range(len(cpu_percent))]

        data = {}

        for core, percent in enumerate(cpu_percent):
            cpu_data = {
                'percent': percent,
                'frequency': cpu_frequency[core],
                'temperature': temperatures[core]
            }
            data['core' + str(core)] = cpu_data

        self.report_data(data)
