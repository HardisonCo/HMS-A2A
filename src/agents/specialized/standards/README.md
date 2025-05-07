# Standards Validation and Migration

This directory contains modules for standards validation, conversion, and management in the HMS-A2A system.

## Overview

The Standards package provides tools for:

1. **Standards Validation**: Validate content against domain-specific standards
2. **Standards Conversion**: Convert standards from HMS-SME format to HMS-A2A format
3. **Standards Migration**: Migrate entire standards databases between formats

## Components

### StandardsRegistry

The StandardsRegistry is a singleton class that manages standards for various domains. It provides caching, domain-specific lookups, and support for multiple standards formats.

```python
from src.agents.specialized.standards_validation import StandardsRegistry

# Get the singleton instance
registry = StandardsRegistry.get_instance()

# Get a specific standard
healthcare_standard = registry.get_standard("STD-HEALTHCARE_PROTOCOL")

# Get all standards for a domain
finance_standards = registry.get_standards_for_domain("finance")
```

### StandardsValidator

The StandardsValidator provides validation against standards, including structure validation for Deal components, content validation, and compliance checking.

```python
from src.agents.specialized.standards_validation import StandardsValidator, ValidationResult

# Create a validator
validator = StandardsValidator()

# Validate a piece of content
result = validator.validate_content(content, standard_id="STD-HEALTHCARE_PROTOCOL")

# Check validation result
if result.is_valid:
    print("Content is valid!")
else:
    print(f"Validation failed with {len(result.violations)} violations")
    for violation in result.violations:
        print(f"- {violation.message} (severity: {violation.severity})")
```

### StandardsConverter

The StandardsConverter transforms standards between different formats, primarily from HMS-SME format to HMS-A2A format.

```python
from src.agents.specialized.standards import StandardsConverter

# Create converter
converter = StandardsConverter()

# Convert a standards file
result = converter.convert_standards_file(
    "/path/to/hms_sme_standards.json",
    "/path/to/output/a2a_standards.json"
)

print(f"Converted {result['standards_count']} standards")
```

## Migration Tools

### standards_migration.py

A script for migrating entire standards databases from HMS-SME to HMS-A2A format.

```bash
# Run migration script
python specialized_agents/standards/standards_migration.py --source /path/to/standards
```

### migrate_standards.sh

A shell script that automates the entire migration process:

```bash
# Run migration script with auto-detection
./scripts/migration/migrate_standards.sh

# Specify source explicitly
./scripts/migration/migrate_standards.sh --source /path/to/standards
```

## Directory Structure

The standards data is organized in the following directory structure:

```
data/
└── standards/
    ├── source/         # Source standards files
    ├── converted/      # Converted individual standards files
    ├── merged/         # Merged standards databases
    └── standards.json  # Symlink to latest standards database
```

## Usage Examples

### Validating a Document Against Standards

```python
from src.agents.specialized.standards_validation import StandardsValidator

validator = StandardsValidator()

# Validate a medical report
result = validator.validate_content(
    medical_report, 
    standard_id="STD-MEDICAL_DOCUMENTATION"
)

# Handle validation result
if not result.is_valid:
    print("Medical report has the following issues:")
    for violation in result.violations:
        print(f"- {violation.message}")
```

### Converting HMS-SME Standards to HMS-A2A Format

```python
from src.agents.specialized.standards import StandardsConverter

converter = StandardsConverter()

# Convert industry standards
converter.convert_industry_standards(
    "source/industry_standards.json",
    "converted/a2a_industry_standards.json"
)

# Merge multiple standards files
converter.merge_standards_files(
    ["converted/a2a_file1.json", "converted/a2a_file2.json"],
    "merged/complete_standards.json"
)
```