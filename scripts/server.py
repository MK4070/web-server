from http.server import HTTPServer
import threading
import os
from request_handler import RequestHandler
from utils.config_reader import Config
from utils.logger import common_logger


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
