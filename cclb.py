from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.request

from utils.loggers import app_logger, file_logger, error_file_logger


SERVERS = ["localhost:7000", "localhost:7001", "localhost:7002", "localhost:7003", "localhost:7004"]
SERVER_COUNT = len(SERVERS)
HOST = "localhost"
PORT = 8080
SERVER_COUNT = 3
thread_counter = 0


class LoadBalancer(BaseHTTPRequestHandler):
    def log_message(self, *args) -> None:
        """Overriding the default method to silence unnecessary logs."""
        app_logger.info(f'Recieved request from {self.client_address[0]}: "{self.command} {self.path} {self.request_version}". Agent: {self.headers.get("User-Agent", "Unknown")}.')

    def do_GET(self):
        """To accept request and systematically call external servers."""
        server = SERVERS[thread_counter % SERVER_COUNT]
        global thread_counter
        thread_counter += 1
        response = urllib.request.urlopen(server)
        status_code = response.status
        data = response.read()

        if status_code == 500:
            self.respond(500, data)
        elif status_code == 404:
            self.respond(500, data)
        elif status_code == 200:
            self.respond(200, data)

    def respond(self, status_code: int, data) -> None:
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(data)
        app_logger.info(f"Server responded with {status_code} status code.")
        file_logger.info(f"Server responded with {status_code} status code.")
        error_file_logger.info(f"Server responded with {status_code} status code.")


if __name__ == "__main__":
    httpd = ThreadingHTTPServer((HOST, PORT), LoadBalancer)
    app_logger.info(f"Load balancer started at {PORT}.")
    httpd.serve_forever()
