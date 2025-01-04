__all__ = ["Server", "RequestHandler", "ReverseProxyHandler"]


from http.server import BaseHTTPRequestHandler
import os
import random
import requests
import socketserver
from scripts.handler_cases import Cases
from utils.logger import common_logger, get_server_logger


Error_page = """\
<!DOCTYPE HTML>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Error Response</title>
    </head>
    <body>
        <h1>Error accessing {path}</h1>
        <p>Error code: {code}</p>
        <p>Message: {msg}</p>
    </body>
</html>
"""


class ReverseProxyHandler(BaseHTTPRequestHandler):

    def __init__(self, *args, custom_param=None, **kwargs):
        self._setup(*custom_param)
        super().__init__(*args, **kwargs)

    def _setup(self, host, starting_port, server_count):
        self.BACKEND_SERVERS = [
            "http://" + host + ":" + str(starting_port + i)
            for i in range(server_count)
        ]

    def do_GET(self):
        backend_url = self.select_backend_server()

        url = backend_url + self.path

        # Forward the request to the selected backend server
        try:
            with requests.get(url) as response:
                # Copy the response from the backend server
                code = response.status_code
                self.log_request(code)
                self.send_response_only(code)
                for key, value in response.headers.items():
                    self.send_header(key, value)
                self.end_headers()

                # Write the response body to the client
                self.wfile.write(response.content)
        except Exception as e:
            self.send_error(502, f"Bad Gateway: {str(e)}")

    def select_backend_server(self):
        # select server randomly
        return random.choice(self.BACKEND_SERVERS)


class RequestHandler(BaseHTTPRequestHandler):

    def handle_error(self, msg):
        """Handles errors by sending a generic error page."""
        content = Error_page.format(path=self.path, code=404, msg=msg)
        log_message = (
            f"Request from "
            f"{self.client_address[0]}:{self.client_address[1]}"
            f" - [{self.command} {self.path} {self.request_version}]"
            f" - {msg}"
        )
        logger = self.server._get_logger()
        logger.error(log_message)
        self.send_error(content.encode())

    def send_error(self, content, status=404):
        self.send_response(status)
        self.send_header("Connection", "close")
        self.send_header("Content-type", self.error_content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    # Handle a GET request.
    def do_GET(self):
        try:
            self.full_path = os.getcwd() + self.path

            for case in Cases:
                handler = case()
                if handler.test(self):
                    handler.act(self)
                    break

        except Exception as msg:
            self.handle_error(msg)

    def log_request(self, code="-", size="-"):
        log_message = (
            f"Request from "
            f"{self.client_address[0]}:{self.client_address[1]}"
            f" - [{self.command} {self.path} {self.request_version}]"
            f" - {code} {size}"
        )
        logger = self.server._get_logger()
        logger.info(log_message)

        common_message = (
            f"({self.server.server_name} - {self.server.num_requests})"
            f" - {self.client_address[0]}:{self.client_address[1]}"
            f" - [{self.command} {self.path} {self.request_version}]"
            f" - {code} {size}"
        )
        common_logger.info(common_message)


class Server(socketserver.TCPServer):
    """
    Server class with custom handler for server specific log.
    """

    def __init__(self, server_address, *args, **kwargs):
        self.server_host, self.server_port = server_address[:2]
        self.server_name = f"S_{self.server_port}"
        self.num_requests = 0
        self.logger = get_server_logger(self.server_name)
        super().__init__(server_address, *args, **kwargs)

    def _get_logger(self):
        return self.logger

    def process_request(self, request, client_address):
        self.num_requests += 1
        super().process_request(request, client_address)
