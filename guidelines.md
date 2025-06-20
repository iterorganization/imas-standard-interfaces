# Schema Development Guidelines

This document provides detailed guidelines for developing standardized schemas in the Standard Interfaces project using a datatree-based structure with DOI-versioned schemas.

## Project Structure and Workflow

### Repository Organization

The Standard Interfaces project follows a structured approach for developing and deploying schemas:

```text
standard-interfaces/
├── definitions/                 # CDL building blocks
│   ├── base/                   # Fundamental patterns (CDL)
│   │   └── polygon-geometry.cdl
│   └── <domain>/               # Domain-specific patterns (CDL)
│       ├── coil-geometry.cdl
│       └── coil-current.cdl
├── schemas/                    # Generated JSON Schemas
│   ├── base/
│   └── <domain>/
└── docs/                       # Documentation and examples
```

### Development Workflow

1. **Define Components** (`definitions/` → CDL files)

   - Create reusable data structure patterns in CDL format
   - Base definitions for fundamental geometry containers
   - Domain definitions for IDS-specific structures

2. **Generate Schemas** (CDL → JSON Schema conversion)

   - Convert CDL files to JSON Schema format
   - Store locally in `schemas/` directory during development
   - Test against example data

3. **Publish Schemas** (Repository → Zenodo)

   - Complete JSON Schemas published to Zenodo with DOI minting
   - Versioned releases create persistent identifiers
   - DOIs serve as stable references for datatree validation

4. **Runtime Usage** (DOI → Datatree validation)
   - Datatree datasets reference schema DOIs in attributes
   - Runtime validation uses DOI-resolved schemas
   - Data consumers can verify structure and provenance

### Schema Composition Flow

```text
CDL Definitions → JSON Schemas → DOI Publication → Datatree Validation
   (repository)      (local)       (Zenodo)         (runtime)
```

**Example**: A complete "PF Active Coils" schema composes:

- `base/polygon-geometry.cdl` (fundamental pattern)
- `pf_active/coil-geometry.cdl` (domain pattern)
- `pf_active/coil-current.cdl` (domain pattern)

These combine into a single JSON Schema published with a DOI that validates entire pf_active datasets.

## Datatree Schema Architecture

### Root Schema Organization

The project uses a datatree structure that organizes schemas as datasets within a hierarchical tree:

```yaml
root/
  attrs:
    - provenance: PROV ontology description (JSON blob)
    - fusion_conventions: version number
    - standard_names: DOI (versioned schema reference)
    - data_schema: DOI (versioned tokamak/stellarator schema)

  /equilibrium (dataset)
    - data variables with schemas
    - attrs: root_schema (DOI), ids_name

  /equilibrium_efit (dataset)
    - data variables with schemas
    - attrs: root_schema (DOI), ids_name
```

### Schema Versioning with DOIs

- **Schema Storage**: Use Zenodo to store schemas with DOI minting
- **DOI References**: Each schema version gets a unique DOI as a Persistent ID (PID)
- **Standard Names**: Reference DOI-versioned schema collections
- **Data Schema**: Separate DOIs for tokamak vs stellarator schemas

### Dataset Attributes

Each dataset must include:

- `root_schema`: DOI reference to the schema defining data structure
- `ids_name`: IDS identifier (e.g., "equilibrium", "pf_active")

## Schema Organization

### Two-Tier Schema System

This project uses a two-tier approach for schema organization:

#### Base Schemas (`definitions/base/`)

- **Format**: JSON Schema directly
- **Purpose**: Fundamental geometry containers
- **Examples**: `polygon_geometry`, `r`, `z`

#### Domain Schemas (`definitions/<domain>/`)

- **Format**: CDL → JSON Schema conversion
- **Purpose**: IDS-specific or application schemas
- **Examples**: `outline_r`, `element_z`, `outline_geometry`

### Schema Organization Rules

1. **Datatree Hierarchy**: Use datatree structure for organization instead of variable prefixes
2. **Descriptive Names**: Use clear, descriptive variable names
3. **Geometry Containers**: Reference coordinates in `node_coordinates` attribute
4. **Dimensions**: Use descriptive dimension names

### Examples

#### Good CDL Structure

```cdl
dimensions:
    outline_node = _ ;
    element = _ ;

variables:
    int outline_geometry ;
        outline_geometry:geometry_type = "polygon" ;
        outline_geometry:node_coordinates = "outline_r outline_z" ;
        outline_geometry:node_count = "outline_node_count" ;

    double outline_r(outline_node) ;
        outline_r:units = "m" ;
        outline_r:long_name = "Coil outline major radius coordinate" ;
        outline_r:_FillValue = _ ;

    double outline_z(outline_node) ;
        outline_z:units = "m" ;
        outline_z:long_name = "Coil outline vertical coordinate" ;
        outline_z:_FillValue = _ ;

    int outline_node_count(element) ;
        outline_node_count:long_name = "Number of nodes per coil outline polygon" ;
```

#### Bad - Inconsistent Naming

```cdl
// WRONG: Inconsistent variable naming
int geometry ;                     // Should be outline_geometry
double r(node) ;                   // Should be outline_r(outline_node)
double vertical_coord(node) ;      // Should be outline_z(outline_node)
```

## File Organization

### File Naming Conventions

- Use lowercase with hyphens: `coil-geometry.cdl`
- Use descriptive names: `coil-current.cdl`, `power-supply.cdl`
- Match IDS structure when applicable

### When to Create New Files

Create separate files for:

- Separate logical components (geometry, current, circuit, power-supply)
- Single-purpose data structures
- Reusable base patterns
- IDS-specific structures

## CDL Format Requirements

### Modern CDL Syntax

Use modern CDL features:

```cdl
// Modern format (required)
string coil_name(coil) ;

// Old format (avoid)
char coil_name(coil, string_length) ;
```

### Required Attributes

Include these attributes:

- `units` for all coordinate and physical variables
- `long_name` for descriptive names
- `geometry_type`, `node_coordinates`, `node_count` for geometry containers
- `_FillValue` for coordinate arrays (use `_` in templates)

### Template Structure

CDL files should include these sections in order:

1. **Global attributes**: title, institution, conventions, source, schema DOI references
2. **Dimensions**: Use `_` for placeholder values
3. **Variables**: Include proper NetCDF attributes and geometry references
4. **Geometry containers**: Follow CF geometry container conventions
5. **No data section**: Templates define structure

## Geometry Data in Datatree Structure

### CF Geometry Containers

Following the datatree schema approach:

- **Geometry Containers**: Metadata variables that define coordinate relationships
- **Geometry Attribution**: Data variables reference geometry containers via `geometry` attribute
- **Multi-level Geometry**: Support layered geometry containers per variable
- **CF Conventions**: Use CF grid conventions for unstructured data

### Geometry Container Pattern

```cdl
// Geometry container (metadata)
int <geometry_type>_geometry ;
    <geometry_type>_geometry:geometry_type = "polygon" ;
    <geometry_type>_geometry:node_coordinates = "r z" ;
    <geometry_type>_geometry:node_count = "node_count" ;

// Referenced coordinates
double r(node) ;
    r:units = "m" ;
    r:long_name = "Major radius coordinate" ;

double z(node) ;
    z:units = "m" ;
    z:long_name = "Vertical coordinate" ;

// Data variable using geometry
double psi_unstructured(time, node) ;
    psi_unstructured:standard_name = "poloidal_flux" ;
    psi_unstructured:geometry = "<geometry_type>_geometry" ;
```

### Structured vs Unstructured Data

**Structured data** (regular grids):

```cdl
double psi_2d(time, r, z) ;
    psi_2d:standard_name = "poloidal_flux" ;
```

**Unstructured data** (irregular meshes):

```cdl
double psi_unstructured(time, node) ;
    psi_unstructured:standard_name = "poloidal_flux" ;
    psi_unstructured:geometry = "mesh_geometry" ;
```

## Standard Patterns

### Geometry Hierarchy Pattern

```cdl
// Container level
<geometry_type>_geometry

// Coordinate level
<geometry_type>_r
<geometry_type>_z

// Topology level
<geometry_type>_node_count
```

### Multi-level Geometries

For complex structures like coils with outlines and elements:

```cdl
outline_geometry     // Coil boundary
element_geometry     // Individual turns/elements
```

## Standard Names and DOI Attribution

### Standard Name Convention

Following the datatree schema approach, use `standard_name` attributes for physical quantities:

```cdl
double psi_2d(time, r, z) ;
    psi_2d:standard_name = "poloidal_flux" ;
    psi_2d:units = "Wb" ;
    psi_2d:long_name = "Poloidal magnetic flux on regular grid" ;

double psi_unstructured(time, node) ;
    psi_unstructured:standard_name = "poloidal_flux" ;
    psi_unstructured:units = "Wb" ;
    psi_unstructured:long_name = "Poloidal magnetic flux on unstructured mesh" ;
    psi_unstructured:geometry = "mesh_geometry" ;
```

### Schema DOI References

Each schema must reference its versioned DOI:

```cdl
// Global attributes
:title = "PF Active Coil Geometry Schema" ;
:institution = "ITER Organization" ;
:source = "IMAS Standard Interfaces" ;
:Conventions = "CF-1.8" ;
:schema_doi = "10.5281/zenodo.XXXXXX" ;  // Schema version DOI
:standard_names_doi = "10.5281/zenodo.YYYYYY" ;  // Standard names DOI
```

### Provenance Attribution

Include provenance information following PROV ontology:

```cdl
:provenance = "{\"@type\": \"prov:Entity\", \"prov:wasGeneratedBy\": {\"@type\": \"prov:Activity\", \"prov:startedAtTime\": \"2025-06-19T00:00:00Z\"}}" ;
```

## Quality Checklist

Before submitting schemas, verify:

### Datatree Structure

- [ ] Root attributes include required DOI references
- [ ] Dataset attributes include `root_schema` and `ids_name`
- [ ] Schema versioning follows DOI conventions

### Schema Content

- [ ] Consistent variable naming within files
- [ ] Geometry container references point to correct variables
- [ ] CF geometry conventions properly implemented
- [ ] Dimension compatibility across variables
- [ ] Modern CDL format usage
- [ ] Required attributes present (`units`, `long_name`, etc.)
- [ ] Descriptive variable names

## Common Mistakes to Avoid

### Datatree Structure Issues

1. **Missing DOI references** in root or dataset attributes
2. **Inconsistent schema versioning** without proper DOI tracking
3. **Missing dataset attributes** (`root_schema`, `ids_name`)

### Schema Content Issues

1. **Inconsistent variable naming** within the same schema
2. **Missing geometry references** in `node_coordinates`
3. **Incorrect CF geometry conventions** for unstructured data
4. **Using old CDL format** with `string_length` dimensions
5. **Missing required attributes** like `units` and `long_name`
6. **Conflicting dimension names** across files
7. **Generic names** without descriptive context

Remember: Consistency and clarity are key to maintainable schemas that work across different scientific applications and integrate properly with the datatree structure.
