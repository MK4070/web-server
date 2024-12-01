from http.server import SimpleHTTPRequestHandler, HTTPServer
import requests
import random
import configparser

config = configparser.ConfigParser()
config.read("config.ini")


class ReverseProxyHandler(SimpleHTTPRequestHandler):
    BACKEND_SERVERS = []

    def __init__(self, request, client_address, server, *, directory=None):
        starting_port = config.getint("Server", "startingPort")
        server_count = config.getint("Server", "serverCount")
        self.BACKEND_SERVERS = [
            "http://localhost:" + str(starting_port + i)
            for i in range(server_count)
        ]
        super().__init__(request, client_address, server, directory=directory)

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
    server.serve_forever()


if __name__ == "__main__":
    run()
