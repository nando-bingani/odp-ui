from os import PathLike

from werkzeug.datastructures import FileStorage


class Archive:
    """Abstract base class for an archival storage system that
    integrates with upload and download endpoints in a Flask app.

    All paths are relative to the archive url.

    ArchiveError is raised for any operational failure.
    """

    def __init__(self, url: str | PathLike):
        self.url = url

    def get(self, path: str | PathLike):
        """Send the contents of the file at `path` to the client,
        or return a redirect."""
        raise NotImplementedError

    def getzip(self, *paths: str | PathLike):
        """Send a zip file of the directories (recursively) and
        files at `paths` to the client."""
        raise NotImplementedError

    def put(self, path: str | PathLike, file: FileStorage):
        """Store the contents of the incoming `file` at `path`."""
        raise NotImplementedError

    def putzip(self, path: str | PathLike, file: FileStorage):
        """Unpack the contents of the incoming `file` into the
        directory at `path`."""
        raise NotImplementedError


class ArchiveError(Exception):
    pass
