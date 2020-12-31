from Malaria.Plugins import MalariaPlugin
import socket
import re


class DNLA(MalariaPlugin):
    __topic__ = "Network"

    def __init__(self, malaria, **kwargs):
        super(DNLA, self).__init__(malaria, **kwargs)
        self.extract_location = re.compile('Location: (.*?)://(.*?):(.*?)/')

    def update(self):
        """
        Create a broadcast socket and listen for LG TVs responding.
        Returns list of IPs unless `first_only` is true, in which case it
        will return the first TV found.
        """
        attempts = 10

        # TODO: Look for other things
        request = 'M-SEARCH * HTTP/1.1\r\n' \
                  'HOST: 239.255.255.250:1900\r\n' \
                  'MAN: "ssdp:discover"\r\n' \
                  'MX: 2\r\n' \
                  'ST: urn:schemas-upnp-org:device:MediaRenderer:1\r\n\r\n'

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)

        discovered = {}
        while attempts > 0:
            sock.sendto(bytes(request, 'utf-8'), ('239.255.255.250', 1900))
            try:
                (response, (address, port)) = sock.recvfrom(512)
                response = response.decode('utf-8')
                try:
                    (location_protocol, location_address, location_port) = self.extract_location.findall(response)[0]
                except:
                    location_address = address
                    location_port = port
                    location_protocol = "unknown"
            except:
                attempts -= 1
                continue
            discovered[str(location_address) + '/' + str(location_port)] = {
                'response': response,
                'protocol': location_protocol,
                'location': location_protocol + '://' + location_address + ':' + str(location_port),
                'remote_address': address,
                'remote_port': port
            }
            attempts -= 1
        self.report_data({
            'dnla_services': discovered
        })
        sock.close()
