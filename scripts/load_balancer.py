from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import random
from utils.config_reader import Config

config = Config.get_config()


class ReverseProxyHandler(BaseHTTPRequestHandler):
    BACKEND_SERVERS = []

    def __init__(self, request, client_address, server, **kwargs):
        starting_port = config.getint("Server", "startingPort")
        server_count = config.getint("Server", "serverCount")
        host = config.get("Server", "host")
        self.BACKEND_SERVERS = [
            "http://" + host + ":" + str(starting_port + i)
            for i in range(server_count)
        ]
        super().__init__(request, client_address, server, **kwargs)

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


def run():
    port = config.getint("LB", "port")
    server = HTTPServer(("", port), ReverseProxyHandler)
    print(f"Serving on port {port}")
    print("CTRL+C to exit.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")


if __name__ == "__main__":
    run()
