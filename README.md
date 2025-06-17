# Standard Interfaces

This project provides standardized schemas and interfaces for scientific data formats.

## Installation

### Recommended: Using Pixi

Pixi manages both conda and PyPI dependencies from `pyproject.toml`:

```bash
# Install pixi (if not already installed)
curl -fsSL https://pixi.sh/install.sh | bash  # Linux/macOS
# or: iwr -useb https://pixi.sh/install.ps1 | iex  # Windows PowerShell

# Install all dependencies and activate environment
pixi install
pixi shell

# Verify your setup is working
pixi run verify-setup
```

### Available Pixi Tasks

```bash
# Setup and verification
pixi run verify-setup     # Check that all dependencies are working
pixi run install-editable # Install package in editable mode

# Development
pixi run test              # Run tests
pixi run test-verbose      # Run tests with verbose output
pixi run lint             # Run linting (configure as needed)
pixi run format           # Format code (configure as needed)

# Documentation
pixi run docs-serve       # Serve documentation locally
pixi run docs-build       # Build documentation
pixi run docs-deploy      # Deploy documentation with versioning

# Building
pixi run build            # Build Python package
pixi run clean            # Clean build artifacts

# Schema processing
pixi run generate-schemas # Generate JSON schemas from CDL files
pixi run build-docs       # Generate documentation
```

### Alternative Installation Methods

### Alternative Installation Methods

#### Using conda (Traditional approach)

This method ensures that `ncgen` (NetCDF utilities) is available for CDL file processing:

```bash
# Create and activate the conda environment
conda env create -f environment.yml
conda activate imas-standard-interfaces

# Install the package in development mode
pip install -e .
```

#### Using conda-lock (Generated from pyproject.toml)

Generate conda lock files from pyproject.toml dependencies:

```bash
# Install conda-lock
conda install -c conda-forge conda-lock

# Generate lock file from pyproject.toml
conda-lock --file pyproject.toml --platform win-64

# Create environment from lock file
conda create --name imas-standard-interfaces --file conda-lock.yml
conda activate imas-standard-interfaces
```

#### Using uv (requires separate ncgen installation)

To install the project dependencies:

```bash
uv sync
```

For development work (includes additional tools like ipykernel for Jupyter notebooks):

```bash
uv sync --group dev
```

**Note**: When using uv, you'll need to install NetCDF utilities separately to get `ncgen`:

- **Windows**: Download from [Unidata NetCDF](https://www.unidata.ucar.edu/downloads/netcdf/)
- **macOS**: `brew install netcdf`
- **Linux**: `sudo apt-get install netcdf-bin` (Ubuntu/Debian) or `sudo yum install netcdf` (RHEL/CentOS)

## Project Structure

This project uses a two-tier approach for schema management:

```text
standard_interfaces/
├── definitions/            # Source CDL schema definitions
│   ├── base/              # Fundamental geometry containers
│   │   ├── polygon-geometry.cdl
│   │   └── mesh-geometry.cdl
│   └── pf_active/         # IDS-specific schemas
│       ├── coil-geometry.cdl
│       ├── coil-current.cdl
│       ├── coil-circuit.cdl
│       └── power-supply.cdl
├── schemas/               # Generated JSON schemas
│   ├── base/             # Generated from definitions/base/
│   └── pf_active/        # Generated from definitions/pf_active/
└── scripts/
    └── cdl2schema.py     # Conversion script
```

### Directory Usage

- **`definitions/`** - Contains authoritative CDL (Common Data form Language) files that define data structures using NetCDF conventions. These are the source of truth and should be edited directly.

- **`schemas/`** - Contains JSON Schema files automatically generated from CDL definitions. **Do not edit these files directly** - they will be overwritten during the build process.

### Workflow

1. Edit CDL files in `definitions/` to define or modify data structures
2. Run the conversion script to generate JSON schemas: `python scripts/cdl2schema.py`
3. Use the generated JSON schemas in applications for validation and documentation

This approach leverages the domain expertise of scientists familiar with NetCDF/CDL while providing modern JSON Schema compatibility for web applications and APIs.

## Namespacing Guidelines

This project uses consistent namespacing conventions to organize variables and prevent naming conflicts across different data domains.

### Quick Reference

**Base Schemas** (generic, reusable):

- **Location**: `definitions/base/`
- **Format**: JSON Schema
- **Namespace**: No prefix
- **Example**: `r`, `z`, `polygon_geometry`

**Domain Schemas** (IDS-specific):

- **Location**: `definitions/<domain>/`
- **Format**: CDL → JSON Schema
- **Namespace**: Domain prefix
- **Example**: `outline_geometry`, `outline_r`, `outline_z`

### Common Prefixes

- `pf_` - Poloidal field coil systems (pf_active IDS)
- `tf_` - Toroidal field coil systems
- `plasma_` - Plasma boundary and profiles
- `vessel_` - Vacuum vessel geometry
- `diag_` - Diagnostic systems
- `eq_` - Equilibrium data structures

**📖 See [guidelines.md](guidelines.md) for detailed rules and examples.**

## NetCDF Geometry Container Namespacing

When working with NetCDF geometry containers, especially in files containing multiple geometries, we recommend using a consistent namespacing pattern to avoid variable name conflicts and improve data organization.

### Namespacing Pattern

Use the geometry container name as a prefix for all related variables:

```cdl
variables:
    // Geometry container
    int <container_name>_geometry ;
        <container_name>_geometry:geometry_type = "polygon" ;
        <container_name>_geometry:node_coordinates = "<container_name>_r <container_name>_z" ;
        <container_name>_geometry:node_count = "<container_name>_polygon_node_count" ;

    // Namespaced coordinate variables
    double <container_name>_r(<container_name>_node) ;
    double <container_name>_z(<container_name>_node) ;

    // Namespaced auxiliary variables
    int <container_name>_polygon_node_count(<container_name>_polygon) ;
```

### Example: Multiple Geometries

```cdl
netcdf tokamak_geometry {
dimensions:
    outline_node = 16 ;
    outline_polygon = 4 ;
    element_node = 100 ;
    element_polygon = 1 ;

variables:
    // Coil outline geometry container
    int outline_geometry ;
        outline_geometry:geometry_type = "polygon" ;
        outline_geometry:node_coordinates = "outline_r outline_z" ;
        outline_geometry:node_count = "outline_polygon_node_count" ;

    double outline_r(outline_node) ;
        outline_r:units = "m" ;
        outline_r:long_name = "Coil outline major radius coordinate" ;

    double outline_z(outline_node) ;
        outline_z:units = "m" ;
        outline_z:long_name = "Coil outline vertical coordinate" ;

    int outline_polygon_node_count(outline_polygon) ;

    // Coil element geometry container
    int element_geometry ;
        element_geometry:geometry_type = "polygon" ;
        element_geometry:node_coordinates = "element_r element_z" ;
        element_geometry:node_count = "element_polygon_node_count" ;

    double element_r(element_node) ;
        element_r:units = "m" ;
        element_r:long_name = "Coil element major radius coordinate" ;

    double element_z(element_node) ;
        element_z:units = "m" ;
        element_z:long_name = "Coil element vertical coordinate" ;

    int element_polygon_node_count(element_polygon) ;

    // Data variables with geometry references
    double current(outline_polygon) ;
        current:units = "A" ;
        current:geometry = "outline_geometry" ;

    double power(element_polygon) ;
        power:units = "W" ;
        power:geometry = "element_geometry" ;
}
```

### Benefits

1. **Prevents naming conflicts** between geometry coordinates and physics variables
2. **Enables multiple geometries** in a single file without ambiguity
3. **Improves discoverability** - tools can identify related variables by prefix
4. **Maintains clear relationships** between data variables and their spatial context
5. **Supports modular design** - geometries can be independently validated and processed

### Recommended Prefixes

- `pf_` - Poloidal field coil systems (pf_active IDS)
- `tf_` - Toroidal field coil systems
- `plasma_` - Plasma boundary and profiles
- `vessel_` - Vacuum vessel geometry
- `diag_` - Diagnostic systems
- `eq_` - Equilibrium data structures
