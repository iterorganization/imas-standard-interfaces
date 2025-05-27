#!/usr/bin/env python3
"""
Generate documentation from JSON schemas using json-schema-for-humans.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from json_schema_for_humans.generate import generate_from_filename
    from json_schema_for_humans.generation_configuration import GenerationConfiguration
except ImportError:
    print("json-schema-for-humans is not installed. Installing with uv...")
    subprocess.check_call(["uv", "add", "--group", "docs", "json-schema-for-humans"])
    print("Please run this script again after installation.")
    sys.exit(1)


def clean_docs_directory(docs_dir: Path) -> None:
    """Clean the documentation directory of old generated files."""
    print(f"Cleaning documentation directory: {docs_dir}")

    # Remove entire docs/schemas directory if it exists
    if docs_dir.exists():
        shutil.rmtree(docs_dir)
        print(f"Removed existing directory: {docs_dir}")

    # Create fresh directory
    docs_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created clean directory: {docs_dir}")


def clean_mkdocs_artifacts(project_root: Path) -> None:
    """Clean MkDocs build artifacts."""
    site_dir = project_root / "site"
    mkdocs_cache = project_root / ".mkdocs_cache"

    for artifact_dir in [site_dir, mkdocs_cache]:
        if artifact_dir.exists():
            print(f"Cleaning MkDocs artifact: {artifact_dir}")
            shutil.rmtree(artifact_dir)

    # Clean any legacy docs_src directory
    docs_src = project_root / "docs_src"
    if docs_src.exists():
        print(f"Removing legacy directory: {docs_src}")
        shutil.rmtree(docs_src)


def generate_schema_docs_with_jsfh(
    schema_path: Path, output_dir: Path
) -> Optional[Path]:
    """Generate documentation for a single schema using json-schema-for-humans."""
    try:
        # Configure the generation
        config = GenerationConfiguration(
            copy_css=True,
            copy_js=True,
            expand_buttons=True,
            show_breadcrumbs=True,
            collapse_long_descriptions=False,
            collapse_long_examples=False,
            link_to_reused_ref=True,
            recursive_detection_depth=25,
            deprecated_from_description=True,
            default_from_description=True,
            examples_as_yaml=False,
            show_toc=True,
        )

        # Generate the HTML documentation
        output_file = output_dir / f"{schema_path.stem.replace('.schema', '')}.html"
        generate_from_filename(schema_path, output_file, config=config)

        print(f"Generated documentation: {output_file}")
        return output_file

    except Exception as e:
        print(f"Error processing {schema_path}: {e}")
        return None


def create_markdown_wrapper(
    html_file: Path, schema_info: Dict[str, Any]
) -> Optional[Path]:
    """Create a markdown file that embeds the HTML documentation."""
    md_file = html_file.with_suffix(".md")

    # Read the generated HTML
    try:
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()
    except Exception as e:
        print(f"Error reading HTML file {html_file}: {e}")
        return None

    # Create markdown content with embedded HTML
    content = [
        f"# {schema_info['title']}",
        "",
        f"**Schema File:** `{schema_info['schema_file']}`",
        "",
        f"{schema_info['description']}",
        "",
        "## Schema Documentation",
        "",
        "The following documentation is automatically generated from the JSON schema:",
        "",
        '<div class="json-schema-docs">',
        html_content,
        "</div>",
        "",
        f"**Raw Schema:** [View {schema_info['schema_file']}](../../schemas/{schema_info['relative_path']})",
    ]

    try:
        with open(md_file, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
        print(f"Created markdown wrapper: {md_file}")
        return md_file
    except Exception as e:
        print(f"Error creating markdown wrapper for {html_file}: {e}")
        return None


def generate_schema_index(
    schemas_info: List[Dict[str, Any]], output_path: Path
) -> None:
    """Generate the main schema index page."""
    content = [
        "# Schema Documentation",
        "",
        "This section contains documentation for all available JSON schemas in the standard interfaces project.",
        "",
        "The documentation is automatically generated using [json-schema-for-humans](https://github.com/coveooss/json-schema-for-humans).",
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
                f"- **[{schema['title']}]({schema['doc_file']})** - {schema['description']}"
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
    schemas_dir = project_root / "schemas"
    docs_dir = project_root / "docs" / "schemas"

    print("Starting documentation generation with json-schema-for-humans...")
    print(f"Project root: {project_root}")
    print(f"Schemas directory: {schemas_dir}")
    print(f"Output directory: {docs_dir}")

    if not schemas_dir.exists():
        print(f"Error: Schema directory not found: {schemas_dir}")
        sys.exit(1)

    # Clean all documentation artifacts
    clean_mkdocs_artifacts(project_root)
    clean_docs_directory(docs_dir)

    # Find all schema files
    schema_files = list(schemas_dir.rglob("*.schema.json"))

    if not schema_files:
        print("No schema files found!")
        return

    print(f"Found {len(schema_files)} schema files")
    schemas_info = []

    # Generate documentation for each schema
    for schema_file in schema_files:
        print(f"Processing: {schema_file.name}")

        # Determine category from path
        relative_path = schema_file.relative_to(schemas_dir)
        category = relative_path.parts[0] if len(relative_path.parts) > 1 else "general"

        # Load schema to get metadata
        try:
            with open(schema_file, "r", encoding="utf-8") as f:
                schema = json.load(f)
        except Exception as e:
            print(f"Error loading schema {schema_file}: {e}")
            continue

        # Generate HTML docs with json-schema-for-humans
        html_file = generate_schema_docs_with_jsfh(schema_file, docs_dir)
        if not html_file:
            continue

        # Prepare schema info
        schema_info = {
            "title": schema.get("title", schema_file.stem.replace("-", " ").title()),
            "description": schema.get(
                "description", f"Schema for {schema_file.stem}"
            ).split(".")[0]
            + "."
            if schema.get("description")
            else f"Schema for {schema_file.stem}",
            "schema_file": schema_file.name,
            "relative_path": str(relative_path),
            "category": category,
        }

        # Create markdown wrapper
        md_file = create_markdown_wrapper(html_file, schema_info)
        if md_file:
            schema_info["doc_file"] = md_file.name
            schemas_info.append(schema_info)

    # Generate category pages
    print("Generating category pages...")
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
                f"- **[{schema['title']}]({schema['doc_file']})** - {schema['description']}"
            )

        category_file = docs_dir / f"{category}.md"
        try:
            with open(category_file, "w", encoding="utf-8") as f:
                f.write("\n".join(category_content))
            print(f"Generated category page: {category_file}")
        except Exception as e:
            print(f"Error generating category page {category_file}: {e}")

    # Generate main schema index
    print("Generating main schema index...")
    generate_schema_index(schemas_info, docs_dir / "index.md")

    print("\n" + "=" * 50)
    print("Documentation generation complete!")
    print(f"Generated docs for {len(schemas_info)} schemas")
    print(f"Generated {len(categories)} category pages")
    print(f"Documentation available in: {docs_dir}")
    print("Documentation generated using json-schema-for-humans")
    print("=" * 50)


if __name__ == "__main__":
    main()
