from http.server import BaseHTTPRequestHandler, HTTPServer
import os

class ServerException(Exception): pass

class case_no_file(object):
    '''File or directory does not exist.'''

    def test(self, handler):
        return not os.path.exists(handler.full_path)
    
    def act(self, handler):
        raise ServerException(f"{handler.path} not found")

class case_existing_file(object):
    '''File exists.'''

    def test(self, handler):
        return os.path.isfile(handler.full_path)
    
    def act(self, handler):
        handler.handle_file(handler.full_path)

class case_always_fail(object):
    '''Base case.'''

    def test(self, handler):
        return True
    
    def act(self, handler):
        raise ServerException(f"Unknown object {handler.path}")

class case_directory_index_file(object):
    '''Serve index.html page for a directory.'''

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))
    
    def act(self, handler):
        handler.handle_file(self.index_path(handler))

class case_directory_no_index_file(object):
    '''Serve listing for a directory without an index.html page.'''

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               not os.path.isfile(self.index_path(handler))
    
    def act(self, handler):
        handler.list_dir(handler.full_path)

class RequestHandler(BaseHTTPRequestHandler):
    '''
    If the requested path maps to a file, that file is served.
    If anything goes wrong, an error page is constructed.
    '''

    Cases = [case_no_file, 
             case_existing_file,
             case_directory_index_file,
             case_directory_no_index_file,
             case_always_fail,
            ]

    Error_page = '''\
    <html>
    <body>
    <h1>Error accessing {path}</h1>
    <p>{msg}</p>
    </body>
    </html>
    '''

    Listing_Page = '''\
    <html>
    <body>
    <h2>Accessing {0}</h2>
    <ul>{1}</ul>
    </body>
    </html>
    '''

    def list_dir(self, full_path):
        try:
            entries = os.listdir(full_path)
            bullets = [f"<li>{e}</li>" for e in entries if not e.startswith('.')]
            page = self.Listing_Page.format(self.path, '\n'.join(bullets))
            self.send_content(page.encode())
        except OSError as msg:
            msg = f"{self.path} cannot be listed. {msg}"
            self.handle_error(msg)

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
            self.full_path = os.getcwd() + self.path
            
            for case in self.Cases:
                handler = case()
                if handler.test(self):
                    handler.act(self)
                    break

        except Exception as msg:
            self.handle_error(msg)

if __name__ == '__main__':
    serverAddress = ('', 8080)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()