#!/usr/bin/env python3
"""
Comprehensive folder reorganization script for HMS-A2A project.
This script properly moves all root folders into the src structure based on their purpose.
"""

import os
import sys
import shutil
from pathlib import Path

# Base project directory
BASE_DIR = Path(".")

# Mapping of root directories to their target locations in the src structure
FOLDER_MAPPING = {
    "common": "src/common",
    "examples": "src/examples",
    "finala2e": "src/domains/economic",  # Financial A2E components
    "genetic_theorem_prover": "src/domains/ga",  # Genetic theorem prover goes to genetic algorithms domain
    "gov_agents": "src/agents/gov",  # Government agents
    "graph": "src/core/graph",  # Graph utilities likely part of core
    "integration": "src/core/integration",  # Integration components to core
    "lean4_economic_foundations": "src/domains/economic/foundations",  # Economic foundations
    "mac": "src/domains/economic/mac",  # Market And Coordinator likely economic domain
    "prover-orchestrator": "src/domains/verification/prover",  # Prover goes to verification domain
    "schemas": "src/schemas",  # Keep schemas separate
    "scripts": "scripts",  # Keep scripts at root level
    "trade_balance": "src/domains/economic/trade"  # Trade balance to economic domain
}

def ensure_directory(path):
    """Ensure directory exists, create if not."""
    path.mkdir(parents=True, exist_ok=True)
    return path

def create_init_files(directory):
    """Create __init__.py files in directory and all subdirectories."""
    for root, dirs, files in os.walk(directory):
        init_file = Path(root) / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            print(f"✓ Created {init_file}")

def move_directory_contents(source, target):
    """Move all contents from source to target directory."""
    source_path = BASE_DIR / source
    target_path = BASE_DIR / target
    
    # Skip if source doesn't exist
    if not source_path.exists():
        print(f"✗ Source directory {source} does not exist, skipping.")
        return False
    
    # Create target directory
    ensure_directory(target_path)
    
    try:
        # Check if this is a straight move or we need to merge contents
        if not target_path.exists() or not any(target_path.iterdir()):
            # If target is empty or doesn't exist, we can do a simple move
            print(f"Moving {source} -> {target}")
            
            # Copy all files and subdirectories
            for item in source_path.iterdir():
                if item.is_dir():
                    shutil.copytree(item, target_path / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, target_path)
        else:
            # Target exists and has content, we need to merge
            print(f"Merging {source} into existing {target}")
            
            # Copy files, merging directories as needed
            for item in source_path.iterdir():
                if item.is_dir():
                    target_subdir = target_path / item.name
                    if not target_subdir.exists():
                        shutil.copytree(item, target_subdir)
                    else:
                        # Recursive merge for directories
                        for sub_item in item.iterdir():
                            if sub_item.is_dir():
                                shutil.copytree(sub_item, target_subdir / sub_item.name, dirs_exist_ok=True)
                            else:
                                shutil.copy2(sub_item, target_subdir)
                else:
                    target_file = target_path / item.name
                    if not target_file.exists():
                        shutil.copy2(item, target_path)
                    else:
                        # Rename duplicate file
                        backup_file = target_path / f"{item.stem}_orig{item.suffix}"
                        shutil.copy2(item, backup_file)
                        print(f"  ⚠ File {item.name} already exists in target, saved as {backup_file.name}")
        
        # Once moved, create __init__.py files
        create_init_files(target_path)
        
        # Once moved, remove the original folder (after successful copy)
        if source != "scripts":  # Keep scripts at root level
            shutil.rmtree(source_path)
            print(f"✓ Removed original directory {source} after move")
        
        return True
    except Exception as e:
        print(f"✗ Failed to move {source} to {target}: {str(e)}")
        return False

def clean_empty_directories():
    """Remove any empty directories at the root level."""
    for item in BASE_DIR.iterdir():
        if item.is_dir() and item.name not in ["src", "scripts", "docs", ".git", "__pycache__"]:
            try:
                # Check if directory is empty
                if not any(item.iterdir()):
                    os.rmdir(item)
                    print(f"✓ Removed empty directory: {item.name}")
            except Exception as e:
                print(f"✗ Failed to check/remove directory {item.name}: {str(e)}")

def update_readme():
    """Update or create a README explaining the new structure."""
    readme_content = """# HMS-A2A Project

## Directory Structure

- `src/` - All source code
  - `src/core/` - Core framework components
  - `src/agents/` - Agent implementations
    - `src/agents/gov/` - Government agents
    - `src/agents/specialized/` - Specialized agents
  - `src/domains/` - Domain-specific modules
    - `src/domains/economic/` - Economic models and foundations
    - `src/domains/verification/` - Verification frameworks
    - `src/domains/ga/` - Genetic algorithms and optimizations
  - `src/common/` - Common utilities
  - `src/schemas/` - Schema definitions
  - `src/examples/` - Example implementations
- `scripts/` - Utility scripts
- `docs/` - Documentation

## Migration Notes

The codebase has been reorganized from a flat structure to this hierarchical one.
You may need to update import paths in your code.
"""
    
    readme_path = BASE_DIR / "README.md"
    
    try:
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print(f"✓ Updated README.md with new structure information")
    except Exception as e:
        print(f"✗ Failed to update README.md: {str(e)}")

def create_import_fix_guidelines():
    """Create a guide for fixing imports after reorganization."""
    guide_content = """# Import Fix Guidelines

After the reorganization, you'll need to update imports in your Python files.
Here are some common patterns:

## Before:
```python
from common.utils import helper
import gov_agents.ustda_agent as ustda
from mac.economist_agent import EconomistAgent
```

## After:
```python
from src.common.utils import helper
import src.agents.gov.ustda_agent as ustda
from src.domains.economic.mac.economist_agent import EconomistAgent
```

## Tips for updating imports:
1. Use find & replace across the codebase
2. For each file, check its imports first before running it
3. Consider using relative imports in tests and examples

## Common replacements:
- `from common` → `from src.common`
- `from gov_agents` → `from src.agents.gov`
- `from mac` → `from src.domains.economic.mac`
- `from trade_balance` → `from src.domains.economic.trade`
- `from genetic_theorem_prover` → `from src.domains.ga`
"""
    
    guide_path = BASE_DIR / "IMPORT_GUIDELINES.md"
    
    try:
        with open(guide_path, 'w') as f:
            f.write(guide_content)
        print(f"✓ Created IMPORT_GUIDELINES.md with instructions for fixing imports")
    except Exception as e:
        print(f"✗ Failed to create import guidelines: {str(e)}")

def main():
    """Main function to reorganize the folders."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("Starting comprehensive folder reorganization...")
    
    # Ensure src directory exists
    ensure_directory(BASE_DIR / "src")
    
    # Create __init__.py in src
    init_file = BASE_DIR / "src" / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        print(f"✓ Created {init_file}")
    
    # Process each folder mapping
    print("\nMoving folders to proper locations:")
    for source, target in FOLDER_MAPPING.items():
        move_directory_contents(source, target)
    
    # Clean up any empty directories
    print("\nCleaning up empty directories:")
    clean_empty_directories()
    
    # Update README with new structure
    print("\nUpdating documentation:")
    update_readme()
    create_import_fix_guidelines()
    
    print("\nReorganization completed.")
    print("NOTE: You will need to update import statements in your code.")
    print("See IMPORT_GUIDELINES.md for assistance.")

if __name__ == "__main__":
    main() 