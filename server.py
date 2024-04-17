import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
from typing import Dict

from utils.constants import HOST
from utils.loggers import app_logger


class Server(BaseHTTPRequestHandler):
    def __init__(self, *args) -> None:
        with open("data.json", "r") as file:
            self.data: Dict = json.load(file)
        super().__init__(*args)

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
    PORT = int(sys.argv[1])
    httpd = HTTPServer((HOST, PORT), Server)
    app_logger.info(f"Server started at {PORT}.")
    httpd.serve_forever()
