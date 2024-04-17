from http.server import HTTPServer, BaseHTTPRequestHandler

from utils.constants import HOST, PORT
from utils.loggers import app_logger


class Server(BaseHTTPRequestHandler):
    def log_message(self) -> None:
        app_logger.info(f'Recieved request from {self.client_address[0]}: "{self.command} {self.path} {self.request_version}".')

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()


if __name__ == "__main__":
    httpd = HTTPServer((HOST, PORT), Server)
    app_logger.info("Load balancer started.")
    httpd.serve_forever()
    