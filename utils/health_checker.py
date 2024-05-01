import threading
import time
from typing import List
import urllib.request

from utils.loggers import app_logger, file_logger


class ServerCluster:
    """To act as the cluster of servers."""

    def __init__(self, servers: List[str]) -> None:
        self.servers: List[List] = [[server, True] for server in servers]


class HealthCheck(threading.Thread):
    """Polls servers every ten seconds to see if they are up. If not, their state will be changed."""

    def __init__(self, cluster: ServerCluster):
        super().__init__()
        self.servers = cluster.servers

    def run(self):
        while True:
            for server in self.servers:
                try:
                    response = urllib.request.urlopen(f"http://{server[0]}")
                    if response.status == 200:
                        self.servers[self.servers.index(server)][1] = True
                        file_logger.info(f"Health-check succeeded for server {server[0]}.")
                    else:
                        raise Exception
                except Exception as e:
                    self.servers[self.servers.index(server)][1] = False
                    app_logger.info(f"Health-check failed for server {server[0]}. Retrying connection after 10s.")
                    file_logger.warning(f"Health-check failed for server {server[0]}. Retrying connection after 10s.")
            time.sleep(10)
