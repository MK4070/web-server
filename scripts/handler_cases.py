import os
import subprocess
from scripts.exceptions import ServerException


class ParentCase(object):
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


# Case Handlers
class CaseNoFile(ParentCase):
    """File or directory does not exist."""

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException(f"{handler.path} not found")


class CaseExistingFile(ParentCase):
    """File exists."""

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)


class CaseAlwaysFail(ParentCase):
    """Base case."""

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException(f"Unknown object {handler.path}")


class CaseDirectoryIndexFile(ParentCase):
    """Serve index.html page for a directory."""

    def test(self, handler):
        return os.path.isdir(handler.full_path) and os.path.isfile(
            self.index_path(handler)
        )

    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))


class CaseDirectoryNoIndexFile(ParentCase):
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


class CaseCGIFile(ParentCase):
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


Cases = [
    CaseNoFile,
    CaseCGIFile,
    CaseExistingFile,
    CaseDirectoryIndexFile,
    CaseDirectoryNoIndexFile,
    CaseAlwaysFail,
]
