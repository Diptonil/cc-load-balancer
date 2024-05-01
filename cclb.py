import sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse

from utils.loggers import app_logger, file_logger, error_file_logger
from utils.health_checker import HealthCheck, ServerCluster


SERVERS = ["localhost:7000", "localhost:7001", "localhost:7002"]
SERVER_COUNT = len(SERVERS)
HOST = "localhost"
PORT = 8080
thread_counter = 0
server_cluster = ServerCluster(SERVERS)


class LoadBalancer(BaseHTTPRequestHandler):
    def log_message(self, *args) -> None:
        """Overriding the default method to silence unnecessary logs."""
        app_logger.info(f'Received request from {self.client_address[0]}: "{self.command} {self.path} {self.request_version}". Agent: {self.headers.get("User-Agent", "Unknown")}.')

    def do_GET(self):
        """To accept request and systematically call external servers."""
        path_splits = self.path.split('/')[1:]
        path = ""
        for unit in path_splits:
            path += f"/{unit}"
        global thread_counter
        for server in server_cluster.servers:
            server_name = SERVERS[thread_counter % SERVER_COUNT]
            if server[1] == False:
                thread_counter += 1
            else:
                break
        response = urllib.request.urlopen(f"http://{server_name}{path}")
        status_code = response.status
        data = response.read()
        if status_code == 500:
            self.respond(500, data, is_error=True)
        elif status_code == 404:
            self.respond(500, data, is_error=True)
        elif status_code == 200:
            self.respond(200, data)
        thread_counter += 1

    def respond(self, status_code: int, data, is_error: bool=False) -> None:
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(data)
        app_logger.info(f"Server responded with {status_code} status code.")
        file_logger.info(f"Server responded with {status_code} status code.")
        if is_error:
            error_file_logger.error(f"Server responded with {status_code} status code.")


if __name__ == "__main__":
    health_checker = HealthCheck(server_cluster)
    health_checker.start()
    httpd = ThreadingHTTPServer((HOST, PORT), LoadBalancer)
    app_logger.info(f"Load balancer started at {PORT}.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        app_logger.info(f"Load balancer stopped.")
        sys.exit(0)
