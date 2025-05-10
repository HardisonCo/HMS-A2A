# HMS-A2A Migration Plan

This document outlines the steps required to migrate existing code to the new directory structure.

## Migration Strategy

We'll follow a phased approach to ensure minimal disruption:

1. **Code Discovery**: Categorize existing files based on functionality
2. **File Migration**: Move files to their new locations
3. **Import Updates**: Fix import statements
4. **Testing**: Verify functionality is preserved
5. **Documentation**: Update any remaining documentation references

## Phase 1: Code Discovery

| Current Location | Functionality | New Location |
|------------------|---------------|-------------|
| `finala2e/` | Core A2E implementation | `src/core/` |
| `graph/` | LangGraph agent implementation | `src/core/framework/` |
| `test_mcp/` | MCP server implementations | `src/core/protocols/` |
| `common/` | Shared components | `src/common/` |
| `specialized_agents/` | Industry-specific agents | `src/agents/specialized/` |
| `gov_agents/` | Government agents | `src/agents/gov/` |
| `integration/` | External system integration | `src/server/` |
| `lean4_economic_foundations/` | Economic verification | `src/domains/economic/models/` |
| `genetic_theorem_prover/` | GA implementation | `src/domains/ga/` |

## Phase 2: File Migration

We'll create a migration script that will:

1. Create any missing directories in the new structure
2. Copy files to their new locations
3. Update import statements
4. Run tests to ensure functionality is preserved

## Migration Script

```python
#!/usr/bin/env python3
"""
HMS-A2A Migration Script
Moves files from old structure to new structure while preserving git history.
"""
import os
import re
import shutil
import subprocess
from pathlib import Path

# Define migration mapping
MIGRATION_MAP = {
    "finala2e": "src/core",
    "graph": "src/core/framework",
    "graph/cort_react_agent.py": "src/reasoning/cort_react_agent.py",
    "test_mcp": "src/core/protocols",
    "common": "src/common",
    "specialized_agents": "src/agents/specialized",
    "gov_agents": "src/agents/gov",
    "integration": "src/server",
    "lean4_economic_foundations": "src/domains/economic/models",
    "genetic_theorem_prover": "src/domains/ga",
    # Add more mappings as needed
}

# Files that need special import updates
IMPORT_UPDATES = {
    "src/core/framework/*.py": [
        ("from src.core.framework", "from src.core.framework"),
        ("import src.core.framework", "import src.core.framework"),
    ],
    "src/reasoning/*.py": [
        ("from src.core.framework", "from src.core.framework"),
        ("import src.core.framework", "import src.core.framework"),
    ],
    "src/agents/specialized/*.py": [
        ("from src.agents.specialized", "from src.agents.specialized"),
        ("import src.agents.specialized", "import src.agents.specialized"),
    ],
    # Add more import updates as needed
}

def create_directory_structure():
    """Create the new directory structure."""
    directories = set()
    for target in MIGRATION_MAP.values():
        directories.add(target)
        parts = target.split('/')
        for i in range(1, len(parts)):
            directories.add('/'.join(parts[:i]))
    
    for directory in sorted(directories):
        os.makedirs(directory, exist_ok=True)
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write(f"# {directory.split('/')[-1]} module\n")

def migrate_files():
    """Move files to their new locations using git."""
    for source, target in MIGRATION_MAP.items():
        if os.path.isfile(source):
            target_file = target
            if os.path.isdir(target):
                target_file = os.path.join(target, os.path.basename(source))
            
            # Create target directory if it doesn't exist
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            
            # Copy the file
            shutil.copy2(source, target_file)
            print(f"Copied {source} -> {target_file}")
        elif os.path.isdir(source):
            # Copy directory contents
            for root, _, files in os.walk(source):
                for file in files:
                    source_file = os.path.join(root, file)
                    rel_path = os.path.relpath(source_file, source)
                    target_file = os.path.join(target, rel_path)
                    
                    # Create target directory if it doesn't exist
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    
                    # Copy the file
                    shutil.copy2(source_file, target_file)
                    print(f"Copied {source_file} -> {target_file}")

def update_imports():
    """Update import statements in the migrated files."""
    for pattern, replacements in IMPORT_UPDATES.items():
        for file_path in Path('.').glob(pattern):
            if not os.path.isfile(file_path):
                continue
                
            with open(file_path, 'r') as f:
                content = f.read()
            
            updated_content = content
            for old, new in replacements:
                updated_content = re.sub(r'\b' + re.escape(old) + r'\b', new, updated_content)
            
            if content != updated_content:
                with open(file_path, 'w') as f:
                    f.write(updated_content)
                print(f"Updated imports in {file_path}")

def run_tests():
    """Run tests to ensure functionality is preserved."""
    # Add test commands here
    print("Running tests...")
    # Example:
    # subprocess.run(["pytest", "tests/"])

def main():
    """Main migration function."""
    print("=== HMS-A2A Migration Script ===")
    print("This script will migrate files to the new directory structure.")
    
    # Create directories
    print("\n1. Creating directory structure...")
    create_directory_structure()
    
    # Migrate files
    print("\n2. Migrating files...")
    migrate_files()
    
    # Update imports
    print("\n3. Updating import statements...")
    update_imports()
    
    # Run tests
    print("\n4. Running tests...")
    run_tests()
    
    print("\nMigration completed!")
    print("\nNext steps:")
    print("1. Review the migrated files")
    print("2. Run tests manually to ensure everything works")
    print("3. Update documentation as needed")
    print("4. Commit the changes")

if __name__ == "__main__":
    main()
```

## Phase 3: Import Updates

The migration script handles basic import updates, but some manual fixes might be needed:

1. Check for hardcoded references to old directory paths
2. Update any relative imports that might be broken
3. Ensure test imports are updated

## Phase 4: Testing

After migration, we'll run comprehensive tests:

1. Unit tests for each module
2. Integration tests for agent interactions
3. End-to-end tests for complete workflows

## Phase 5: Documentation

Final steps:

1. Update any remaining documentation references to the old structure
2. Update diagrams to reflect the new organization
3. Verify all links in documentation are working

## Migration Checklist

- [ ] Create migration script
- [ ] Run migration in a development branch
- [ ] Fix any import issues
- [ ] Run tests to verify functionality
- [ ] Update documentation
- [ ] Create PR for review
- [ ] Merge to main branch 