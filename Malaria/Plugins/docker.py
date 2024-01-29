from Malaria.Plugins import MalariaPlugin
import docker


class Docker(MalariaPlugin):
    __topic__ = "Docker/stats"
    
    def __init__(self, malaria, **kwargs):
        super(Docker, self).__init__(malaria, **kwargs)
        self.client = docker.from_env()

    def update(self):
        containers = self.client.containers.list()
        data = {c.name: c.stats(stream=False) for c in containers}
        self.report_data(data)