#!/usr/bin/env python3
"""
HMS-A2A Unused File Cleanup

This script identifies and optionally removes files that have been migrated 
to the new structure and are no longer needed in their original locations.
"""
import os
import shutil
import sys
from pathlib import Path

# Define directories to check for unused files after migration
ORIGINAL_DIRS = [
    "finala2e",
    "graph",
    "test_mcp",
    "common",
    "specialized_agents",
    "gov_agents",
    "integration",
    "lean4_economic_foundations",
    "genetic_theorem_prover",
]

# Files that shouldn't be removed (key config files, etc.)
KEEP_FILES = [
    "README.md",
    "pyproject.toml",
    "setup.py",
    "requirements.txt",
    ".gitignore",
    "LICENSE",
]

def find_migrated_files():
    """Find all files that have been migrated to the new structure.
    
    Returns:
        list: Paths of original files that have been migrated
    """
    migrated_files = []
    
    # Check if the new structure exists
    if not os.path.exists("src"):
        print("Error: src/ directory not found. Migration may not have been completed.")
        return []
    
    # Walk through original directories and check if files exist in new structure
    for original_dir in ORIGINAL_DIRS:
        if not os.path.exists(original_dir):
            continue
            
        for root, _, files in os.walk(original_dir):
            for file in files:
                # Skip special files
                if file in KEEP_FILES:
                    continue
                
                original_file = os.path.join(root, file)
                rel_path = os.path.relpath(original_file, original_dir)
                
                # Check various potential new locations
                potential_new_locations = [
                    os.path.join("src/core", rel_path),
                    os.path.join("src/core/framework", rel_path),
                    os.path.join("src/core/protocols", rel_path),
                    os.path.join("src/common", rel_path),
                    os.path.join("src/agents/specialized", rel_path),
                    os.path.join("src/agents/gov", rel_path),
                    os.path.join("src/server", rel_path),
                    os.path.join("src/domains/economic/models", rel_path),
                    os.path.join("src/domains/ga", rel_path),
                ]
                
                # If any of the potential new locations exist, consider the file migrated
                for new_location in potential_new_locations:
                    if os.path.exists(new_location):
                        migrated_files.append(original_file)
                        break
    
    return migrated_files

def remove_files(file_list, dry_run=True):
    """Remove files from the list.
    
    Args:
        file_list: List of files to remove
        dry_run: If True, only print what would be done without making changes
        
    Returns:
        int: Number of files that would be/were removed
    """
    removed_count = 0
    
    for file_path in file_list:
        if os.path.exists(file_path):
            if dry_run:
                print(f"Would remove: {file_path}")
            else:
                try:
                    os.remove(file_path)
                    print(f"Removed: {file_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"Error removing {file_path}: {e}")
    
    return removed_count

def main():
    """Main function to identify and clean up unused files."""
    print("=== HMS-A2A Unused File Cleanup ===")
    
    # Check for dry-run flag and force flag
    dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
    force = "--force" in sys.argv or "-f" in sys.argv
    
    if dry_run:
        print("DRY RUN MODE: No changes will be made.")
    
    # Find migrated files
    print("\nSearching for migrated files...")
    migrated_files = find_migrated_files()
    
    if not migrated_files:
        print("No migrated files found.")
        return
    
    print(f"\nFound {len(migrated_files)} files that appear to have been migrated:")
    for file in migrated_files[:10]:  # Show first 10 files
        print(f"  - {file}")
    
    if len(migrated_files) > 10:
        print(f"  ... and {len(migrated_files) - 10} more")
    
    # Confirm before removal
    if not dry_run and not force:
        confirm = input("\nDo you want to remove these files? [y/N] ").lower()
        if confirm != 'y':
            print("Operation cancelled.")
            return
    
    # Remove files
    print("\nRemoving files...")
    removed_count = remove_files(migrated_files, dry_run)
    
    print(f"\n{removed_count} files would be removed." if dry_run else f"\n{removed_count} files removed.")
    
    if dry_run:
        print("\nTo actually remove these files, run: python cleanup_unused.py")
        print("Or to skip confirmation: python cleanup_unused.py --force")

if __name__ == "__main__":
    main() 