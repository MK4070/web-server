from http.server import BaseHTTPRequestHandler, HTTPServer
import os

class ServerException(Exception): pass

class RequestHandler(BaseHTTPRequestHandler):
    '''Handle HTTP requests by returning a fixed 'page'.'''
    Error_page = '''\
    <html>
    <body>
    <h1>Error accessing {path}</h1>
    <p>{msg}</p>
    </body>
    </html>
    '''
    def handle_file(self, full_path):
        """Handles the serving of the requested file."""
        try:
            # bad idea
            # reading the whole file into memory when serving
            with open(full_path, 'rb') as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as msg:
            msg = f"{self.path} cannot be read: {msg}"
            self.handle_error(msg)

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
            full_path = os.getcwd() + self.path
            # doesn't exist
            if not os.path.exists(full_path):
                raise ServerException(f"{self.path} not found.")
            # it's a file
            elif os.path.isfile(full_path):
                self.handle_file(full_path)
            # something we don't handle
            else:
                raise ServerException(f"Unknown object {self.path}")
        except Exception as msg:
            self.handle_error(msg)

if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()