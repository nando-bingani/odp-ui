from os import PathLike
from pathlib import Path
from urllib.parse import urlparse

from werkzeug.datastructures import FileStorage

from odp.ui.lib.archive import Archive, ArchiveError


class FilesystemArchive(Archive):

    def __init__(self, url: str | PathLike):
        super().__init__(url)
        self.dir = Path(urlparse(url).path)

    def get(self, path: str | PathLike):
        """Send the contents of the file at `path` to the client."""

    def put(self, path: str | PathLike, file: FileStorage):
        """Store the contents of the incoming `file` at `path`."""
        try:
            (self.dir / path).parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        except OSError as e:
            raise ArchiveError('Error creating directory: ' + str(e)) from e

        try:
            file.seek(0)
            file.save(self.dir / path)
        except OSError as e:
            raise ArchiveError('Error saving file: ' + str(e)) from e
