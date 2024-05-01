from http.server import HTTPServer, BaseHTTPRequestHandler

from utils.constants import HOST, PORT
from utils.loggers import app_logger


class LoadBalancer(BaseHTTPRequestHandler):
    def log_message(self, *args) -> None:
        """Overriding the default method to silence unnecessary logs."""
        app_logger.info(f'Recieved request from {self.client_address[0]}: "{self.command} {self.path} {self.request_version}". Agent: {self.headers.get("User-Agent", "Unknown")}.')

    def do_GET(self):
        """To accept request and systematically call external servers."""
        self.send_response(200)
        self.send_header('Content-type', "text/html")
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()


if __name__ == "__main__":
    httpd = HTTPServer((HOST, PORT), LoadBalancer)
    app_logger.info(f"Load balancer started at {PORT}.")
    httpd.serve_forever()
