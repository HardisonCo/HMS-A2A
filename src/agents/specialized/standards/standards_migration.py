#!/usr/bin/env python3
"""
Standards Migration Script

This script provides functionality to migrate standards from HMS-SME format
to HMS-A2A format. It handles both batch migration of entire standards databases
and incremental migration of individual standards.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from specialized_agents.standards.standards_converter import StandardsConverter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("standards_migration")

def setup_directories() -> Dict[str, Path]:
    """
    Set up directories for standards migration.
    
    Returns:
        Dictionary of directory paths
    """
    # Base directories
    base_dir = Path(__file__).parent.parent.parent
    data_dir = base_dir / "data"
    standards_dir = data_dir / "standards"
    
    # Create directories if they don't exist
    for directory in [data_dir, standards_dir]:
        directory.mkdir(exist_ok=True)
        
    # Create subdirectories
    source_dir = standards_dir / "source"
    converted_dir = standards_dir / "converted"
    merged_dir = standards_dir / "merged"
    
    for directory in [source_dir, converted_dir, merged_dir]:
        directory.mkdir(exist_ok=True)
    
    return {
        "base": base_dir,
        "data": data_dir,
        "standards": standards_dir,
        "source": source_dir,
        "converted": converted_dir,
        "merged": merged_dir
    }

def copy_source_standards(source_path: str, target_dir: Path) -> List[Path]:
    """
    Copy source standards files to the standards directory.
    
    Args:
        source_path: Path to source standards file or directory
        target_dir: Target directory for copied files
        
    Returns:
        List of copied file paths
    """
    import shutil
    
    source_path = Path(source_path)
    copied_files = []
    
    if source_path.is_file():
        # Single file
        target_file = target_dir / source_path.name
        shutil.copy2(source_path, target_file)
        logger.info(f"Copied {source_path} to {target_file}")
        copied_files.append(target_file)
        
    elif source_path.is_dir():
        # Directory of files
        for file_path in source_path.glob("**/*.json"):
            # Create relative path structure in target directory
            rel_path = file_path.relative_to(source_path)
            target_file = target_dir / rel_path
            
            # Create parent directories if needed
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(file_path, target_file)
            logger.info(f"Copied {file_path} to {target_file}")
            copied_files.append(target_file)
    
    return copied_files

def convert_standards_files(source_files: List[Path], output_dir: Path) -> List[Path]:
    """
    Convert standards files from HMS-SME to HMS-A2A format.
    
    Args:
        source_files: List of source standards files
        output_dir: Output directory for converted files
        
    Returns:
        List of converted file paths
    """
    converter = StandardsConverter()
    converted_files = []
    
    for source_file in source_files:
        # Determine file type based on filename
        file_type = "industry" if "industry" in source_file.name.lower() else "standard"
        
        # Create output file path
        output_file = output_dir / f"a2a_{source_file.stem}.json"
        
        logger.info(f"Converting {source_file} ({file_type} type) to {output_file}")
        
        # Convert file based on type
        if file_type == "industry":
            result = converter.convert_industry_standards(str(source_file), str(output_file))
        else:
            result = converter.convert_standards_file(str(source_file), str(output_file))
        
        if "error" not in result:
            converted_files.append(output_file)
            logger.info(f"Successfully converted {result.get('standards_count', 0)} standards to {output_file}")
        else:
            logger.error(f"Error converting {source_file}: {result.get('error', 'Unknown error')}")
    
    return converted_files

def merge_converted_files(converted_files: List[Path], output_dir: Path) -> Path:
    """
    Merge converted files into a single standards database.
    
    Args:
        converted_files: List of converted standards files
        output_dir: Output directory for merged file
        
    Returns:
        Path to merged file
    """
    if not converted_files:
        logger.error("No files to merge")
        return None
    
    converter = StandardsConverter()
    merged_file = output_dir / f"standards_database_{datetime.now().strftime('%Y%m%d')}.json"
    
    logger.info(f"Merging {len(converted_files)} files into {merged_file}")
    
    # Convert paths to strings for the converter
    file_paths = [str(file) for file in converted_files]
    
    # Merge files
    result = converter.merge_standards_files(file_paths, str(merged_file))
    
    if "error" not in result:
        logger.info(f"Successfully merged {result.get('standards_count', 0)} standards to {merged_file}")
        return merged_file
    else:
        logger.error(f"Error merging files: {result.get('error', 'Unknown error')}")
        return None

def create_symlink_to_latest(merged_file: Path, standards_dir: Path) -> bool:
    """
    Create a symlink to the latest standards database.
    
    Args:
        merged_file: Path to the latest merged file
        standards_dir: Standards directory
        
    Returns:
        True if successful, False otherwise
    """
    if not merged_file or not merged_file.exists():
        logger.error("No merged file to create symlink for")
        return False
    
    symlink_path = standards_dir / "standards.json"
    
    # Remove existing symlink if it exists
    if symlink_path.exists():
        if symlink_path.is_symlink():
            symlink_path.unlink()
        else:
            # Backup existing file if it's not a symlink
            backup_path = standards_dir / f"standards_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            symlink_path.rename(backup_path)
            logger.info(f"Backed up existing standards file to {backup_path}")
    
    # Create relative path for symlink
    rel_path = os.path.relpath(merged_file, symlink_path.parent)
    
    # Create symlink
    try:
        symlink_path.symlink_to(rel_path)
        logger.info(f"Created symlink {symlink_path} -> {rel_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating symlink: {str(e)}")
        
        # If symlink creation fails (e.g., on Windows), copy the file instead
        try:
            import shutil
            shutil.copy2(merged_file, symlink_path)
            logger.info(f"Copied {merged_file} to {symlink_path} (symlink creation failed)")
            return True
        except Exception as e2:
            logger.error(f"Error copying file: {str(e2)}")
            return False

def run_migration(source_path: str) -> Tuple[bool, str]:
    """
    Run the migration process from end to end.
    
    Args:
        source_path: Path to source standards file or directory
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Set up directories
        directories = setup_directories()
        
        # 1. Copy source files
        logger.info("Step 1: Copying source standards files")
        source_files = copy_source_standards(source_path, directories["source"])
        
        if not source_files:
            return False, "No source files found or copied"
        
        # 2. Convert files to HMS-A2A format
        logger.info("Step 2: Converting standards to HMS-A2A format")
        converted_files = convert_standards_files(source_files, directories["converted"])
        
        if not converted_files:
            return False, "No files were successfully converted"
        
        # 3. Merge converted files
        logger.info("Step 3: Merging converted standards files")
        merged_file = merge_converted_files(converted_files, directories["merged"])
        
        if not merged_file:
            return False, "Failed to merge converted files"
        
        # 4. Create symlink to latest
        logger.info("Step 4: Creating symlink to latest standards database")
        symlink_created = create_symlink_to_latest(merged_file, directories["standards"])
        
        # Generate success message
        message = f"""
Standards migration completed successfully:
- Copied {len(source_files)} source files
- Converted {len(converted_files)} files to HMS-A2A format
- Created merged standards database at {merged_file}
- {'Created' if symlink_created else 'Failed to create'} symlink to latest database
"""
        
        return True, message
        
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        return False, f"Migration failed: {str(e)}"

def main():
    """
    Main function to run the standards migration.
    """
    parser = argparse.ArgumentParser(
        description='Migrate standards from HMS-SME format to HMS-A2A format'
    )
    
    parser.add_argument('--source', '-s', required=True,
                       help='Source standards file or directory containing standards files')
    
    args = parser.parse_args()
    
    success, message = run_migration(args.source)
    
    if success:
        logger.info("Migration completed successfully")
        print(message)
        return 0
    else:
        logger.error(f"Migration failed: {message}")
        print(f"ERROR: {message}")
        return 1

if __name__ == "__main__":
    sys.exit(main())