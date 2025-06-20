# IMAS Standard Interfaces Development Workplan

## Project Overview

The IMAS Data Dictionary provides multiple pathways for representing the same physical quantities, creating a flexibility that ultimately undermines dataset interoperability when different implementations choose different representation approaches. A recent analysis of IMAS grid types reveals the scale of this challenge: multiple IDSs including `core_profiles`, `equilibrium`, `plasma_initiation`, and `plasma_profiles` each contain `profiles_2d/grid_type` nodes that each define 29 different coordinate systems for representing 2D profile data, ranging from simple rectangular (R,Z) grids to complex flux surface coordinates with poloidal angle definitions and Fourier mode representations. This proliferation extends beyond grid types to affect all data representations - the ongoing standardization versus General Grid Description (GGD) debate exemplifies how multiple representation approaches fragment data compatibility. This fundamental challenge encompasses the core interoperability issue: while the Data Dictionary provides consistent naming and units, it offers too many optional pathways for representing the same physical quantities, and different implementations choose different approaches without standardized selection criteria, creating incompatible data silos that hinder reproducible fusion science.

Standard interfaces solve this critical interoperability issue by defining concrete interfaces that eliminate ambiguity in data representation. These interfaces combine a variable name with an ordered list of dimensions, a standard name, units, and where applicable, linked geometric data. This comprehensive specification approach ensures that each physical quantity has a unique, unambiguous representation that enables automated data discovery, validation, and integration across different facilities and analysis codes. Rather than offering multiple optional pathways that fragment the community into incompatible data silos, standard interfaces provide the single, well-defined representation necessary for reproducible fusion science.

## Self-Describing Datasets and Data Independence

A fundamental goal of standard interfaces is the creation of self-describing datasets that contain all necessary metadata for complete interpretation without requiring external data silos or facility-specific documentation. Traditional fusion datasets often rely on implicit knowledge about coordinate systems, measurement locations, and physical quantity definitions that are stored separately from the data itself, creating dependencies that fragment when datasets are shared across institutions or analysis frameworks.

Self-describing standard interface datasets embed complete semantic and geometric context directly within the data structure through two complementary metadata systems: standard names that provide unambiguous identification of physical quantities, and geometry containers that establish explicit spatial relationships for all measurements. Standard names eliminate the need for external lookup tables or facility-specific conventions by providing standardized vocabulary that uniquely identifies what each variable represents - for example, distinguishing between `plasma_electron_temperature_on_magnetic_axis` and `plasma_electron_temperature_volume_averaged` removes ambiguity that would otherwise require consultation of analysis documentation. Geometry containers establish complete spatial context by embedding coordinate system definitions, measurement positions, sensor orientations, and coordinate transformations directly within the dataset, eliminating dependencies on external geometric databases or CAD files.

This self-describing approach enables datasets to travel independently across research groups, analysis codes, and long-term archives while maintaining complete interpretability. When a magnetics equilibrium reconstruction contains both magnetic sensor measurements with embedded position vectors and plasma current profiles with explicit flux coordinate definitions, the dataset becomes entirely self-contained for equilibrium analysis without requiring access to tokamak geometry databases or facility-specific calibration files. The combination of standard names and geometry containers creates datasets that function as complete data packages rather than fragments requiring external context for meaningful interpretation.

The data independence achieved through self-describing datasets fundamentally transforms collaborative research by enabling automated data discovery, validation, and integration across different facilities and computational frameworks. Researchers can process datasets from unfamiliar tokamaks without facility-specific knowledge, machine learning algorithms can operate across multi-machine datasets without manual harmonization, and long-term data preservation becomes feasible without maintaining external metadata dependencies that degrade over time.

## Project Goals and Implementation Strategy

This workplan develops concrete standard interfaces for fusion data exchange using magnetics equilibrium reconstruction as the primary demonstration domain. The project focuses specifically on interface definition and data exchange format specification rather than workflow execution or computational implementation, establishing common formats for storing equilibrium calculation results, experimental measurements, and geometric data that enable seamless data exchange between different analysis codes and facilities.

### Demonstration Domain Selection

Magnetics equilibrium reconstruction serves as the demonstration domain because it encompasses the full spectrum of data exchange format challenges that standard interfaces must address. This domain requires precise specification of magnetic sensor measurement formats with explicit spatial positioning, plasma current profile representations with coordinate system specifications, and critically, standardized storage formats for equilibrium solver results including flux coordinate systems, safety factor profiles, and plasma boundary definitions. The complexity of equilibrium data exchange - spanning multiple IDSs including pf_active, pf_passive, wall, magnetics, and equilibrium - provides comprehensive testing for interface specifications while addressing a critical data storage capability required across all tokamak facilities.

### Implementation Approach

The project employs a five-phase chronological approach beginning with foundational geometry container frameworks (Months 1-2), followed by complete equilibrium interface implementation (Months 3-5), then schema generation and validation (Months 6-7), data population and testing (Months 8-9), and final documentation and release preparation (Months 10-12). This progression ensures that each phase builds upon established foundations while maintaining focus on practical data exchange needs demonstrated through ITER, WEST, and MAST tokamak datasets.

### Standard Names Scope

The workplan explicitly excludes comprehensive development of fusion standard names, recognizing this as a separate community-wide standardization effort. Where standard names are required for interface specifications but do not yet exist in established vocabularies, placeholder standard names shall be prefixed with an underscore (e.g., `_magnetic_sensor_radial_position`, `_plasma_current_density_toroidal_component`) to clearly indicate development needs. A keyword-value mapping system shall be maintained in the imas-standard-names repository linking each placeholder standard name to a concise description of the physical quantity it represents, creating a structured record of standard name requirements for future community standardization efforts.

### Validation Strategy

Interface validation occurs through format specification completeness, schema compliance testing, and multi-machine data representation capability rather than through executing reconstruction workflows or running computational codes. The project creates self-describing datasets that embed complete semantic and geometric context directly within the data structure through standard names and geometry containers, enabling datasets to travel independently across research groups, analysis codes, and long-term archives while maintaining complete interpretability without external dependencies.

### Graphical Abstract

The following diagram illustrates the complete workflow from human-readable interface definitions through automated schema generation to final validation-ready data exchange formats. The process demonstrates how two parallel development streams - CDL interface specifications and foundational schema components - converge to create comprehensive validation capabilities that support interoperable fusion data exchange.

```
Base Schema Development (Phase 1)         CDL Interface Definitions (Phase 2)
├── geometry_base.schema.json             ├── pf_active.cdl
├── coordinate_systems.schema.json        ├── pf_passive.cdl
└── standard_names_map.json               ├── tf_active.cdl
         │                                ├── wall.cdl
         │                                ├── magnetics.cdl
         │                                └── equilibrium.cdl
         │                                         │ │
         └─────────────┬───────────────────────────┘ │
                       ▼                             │
         IDS-Specific JSON Schemas (Phase 3)         │
         ├── pf_active.schema.json                   │
         ├── pf_passive.schema.json                  │
         ├── tf_active.schema.json                   │
         ├── wall.schema.json                        │
         ├── magnetics.schema.json                   │
         └── equilibrium.schema.json                 │
                       │                             │
                       ▼                             ▼
         Composite Data-Tree Schema (Phase 3)      Multi-Machine NetCDF Datasets (Phase 4)
         └── datatree.schema.json                  ├── ITER.nc
                       │                           ├── WEST.nc
                       ▼                           └── MAST.nc
              Zenodo Release (DOI) (Phase 5)               │
              └── datatree.schema.json                     │
                       │                                   │
                       └─────────────┬─────────────────────┘
                                     ▼
                                    Example Validated Datatrees (separate resources)
                                    ├── ITER.nc
                                    ├── WEST.nc
                                    └── MAST.nc
```

**Workflow**: Two parallel development streams converge to create comprehensive validation capabilities. In Phase 2, complete CDL interface definitions are developed for all equilibrium-related components, organized by their role as either equilibrium reconstruction inputs (pf_active, pf_passive, tf_active, wall, magnetics) or outputs (equilibrium). Phase 3 automated scripts process these CDL interface definitions to generate all corresponding IDS-specific JSON schemas simultaneously, while developers create base schemas for geometry containers, coordinate systems, and standard names separately to provide foundational validation components. Composite data-tree schemas inherit from both IDS schemas and base schemas to create comprehensive validation systems that validate complete multi-IDS datasets. The project releases the final datatree schema via Zenodo with DOI assignment, enabling researchers to validate their equilibrium datasets against the standard interface specifications. The project provides example datasets as separate netCDF resources.

## Phase 1: Foundation and Geometry Standards (Months 1-2)

The first phase establishes the technical foundation by developing comprehensive geometry specifications, geometry container frameworks, and metadata conventions for fusion data exchange. This phase creates the fundamental building blocks that enable self-describing datasets through standardized geometric representations and metadata systems.

### Fusion Conventions Geometry Specification Development

The primary deliverable of Phase 1 involves creating a comprehensive geometry specification within the Fusion Conventions that defines standardized approaches for representing tokamak geometric elements in data exchange formats. This specification establishes the foundational framework that all subsequent interface development will build upon.

The geometry specification defines standardized geometry types including points, vectors, lines, polygons, surfaces, and complex composite structures that can represent tokamak components from simple sensor positions to complex multi-element diagnostic arrays. Each geometry type includes complete metadata requirements, coordinate system specifications, and validation criteria that ensure geometric data travels with datasets while maintaining spatial context and enabling automated processing.

Multi-element geometry variants accommodate complex diagnostic configurations including multi-point sensor arrays, multi-vector field measurements, multi-line sight-line collections, multi-polygon boundary definitions, and multi-surface plasma-facing component assemblies. The specification provides clear guidelines for when to use each geometry type and how to combine them for complex tokamak structures.

### Geometry Container Framework Implementation

Building upon the Fusion Conventions geometry specification, the project develops practical geometry container implementations that translate the specification into working data structures. Geometry containers provide the mechanism for attaching geometric context to data variables through metadata attributes, establishing explicit spatial relationships without coordinate duplication.

Geometry containers support flexible representation of complex tokamak structures while ensuring essential spatial context travels with datasets, enabling complete data interpretation without external dependencies. Maintaining the link to established conventions ensures that third party tooling, such as the `ncgen` application, developed for these large communities can be utilised within the Fusion community. Geometry containers support flexible representation of complex tokamak structures while ensuring essential spatial context travels with datasets, enabling complete data interpretation without external dependencies.

Templates for geometry containers shall include standardized component identification systems, coordinate system transformation capabilities, and validation frameworks that ensure geometric consistency across different data sources and analysis codes. The framework provides clear pathways for linking to external CAD models while maintaining self-contained geometric representations for data exchange.

### Coordinate System and Metadata Convention Development

Comprehensive coordinate system specifications define standard representations for cylindrical coordinates (R, phi, Z), Cartesian coordinates (X, Y, Z), and specialized fusion coordinate systems including flux coordinates and field-aligned coordinates. Each coordinate system includes proper transformation relationships, datum specifications, and metadata requirements that enable automated coordinate conversions.

Metadata conventions establish standardized approaches for linking geometric containers to data variables, specifying coordinate system references, and maintaining spatial relationship information. These conventions ensure that geometric context remains explicitly attached to measurements throughout data processing workflows while supporting different coordinate representations as required by various analysis codes.

The coordinate system framework includes sufficient metadata linking to source equilibrium data for flux coordinates, enabling external codes to perform coordinate transforms while maintaining complete traceability of coordinate system definitions and their relationships to underlying physics calculations.

### Standard Names and Interface Definition Infrastructure

Foundation development for standard names provides the framework for unambiguous identification of physical quantities in interface specifications. While comprehensive standard name development remains outside this project scope, the infrastructure created here enables systematic placeholder management and future integration with community-wide standardization efforts.

Interface definition standards establish the framework for using Common Data Language (CDL) format with geometry container integration, namespacing conventions, and metadata linking approaches. These standards define concrete interfaces that enable interoperable data exchange by establishing specific data representation pathways rather than maintaining compatibility with existing IDS conventions that offer multiple optional approaches for the same physical quantities.

### Documentation Infrastructure and Community Integration

Comprehensive documentation infrastructure supports the geometry specification, container framework, and metadata conventions through automated documentation generation, validation examples, and practical implementation guidance. The documentation system provides clear pathways for integration with existing analysis frameworks.

**Deliverables:**

- Fusion Conventions Geometry Specification - Comprehensive geometry type definitions, metadata requirements, and validation criteria for tokamak data exchange
- geometry_base.schema.json - Foundational geometry container validation schemas implementing the Fusion Conventions specification
- coordinate_systems.schema.json - Coordinate system transformation and validation specifications for cylindrical (R, phi, Z) and Cartesian (X, Y, Z) systems
- geometry_container_framework.json - Complete implementation specifications for geometry containers with tokamak-specific extensions
- metadata_conventions.json - Standardized metadata linking conventions for geometric context attachment
- standard_names_map.json - Keyword-value mapping infrastructure for placeholder standard names with underscore prefixes
- CDL interface definition standards and namespacing conventions following Fusion Conventions
- MkDocs documentation infrastructure with automated GitHub Actions CI
- Repository integration with automated GitHub Pages deployment and community contribution pathways

## Phase 2: Complete Equilibrium Interface Development (Months 3-5)

Phase two develops comprehensive CDL interface specifications for all equilibrium-related components, organized by their role in equilibrium reconstruction workflows. This phase distinguishes between equilibrium reconstruction input data and equilibrium reconstruction output data that other codes require.

### Equilibrium Reconstruction Input Interfaces

Input interfaces define the experimental measurements and geometric specifications required by equilibrium reconstruction codes. These interfaces ensure standardized formats for all data that feeds into equilibrium analysis workflows.

#### Poloidal Field System Inputs

PF active system interfaces define coil geometry specifications, current control parameters, and operational measurements required for equilibrium reconstruction. PF passive system interfaces encompass conducting structure geometries and electromagnetic response characteristics that affect plasma equilibrium.

#### Toroidal Field System Inputs

TF active system interfaces define toroidal field coil geometry specifications, current control parameters, and operational measurements. These interfaces provide standardized formats for toroidal field system data required for equilibrium reconstruction magnetic field calculations and plasma confinement analysis.

#### Diagnostic Measurement Inputs

Magnetic sensor interfaces define probe geometries, measurement specifications, and calibration metadata for all diagnostic systems. Interface specifications accommodate magnetic probes, flux loops, Rogowski coils, and diamagnetic loops with standardized variable naming and geometry container links.

#### Boundary Condition Inputs

Wall interface specifications define first wall geometries, material properties, and conducting structure data required for equilibrium boundary conditions.

### Equilibrium Reconstruction Output Interfaces

Output interfaces define the computational results and derived quantities that equilibrium reconstruction codes produce for use by other analysis codes. These interfaces standardize flux surface representations, safety factor calculations, and plasma boundary definitions.

#### Plasma State Outputs

Equilibrium solver interfaces define flux coordinate systems, magnetic axis and x-point locations, separatrix topology, and divertor strike point locations. Current density profile interfaces define spatial coordinate specifications and interpolation requirements for different coordinate representations. Safety factor profiles and flux surface geometry specifications with proper metadata linking to source calculations.

#### Derived Quantity Outputs

Magnetic field representations on coordinate grids for use by transport and heating codes. Plasma volume and surface area calculations required for global analysis. Coordinate transformation matrices between different coordinate systems.

### Multi-Machine Implementation

CDL interface implementations cover ITER design specifications, WEST experimental configurations, and MAST operational setups to ensure broad applicability across different tokamak designs. Each implementation demonstrates interface flexibility while maintaining core compatibility requirements for both input and output data specifications.

**Deliverables:**

Complete CDL interface specifications organized by equilibrium workflow role:

Equilibrium Input Interfaces:

- pf_active.cdl
- pf_passive.cdl
- tf_active.cdl
- wall.cdl
- magnetics.cdl

Equilibrium Output Interfaces:

- equilibrium.cdl

**Note:** While the CDL file names correspond to Data Dictionary IDS names for organizational clarity, these CDL specifications do not intend to reproduce all functionality within an IDS. These CDL interfaces define concrete interfaces for data interoperability that eliminate ambiguity in data representation - for this reason, we cannot maintain a link between the Data Dictionary IDSs and these structures. The Data Dictionary IDSs may provide inspiration, but maintaining a direct link is neither necessary nor desirable. These CDL interfaces focus specifically on equilibrium reconstruction data exchange requirements rather than comprehensive IDS implementation.

## Phase 3: Schema Generation and Validation (Months 6-7)

Phase three develops automated processing algorithms to convert all CDL interface definitions into corresponding JSON validation schemas and establishes comprehensive validation capabilities for equilibrium data exchange workflows.

### CDL-to-JSON Schema Conversion

Automated conversion algorithms parse the complete set of CDL interface definitions developed in Phase 2 and generate corresponding JSON schemas that enforce the specified interface requirements. These algorithms process variable definitions, dimensional constraints, standard name requirements, and geometry metadata specifications to create comprehensive validation schemas for both equilibrium input and output data.

The conversion system handles all CDL variable declarations, attribute specifications, and dimensional requirements while generating appropriate JSON schema validation rules. Standard name mapping integration ensures that placeholder standard names are properly incorporated into the validation system with appropriate references to the standard_names_map.json resource.

### Complete Schema Integration

The conversion algorithms generate IDS-specific schemas that integrate with the foundational geometry and coordinate system schemas developed in Phase 1. Composite schema generation combines base validation components with IDS-specific requirements to create comprehensive validation systems that support complete equilibrium reconstruction workflows.

Schema composition ensures that geometry container references, coordinate system specifications, and standard name requirements are properly validated across all interface components while maintaining compatibility with the foundational schemas from Phase 1.

### Comprehensive Validation Framework

Automated testing systems validate the conversion algorithms and generated schemas using the complete CDL specification set. Testing ensures that generated schemas properly enforce interface requirements for both equilibrium inputs and outputs while maintaining compatibility with the geometry container framework and standard name conventions.

**Deliverables:**

- CDL-to-JSON schema conversion algorithms and processing scripts
- Complete IDS-specific JSON schemas for all equilibrium components:
  - pf_active.schema.json
  - pf_passive.schema.json
  - tf_active.schema.json
  - wall.schema.json
  - magnetics.schema.json
  - equilibrium.schema.json
- Composite data-tree schema for complete equilibrium workflows:
  - datatree.schema.json
- Comprehensive validation testing framework

## Phase 4: Data Population and Validation (Months 8-9)

Phase four populates the interface specifications with actual geometric and experimental data for ITER, WEST, and MAST tokamaks, creating comprehensive data-trees that demonstrate practical interface implementation and validation.

### Multi-Machine Data Integration

Data-trees shall be created containing actual geometric specifications, experimental measurements, and computational results for each target machine. These data-trees demonstrate interface scalability across different tokamak configurations while maintaining consistency through standardized variable naming and geometry container implementations.

ITER data integration includes design specifications, planned diagnostic configurations, and anticipated operational scenarios. WEST data encompasses experimental magnetic sensor measurements, equilibrium reconstructions, and associated plasma profile data. MAST data includes spherical tokamak-specific configurations and unique diagnostic arrangements.

### Comprehensive Validation Testing

All populated data-trees shall undergo comprehensive validation testing using the schema systems developed in earlier phases. Validation testing ensures geometry container consistency, variable naming compliance, dimensional correctness, and cross-IDS compatibility across all implementations.

Validation results identify any remaining interface specification issues and guide final refinements to ensure robust data exchange capabilities. Testing includes both individual IDS validation and complete data-tree validation with cross-reference verification.

### Performance and Scalability Assessment

Performance testing evaluates interface efficiency for different data access patterns and computational workflows. Scalability assessment ensures interface specifications support both small diagnostic datasets and large simulation outputs without computational bottlenecks.

**Deliverables:**

- ITER.nc, WEST.nc, MAST.nc - Populated example data-trees with actual geometric and experimental data
- Comprehensive validation testing results using datatree.schema.json
- Performance and scalability assessment reports
- Refined interface specifications based on validation feedback

## Phase 5: Documentation, Integration, and Release (Months 10-12)

The final phase completes comprehensive documentation, establishes automated publishing workflows, and ensures long-term maintenance capabilities for the standard interfaces.

### Comprehensive Documentation System

Complete documentation shall include technical specifications, usage guides, implementation examples, and best practices for all interface components. Documentation structure supports both tutorial-style learning paths and reference-style technical specifications with automated cross-references and example validation.

Usage examples demonstrate complete workflows from data acquisition through analysis with real datasets from all target machines. These examples serve as both documentation and validation testing for interface implementations while providing practical guidance for adoption across different research groups.

### Automated Publishing and Maintenance

GitHub Actions workflows shall automate documentation building, schema generation, example testing, and release packaging. Automated systems ensure documentation consistency with code development while maintaining up-to-date examples and validation results.

Release workflows include automated Zenodo publishing with versioned DOI assignment for the global datatree.schema.json file. The GitHub CI shall automatically embed DOIs for both the global interface schema and the standard names dictionary within all IDS CDL files to ensure persistent references are maintained throughout the interface specifications.

**Deliverables:**

**Comprehensive Documentation System:**

- Technical specifications documentation for all interface components with automated cross-references
- Usage guides with tutorial-style learning paths and reference-style technical specifications
- Implementation examples demonstrating complete workflows from data acquisition through analysis
- Best practices documentation for interface adoption across different research groups
- Real dataset examples from ITER, WEST, and MAST demonstrating practical implementation
- Validation testing documentation serving as both examples and implementation guidance

**Automated Publishing and Maintenance:**

- GitHub Actions workflows for automated documentation building and deployment
- GitHub Actions workflows for automated schema generation from CDL definitions
- Release packaging workflows with version control and dependency management
- Zenodo publishing workflows with versioned DOI assignment for global datatree schema
- Automated DOI embedding in all IDS CDL files for persistent reference maintenance
- Continuous integration systems ensuring documentation consistency with code development

## Key Technical Requirements

The implementation develops comprehensive data exchange interfaces that attach geometric and measurement context to data variables through metadata attributes, establishing the foundation for reproducible fusion data analysis. The geometry container concept enables explicit spatial context specification without coordinate duplication, supporting standardized coordinate systems for cylindrical, Cartesian, and flux coordinates with proper transformation relationships for interoperable magnetics equilibrium data exchange.

Interface specifications encompass variable names, dimensions, standard names, units, and geometry metadata requirements from magnetic sensors through equilibrium solver outputs. The composable JSON schema validation system enforces geometric consistency, variable naming compliance, dimensional correctness, and cross-IDS compatibility while supporting multi-machine data-trees with different tokamak configurations.

CDL template implementations must follow established IDS namespacing conventions with geometry container-based prefixes enabling variable organization without excessive nesting structures. The validation infrastructure must support complete magnetics equilibrium data representations from experimental data acquisition through computational analysis results while maintaining geometry container consistency across all components.

Automated schema generation from CDL definitions requires processing scripts that compose base validation schemas with IDS-specific templates to produce comprehensive validation systems capable of validating complete data-trees in single operations. Documentation automation must ensure consistency between code development and usage examples while supporting continuous integration testing throughout the development cycle.

## Deliverables and Timeline

The project deliverables include geometry_base.schema.json and coordinate_systems.schema.json for foundational validation following CF Conventions and ITER Fusion Conventions, standard_names_map.json for placeholder standard name management, complete CDL interface definitions (pf_active.cdl, pf_passive.cdl, tf_active.cdl, wall.cdl, magnetics.cdl, equilibrium.cdl) following established IDS namespacing conventions, corresponding IDS-specific validation schemas (pf_active.schema.json, pf_passive.schema.json, tf_active.schema.json, wall.schema.json, magnetics.schema.json, equilibrium.schema.json), composite datatree.schema.json for complete multi-IDS dataset validation released via Zenodo with DOI assignment, populated example datasets (ITER.nc, WEST.nc, MAST.nc) demonstrating practical implementation, automated processing scripts for CDL-to-schema conversion and continuous integration testing, and comprehensive documentation system with extensive usage examples and automated GitHub CI builds.

The timeline spans twelve months with Phase 1 establishing geometry container foundations and interface standards, Phase 2 implementing complete equilibrium interface definitions organized by workflow role (inputs vs outputs), Phase 3 developing automated CDL-to-JSON schema conversion and generating all validation schemas, Phase 4 populating interfaces with actual data and conducting validation testing, and Phase 5 completing documentation automation and establishing long-term maintenance workflows. Continuous integration testing throughout development maintains consistency with Fusion Conventions while automated documentation ensures accessibility and adoption across the research community.

## Success Metrics and Impact

Success metrics include validated interface implementations across three different tokamak configurations, comprehensive documentation with automated builds and extensive usage examples, demonstrated magnetics equilibrium data representations from experimental measurements through computational analysis results, and established maintenance workflows ensuring long-term interface evolution based on community requirements.

The project impact extends beyond immediate deliverables to establish the foundation for interoperable fusion data exchange that enables reproducible research, cross-facility comparisons, and integrated analysis workflows. By providing concrete interfaces with standardized variable names, dimensions, and geometry metadata, the project addresses the critical barrier preventing meaningful data integration across different fusion research facilities and computational frameworks.

Long-term impact includes enabling automated data analysis pipelines that span multiple facilities, supporting advanced machine learning applications through consistent data representations, facilitating collaborative research through standardized data exchange protocols, and establishing the foundation for comprehensive fusion data repositories that serve the broader research community. These outcomes advance fusion science by removing data interoperability barriers and enabling the collaborative analysis approaches essential for achieving fusion energy goals.
Success metrics include validated interface implementations across three different tokamak configurations, comprehensive documentation with automated builds and extensive usage examples, demonstrated magnetics equilibrium data representations from experimental measurements through computational analysis results, and established maintenance workflows ensuring long-term interface evolution based on community requirements.

The project impact extends beyond immediate deliverables to establish the foundation for interoperable fusion data exchange that enables reproducible research, cross-facility comparisons, and integrated analysis workflows. By providing concrete interfaces with standardized variable names, dimensions, and geometry metadata, the project addresses the critical barrier preventing meaningful data integration across different fusion research facilities and computational frameworks.

Long-term impact includes enabling automated data analysis pipelines that span multiple facilities, supporting advanced machine learning applications through consistent data representations, facilitating collaborative research through standardized data exchange protocols, and establishing the foundation for comprehensive fusion data repositories that serve the broader research community. These outcomes advance fusion science by removing data interoperability barriers and enabling the collaborative analysis approaches essential for achieving fusion energy goals.
