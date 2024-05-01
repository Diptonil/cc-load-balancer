import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
from typing import Dict, List, Union

from utils.constants import HOST
from utils.loggers import app_logger


Data = Dict[str, List[Dict[str, Union[str, int, float]]]]


class Server(BaseHTTPRequestHandler):
    def __init__(self, *args) -> None:
        with open("data.json", "r") as file:
            self.data: Data = json.load(file)
        super().__init__(*args)

    def log_message(self, *args) -> None:
        """Overriding the default method to silence unnecessary logs."""
        app_logger.info(f'Recieved request from {self.client_address[0]}: "{self.command} {self.path} {self.request_version}". Agent: {self.headers.get("User-Agent", "Unknown")}.')

    def do_GET(self):
        """To accept request and systematically call corresponding methods to execute the operations."""
        path = self.path.split('/')
        if len(path) < 2 or path[1] == '':
            self.respond({"response": True}, "Trial")
        elif path[1] == 'user':
            self.user_response(path)
        elif path[1] == 'product':
            self.product_response(path)
        elif path[1] == 'users':
            self.users_response()
        elif path[1] == 'products':
            self.products_response()
        else:
            self.error_response()

    def product_response(self, path: List[str]) -> None:
        """Querying a certain product."""
        result_set = self.data["products"]
        for item in result_set:
            if item.get('id') == int(path[2]):
                self.respond(item, "Product")
                return
        self.not_found_response()

    def user_response(self, path: List[str]) -> None:
        """Querying a certain user."""
        result_set = self.data["users"]
        for item in result_set:
            print(type(item['id']), type(path[2]))
            if item.get('id') == int(path[2]):
                self.respond(item, "User")
                return
        self.not_found_response()

    def products_response(self) -> None:
        """Querying all products."""
        result_set = self.data["products"]
        self.respond(result_set, "Product")

    def users_response(self) -> None:
        """Querying all users."""
        result_set = self.data["users"]
        self.respond(result_set, "User")

    def error_response(self) -> None:
        """For all general server errors and faults."""
        self.send_response(500)
        self.send_header('Content-type', "text/html")
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(b"Bad request")
        app_logger.info("Unsupported request recieved. Server has no implementation for the same.")

    def not_found_response(self) -> None:
        """For all general errors in which data is not found."""
        self.send_response(404)
        self.send_header('Content-type', "text/html")
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(b"Requested data not found.")
        app_logger.info("Requested data not found.")

    def respond(self, item: Dict, log: str) -> None:
        """For all general JSON responses."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(item).encode('utf-8'))
        app_logger.info(f"{log} data sent.")


if __name__ == "__main__":
    PORT = int(sys.argv[1])
    httpd = HTTPServer((HOST, PORT), Server)
    app_logger.info(f"Server started at {PORT}.")
    httpd.serve_forever()
