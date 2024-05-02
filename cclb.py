import datetime
import gzip
from typing import Dict
from io import BytesIO
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

    def date_time_string(self) -> str:
        """Overriding the default method to set Date headers."""
        current_date_time = datetime.datetime.now()
        formatted_date = current_date_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
        return formatted_date
    
    def version_string(self) -> str:
        """Overriding the default method to set Server headers."""
        return 'CCLoadBalancer/1.0'
    
    def get_compressed_data(self, data) -> bytes:
        """To compress data into GZIP format."""
        compressed_stream = BytesIO()
        with gzip.GzipFile(fileobj=compressed_stream, mode='wb') as gzip_file:
            gzip_file.write(data)
        compressed_data = compressed_stream.getvalue()
        return compressed_data
    
    def do_GET(self):
        """To accept request and systematically call external servers. Health-checks functional."""
        # Choosing server based on health-checks.
        path_splits = self.path.split('/')[1:]
        path = ""
        for unit in path_splits:
            path += f"/{unit}"
        global thread_counter
        server_name = SERVERS[thread_counter % SERVER_COUNT]
        current_server_is_online = server_cluster.servers[server_name]
        while not current_server_is_online:
            thread_counter += 1
            server_name = SERVERS[thread_counter % SERVER_COUNT]
            current_server_is_online = server_cluster.servers[server_name]

        # Polling server cluster.
        response = urllib.request.urlopen(f"http://{server_name}{path}")
        status_code = response.status
        headers = {
            "Content-Disposition": response.getheader('Content-Disposition'),
            "Content-Type": response.getheader('Content-Type'),
            "Cache-Control": response.getheader('Cache-Control'),
            "ETag": response.getheader("ETag")
        }
        data = response.read()
        if status_code == 500:
            self.respond(500, data, headers=headers, is_error=True)
        elif status_code == 404:
            self.respond(500, data, headers=headers, is_error=True)
        elif status_code == 200:
            self.respond(200, data, headers=headers)
        thread_counter += 1

    def respond(self, status_code: int, data, headers: Dict[str, str], is_error: bool=False) -> None:
        """Write response to the client along with sending all headers."""
        data = self.get_compressed_data(data)
        self.send_response(status_code)
        self.send_header('Content-type', headers["Content-Type"])
        self.send_header('Cache-Control', 'no-cache' if not headers["Cache-Control"] else headers["Cache-Control"])
        self.send_header('Connection', 'close')
        self.send_header('Content-Encoding', 'gzip') 
        self.send_header('Content-Length', len(data))
        if headers["Content-Disposition"]:
            self.send_header('Content-Disposition', headers["Content-Disposition"])
        if headers["ETag"]:
            self.send_header('ETag', headers["ETag"])
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
