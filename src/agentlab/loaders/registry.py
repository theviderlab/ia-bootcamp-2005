"""
Document loader registry.

Manages multiple document loaders and routes files to appropriate loader.
"""

from pathlib import Path
from agentlab.models import DocumentLoader


class DocumentLoaderRegistry:
    """
    Registry for document loaders.

    Maintains a list of loaders and routes files to the appropriate one.
    Makes it easy to add support for new file formats (PDF, HTML, DOCX, etc.).
    """

    def __init__(self):
        """Initialize empty registry."""
        self._loaders: list[DocumentLoader] = []

    def register(self, loader: DocumentLoader) -> None:
        """
        Register a document loader.

        Args:
            loader: Loader instance to register.
        """
        self._loaders.append(loader)

    def get_loader(self, file_path: str | Path) -> DocumentLoader | None:
        """
        Get appropriate loader for a file.

        Args:
            file_path: Path to file.

        Returns:
            Loader that supports the file, or None if no loader found.
        """
        for loader in self._loaders:
            if loader.supports(file_path):
                return loader
        return None

    def load(self, file_path: str | Path) -> str:
        """
        Load document using appropriate loader.

        Args:
            file_path: Path to document.

        Returns:
            Document content as text.

        Raises:
            RuntimeError: If no loader supports the file type.
        """
        loader = self.get_loader(file_path)

        if loader is None:
            path = Path(file_path)
            raise RuntimeError(
                f"No loader found for file type: {path.suffix}. "
                f"Please register a loader for this format."
            )

        return loader.load(file_path)

    def supports(self, file_path: str | Path) -> bool:
        """
        Check if any registered loader supports the file.

        Args:
            file_path: Path to check.

        Returns:
            True if a loader is available for this file type.
        """
        return self.get_loader(file_path) is not None
