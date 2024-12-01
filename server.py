from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import subprocess
import configparser
import threading

# import sys

config = configparser.ConfigParser()
config.read("config.ini")


class ServerException(Exception):
    pass


class base_class(object):
    """Parent for case handlers."""

    def handle_file(self, handler, full_path):
        """Handles the serving of the requested file."""
        try:
            # bad idea
            # reading the whole file into memory when serving
            with open(full_path, "rb") as reader:
                content = reader.read()
            handler.send_content(content)
        except IOError as msg:
            msg = f"{full_path} cannot be read: {msg}"
            handler.handle_error(msg)

    def index_path(self, handler):
        return os.path.join(handler.full_path, "index.html")

    def test(self, handler):
        assert False, "Not implemented."

    def act(self, handler):
        assert False, "Not implemented."


class case_no_file(base_class):
    """File or directory does not exist."""

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException(f"{handler.path} not found")


class case_existing_file(base_class):
    """File exists."""

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)


class case_always_fail(base_class):
    """Base case."""

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException(f"Unknown object {handler.path}")


class case_directory_index_file(base_class):
    """Serve index.html page for a directory."""

    def test(self, handler):
        return os.path.isdir(handler.full_path) and os.path.isfile(
            self.index_path(handler)
        )

    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))


class case_directory_no_index_file(base_class):
    """Serve listing for a directory without an index.html page."""

    Listing_Page = """\
    <html>
    <body>
    <h2>Accessing {0}</h2>
    <ul>{1}</ul>
    </body>
    </html>
    """

    def list_dir(self, handler):
        try:
            entries = os.listdir(handler.full_path)
            bullets = [
                f"<li>{e}</li>" for e in entries if not e.startswith(".")
            ]
            page = self.Listing_Page.format(handler.path, "\n".join(bullets))
            handler.send_content(page.encode())
        except OSError as msg:
            msg = f"{handler.path} cannot be listed. {msg}"
            handler.handle_error(msg)

    def test(self, handler):
        return os.path.isdir(handler.full_path) and not os.path.isfile(
            self.index_path(handler)
        )

    def act(self, handler):
        self.list_dir(handler)


class case_cgi_file(base_class):
    """Something runnable."""

    def run_cgi(self, handler):
        cmd = ["python", handler.full_path]

        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as proc:
            data, errors = proc.communicate()

        if errors:
            handler.handle_error(errors)
            return

        handler.send_content(data)

    def test(self, handler):
        # if filepath endswith .py? if so, run this
        return os.path.isfile(
            handler.full_path
        ) and handler.full_path.endswith(".py")

    def act(self, handler):
        self.run_cgi(handler)


class RequestHandler(BaseHTTPRequestHandler):
    Cases = [
        case_no_file,
        case_cgi_file,
        case_existing_file,
        case_directory_index_file,
        case_directory_no_index_file,
        case_always_fail,
    ]

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

            for case in self.Cases:
                handler = case()
                if handler.test(self):
                    handler.act(self)
                    break

        except Exception as msg:
            self.handle_error(msg)


def start_server(port):
    with HTTPServer(("", port), RequestHandler) as server:
        print(f"Serving on port {port}")
        server.serve_forever()


def run():
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
