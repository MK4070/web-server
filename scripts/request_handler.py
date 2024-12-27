import os
from http.server import BaseHTTPRequestHandler
from handler_cases import Cases


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
        log_message = "Response from {}:{}".format(
            self.server.server_address[0],  # Server IP
            self.server.server_address[1],  # Server Port
        )
        print(log_message)
        return super().log_request(code, size)
