"""
Text file loader implementation.

Supports plain text files (.txt, .md, .log, etc.).
"""

from pathlib import Path


class TextFileLoader:
    """
    Loader for plain text files.

    Supports common text file extensions with UTF-8 encoding.
    """

    SUPPORTED_EXTENSIONS = {".txt", ".md", ".log", ".text", ".markdown"}

    def load(self, file_path: str | Path) -> str:
        """
        Load text file content.

        Args:
            file_path: Path to text file.

        Returns:
            File content as string.

        Raises:
            FileNotFoundError: If file doesn't exist.
            RuntimeError: If file cannot be read.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.supports(path):
            raise RuntimeError(
                f"Unsupported file extension: {path.suffix}. "
                f"Supported: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except UnicodeDecodeError as e:
            raise RuntimeError(
                f"Failed to decode file {file_path} as UTF-8: {e}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Failed to read file {file_path}: {e}") from e

    def supports(self, file_path: str | Path) -> bool:
        """
        Check if this loader supports the given file type.

        Args:
            file_path: Path to check.

        Returns:
            True if file extension is in supported list.
        """
        path = Path(file_path)
        return path.suffix.lower() in self.SUPPORTED_EXTENSIONS
