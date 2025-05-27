#!/usr/bin/env python3
"""
CDL to JSON Schema Converter

Converts NetCDF CDL (Common Data Language) files to JSON Schema format
for validation of scientific data structures following CF conventions.

This script is designed specifically for the Standard Interfaces project,
which standardizes schemas for tokamak/fusion data structures.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CDLVariable:
    """Represents a NetCDF variable definition from CDL"""

    name: str
    data_type: str
    dimensions: List[str]
    attributes: Dict[str, Any]


@dataclass
class CDLDimension:
    """Represents a NetCDF dimension definition from CDL"""

    name: str
    size: Optional[int]  # None for unlimited dimensions marked with _


class CDLParser:
    """Parser for NetCDF CDL files"""

    def __init__(self):
        self.global_attributes = {}
        self.dimensions = {}
        self.variables = {}

    def parse_cdl_file(self, cdl_path: Path) -> Dict[str, Any]:
        """Parse a CDL file and extract structure information"""

        with open(cdl_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove comments
        content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)

        # Parse sections
        self._parse_global_attributes(content)
        self._parse_dimensions(content)
        self._parse_variables(content)

        return {
            "global_attributes": self.global_attributes,
            "dimensions": self.dimensions,
            "variables": self.variables,
            "source_file": str(cdl_path),
        }

    def _parse_global_attributes(self, content: str):
        """Extract global attributes from CDL content"""
        # Look for global attributes at the start (before dimensions)
        attr_pattern = r'^\s*:(\w+)\s*=\s*"([^"]*)"'

        for match in re.finditer(attr_pattern, content, re.MULTILINE):
            attr_name = match.group(1)
            attr_value = match.group(2)
            self.global_attributes[attr_name] = attr_value

    def _parse_dimensions(self, content: str):
        """Extract dimension definitions from CDL content"""
        # Find dimensions section
        dim_match = re.search(
            r"dimensions:\s*\n(.*?)(?=variables:|$)", content, re.DOTALL
        )
        if not dim_match:
            return

        dim_content = dim_match.group(1)

        # Parse individual dimension lines
        dim_pattern = r"(\w+)\s*=\s*([_\d]+|\d+)"

        for match in re.finditer(dim_pattern, dim_content):
            dim_name = match.group(1)
            dim_size_str = match.group(2).strip()

            # Handle template placeholders
            if dim_size_str == "_":
                dim_size = None  # Unlimited/placeholder
            else:
                try:
                    dim_size = int(dim_size_str)
                except ValueError:
                    dim_size = None

            self.dimensions[dim_name] = CDLDimension(dim_name, dim_size)

    def _parse_variables(self, content: str):
        """Extract variable definitions from CDL content"""
        # Find variables section
        var_match = re.search(r"variables:\s*\n(.*?)(?=data:|$)", content, re.DOTALL)
        if not var_match:
            return

        var_content = var_match.group(1)

        # Split into individual variable blocks
        var_blocks = re.split(r"\n\s*(?=\w+\s+\w+)", var_content)

        for block in var_blocks:
            if not block.strip():
                continue

            self._parse_variable_block(block)

    def _parse_variable_block(self, block: str):
        """Parse a single variable definition block"""
        lines = block.strip().split("\n")
        if not lines:
            return

        # Parse variable declaration line
        decl_line = lines[0].strip()
        var_match = re.match(r"(\w+)\s+(\w+)(?:\(([^)]+)\))?\s*;", decl_line)

        if not var_match:
            return

        data_type = var_match.group(1)
        var_name = var_match.group(2)
        dimensions_str = var_match.group(3) or ""

        # Parse dimensions
        dimensions = []
        if dimensions_str:
            dimensions = [d.strip() for d in dimensions_str.split(",")]

        # Parse attributes
        attributes = {}
        for line in lines[1:]:
            line = line.strip()
            if not line or line == ";":
                continue

            # Parse attribute line: variable_name:attribute = "value" ;
            attr_match = re.match(r'(\w+):(\w+)\s*=\s*"([^"]*)"', line)
            if attr_match and attr_match.group(1) == var_name:
                attr_name = attr_match.group(2)
                attr_value = attr_match.group(3)
                attributes[attr_name] = attr_value
            else:
                # Try numeric or other values
                attr_match = re.match(r"(\w+):(\w+)\s*=\s*([^;]+)", line)
                if attr_match and attr_match.group(1) == var_name:
                    attr_name = attr_match.group(2)
                    attr_value = attr_match.group(3).strip()

                    # Try to parse as number or keep as string
                    try:
                        if "." in attr_value:
                            attr_value = float(attr_value)
                        else:
                            attr_value = int(attr_value)
                    except ValueError:
                        pass  # Keep as string

                    attributes[attr_name] = attr_value

        self.variables[var_name] = CDLVariable(
            var_name, data_type, dimensions, attributes
        )


class JSONSchemaGenerator:
    """Generates JSON Schema from parsed CDL structure"""

    def __init__(self, base_url: str = "https://schemas.standard-interfaces.org"):
        self.base_url = base_url

    def generate_schema(
        self, cdl_data: Dict[str, Any], schema_id: str
    ) -> Dict[str, Any]:
        """Generate JSON Schema from CDL data"""

        # Determine domain from variables (look for namespace prefixes)
        domain = self._detect_domain(cdl_data["variables"])

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": f"{self.base_url}/{domain}/{schema_id}",
            "title": cdl_data["global_attributes"].get("title", "NetCDF Schema"),
            "description": f"Schema for {cdl_data['global_attributes'].get('title', 'NetCDF data')} - Generated from CDL",
            "type": "object",
            "properties": {
                "dimensions": self._generate_dimensions_schema(cdl_data["dimensions"]),
                "variables": self._generate_variables_schema(cdl_data["variables"]),
                "global_attributes": self._generate_global_attributes_schema(
                    cdl_data["global_attributes"]
                ),
            },
            "required": ["dimensions", "variables"],
            "additionalProperties": True,
            "x-source": {
                "format": "CDL",
                "file": cdl_data["source_file"],
                "generated": datetime.now().isoformat(),
                "generator": "cdl_to_json_schema.py",
            },
        }

        return schema

    def _detect_domain(self, variables: Dict[str, CDLVariable]) -> str:
        """Detect domain namespace from variable names"""

        # Known domain prefixes
        domain_prefixes = {
            "pf_": "pf_active",
            "tf_": "tf_active",
            "plasma_": "plasma",
            "vessel_": "vessel",
            "diag_": "diagnostics",
            "eq_": "equilibrium",
        }

        for var_name in variables.keys():
            for prefix, domain in domain_prefixes.items():
                if var_name.startswith(prefix):
                    return domain

        return "base"  # Default for non-prefixed variables

    def _generate_dimensions_schema(
        self, dimensions: Dict[str, CDLDimension]
    ) -> Dict[str, Any]:
        """Generate dimensions schema section"""

        properties = {}
        required = []

        for dim_name, dim_obj in dimensions.items():
            properties[dim_name] = {
                "type": "integer",
                "description": f"Dimension: {dim_name}",
            }

            # Add constraints based on dimension usage
            if dim_name.endswith("_node"):
                properties[dim_name]["minimum"] = 3
                properties[dim_name]["description"] += " (minimum 3 for polygon nodes)"
            elif dim_name.endswith("_element"):
                properties[dim_name]["minimum"] = 1
                properties[dim_name]["description"] += " (number of elements)"
            else:
                properties[dim_name]["minimum"] = 1

            required.append(dim_name)

        return {
            "type": "object",
            "description": "Dimension definitions",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        }

    def _generate_variables_schema(
        self, variables: Dict[str, CDLVariable]
    ) -> Dict[str, Any]:
        """Generate variables schema section"""

        properties = {}
        required = []

        for var_name, var_obj in variables.items():
            var_schema = self._generate_variable_schema(var_obj)
            properties[var_name] = var_schema

            # Geometry containers and coordinates are typically required
            if (
                var_obj.attributes.get("geometry_type")
                or var_obj.attributes.get("units")
                or "geometry" in var_name
            ):
                required.append(var_name)

        return {
            "type": "object",
            "description": "Variable definitions",
            "properties": properties,
            "required": required,
            "additionalProperties": True,
        }

    def _generate_variable_schema(self, variable: CDLVariable) -> Dict[str, Any]:
        """Generate schema for a single variable"""

        var_schema = {
            "type": "object",
            "description": variable.attributes.get(
                "long_name", f"Variable: {variable.name}"
            ),
            "properties": {},
        }

        # Add dimensions property
        if variable.dimensions:
            var_schema["properties"]["dimensions"] = {
                "type": "array",
                "items": {"type": "string", "pattern": "^[a-zA-Z_][a-zA-Z0-9_]*$"},
                "minItems": len(variable.dimensions),
                "maxItems": len(variable.dimensions),
                "description": "Dimension names for this variable",
            }

        # Add attribute properties based on NetCDF/CF conventions
        if "units" in variable.attributes:
            var_schema["properties"]["units"] = {
                "type": "string",
                "description": "Units of measurement",
                "examples": [variable.attributes["units"]],
            }

        if "long_name" in variable.attributes:
            var_schema["properties"]["long_name"] = {
                "type": "string",
                "description": "Descriptive name for the variable",
            }

        if "standard_name" in variable.attributes:
            var_schema["properties"]["standard_name"] = {
                "type": "string",
                "description": "CF standard name",
            }

        # Geometry container specific attributes
        if "geometry_type" in variable.attributes:
            var_schema["properties"]["geometry_type"] = {
                "type": "string",
                "enum": ["polygon", "line", "point"],
                "description": "Type of geometry represented",
            }

        if "node_coordinates" in variable.attributes:
            var_schema["properties"]["node_coordinates"] = {
                "type": "string",
                "pattern": "^[a-zA-Z_][a-zA-Z0-9_]*\\s+[a-zA-Z_][a-zA-Z0-9_]*$",
                "description": "Space-separated coordinate variable names",
            }

        if "node_count" in variable.attributes:
            var_schema["properties"]["node_count"] = {
                "type": "string",
                "pattern": "^[a-zA-Z_][a-zA-Z0-9_]*$",
                "description": "Variable containing node count per element",
            }

        # Fill value handling
        if "_FillValue" in variable.attributes:
            var_schema["properties"]["_FillValue"] = {
                "type": "number",
                "description": "Value used for missing data",
            }

        # Validation ranges
        if "valid_min" in variable.attributes:
            var_schema["properties"]["valid_min"] = {
                "type": "number",
                "description": "Minimum valid value",
            }

        if "valid_max" in variable.attributes:
            var_schema["properties"]["valid_max"] = {
                "type": "number",
                "description": "Maximum valid value",
            }

        # Required properties based on variable type
        required = []
        if variable.dimensions:
            required.append("dimensions")
        if "units" in variable.attributes:
            required.append("units")
        if "geometry_type" in variable.attributes:
            required.extend(["geometry_type", "node_coordinates", "node_count"])

        if required:
            var_schema["required"] = required

        var_schema["additionalProperties"] = True

        return var_schema

    def _generate_global_attributes_schema(
        self, global_attrs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate global attributes schema section"""

        return {
            "type": "object",
            "description": "Global metadata attributes",
            "properties": {
                "title": {"type": "string", "description": "Title of the dataset"},
                "institution": {
                    "type": "string",
                    "description": "Institution responsible for the data",
                },
                "source": {
                    "type": "string",
                    "description": "Method of production of the original data",
                },
                "conventions": {
                    "type": "string",
                    "description": "Name of conventions followed",
                    "examples": ["CF-1.8", "CF-1.8, IMAS-3.0"],
                },
                "comment": {
                    "type": "string",
                    "description": "Additional information about the dataset",
                },
            },
            "additionalProperties": True,
        }


def main():
    """Main conversion function"""

    parser = argparse.ArgumentParser(
        description="Convert NetCDF CDL files to JSON Schema format"
    )
    parser.add_argument(
        "input_path",
        type=Path,
        help="Path to CDL file or directory containing CDL files",
    )
    parser.add_argument(
        "output_path", type=Path, help="Output directory for generated JSON schemas"
    )
    parser.add_argument(
        "--base-url",
        default="https://schemas.standard-interfaces.org",
        help="Base URL for schema IDs",
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing schema files"
    )

    args = parser.parse_args()

    # Ensure output directory exists
    args.output_path.mkdir(parents=True, exist_ok=True)
    # Initialize generator
    generator = JSONSchemaGenerator(args.base_url)

    # Find CDL files to process
    if args.input_path.is_file():
        cdl_files = [args.input_path]
    elif args.input_path.is_dir():
        cdl_files = list(args.input_path.rglob("*.cdl"))
    else:
        print(f"Error: {args.input_path} is not a valid file or directory")
        sys.exit(1)

    if not cdl_files:
        print(f"No CDL files found in {args.input_path}")
        sys.exit(1)

    # Process each CDL file
    for cdl_file in cdl_files:
        print(f"Processing: {cdl_file}")

        try:
            # Create fresh parser for each file
            parser_obj = CDLParser()
            # Parse CDL file
            cdl_data = parser_obj.parse_cdl_file(cdl_file)

            # Generate schema ID from filename
            schema_id = cdl_file.stem.replace("_", "-") + ".schema.json"

            # Generate JSON Schema
            schema = generator.generate_schema(cdl_data, schema_id)

            # Determine output subdirectory based on domain
            domain = generator._detect_domain(cdl_data["variables"])
            output_dir = args.output_path / domain
            output_dir.mkdir(parents=True, exist_ok=True)

            # Write output file
            output_file = output_dir / schema_id

            if output_file.exists() and not args.force:
                print(
                    f"  Skipping {output_file} (already exists, use --force to overwrite)"
                )
                continue

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(schema, f, indent=2, ensure_ascii=False)

            print(f"  Generated: {output_file}")

        except Exception as e:
            print(f"  Error processing {cdl_file}: {e}")
            continue

    print("Conversion complete!")


if __name__ == "__main__":
    main()
