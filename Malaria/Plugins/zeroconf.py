from Malaria.Plugins import MalariaPlugin
from zeroconf import Zeroconf, ServiceBrowser
import logging 


class ZeroconfMalaria(MalariaPlugin):
    __topic__ = "Network"
    __services = [
        "http",
        "https",
        "ssh",
        "afpovertcp",
        "nfs",
        "smb",
        "ftp",
        "ipp",
        "upnp",
        "htsp",
        "airplay",
        "airplay",
        "device-info",
        "adisk",
        "udisks-ssh",
        "sftp-ssh",
        "workstation",
        "amba-cam",
        "appletv",
        "appletv-itunes",
        "axis-video",
        "babyphone",
        "cctv",
        "daap",
        "cytv",
        "dvbservdsc",
        "kerberos",
        "ntp",
        "rdp",
        "rsync",
        "rtsp",
        "scanner",
        "sip",
        "skype",
        "tivo-hme",
        "tivo-remote",
        "touch-able",
        "touch-remote",
        "eyetvsn",
        "rfb",
        "xbmc-events",
        "xbmc-jsonrpc",
        "roap",
    ]

    def __init__(self, malaria, **kwargs):
        super(ZeroconfMalaria, self).__init__(malaria, **kwargs)
        self.zeroconf = Zeroconf()
        services = ["_" + service + "._tcp.local." for service in ZeroconfMalaria.__services]
        self.browser = ServiceBrowser(self.zeroconf, services, self)

    def remove_service(self, zeroconf, type, name):
        logging.info("Service %s removed" % (name,))

    def update_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            service_data = {
                info.server + '/' + str(info.port): {
                    "type": info.type,
                    "name": info.name,
                    "weight": info.weight,
                    "priority": info.priority,
                    "server": info.server,
                    "properties": info.properties
                }
            }
            self.report_data({
                'advertised_services': service_data
            })

    def add_service(self, zeroconf, type, name):
        logging.info("Service %s added" % (name,))
        info = zeroconf.get_service_info(type, name)
        if info:
            service_data = {
                info.server + '/' + str(info.port): {
                    "type": info.type,
                    "name": info.name,
                    "weight": info.weight,
                    "priority": info.priority,
                    "server": info.server,
                    "properties": info.properties
                }
            }
            self.report_data({
                'advertised_services': service_data
            })
