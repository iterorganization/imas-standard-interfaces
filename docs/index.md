# Standard Interfaces Documentation

Welcome to the Standard Interfaces documentation. This project provides NetCDF schemas and examples for tokamak data interfaces.

## Overview

Standard Interfaces defines a set of JSON schemas for representing tokamak physics data in a standardized format. These schemas ensure data consistency and enable interoperability between different analysis tools and systems.

## Key Features

- **📋 JSON Schema Definitions** - Structured schemas for different tokamak systems
- **🔧 Validation Tools** - Built-in validation for data compliance
- **📚 Comprehensive Documentation** - Detailed documentation for each schema
- **🧪 Examples** - Real-world usage examples and test cases

## Schema Categories

### [Base Schemas](schemas/base.md)

Fundamental geometric and data structures used across multiple systems.

### [PF Active Coils](schemas/pf_active.md)

Schemas for poloidal field active coil systems, including current and geometry definitions.

### [TF Active Coils](schemas/tf_active.md)

Schemas for toroidal field active coil systems and their geometric representations.

## Quick Start

1. **Install dependencies:**

   ```bash
   uv sync --group docs
   ```

2. **Serve documentation locally:**

   ```bash
   uv run mkdocs serve
   ```

3. **Build and deploy:**
   ```bash
   uv run mike deploy --push --update-aliases 1.0 latest
   ```

## Contributing

To contribute to the schemas or documentation:

1. Make changes to schema files in `standard_interfaces/schemas/`
2. Update documentation in `docs/`
3. Run the documentation generator: `python -m standard_interfaces.docs.generate`
4. Test locally with `mkdocs serve`
5. Submit a pull request

## Version History

This documentation is versioned using `mike`. You can view different versions using the version selector in the top navigation.
