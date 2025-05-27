# Schema Development Guidelines

This document provides detailed guidelines for developing standardized schemas in the Standard Interfaces project.

## Namespacing Conventions

### Two-Tier Schema System

This project uses a two-tier approach for schema organization:

#### Base Schemas (`definitions/base/`)

- **Format**: JSON Schema directly
- **Namespace**: No prefix (generic, reusable)
- **Purpose**: Fundamental geometry containers
- **Examples**: `polygon_geometry`, `r`, `z`

#### Domain Schemas (`definitions/<domain>/`)

- **Format**: CDL → JSON Schema conversion
- **Namespace**: Domain-specific prefix
- **Purpose**: IDS-specific or application schemas
- **Examples**: `pf_outline_r`, `pf_element_z`, `pf_outline_geometry`

### Required Namespace Prefixes

When creating domain-specific schemas, use these standardized prefixes:

- `pf_` - Poloidal field coil systems (pf_active IDS)
- `tf_` - Toroidal field coil systems
- `plasma_` - Plasma boundary and profiles
- `vessel_` - Vacuum vessel geometry
- `diag_` - Diagnostic systems
- `eq_` - Equilibrium data structures

### Namespacing Rules

1. **Consistency**: ALL variables in a domain schema MUST use the same prefix
2. **Hierarchy**: Use descriptive sub-namespaces (e.g., `pf_outline_r`, `pf_element_r`)
3. **Geometry Containers**: Reference namespaced coordinates in `node_coordinates` attribute
4. **Dimensions**: Include namespace in dimension names when domain-specific

### Examples

#### Good CDL Structure

```cdl
dimensions:
    pf_outline_node = _ ;
    pf_element = _ ;

variables:
    int pf_outline_geometry ;
        pf_outline_geometry:geometry_type = "polygon" ;
        pf_outline_geometry:node_coordinates = "pf_outline_r pf_outline_z" ;
        pf_outline_geometry:node_count = "pf_outline_node_count" ;

    double pf_outline_r(pf_outline_node) ;
        pf_outline_r:units = "m" ;
        pf_outline_r:long_name = "PF coil outline major radius coordinate" ;
        pf_outline_r:_FillValue = _ ;

    double pf_outline_z(pf_outline_node) ;
        pf_outline_z:units = "m" ;
        pf_outline_z:long_name = "PF coil outline vertical coordinate" ;
        pf_outline_z:_FillValue = _ ;

    int pf_outline_node_count(pf_element) ;
        pf_outline_node_count:long_name = "Number of nodes per PF coil outline polygon" ;
```

#### Bad - Missing Prefixes

```cdl
// WRONG: Inconsistent namespacing
int geometry ;                     // Should be pf_outline_geometry
double outline_r(outline_node) ;   // Should be pf_outline_r(pf_outline_node)
double z(node) ;                   // Should be pf_outline_z(pf_outline_node)
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
// Modern format (preferred)
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

1. **Global attributes**: title, institution, conventions, source
2. **Dimensions**: Use `_` for placeholder values
3. **Variables**: Include proper NetCDF attributes
4. **Geometry containers**: Follow CF geometry container conventions
5. **No data section**: Templates define structure only

## Standard Patterns

### Geometry Hierarchy Pattern

```cdl
// Container level
<namespace>_<geometry_type>_geometry

// Coordinate level
<namespace>_<geometry_type>_r
<namespace>_<geometry_type>_z

// Topology level
<namespace>_<geometry_type>_node_count
```

### Multi-level Geometries

For complex structures like coils with outlines and elements:

```cdl
pf_outline_geometry     // Coil boundary
pf_element_geometry     // Individual turns/elements
```

## Quality Checklist

Before submitting schemas, verify:

- [ ] Namespace consistency within files
- [ ] Geometry container references point to correct variables
- [ ] Dimension compatibility across variables
- [ ] CF convention compliance
- [ ] Modern CDL format usage
- [ ] Required attributes present
- [ ] Descriptive variable names

## Common Mistakes to Avoid

1. **Inconsistent prefixes** within the same domain
2. **Missing geometry references** in `node_coordinates`
3. **Using old CDL format** with `string_length` dimensions
4. **Missing required attributes** like `units` and `long_name`
5. **Conflicting dimension names** across files
6. **Generic names** without proper namespacing

Remember: Consistency and clarity are key to maintainable schemas that work across different scientific applications.
