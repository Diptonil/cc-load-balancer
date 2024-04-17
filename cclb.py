from http.server import HTTPServer, BaseHTTPRequestHandler


HOST = "localhost"
PORT = 80


class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Send message back to client
        message = "Hello, world!"
        
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return


if __name__ == "__main__":
    httpd = HTTPServer((HOST, PORT), Server)
    httpd.serve_forever()
    