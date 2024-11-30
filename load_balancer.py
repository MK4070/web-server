from http.server import SimpleHTTPRequestHandler, HTTPServer
import requests
import random


class ReverseProxyHandler(SimpleHTTPRequestHandler):
    BACKEND_SERVERS = [
        "http://localhost:8081",
        "http://localhost:8082",
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


if __name__ == "__main__":
    serverAddress = ("", 8080)
    server = HTTPServer(serverAddress, ReverseProxyHandler)
    server.serve_forever()
