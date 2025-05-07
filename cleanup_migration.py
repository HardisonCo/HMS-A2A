#!/usr/bin/env python3
"""
Cleanup script for the migration process.
This script fixes the file organization, removes duplicates, and properly sets up the directory structure.
"""

import os
import sys
import shutil
from pathlib import Path

# Source files and their target locations
FILE_MAPPING = {
    "win_win_calculation_framework.py": "src/domains/economic/models/",
    "moneyball_deal_model.py": "src/domains/economic/models/",
    "economic_formula_proofs.py": "src/domains/economic/models/",
    "trade_base.py": "src/domains/economic/models/",
    "trade_agent.py": "src/domains/economic/models/",
    
    "formal_verification_framework.py": "src/domains/verification/",
    "unified_model_validation.py": "src/domains/verification/",
    
    "o3_performance_optimization.py": "src/domains/ga/",
    "o3_deal_roadmap_optimization.py": "src/domains/ga/",
    "o3_deal_optimization.py": "src/domains/ga/",
    
    "ustda_agent.py": "src/agents/gov/",
    "usitc_agent.py": "src/agents/gov/",
    
    "task_manager.py": "src/core/",
    "run_graph_agent.py": "src/core/",
    "deal_monitoring_system.py": "src/core/",
    
    "test_win_win_framework.py": "tests/",
    "test_moneyball_model.py": "tests/",
    "test_integrated_agent.py": "tests/",
    "test_agency_integration.py": "tests/",
    "simple_agency_integration_test.py": "tests/",
    "validate_moneyball_implementation.py": "tests/",
    
    "deploy_moneyball_model.py": "src/common/"
}

BASE_DIR = Path(".")

def check_files():
    """Check which files have been successfully moved and remove originals."""
    for source_file, target_dir in FILE_MAPPING.items():
        source_path = BASE_DIR / source_file
        target_path = BASE_DIR / target_dir / source_file
        
        # Check if target directory exists, create if not
        target_dir_path = BASE_DIR / target_dir
        if not target_dir_path.exists():
            try:
                os.makedirs(target_dir_path, exist_ok=True)
                print(f"✓ Created directory: {target_dir}")
            except Exception as e:
                print(f"✗ Failed to create directory {target_dir}: {str(e)}")
                continue
        
        # Check if source file exists
        if not source_path.exists():
            if target_path.exists():
                print(f"✓ {source_file} already moved to {target_dir}.")
            else:
                print(f"✗ {source_file} not found in source or target location.")
            continue
            
        # Check if target file exists
        if target_path.exists():
            # If both source and target exist, remove the source
            print(f"⚠ Duplicate found: {source_file}")
            try:
                os.remove(source_path)
                print(f"  ✓ Removed duplicate: {source_file}")
            except Exception as e:
                print(f"  ✗ Failed to remove: {source_file} - {str(e)}")
        else:
            # Move the file to target directory
            try:
                shutil.copy2(source_path, target_path)
                print(f"✓ Moved {source_file} to {target_dir}")
                os.remove(source_path)
            except Exception as e:
                print(f"✗ Failed to move {source_file} to {target_dir}: {str(e)}")

def fix_specialized_agents():
    """Fix the specialized agents folder structure."""
    root_specialized = BASE_DIR / "specialized_agents"
    target_specialized = BASE_DIR / "src" / "agents" / "specialized"
    
    # Check if we have the root specialized_agents folder that needs to be moved
    if root_specialized.exists():
        print("⚠ Found root specialized_agents folder that needs to be organized.")
        
        # Make sure the target directory exists
        os.makedirs(target_specialized, exist_ok=True)
        
        # Check if we already have content in the target directory
        if any(target_specialized.iterdir()):
            print("⚠ Target specialized agents directory already has content.")
            
            # For each subdirectory in the root specialized_agents folder
            for item in root_specialized.iterdir():
                if item.is_dir():
                    target_subdir = target_specialized / item.name
                    
                    # If this subdirectory doesn't exist in target, copy the entire directory
                    if not target_subdir.exists():
                        try:
                            shutil.copytree(item, target_subdir)
                            print(f"✓ Copied {item.name} to target specialized agents directory")
                        except Exception as e:
                            print(f"✗ Failed to copy {item.name}: {str(e)}")
                    else:
                        print(f"⚠ {item.name} already exists in target directory, skipping.")
            
            # Now remove the root specialized_agents directory after moving everything
            try:
                shutil.rmtree(root_specialized)
                print("✓ Removed root specialized_agents directory after copying contents")
            except Exception as e:
                print(f"✗ Failed to remove root specialized_agents directory: {str(e)}")
        else:
            # If target is empty, simply move the entire directory
            try:
                # Move contents instead of the directory itself
                for item in root_specialized.iterdir():
                    if item.is_dir():
                        shutil.copytree(item, target_specialized / item.name)
                    else:
                        shutil.copy2(item, target_specialized)
                shutil.rmtree(root_specialized)
                print("✓ Moved root specialized_agents to target location")
            except Exception as e:
                print(f"✗ Failed to move specialized_agents: {str(e)}")
    else:
        print("✓ No root specialized_agents folder found, structure seems correct.")

def fix_agent_duplication():
    """Fix the agent.py duplication issue."""
    root_agent = BASE_DIR / "agent.py"
    core_agent = BASE_DIR / "src" / "core" / "agent.py"
    
    if root_agent.exists() and core_agent.exists():
        print("⚠ Found duplicate agent.py files.")
        
        # The file in src/core/agent.py is the one we want to keep
        # It has the more comprehensive A2ECombinedAgent implementation
        try:
            # Check if root agent.py is a simple CurrencyAgent implementation
            with open(root_agent, 'r') as f:
                content = f.read()
                
            if "CurrencyAgent" in content and "A2ECombinedAgent" not in content:
                # This is the simpler version, safe to remove
                os.remove(root_agent)
                print("✓ Removed duplicate agent.py from root directory (kept the one in src/core)")
            else:
                # If we're unsure, rename instead of removing
                backup_path = BASE_DIR / "agent.py.bak"
                shutil.move(root_agent, backup_path)
                print(f"⚠ Renamed root agent.py to agent.py.bak as a precaution - please verify content.")
        except Exception as e:
            print(f"✗ Failed to handle agent.py duplication: {str(e)}")
    elif root_agent.exists() and not core_agent.exists():
        # If only the root agent exists, move it to core
        try:
            # Make sure the core directory exists
            os.makedirs(BASE_DIR / "src" / "core", exist_ok=True)
            shutil.copy2(root_agent, core_agent)
            os.remove(root_agent)
            print("✓ Moved agent.py from root to src/core directory")
        except Exception as e:
            print(f"✗ Failed to move agent.py to src/core: {str(e)}")
    elif not root_agent.exists() and core_agent.exists():
        print("✓ No agent.py duplication found (only exists in src/core as expected).")
    else:
        print("⚠ No agent.py found in either location.")

def create_init_files():
    """Create necessary __init__.py files in all directories."""
    dirs = [
        "src",
        "src/core",
        "src/agents",
        "src/agents/gov",
        "src/agents/specialized",
        "src/domains",
        "src/domains/economic",
        "src/domains/economic/models",
        "src/domains/economic/negotiation",
        "src/domains/verification",
        "src/domains/ga",
        "src/common",
        "src/reasoning",
        "src/server",
        "src/ffi",
        "tests",
        "tests/unit",
        "tests/integration",
        "schemas",
        "deployment",
        "examples"
    ]
    
    for dir_path in dirs:
        dir_full_path = BASE_DIR / dir_path
        
        # Create directory if it doesn't exist
        if not dir_full_path.exists():
            try:
                os.makedirs(dir_full_path, exist_ok=True)
                print(f"✓ Created directory: {dir_path}")
            except Exception as e:
                print(f"✗ Failed to create directory {dir_path}: {str(e)}")
                continue
        
        # Create __init__.py file if it doesn't exist
        init_file = dir_full_path / "__init__.py"
        if not init_file.exists():
            try:
                init_file.touch()
                print(f"✓ Created {init_file}")
            except Exception as e:
                print(f"✗ Failed to create {init_file} - {str(e)}")

def fix_imports():
    """Fix broken imports across migrated files."""
    print("Fixing imports in key files is a manual process that's best done file by file.")
    print("You should review each file after migration to update import paths.")
    print("Common patterns to update:")
    print("  - 'from trade_base import' → 'from src.domains.economic.models.trade_base import'")
    print("  - 'from moneyball_deal_model import' → 'from src.domains.economic.models.moneyball_deal_model import'")
    print("  - 'import ustda_agent' → 'from src.agents.gov import ustda_agent'")
    print()
    print("For test files, consider using relative imports like:")
    print("  - 'from ..src.domains.economic.models.win_win_calculation_framework import'")
    print()
    print("For proper packaging, you should also create a setup.py file.")

def main():
    """Main function."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("Starting cleanup and organization process...")
    
    # Create directory structure and __init__.py files first
    print("\n1. Creating directory structure and __init__.py files...")
    create_init_files()
    
    # Move files
    print("\n2. Moving and organizing files...")
    check_files()
    
    # Fix specialized agents folder structure
    print("\n3. Fixing specialized agents folder structure...")
    fix_specialized_agents()
    
    # Fix agent.py duplication
    print("\n4. Fixing agent.py duplication...")
    fix_agent_duplication()
    
    # Print import update guidelines
    print("\n5. Import path updates needed:")
    fix_imports()
    
    print("\nCleanup completed.")

if __name__ == "__main__":
    main() 