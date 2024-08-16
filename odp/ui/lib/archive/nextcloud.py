from werkzeug.datastructures import FileStorage

from odp.ui.lib.archive import Archive


class NextcloudArchive(Archive):

    def get(self, path: str):
        """Send the contents of the file at `path` to the client,
        or return a redirect to the relevant Nextcloud folder."""

    def getzip(self, *paths: str):
        """Send a zip file of the directories and files at `paths`
        to the client."""

    def put(self, path: str, file: FileStorage):
        """Store the contents of the incoming `file` at `path`."""

    def putzip(self, path: str, file: FileStorage):
        """Unpack the contents of the incoming `file` into the
        directory at `path`."""
