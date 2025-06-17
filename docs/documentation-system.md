# Documentation Generation System

This document describes the cleaned-up documentation generation system for the imas-standard-interfaces project.

## Overview

The documentation system centers on a unified command-line interface that provides:

- **Primary CLI**: `docs.py` - Click-based interface for all documentation tasks
- **Core Generator**: `scripts/generate_docs.py` - The main documentation generator

## Architecture

```text
docs/
├── scripts/
│   ├── generate_docs.py          # Main generator (json-schema-for-humans)
│   └── generate_cdl_docs.py      # CDL-specific documentation
├── docs.py                       # Primary CLI entry point
└── docs/                         # Generated documentation output
```

## Usage

### Primary Commands

```bash
# Main entry point (recommended)
python docs.py generate
pixi run build-docs

# Alternative using scripts directly
python scripts/generate_docs.py
```

### Development Commands

```bash
# Serve documentation locally
python docs.py dev-serve
python docs.py serve

# Clean and build
python docs.py clean
python docs.py build
```

## Features

### Modern Documentation Generator (`scripts/generate_docs.py`)

- Uses `json-schema-for-humans` for rich, interactive documentation
- Generates both HTML and Markdown output
- Supports schema categorization
- Creates index pages and cross-references
- Includes CSS and JavaScript for interactive features
- Proper error handling and cleanup

### Click-based CLI (`docs.py`)

- Modern click-based command interface
- Supports commands: generate, serve, build, deploy, clean
- Interactive prompts for deployment options
- Proper error handling and user feedback
- Integrated with uv/pixi workflows

### Development Tools

- **Local Server**: `serve.py` provides HTTP server for testing
- **Management Script**: `manage.py` provides comprehensive workflow management
- **CDL Integration**: Ready for CDL dataset HTML embedding

## Configuration

- **MkDocs**: `mkdocs.yml` for site generation
- **Pixi**: `pyproject.toml` task definitions
- **Dependencies**: Managed through `uv` and pixi

## Future Enhancements

The cleaned-up structure enables:

1. **CDL Dataset Integration**: Easy addition of MkDocs plugin for `{{ cdl:category:filename }}` tags
2. **Enhanced Validation**: Pre-generation schema validation
3. **Performance Optimization**: Caching and incremental builds
4. **Custom Themes**: Easier customization of generated documentation

## Dependencies

- `json-schema-for-humans>=0.47.0` - Primary documentation generator
- `mkdocs>=1.5.0` - Static site generation
- `mkdocs-material>=9.4.0` - Material theme
- `click>=8.2.1` - Command-line interfaces
