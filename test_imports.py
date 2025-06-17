#!/usr/bin/env python3
"""Test script to verify imports work correctly."""

try:
    from standard_interfaces.pydantic_validator import CoordinateModel, StandardAttrs

    print("✓ Imports successful")

    # Test basic StandardAttrs
    attrs = StandardAttrs(standard_name=None, units=None)
    print(f"✓ StandardAttrs created: {attrs}")

    # Test basic CoordinateModel
    model = CoordinateModel()
    print(f"✓ CoordinateModel created: {model}")

    print("All basic tests passed!")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback

    traceback.print_exc()
