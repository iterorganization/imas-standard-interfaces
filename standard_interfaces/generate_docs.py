#!/usr/bin/env python3
"""
Generate documentation from JSON schemas.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List


def generate_property_docs(
    properties: Dict[str, Any], required: List[str], level: int = 0
) -> str:
    """Generate documentation for schema properties."""
    if not properties:
        return ""

    docs = []
    indent = "  " * level

    for prop_name, prop_def in properties.items():
        # Property name with required indicator
        is_required = prop_name in required
        req_indicator = " ⭐" if is_required else ""
        docs.append(f"{indent}- **`{prop_name}`**{req_indicator}")

        # Type information
        prop_type = prop_def.get("type", "unknown")
        if prop_type == "array" and "items" in prop_def:
            items_type = prop_def["items"].get("type", "unknown")
            docs.append(f"{indent}  - Type: Array of {items_type}")
        else:
            docs.append(f"{indent}  - Type: {prop_type}")

        # Description
        if "description" in prop_def:
            docs.append(f"{indent}  - Description: {prop_def['description']}")

        # Enum values
        if "enum" in prop_def:
            enum_values = ", ".join(f"`{v}`" for v in prop_def["enum"])
            docs.append(f"{indent}  - Allowed values: {enum_values}")

        # Handle nested objects
        if prop_def.get("type") == "object" and "properties" in prop_def:
            docs.append(f"{indent}  - Properties:")
            nested_required = prop_def.get("required", [])
            docs.append(
                generate_property_docs(
                    prop_def["properties"], nested_required, level + 2
                )
            )

        # Handle arrays with object items
        elif prop_def.get("type") == "array" and isinstance(
            prop_def.get("items"), dict
        ):
            items = prop_def["items"]
            if items.get("type") == "object" and "properties" in items:
                docs.append(f"{indent}  - Array item properties:")
                items_required = items.get("required", [])
                docs.append(
                    generate_property_docs(
                        items["properties"], items_required, level + 2
                    )
                )

    return "\n".join(docs)


def generate_schema_docs(schema_path: Path, output_path: Path) -> None:
    """Generate documentation for a single schema."""
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except Exception as e:
        print(f"Error loading schema {schema_path}: {e}")
        return

    # Extract schema information
    title = schema.get("title", schema_path.stem.replace("-", " ").title())
    description = schema.get("description", f"Schema definition for {title}")
    schema_type = schema.get("type", "object")
    required = schema.get("required", [])

    # Generate markdown content
    content = [
        f"# {title}",
        "",
        f"**Schema File:** `{schema_path.name}`",
        f"**Type:** {schema_type}",
        "",
    ]

    if description:
        content.extend(
            [
                "## Description",
                "",
                description,
                "",
            ]
        )

    # Add schema metadata
    if "$id" in schema:
        content.extend(
            [
                "## Schema Information",
                "",
                f"- **Schema ID:** `{schema['$id']}`",
            ]
        )

    if "$schema" in schema:
        content.append(f"- **JSON Schema Version:** `{schema['$schema']}`")

    content.append("")

    # Generate properties documentation
    if "properties" in schema:
        content.extend(
            [
                "## Properties",
                "",
                "⭐ = Required property",
                "",
                generate_property_docs(schema["properties"], required),
                "",
            ]
        )

    # Add dimensions section if present
    if "properties" in schema and "dimensions" in schema["properties"]:
        dims = schema["properties"]["dimensions"]
        if "properties" in dims:
            content.extend(
                [
                    "## Dimensions",
                    "",
                    "This schema defines the following dimensions:",
                    "",
                ]
            )

            for dim_name, dim_def in dims["properties"].items():
                desc = dim_def.get("description", f"Dimension: {dim_name}")
                content.append(f"- **`{dim_name}`**: {desc}")

            content.append("")

    # Add example if we can generate one
    content.extend(
        [
            "## Example Structure",
            "",
            "```json",
            json.dumps(generate_example(schema), indent=2),
            "```",
            "",
        ]
    )

    # Add raw schema
    content.extend(
        [
            "## Raw Schema",
            "",
            '??? info "View raw JSON schema"',
            "    ```json",
            "    " + json.dumps(schema, indent=4).replace("\n", "\n    "),
            "    ```",
        ]
    )

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
        print(f"Generated documentation: {output_path}")
    except Exception as e:
        print(f"Error processing {schema_path}: {e}")


def generate_example(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a minimal example from schema."""
    if schema.get("type") != "object" or "properties" not in schema:
        return {}

    example = {}
    required = schema.get("required", [])

    for prop_name, prop_def in schema["properties"].items():
        # Only include required properties and some optional ones
        if prop_name in required or len(example) < 3:
            prop_type = prop_def.get("type")

            if prop_type == "string":
                if "enum" in prop_def:
                    example[prop_name] = prop_def["enum"][0]
                else:
                    example[prop_name] = f"example_{prop_name}"
            elif prop_type == "number":
                example[prop_name] = 1.0
            elif prop_type == "integer":
                example[prop_name] = 1
            elif prop_type == "boolean":
                example[prop_name] = True
            elif prop_type == "array":
                if "items" in prop_def:
                    items_type = prop_def["items"].get("type")
                    if items_type == "string":
                        example[prop_name] = ["example"]
                    elif items_type == "number":
                        example[prop_name] = [1.0]
                    else:
                        example[prop_name] = []
                else:
                    example[prop_name] = []
            elif prop_type == "object":
                if "properties" in prop_def:
                    example[prop_name] = generate_example(prop_def)
                else:
                    example[prop_name] = {}

    return example


def generate_schema_index(
    schemas_info: List[Dict[str, Any]], output_path: Path
) -> None:
    """Generate the main schema index page."""
    content = [
        "# Schema Documentation",
        "",
        "This section contains documentation for all available JSON schemas in the standard interfaces project.",
        "",
        "## Available Schemas",
        "",
    ]

    # Group schemas by category
    categories = {}
    for schema_info in schemas_info:
        category = schema_info["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(schema_info)

    for category, schemas in categories.items():
        content.extend(
            [
                f"### {category.replace('_', ' ').title()}",
                "",
            ]
        )

        for schema in schemas:
            content.append(
                f"- **[{schema['title']}]({schema['file']})** - {schema['description']}"
            )

        content.append("")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
        print(f"Generated schema index: {output_path}")
    except Exception as e:
        print(f"Error generating schema index: {e}")


def main():
    """Main function to generate all documentation."""
    project_root = Path(__file__).parent.parent
    schemas_dir = Path(__file__).parent / "schemas"
    docs_dir = project_root / "docs_src" / "schemas"

    if not schemas_dir.exists():
        print(f"Error: Schema directory not found: {schemas_dir}")
        sys.exit(1)

    # Clean output directory
    if docs_dir.exists():
        import shutil

        shutil.rmtree(docs_dir)
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Find all schema files
    schema_files = list(schemas_dir.rglob("*.schema.json"))

    if not schema_files:
        print("No schema files found!")
        return

    schemas_info = []

    # Generate documentation for each schema
    for schema_file in schema_files:
        # Determine category from path
        relative_path = schema_file.relative_to(schemas_dir)
        category = relative_path.parts[0] if len(relative_path.parts) > 1 else "general"

        # Generate output path
        output_file = docs_dir / f"{schema_file.stem.replace('.schema', '')}.md"

        # Generate docs
        generate_schema_docs(schema_file, output_file)

        # Collect schema info for index
        try:
            with open(schema_file, "r", encoding="utf-8") as f:
                schema = json.load(f)

            schemas_info.append(
                {
                    "title": schema.get(
                        "title", schema_file.stem.replace("-", " ").title()
                    ),
                    "description": schema.get("description", "").split(".")[0] + "."
                    if schema.get("description")
                    else f"Schema for {schema_file.stem}",
                    "file": output_file.name,
                    "category": category,
                }
            )
        except Exception as e:
            print(f"Error processing schema info for {schema_file}: {e}")

    # Generate category pages
    categories = {}
    for schema in schemas_info:
        category = schema["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(schema)

    for category, schemas in categories.items():
        category_content = [
            f"# {category.replace('_', ' ').title()} Schemas",
            "",
            f"Documentation for {category.replace('_', ' ')} related schemas.",
            "",
        ]

        for schema in schemas:
            category_content.append(
                f"- **[{schema['title']}]({schema['file']})** - {schema['description']}"
            )

        category_file = docs_dir / f"{category}.md"
        try:
            with open(category_file, "w", encoding="utf-8") as f:
                f.write("\n".join(category_content))
            print(f"Generated category page: {category_file}")
        except Exception as e:
            print(f"Error generating category page {category_file}: {e}")

    # Generate main schema index
    generate_schema_index(schemas_info, docs_dir / "index.md")

    print("\nDocumentation generation complete!")
    print(f"Generated docs for {len(schemas_info)} schemas")
    print(f"Documentation available in: {docs_dir}")


if __name__ == "__main__":
    main()
