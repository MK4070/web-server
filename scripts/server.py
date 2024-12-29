# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os
from utils.config_reader import Config
from utils.logger import common_logger, get_thread_logger
from scripts.handler_cases import Cases


class RequestHandler(BaseHTTPRequestHandler):
    Error_page = """\
    <html>
    <body>
    <h1>Error accessing {path}</h1>
    <p>{msg}</p>
    </body>
    </html>
    """

    def handle_error(self, msg):
        """Handles errors by sending a generic error page."""
        content = self.Error_page.format(path=self.path, msg=msg)
        self.send_content(content.encode(), 404)

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
        logger = get_thread_logger(self.server.name)
        logger.info(log_message)

        common_message = (
            f"({self.server.name} - {self.server.num_requests})"
            f" - {self.client_address[0]}:{self.client_address[1]}"
            f" - [{self.command} {self.path} {self.request_version}]"
            f" - {code} {size}"
        )
        common_logger.info(common_message)


class Server(HTTPServer):
    """
    Server class with custom handler for server specific log.
    """

    def __init__(
        self, name, server_address, RequestHandlerClass, bind_and_activate=True
    ):
        self.name = name
        self.num_requests = 0
        super().__init__(
            server_address, RequestHandlerClass, bind_and_activate
        )

    def process_request(self, request, client_address):
        self.num_requests += 1
        super().process_request(request, client_address)


def start_server(server_name, host, port, thread_name):
    with Server(server_name, ("", port), RequestHandler) as server:
        print(f"Serving on port {port}")
        common_logger.info(
            f"Server starting on {host}:{port} (Thread: {thread_name})"
        )
        server.serve_forever()


def run():
    config = Config.get_config()
    os.chdir(config.get("Server", "servingDirectory"))
    host = config.get("Server", "host")
    starting_port = config.getint("Server", "startingPort")
    server_count = config.getint("Server", "serverCount")

    for i in range(server_count):
        port = starting_port + i
        thread_name = f"T_{i+1}"
        thread = threading.Thread(
            target=start_server,
            args=("S_" + str(port), host, port, thread_name),
            name=thread_name,
        )
        thread.daemon = True
        thread.start()

    print("CTRL+C to exit.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Servers stopped.")


if __name__ == "__main__":
    run()
