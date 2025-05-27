#!/usr/bin/env python3
"""
Build Script for Standard Interfaces Schema Generation

Automatically converts CDL definitions to JSON schemas and validates the output.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List


def run_command(cmd: List[str], cwd: Path = None) -> bool:
    """Run a command and return success status"""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, check=True
        )
        print(f"✓ {' '.join(cmd)}")
        if result.stdout:
            print(f"  {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {' '.join(cmd)}")
        print(f"  Error: {e.stderr.strip()}")
        return False


def main():
    """Main build function"""

    parser = argparse.ArgumentParser(
        description="Build Standard Interfaces schemas from CDL definitions"
    )
    parser.add_argument(
        "--clean", action="store_true", help="Clean generated schemas before building"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate generated schemas"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Get project root directory
    project_root = Path(__file__).parent.parent

    print("🔧 Building Standard Interfaces Schemas")
    print(f"📁 Project root: {project_root}")
    print()

    # Clean if requested
    if args.clean:
        print("🧹 Cleaning generated schemas...")
        schemas_dir = project_root / "schemas"

        # Remove all generated schema files but keep directory structure
        for schema_file in schemas_dir.rglob("*.schema.json"):
            if "base/" not in str(schema_file):  # Don't remove base schemas
                schema_file.unlink()
                if args.verbose:
                    print(f"  Removed: {schema_file}")
        print("✓ Clean complete")
        print()

    # Convert CDL files to JSON schemas
    print("🔄 Converting CDL definitions to JSON schemas...")

    converter_script = project_root / "scripts" / "cdl_to_json_schema.py"
    definitions_dir = project_root / "definitions"
    schemas_dir = project_root / "schemas"

    cmd = [
        sys.executable,
        str(converter_script),
        str(definitions_dir),
        str(schemas_dir),
        "--force",
    ]

    if not run_command(cmd, cwd=project_root):
        print("❌ Schema conversion failed")
        return 1

    print()

    # Validate schemas if requested
    if args.validate:
        print("✅ Validating generated schemas...")

        # Check that all CDL files have corresponding schemas
        cdl_files = list(definitions_dir.rglob("*.cdl"))
        missing_schemas = []

        for cdl_file in cdl_files:
            # Determine expected schema path
            rel_path = cdl_file.relative_to(definitions_dir)
            schema_name = cdl_file.stem.replace("_", "-") + ".schema.json"
            expected_schema = schemas_dir / rel_path.parent / schema_name

            if not expected_schema.exists():
                missing_schemas.append((cdl_file, expected_schema))

        if missing_schemas:
            print("❌ Missing schemas:")
            for cdl_file, schema_file in missing_schemas:
                print(f"  {cdl_file} -> {schema_file}")
            return 1

        print("✓ All CDL files have corresponding schemas")

        # Validate JSON syntax
        import json

        schema_files = list(schemas_dir.rglob("*.schema.json"))
        invalid_schemas = []

        for schema_file in schema_files:
            try:
                with open(schema_file, "r") as f:
                    json.load(f)
                if args.verbose:
                    print(f"  ✓ {schema_file}")
            except json.JSONDecodeError as e:
                invalid_schemas.append((schema_file, str(e)))

        if invalid_schemas:
            print("❌ Invalid JSON schemas:")
            for schema_file, error in invalid_schemas:
                print(f"  {schema_file}: {error}")
            return 1

        print(f"✓ All {len(schema_files)} schemas have valid JSON syntax")
        print()

    # Summary
    print("🎉 Build complete!")

    # Show generated schemas
    schema_files = list(schemas_dir.rglob("*.schema.json"))
    print(f"📊 Generated {len(schema_files)} schemas:")

    for schema_file in sorted(schema_files):
        rel_path = schema_file.relative_to(schemas_dir)
        print(f"  📄 {rel_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
