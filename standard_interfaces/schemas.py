"""Schemas resource management for Standard Interfaces."""

from typing import Final, Literal

from standard_interfaces.resources import Resource


class Schemas(Resource):
    """Manage Standard Interface JSON schema files."""

    RESOURCE_TYPE: Final[Literal["schemas"]] = "schemas"
    FILE_EXTENSION: Final[Literal[".schema.json"]] = ".schema.json"

    @property
    def resource_type(self) -> Literal["schemas"]:
        """Return the type of resource."""
        return self.RESOURCE_TYPE

    @property
    def file_extension(self) -> Literal[".schema.json"]:
        """Return the file extension for this resource type."""
        return self.FILE_EXTENSION
