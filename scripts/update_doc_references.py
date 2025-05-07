#!/usr/bin/env python3
"""
HMS-A2A Documentation Reference Updater

This script updates documentation references to match the new directory structure.
It scans markdown and Python files in the docs/ and src/ directories for
references to old file paths and updates them to the new structure.
"""
import os
import re
import sys
from pathlib import Path

# Define path mappings (old -> new)
PATH_MAPPINGS = {
    'finala2e': 'src/core',
    'graph': 'src/core/framework',
    'test_mcp': 'src/core/protocols',
    'common': 'src/common',
    'specialized_agents': 'src/agents/specialized',
    'gov_agents': 'src/agents/gov',
    'integration': 'src/server',
    'lean4_economic_foundations': 'src/domains/economic/models',
    'genetic_theorem_prover': 'src/domains/ga',
    # Add more mappings as needed
}

# Reverse mapping for more efficient lookups
REVERSE_MAPPINGS = {v: k for k, v in PATH_MAPPINGS.items()}

def find_doc_files():
    """Find all documentation files to update."""
    docs = list(Path('docs').glob('**/*.md'))
    docs.extend(Path('docs').glob('**/*.rst'))
    docs.extend(Path('src').glob('**/*.md'))
    docs.extend(Path('src').glob('**/*.rst'))
    docs.extend(Path('.').glob('*.md'))
    return docs

def update_file_references(file_path, dry_run=True):
    """Update file references in a single file.
    
    Args:
        file_path: Path to the file to update
        dry_run: If True, only print what would be done without making changes
        
    Returns:
        bool: True if changes were made, False otherwise
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Update references in Markdown links and code blocks
    # e.g., [Example](finala2e/example.py) -> [Example](src/core/example.py)
    for old_path, new_path in PATH_MAPPINGS.items():
        # Match only where the old_path is part of a file path (e.g., in markdown links)
        content = re.sub(
            r'(\[[^]]+\]\()(' + re.escape(old_path) + r'/[^)]+\))',
            lambda m: m.group(1) + m.group(2).replace(old_path, new_path),
            content
        )
        
        # Match code references like `finala2e/example.py`
        content = re.sub(
            r'`(' + re.escape(old_path) + r'/[^`]+)`',
            lambda m: '`' + m.group(1).replace(old_path, new_path) + '`',
            content
        )
        
        # Match import statements in Python code blocks
        content = re.sub(
            r'(from|import)\s+' + re.escape(old_path) + r'(\.[a-zA-Z0-9_]+)*',
            lambda m: m.group(0).replace(old_path, new_path.replace('/', '.')),
            content
        )
    
    # Check if content has changed
    if content != original_content:
        if dry_run:
            print(f"Would update references in {file_path}")
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated references in {file_path}")
        return True
    return False

def main():
    """Main function to update documentation references."""
    print("=== HMS-A2A Documentation Reference Updater ===")
    
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("DRY RUN MODE: No changes will be made.")
    
    doc_files = find_doc_files()
    print(f"Found {len(doc_files)} documentation files to check.")
    
    updated_count = 0
    for file_path in doc_files:
        if update_file_references(file_path, dry_run):
            updated_count += 1
    
    print(f"\n{updated_count} files would be updated." if dry_run else f"\n{updated_count} files updated.")
    
    if dry_run:
        print("\nTo perform the actual updates, run: python update_doc_references.py")

if __name__ == "__main__":
    main() 