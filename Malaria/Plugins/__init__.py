import re


class MalariaPlugin():
    __topic__ = None
    __always_report__ = []

    @classmethod
    def is_available(cls):
        """
        Perform any necessary hardware availability tests
        """
        return False

    def __init__(self, malaria, **kwargs):
        self.malaria = malaria
        self.last_report = {}
        self.patterns = []
        for pattern in self.__always_report__:
            p = re.compile(pattern)
            self.patterns.append(p)

    def update(self):
        """
        Update the readings held internally
        """
        pass

    def flatten(self, dd, separator='/', prefix=''):

        def is_flattenable(d):
            if isinstance(d, dict):
                return True
            if isinstance(d, list):
                return True
            elif getattr(d.__class__, "as_dict", None) is not None:
                return True
            elif getattr(d.__class__, "_asdict", None) is not None:
                return True
            return False

        if isinstance(dd, list):
            dd = dict(zip(range(len(dd)), dd))
            dd = {str(k): v for k, v in dd.items()}

        if getattr(dd.__class__, "as_dict", None) is not None:
            dd = dd.as_dict()
        elif getattr(dd.__class__, "_asdict", None) is not None:
            dd = dd._asdict()

        def tostr(k):
            if type(k) == bytes:
                k = k.decode('utf-8')
            return k

        return {str(prefix) + str(separator) + tostr(k) if prefix else tostr(k): v
                for kk, vv in dd.items()
                for k, v in self.flatten(vv, separator, kk).items()
                } if is_flattenable(dd) else {prefix: dd}

    def report_data(self, data_dictionary, always=False):
        data_dictionary = self.flatten(data_dictionary)
        for k, v in data_dictionary.items():
            do_report = always
            if do_report is False and len(self.patterns) > 0:
                for p in self.patterns:
                    if p.match(k):
                        do_report = True
            if do_report is False and k in self.last_report.keys() and self.last_report[k] == v:
                continue
            self.report_reading(k, v)

        self.last_report = data_dictionary

    def report_reading(self, key, value):
        if self.__topic__ is not None:
            key = '/'.join([self.__topic__, str(key)])
        else:
            key = '/'.join([self.__class__.__name__, str(key)])

        self.malaria.report_reading(key, value)
