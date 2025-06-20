# IMAS Schemas

Use Zenodo to store schemas - this will mint DOI Digital Resource Identifiers that serve as types of Persistent IDs (PIDs)

## data-tree

- attrs
  - provenance description using the prov ontology (json blob - stringified)
  - fusion_conventions (version number)
  - standard_names = DOI, this DOI would be versioned (schema ver)
  - data_schema = DOI (also versioned) - standard tokamak schema. We shall include versions for stellarators etc.

### /equilibrium (dataset)

- data (schema and other data define this data)
  - psi_2d = (time, r, z), [nd_array]
    - attrs
      - standard_name = poloidal_flux
  - psi_unstructured = (time, node), [nd_array]
    - attrs
      - standard_name = poloidal_flux
      - geometry = container that links nodes to r, z points (use CF grid conventions)
- attrs
  - root schema (DOI)
  - ids_name = equilibrium

### /equilibrium_efit

- data
- attrs
  - root schema (DOI)
  - ids_name = equilibrium

### /other_data

## Geometry data

We shall use geometry containers. A geometry attribute that attaches to data variables identifies the geometry container(s).
Geometry containers are metadata only variables
We shall store multiple levels of geometry data for each variable. We shall use multiple geometry containers.
Schemas shall validate the geometry container (shape and content)
