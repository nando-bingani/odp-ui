from odp.ui.lib.archive import Archive


class WebsiteArchive(Archive):
    """Read-only archive with its own web interface for data access."""

    def get(self, path: str):
        """Return a redirect to the relevant web page."""
