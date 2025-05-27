"""
Utility functions for accessing schema and definition files.

This module provides a centralized way to access schema files and CDL definitions
using importlib.resources, making the package relocatable and properly handling
bundled data files.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from importlib.resources import files, as_file


def _get_data_root(data_type: str):
    """
    Get the root directory for data files (schemas or definitions).

    Args:
        data_type: Either "schemas" or "definitions"

    Returns:
        Path object (development mode) or importlib.resources reference (installed mode)
    """
    # First check if we're in development mode (data in project root)
    package_dir = Path(__file__).parent
    project_root = package_dir.parent
    dev_data_path = project_root / data_type

    if dev_data_path.exists():
        # Development case: return Path object
        return dev_data_path
    else:
        # Installed case: return importlib.resources reference
        try:
            return files("standard_interfaces") / data_type
        except (ModuleNotFoundError, FileNotFoundError):
            raise FileNotFoundError(
                f"{data_type.capitalize()} directory not found in development ({dev_data_path}) or installed package"
            )


def _get_schemas_root():
    """Get the schemas root directory, handling both development and installed cases."""
    return _get_data_root("schemas")


def _get_definitions_root():
    """Get the definitions root directory, handling both development and installed cases."""
    return _get_data_root("definitions")


def _get_data_file_path(data_root, category: str, filename: str) -> Path:
    """
    Get the path to a data file (schema or definition).

    Args:
        data_root: Root directory (Path or importlib.resources reference)
        category: The category subdirectory
        filename: The filename

    Returns:
        Path to the file
    """
    if isinstance(data_root, Path):
        # Development case: direct Path
        return data_root / category / filename
    else:
        # Installed case: importlib.resources with as_file
        resource = data_root / category / filename
        with as_file(resource) as file_path:
            return file_path


def _load_data_file_content(data_root, category: str, filename: str) -> str:
    """
    Load content from a data file (schema or definition).

    Args:
        data_root: Root directory (Path or importlib.resources reference)
        category: The category subdirectory
        filename: The filename

    Returns:
        File content as a string
    """
    if isinstance(data_root, Path):
        # Development case: direct file access
        file_path = data_root / category / filename
        return file_path.read_text()
    else:
        # Installed case: importlib.resources
        resource = data_root / category / filename
        return resource.read_text()


def _list_data_files(
    data_root, file_extension: str, category: Optional[str] = None
) -> List[str]:
    """
    List data files in a directory.

    Args:
        data_root: Root directory (Path or importlib.resources reference)
        file_extension: File extension to filter by (e.g., '.schema.json', '.cdl')
        category: Optional category to filter by. If None, returns all files.

    Returns:
        List of file names
    """
    files = []

    if category:
        # List files in specific category
        category_dir = data_root / category
        if isinstance(data_root, Path):
            if category_dir.is_dir():
                for item in category_dir.iterdir():
                    if item.name.endswith(file_extension):
                        files.append(item.name)
        else:
            # importlib.resources case
            try:
                for item in category_dir.iterdir():
                    if item.name.endswith(file_extension):
                        files.append(item.name)
            except (FileNotFoundError, AttributeError):
                pass
    else:
        # List all files across all categories
        if isinstance(data_root, Path):
            for category_dir in data_root.iterdir():
                if category_dir.is_dir() and not category_dir.name.startswith("__"):
                    for item in category_dir.iterdir():
                        if item.name.endswith(file_extension):
                            files.append(f"{category_dir.name}/{item.name}")
        else:
            # importlib.resources case
            try:
                for category_dir in data_root.iterdir():
                    if not category_dir.name.startswith("__"):
                        try:
                            for item in category_dir.iterdir():
                                if item.name.endswith(file_extension):
                                    files.append(f"{category_dir.name}/{item.name}")
                        except (FileNotFoundError, AttributeError):
                            pass
            except (FileNotFoundError, AttributeError):
                pass

    return sorted(files)


def _list_data_categories(data_root) -> List[str]:
    """
    List data categories (subdirectories).

    Args:
        data_root: Root directory (Path or importlib.resources reference)

    Returns:
        List of category names
    """
    categories = []

    if isinstance(data_root, Path):
        for item in data_root.iterdir():
            if item.is_dir() and not item.name.startswith("__"):
                categories.append(item.name)
    else:
        # importlib.resources case
        try:
            for item in data_root.iterdir():
                if not item.name.startswith("__"):
                    categories.append(item.name)
        except (FileNotFoundError, AttributeError):
            pass

    return sorted(categories)


def get_schema_path(schema_category: str, schema_name: str) -> Path:
    """
    Get the path to a schema file.

    Args:
        schema_category: The schema category (e.g., 'base', 'pf_active', 'tf_active')
        schema_name: The schema file name (with or without .schema.json extension)

    Returns:
        Path to the schema file
    """
    if not schema_name.endswith(".schema.json"):
        schema_name += ".schema.json"

    schemas_root = _get_schemas_root()
    return _get_data_file_path(schemas_root, schema_category, schema_name)


def load_schema(schema_category: str, schema_name: str) -> Dict[str, Any]:
    """
    Load a JSON schema file.

    Args:
        schema_category: The schema category (e.g., 'base', 'pf_active', 'tf_active')
        schema_name: The schema file name (with or without .schema.json extension)

    Returns:
        Parsed JSON schema as a dictionary
    """
    if not schema_name.endswith(".schema.json"):
        schema_name += ".schema.json"

    schemas_root = _get_schemas_root()
    content = _load_data_file_content(schemas_root, schema_category, schema_name)
    return json.loads(content)


def get_definition_path(definition_category: str, definition_name: str) -> Path:
    """
    Get the path to a CDL definition file.

    Args:
        definition_category: The definition category (e.g., 'pf_active', 'tf_active')
        definition_name: The definition file name (with or without .cdl extension)

    Returns:
        Path to the definition file
    """
    if not definition_name.endswith(".cdl"):
        definition_name += ".cdl"

    definitions_root = _get_definitions_root()
    return _get_data_file_path(definitions_root, definition_category, definition_name)


def load_definition(definition_category: str, definition_name: str) -> str:
    """
    Load a CDL definition file.

    Args:
        definition_category: The definition category (e.g., 'pf_active', 'tf_active')
        definition_name: The definition file name (with or without .cdl extension)

    Returns:
        CDL file content as a string
    """
    if not definition_name.endswith(".cdl"):
        definition_name += ".cdl"

    definitions_root = _get_definitions_root()
    return _load_data_file_content(
        definitions_root, definition_category, definition_name
    )


def list_schemas(schema_category: Optional[str] = None) -> List[str]:
    """
    List available schema files.

    Args:
        schema_category: Optional category to filter by. If None, returns all schemas.

    Returns:
        List of schema file names
    """
    schemas_root = _get_schemas_root()
    return _list_data_files(schemas_root, ".schema.json", schema_category)


def list_definitions(definition_category: Optional[str] = None) -> List[str]:
    """
    List available CDL definition files.

    Args:
        definition_category: Optional category to filter by. If None, returns all definitions.

    Returns:
        List of definition file names
    """
    definitions_root = _get_definitions_root()
    return _list_data_files(definitions_root, ".cdl", definition_category)


def get_schema_categories() -> List[str]:
    """
    Get list of available schema categories.

    Returns:
        List of schema category names
    """
    schemas_root = _get_schemas_root()
    return _list_data_categories(schemas_root)


def get_definition_categories() -> List[str]:
    """
    Get list of available definition categories.

    Returns:
        List of definition category names
    """
    definitions_root = _get_definitions_root()
    return _list_data_categories(definitions_root)
