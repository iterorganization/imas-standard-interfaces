---
applyTo: "*.cdl *.md"
---

# Schema Development Instructions

This document provides step-by-step instructions for developing standardized schemas in the Standard Interfaces project. These schemas define data formats for scientific applications.

## Understanding the Project Structure

Before creating or modifying schemas, familiarize yourself with this directory structure:

```
standard_interfaces/
├── definitions/            # Source CDL schema definitions
│   ├── base/              # Fundamental geometry containers
│   └── <domain>/          # Domain-specific schemas (e.g., pf_active)
├── schemas/               # Generated JSON schemas (DO NOT EDIT)
├── standard_interfaces/   # Conversion tools and package code
└── tests/                 # Test suite for schema validation and tools
```

## How to Organize Schemas

### Step 1: Choose the Correct Schema Type

Follow this two-tier approach when creating schemas:

1. **Base Schemas** (`definitions/base/`):

   - Use JSON Schema format directly
   - No namespace prefix (generic, reusable)
   - For fundamental geometry containers
   - Example: `polygon_geometry`, `r`, `z`

2. **Domain Schemas** (`definitions/<domain>/`):
   - Use CDL format → generate JSON Schema
   - Domain-specific namespace prefix
   - For IDS-specific or application schemas
   - Example: `outline_geometry`, `outline_r`, `outline_z`

## Step 2: Apply Namespace Prefixes

### Action Required: Add Domain Prefixes to conflicting Variables

When creating domain-specific schemas, you ONLY add namespace prefixes to conflicting variable names:

**Use These Prefixes:**

- `pf_` - Poloidal field coil systems (pf_active IDS)
- `tf_` - Toroidal field coil systems
- `plasma_` - Plasma boundary and profiles
- `vessel_` - Vacuum vessel geometry
- `diag_` - Diagnostic systems
- `eq_` - Equilibrium data structures

### Follow These Namespacing Rules

1. **Consistency**: ALL variables in a domain schema must use the same prefix
2. **Hierarchy**: Use descriptive sub-namespaces (e.g., `pf_outline_r`, `pf_element_r`)
3. **Geometry Containers**: Reference namespaced coordinates in node_coordinates attribute
4. **Dimensions**: Include namespace in dimension names when domain-specific

### Examples

**Good CDL Structure:**

```cdl
dimensions:
    outline_node = _ ;
    element = _ ;

variables:
    int outline_geometry ;
        outline_geometry:node_coordinates = "outline_r outline_z" ;
        outline_geometry:node_count = "outline_node_count" ;

    double outline_r(outline_node) ;
        outline_r:units = "m" ;
        outline_r:long_name = "Outline major radius coordinate" ;
```

**Bad - Missing Prefixes:**

```cdl
int geometry ;              // Should be outline_geometry
double outline_r(outline_node) ;    // Should be outline_r(outline_node)
```

## Step 3: Write CDL Files

### Use This Template Structure

Include these sections in order:

1. **Global attributes**: title, institution, conventions, source
2. **Dimensions**: Use `_` for placeholder values in templates
3. **Variables**: Include proper NetCDF attributes (units, long_name, etc.)
4. **Geometry containers**: Follow CF geometry container conventions
5. **No data section**: Templates define structure, not actual data

### Use Modern CDL Format

- **Use `string` type for character variables**: Modern CDL supports variable-length strings
- **Avoid `string_length` dimensions**: No longer needed with modern CDL format
- **String variable syntax**: `string variable_name(dimension)` instead of `char variable_name(dimension, string_length)`

**Example:**

```cdl
// Modern format (preferred)
string coil_name(coil) ;

// Old format (avoid)
char coil_name(coil, string_length) ;
```

### Include These Required Attributes

Add these attributes to your variables:

- `units` for all coordinate and physical variables
- `long_name` for descriptive names
- `geometry_type`, `node_coordinates`, `node_count` for geometry containers
- `_FillValue` for coordinate arrays (use `_` in templates)

## Step 4: Name Your Files

Follow these naming rules:

- Use lowercase with hyphens: `coil-geometry.cdl`
- Use descriptive names reflecting content: `coil-current.cdl`, `power-supply.cdl`
- Match IDS structure when applicable

## Step 5: Decide When to Create New Files

Create separate files in these situations:

- Separate logical components (geometry, current, circuit, power-supply)
- Keep files focused on single data structure
- Create base schemas for reusable patterns
- Create domain schemas for IDS-specific structures

## Step 6: Check Your Work

Before submitting, verify these requirements:

- Ensure namespace consistency within files
- Verify geometry container references point to correct variables
- Check dimension compatibility across variables
- Check CF convention compliance

## Summary

To create a new schema:

1. **Choose schema type**: Base (JSON) or Domain (CDL)
2. **Apply prefixes**: Add domain namespace to all variables
3. **Write CDL**: Follow template structure with modern format
4. **Name file**: Use lowercase with hyphens
5. **Separate concerns**: Create new files for distinct components
6. **Check work**: Verify namespace consistency and CF compliance

Remember: Base schemas are generic and reusable, domain schemas use scientific conventions with consistent namespacing.

## Reference: Common Patterns

Use these standard patterns when building your schemas:

### Geometry Hierarchy

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

Remember: Base schemas are generic and reusable, domain schemas leverage scientific conventions and use consistent namespacing.
