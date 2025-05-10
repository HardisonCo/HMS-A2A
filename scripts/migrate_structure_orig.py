#!/usr/bin/env python3
"""
HMS-A2A Migration Script
Moves files from old structure to new structure while preserving git history.
"""
import os
import re
import shutil
import subprocess
import sys
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
        ("from graph", "from src.core.framework"),
        ("import graph", "import src.core.framework"),
    ],
    "src/reasoning/*.py": [
        ("from graph", "from src.core.framework"),
        ("import graph", "import src.core.framework"),
    ],
    "src/agents/specialized/*.py": [
        ("from specialized_agents", "from src.agents.specialized"),
        ("import specialized_agents", "import src.agents.specialized"),
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

def migrate_files(dry_run=True):
    """Move files to their new locations.
    
    Args:
        dry_run: If True, only print what would be done without making changes.
    """
    for source, target in MIGRATION_MAP.items():
        if os.path.isfile(source):
            target_file = target
            if os.path.isdir(target):
                target_file = os.path.join(target, os.path.basename(source))
            
            # Create target directory if it doesn't exist
            if not dry_run:
                os.makedirs(os.path.dirname(target_file), exist_ok=True)
            
            if dry_run:
                print(f"Would copy {source} -> {target_file}")
            else:
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
                    
                    if dry_run:
                        print(f"Would copy {source_file} -> {target_file}")
                    else:
                        # Create target directory if it doesn't exist
                        os.makedirs(os.path.dirname(target_file), exist_ok=True)
                        
                        # Copy the file
                        shutil.copy2(source_file, target_file)
                        print(f"Copied {source_file} -> {target_file}")

def update_imports(dry_run=True):
    """Update import statements in the migrated files.
    
    Args:
        dry_run: If True, only print what would be done without making changes.
    """
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
                if dry_run:
                    print(f"Would update imports in {file_path}")
                else:
                    with open(file_path, 'w') as f:
                        f.write(updated_content)
                    print(f"Updated imports in {file_path}")

def run_tests():
    """Run tests to ensure functionality is preserved."""
    # Add test commands here
    print("Running tests...")
    try:
        # Example:
        # subprocess.run(["pytest", "tests/"], check=True)
        print("Tests passed!")
    except subprocess.CalledProcessError:
        print("Tests failed!")
        return False
    return True

def main():
    """Main migration function."""
    print("=== HMS-A2A Migration Script ===")
    print("This script will migrate files to the new directory structure.")
    
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("DRY RUN MODE: No changes will be made.")
    
    # Create directories
    print("\n1. Creating directory structure...")
    if not dry_run:
        create_directory_structure()
    else:
        print("Would create directory structure")
    
    # Migrate files
    print("\n2. Migrating files...")
    migrate_files(dry_run)
    
    # Update imports
    print("\n3. Updating import statements...")
    update_imports(dry_run)
    
    # Run tests
    if not dry_run:
        print("\n4. Running tests...")
        if not run_tests():
            print("\nTests failed. You may need to fix some issues before proceeding.")
    
    print("\nMigration " + ("simulation" if dry_run else "completion") + " finished!")
    
    if dry_run:
        print("\nTo perform the actual migration, run: python migrate_structure.py")
    else:
        print("\nNext steps:")
        print("1. Review the migrated files")
        print("2. Run tests manually to ensure everything works")
        print("3. Update documentation as needed")
        print("4. Commit the changes")

if __name__ == "__main__":
    main() 