import threading
import time
from typing import List, Dict
import urllib.request

from utils.loggers import app_logger


class ServerCluster:
    """To act as the cluster of servers."""

    def __init__(self, servers: List[str]) -> None:
        self.servers: Dict[List] = {server: True for server in servers}


class HealthCheck(threading.Thread):
    """Polls servers every ten seconds to see if they are up. If not, their state will be changed."""

    def __init__(self, cluster: ServerCluster):
        super().__init__()
        self.servers = cluster.servers
        self.daemon = True

    def run(self):
        while True:
            for server_name, _ in self.servers.items():
                try:
                    response = urllib.request.urlopen(f"http://{server_name}")
                    if response.status == 200:
                        self.servers[server_name] = True
                    else:
                        raise Exception
                except Exception as e:
                    self.servers[server_name] = False
                    app_logger.warning(f"Health-check failed for server {server_name}. Retrying connection after 10s.")
            time.sleep(10)
