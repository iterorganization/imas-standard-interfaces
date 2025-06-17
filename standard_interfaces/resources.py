import abc
from typing import Final, Literal
import importlib.resources
import importlib.resources.abc
import pathlib
import shlex


ResourceTypeT = Literal["definitions", "schemas"]
FileExtensionT = Literal[".cdl", ".schema.json"]

RESOURCE_EXTENSIONS: Final[dict[ResourceTypeT, FileExtensionT]] = {
    "definitions": ".cdl",
    "schemas": ".schema.json",
}


class Resource(abc.ABC):
    """Locate project resources."""

    path: pathlib.Path

    def __init__(self):
        """Define resource path."""
        self.path = self._get_path()

    def _get_path(self) -> pathlib.Path:
        """Set the path to the resource directory."""
        filesystem_path = pathlib.Path(__file__).parents[1] / self.resource_type

        if filesystem_path.exists():
            # Development case: return Path object
            return filesystem_path
        else:
            # Installed case: return importlib.resources reference
            resource_path = importlib.resources.files("standard_interfaces.resources")
            assert isinstance(resource_path, pathlib.Path), "must be a Path instance"
            return resource_path / self.resource_type

    @property
    @abc.abstractmethod
    def resource_type(self) -> ResourceTypeT:
        """Return the type of resource."""
        pass

    @property
    def file_extension(self) -> FileExtensionT:
        """Return the file extension for this resource type."""
        return RESOURCE_EXTENSIONS[self.resource_type]

    def get_file(self, category: str, filename: str) -> str:
        """
        Return quoted full path to a data file (schema or definition).

        Args:
            category: The category subdirectory
            filename: The filename

        Returns:
            Path to the file
        """
        if not filename.endswith(self.file_extension):
            filename += self.file_extension
        return (self.path / category / filename).as_posix()

    def categories(self) -> list[str]:
        """
        Return a list of categories available in the resource.

        Returns:
            List of category names
        """
        return [
            str(category.name) for category in self.path.iterdir() if category.is_dir()
        ]

    def files(self) -> dict[str, list[str]]:
        """
        Return a dictionary of categories and their files.

        Returns:
            Dictionary with category names as keys and lists of file names as values
        """
        return {
            str(category.name): [
                str(file.name) for file in category.iterdir() if file.is_file()
            ]
            for category in self.path.iterdir()
            if category.is_dir()
        }
