from http.server import HTTPServer
import threading
import os
from request_handler import RequestHandler
from utils.config_reader import Config


def start_server(port):
    with HTTPServer(("", port), RequestHandler) as server:
        print(f"Serving on port {port}")
        server.serve_forever()


def run():
    config = Config.get_config()
    os.chdir(config.get("Server", "servingDirectory"))
    starting_port = config.getint("Server", "startingPort")
    server_count = config.getint("Server", "serverCount")
    ports = [starting_port + i for i in range(server_count)]
    for p in ports:
        thread = threading.Thread(target=start_server, args=(p,))
        thread.daemon = True
        thread.start()
    print("CTRL+C to exit.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nServers stopped.")


if __name__ == "__main__":
    run()
