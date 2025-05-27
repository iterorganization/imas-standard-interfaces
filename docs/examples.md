# Examples

This page provides practical examples of using the Standard Interfaces schemas.

## Basic Usage

### Validating Data Against a Schema

```python
import json
import jsonschema
from pathlib import Path

# Load schema
schema_path = Path("standard_interfaces/schemas/pf_active/coil-current.schema.json")
with open(schema_path) as f:
    schema = json.load(f)

# Example data
data = {
    "dimensions": {
        "time": 100,
        "coil": 6
    },
    "variables": {
        "time": {
            "dimensions": ["time"],
            "data": list(range(100))
        }
    }
}

# Validate
try:
    jsonschema.validate(data, schema)
    print("✅ Data is valid!")
except jsonschema.ValidationError as e:
    print(f"❌ Validation error: {e.message}")
```

### Creating Test Data

```python
import numpy as np

def create_coil_current_data(n_time=100, n_coils=6):
    """Create example PF coil current data."""
    return {
        "dimensions": {
            "time": n_time,
            "coil": n_coils
        },
        "variables": {
            "time": {
                "dimensions": ["time"],
                "data": np.linspace(0, 10, n_time).tolist(),
                "units": "s",
                "long_name": "Time"
            },
            "current": {
                "dimensions": ["time", "coil"],
                "data": np.random.randn(n_time, n_coils).tolist(),
                "units": "A",
                "long_name": "Coil current"
            }
        },
        "attributes": {
            "title": "PF Coil Current Data",
            "source": "Example generator"
        }
    }

# Generate and save example data
example_data = create_coil_current_data()
with open("example_coil_current.json", "w") as f:
    json.dump(example_data, f, indent=2)
```

## Integration Examples

### With xarray

```python
import xarray as xr
import json

def json_to_xarray(json_data):
    """Convert JSON schema-compliant data to xarray Dataset."""
    dims = json_data["dimensions"]
    variables = json_data["variables"]
    attrs = json_data.get("attributes", {})

    data_vars = {}
    coords = {}

    for var_name, var_def in variables.items():
        data = np.array(var_def["data"])
        dims_list = var_def["dimensions"]

        if len(dims_list) == 1 and var_name in dims:
            # This is a coordinate
            coords[var_name] = (dims_list, data)
        else:
            # This is a data variable
            attrs_var = {k: v for k, v in var_def.items()
                        if k not in ["data", "dimensions"]}
            data_vars[var_name] = (dims_list, data, attrs_var)

    return xr.Dataset(data_vars, coords=coords, attrs=attrs)

# Load and convert
with open("example_coil_current.json") as f:
    data = json.load(f)

ds = json_to_xarray(data)
print(ds)
```

### Schema Validation in CI/CD

```yaml
# .github/workflows/validate-schemas.yml
name: Validate Schemas

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Validate schemas
        run: |
          python -m pytest tests/ -v      - name: Generate documentation
        run: |
          uv run python -m standard_interfaces.docs.generate
          uv run mkdocs build
```

## Real-World Scenarios

### Tokamak Shot Data Processing

```python
class ShotDataProcessor:
    def __init__(self, schema_dir):
        self.schemas = self.load_schemas(schema_dir)

    def load_schemas(self, schema_dir):
        schemas = {}
        for schema_file in Path(schema_dir).rglob("*.schema.json"):
            with open(schema_file) as f:
                schema_name = schema_file.stem
                schemas[schema_name] = json.load(f)
        return schemas

    def validate_shot_data(self, shot_data, data_type):
        """Validate shot data against appropriate schema."""
        if data_type not in self.schemas:
            raise ValueError(f"Unknown data type: {data_type}")

        schema = self.schemas[data_type]
        jsonschema.validate(shot_data, schema)
        return True

    def process_shot(self, shot_number, data_types):
        """Process a complete shot with multiple data types."""
        results = {}

        for data_type in data_types:
            # Load raw data (implementation specific)
            raw_data = self.load_raw_data(shot_number, data_type)

            # Convert to standard format
            standard_data = self.convert_to_standard(raw_data, data_type)

            # Validate against schema
            self.validate_shot_data(standard_data, data_type)

            results[data_type] = standard_data

        return results
```

### Multi-Device Data Exchange

```python
def export_for_external_analysis(shot_data, output_format="json"):
    """Export validated data for external analysis tools."""

    if output_format == "json":
        return json.dumps(shot_data, indent=2)

    elif output_format == "netcdf":
        # Convert to xarray then NetCDF
        ds = json_to_xarray(shot_data)
        return ds.to_netcdf()

    elif output_format == "hdf5":
        # Convert to HDF5 format
        import h5py
        # Implementation specific
        pass

    else:
        raise ValueError(f"Unsupported format: {output_format}")
```

## Testing Patterns

### Schema Evolution Testing

```python
def test_schema_backward_compatibility():
    """Test that new schema versions are backward compatible."""
    old_schema = load_schema("v1.0/coil-current.schema.json")
    new_schema = load_schema("v1.1/coil-current.schema.json")

    # Generate test data from old schema
    test_data = generate_test_data(old_schema)

    # Should validate against new schema
    jsonschema.validate(test_data, new_schema)
```

### Performance Testing

```python
def test_large_dataset_validation():
    """Test validation performance with large datasets."""
    import time

    # Generate large dataset
    large_data = create_coil_current_data(n_time=10000, n_coils=20)

    start_time = time.time()
    jsonschema.validate(large_data, schema)
    validation_time = time.time() - start_time

    # Should validate in reasonable time
    assert validation_time < 1.0, f"Validation too slow: {validation_time}s"
```
