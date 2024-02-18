from Malaria.Plugins import MalariaPlugin
import docker


class Docker(MalariaPlugin):
    __topic__ = "Docker"

    def __init__(self, malaria, **kwargs):
        super(Docker, self).__init__(malaria, **kwargs)
        self.client = docker.from_env()
        containers = self.client.containers.list(all=True)
        for c in containers:

            ha_topic = '/'.join([
                        self.__topic__,
                        'status',
                        c.name
            ])

            self.malaria.register_homeassistant_sensor(
                ha_topic,
                None,
                f"Container {c.name} status",
                '',
                'string'
            )

    def update(self):
        containers = self.client.containers.list(all=True)
        data = {}
        data['stats'] = {}
        data['status'] = {}
        for c in containers:
            data['stats'][c.name] = c.stats(stream=False)
            data['status'][c.name] = c.status

        self.report_data(data, True)