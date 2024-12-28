import os
from http.server import BaseHTTPRequestHandler
from handler_cases import Cases
from utils.logger import common_logger, get_thread_logger


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
