#!/usr/bin/env python3
"""
HMS-A2A Code Inventory Script

Scans specified project directories for Python and Lean files,
extracts metadata (LOC, imports), and generates CSV and Mermaid diagram outputs.

Plan Ref: HMS-A2A MIGRATION MASTER PLAN (v 2.1), Section 1.1
"""

import os
import csv
import ast
import re
import argparse
from pathlib import Path
from collections import defaultdict

# Optional networkx+pydot for DOT export (used when --write-dot)
try:
    import networkx as nx  # type: ignore
    import pydot  # noqa: F401  # networkx's write_dot needs pydot installed
    HAS_NETWORKX = True
except ImportError:  # pragma: no cover
    HAS_NETWORKX = False

# --- Configuration ---

# Directories to scan relative to the project root (where this script is run from)
# Assuming script is run from the root of the HardisonCo workspace
PROJECT_ROOT = Path(__file__).resolve().parents[2] # Adjust if script location changes
TARGET_DIRS = [
    PROJECT_ROOT / "core" / "lean4_economic_foundations",
    PROJECT_ROOT / "core" / "graph",
    PROJECT_ROOT / "core" / "genetic_theorem_prover",
    PROJECT_ROOT / "core" / "prover-orchestrator", # Scan Rust files here too? For now, focus on py/lean
]

# Output file paths
OUTPUT_DIR = PROJECT_ROOT / "docs" / "architecture" / "generated_inventory"
CSV_OUTPUT_FILE = OUTPUT_DIR / "inventory.csv"
MERMAID_OUTPUT_FILE = OUTPUT_DIR / "inventory_dependencies.mmd"
DOT_OUTPUT_FILE = OUTPUT_DIR / "inventory_dependencies.dot"

# File extensions to scan
PYTHON_EXT = ".py"
LEAN_EXT = ".lean"
RUST_EXT = ".rs" # Added for prover-orchestrator, though import parsing is basic
SUPPORTED_EXTENSIONS = {PYTHON_EXT, LEAN_EXT, RUST_EXT}


# --- Helper Functions ---

def count_loc(file_path: Path) -> int:
    """Counts non-empty, non-comment lines in a file."""
    loc = 0
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith(('#', '//', '--')): # Basic comment handling
                    loc += 1
    except Exception as e:
        print(f"Warning: Could not count LOC for {file_path}: {e}")
    return loc

def get_python_imports(file_path: Path) -> list[str]:
    """Extracts top-level imports from a Python file using AST."""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Handle 'import a.b.c' - take the top level 'a'
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    # Handle 'from x import y' or 'from .x import y'
                    if node.module:
                         # Take top level, ignore relative './../' for now
                        imports.add(node.module.split('.')[0])
    except SyntaxError as e:
         print(f"Warning: Could not parse Python imports for {file_path} (SyntaxError): {e}")
    except Exception as e:
        print(f"Warning: Could not parse Python imports for {file_path}: {e}")
    # Filter out relative imports starting with '.'
    return sorted([imp for imp in list(imports) if not imp.startswith('.')])


def get_lean_imports(file_path: Path) -> list[str]:
    """Extracts imports from a Lean file using regex."""
    imports = set()
    import_pattern = re.compile(r"^\s*import\s+([\w\.]+)", re.MULTILINE)
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            for match in import_pattern.finditer(content):
                imports.add(match.group(1).split('.')[0]) # Get top level
    except Exception as e:
        print(f"Warning: Could not parse Lean imports for {file_path}: {e}")
    return sorted(list(imports))

def get_rust_imports(file_path: Path) -> list[str]:
    """Extracts external crate imports from a Rust file using regex."""
    imports = set()
    # Matches 'use external_crate::...' or 'extern crate external_crate;'
    # Does not handle renamed imports perfectly ('use ext_crate as alias;')
    # Does not handle 'self::' or 'super::' or 'crate::'
    import_pattern = re.compile(r"^\s*(?:use|extern\s+crate)\s+([\w]+)(?:::[^;]+|;)", re.MULTILINE)
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            for match in import_pattern.finditer(content):
                 # Basic filter for common std/core/alloc crates
                crate_name = match.group(1)
                if crate_name not in ['std', 'core', 'alloc', 'self', 'super', 'crate']:
                    imports.add(crate_name)
    except Exception as e:
        print(f"Warning: Could not parse Rust imports for {file_path}: {e}")
    return sorted(list(imports))


def get_module_name(file_path: Path, root_dir: Path) -> str:
    """Generates a unique module identifier from its path."""
    relative_path = file_path.relative_to(root_dir)
    # Replace path separators with dots, remove extension
    module_id = str(relative_path.with_suffix('')).replace(os.sep, '.')
    # Prefix with the top-level scanned directory name for uniqueness
    return f"{root_dir.name}.{module_id}"

# --- Main Logic ---

def main():
    """Main function to scan files and generate outputs."""
    parser = argparse.ArgumentParser(description="HMS-A2A inventory + dependency extractor")
    parser.add_argument("--write-dot", action="store_true", help="Also emit NetworkX DOT graph (requires networkx+pydot)")
    parser.add_argument("--classify", action="store_true", help="Classify modules as Pure/IO/Service and write inventory.xlsx (requires pandas & openpyxl)")
    args = parser.parse_args()

    print("Starting HMS-A2A Code Inventory Scan...")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Scanning Dirs: {[d.relative_to(PROJECT_ROOT) for d in TARGET_DIRS]}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Outputting to: {OUTPUT_DIR.relative_to(PROJECT_ROOT)}")

    inventory_data = []
    dependencies = defaultdict(set) # module_id -> set(imported_module_id)

    # Scan files
    scanned_files = 0
    for target_dir in TARGET_DIRS:
        if not target_dir.exists():
            print(f"Warning: Target directory not found, skipping: {target_dir}")
            continue
        print(f"Scanning {target_dir.relative_to(PROJECT_ROOT)}...")
        for file_path in target_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix in SUPPORTED_EXTENSIONS:
                scanned_files += 1
                relative_path = file_path.relative_to(PROJECT_ROOT)
                loc = count_loc(file_path)
                imports = []
                language = "Unknown"
                module_id = get_module_name(file_path, target_dir) # Module ID relative to its scan root

                if file_path.suffix == PYTHON_EXT:
                    language = "Python"
                    imports = get_python_imports(file_path)
                elif file_path.suffix == LEAN_EXT:
                    language = "Lean"
                    imports = get_lean_imports(file_path)
                elif file_path.suffix == RUST_EXT:
                    language = "Rust"
                    imports = get_rust_imports(file_path) # Basic Rust import parsing

                kind = "Unknown"  # default, will update if classify flag
                inventory_data.append({
                    "module_id": module_id,
                    "relative_path": str(relative_path),
                    "language": language,
                    "loc": loc,
                    "imports": ", ".join(imports),
                    "kind": kind,
                })
                # Store dependencies for Mermaid diagram (simple mapping by top-level import name for now)
                # This is an approximation - doesn't resolve imports to actual scanned modules perfectly
                for imp in imports:
                     # Only add if it's likely another module in our scanned set (heuristic)
                     # This needs refinement based on actual module structure/names
                     # For now, just add the raw import name
                     dependencies[module_id].add(imp)


    print(f"Scanned {scanned_files} files.")

    # If classification requested, perform simple heuristic classification
    if args.classify:
        print("Classifying modules (heuristic)...")
        for item in inventory_data:
            path_lower = item["relative_path"].lower()
            lang = item["language"]
            heuristics_io = ["io", "file", "socket", "network", "cli", "http", "requests"]
            heuristics_service = ["main", "server", "supervisor", "agent", "orchestrator"]
            if any(tok in path_lower for tok in heuristics_service):
                item["kind"] = "Service"
            elif any(tok in path_lower for tok in heuristics_io):
                item["kind"] = "IO"
            else:
                item["kind"] = "Pure"

    # Write CSV
    if inventory_data:
        print(f"Writing inventory to {CSV_OUTPUT_FILE.relative_to(PROJECT_ROOT)}...")
        headers = inventory_data[0].keys()
        try:
            with open(CSV_OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(inventory_data)
            print("CSV inventory generated successfully.")
        except IOError as e:
            print(f"Error writing CSV file: {e}")
    else:
        print("No files found to inventory.")
        return # Exit if no data

    # Generate Mermaid Diagram
    print(f"Generating Mermaid dependency graph to {MERMAID_OUTPUT_FILE.relative_to(PROJECT_ROOT)}...")
    mermaid_lines = ["```mermaid", "graph TD;"]
    module_ids = {item['module_id'] for item in inventory_data}

    # Define nodes (modules)
    for module_id in sorted(list(module_ids)):
        # Sanitize module_id for Mermaid node ID (replace dots, etc.)
        node_id = re.sub(r'[^\w-]', '_', module_id)
        mermaid_lines.append(f'  {node_id}["{module_id}"];') # Use full ID as label

    # Define edges (dependencies) - This is still approximate
    # We need a better way to map import names back to module_ids
    # For now, draw arrows based on raw import strings if they match a known module prefix
    print("Generating dependency links (approximation)...")
    link_count = 0
    linked_imports = set() # Track which imports we successfully linked
    for module_id, imported_names in dependencies.items():
        source_node_id = re.sub(r'[^\w-]', '_', module_id)
        for imp_name in imported_names:
            # Try to find a target module ID that starts with the import name
            # This is imperfect but better than nothing.
            # e.g. import 'core.graph.utils' might link to 'graph.utils' module
            found_target = False
            for target_module_id in module_ids:
                 # Check if target module ID starts with the import name (after its root dir prefix)
                 # e.g., target 'graph.cli' starts with imp_name 'cli' (if imported as 'cli') - less likely
                 # e.g., target 'graph.cli' matches imp_name 'graph' - more likely
                 # Let's try matching the *start* of the target module ID
                 # or if the import name matches the *last part* of the target ID
                 simplified_target_id = target_module_id.split('.', 1)[-1] # Remove top dir prefix for matching
                 if target_module_id.startswith(imp_name) or simplified_target_id.startswith(imp_name):
                    target_node_id = re.sub(r'[^\w-]', '_', target_module_id)
                    mermaid_lines.append(f'  {source_node_id} --> {target_node_id};')
                    link_count += 1
                    linked_imports.add(f"{module_id} -> {imp_name}")
                    found_target = True
                    # break # Uncomment if you only want one link per import

            # Optionally, represent unlinked imports differently?
            # if not found_target and imp_name not in ['os', 'sys', 'pathlib', 're', 'ast', 'csv', 'collections', 'serde', 'tokio', 'pyo3', 'anyhow', 'thiserror', 'log']: # Common stdlib/external
            #    # Add a node for the external/unresolved import?
            #    ext_node_id = f"ext_{re.sub(r'[^\\w-]', '_', imp_name)}"
            #    mermaid_lines.append(f'  {ext_node_id}[("{imp_name}")];') # Style external nodes
            #    mermaid_lines.append(f'  {source_node_id} -.-> {ext_node_id};') # Dashed line


    mermaid_lines.append("```")

    try:
        with open(MERMAID_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(mermaid_lines))
        print(f"Mermaid diagram generated successfully ({link_count} links established).")
        # print(f"DEBUG: Linked imports: {linked_imports}") # Uncomment for debugging linkage
    except IOError as e:
        print(f"Error writing Mermaid file: {e}")

    print("Inventory scan completed.")

    # Optionally export DOT graph via networkx
    if args.write_dot:
        if not HAS_NETWORKX:
            print("networkx or pydot not installed; skipping DOT export. Run 'pip install networkx pydot' and re-run with --write-dot")
        else:
            print(f"Generating NetworkX DOT graph to {DOT_OUTPUT_FILE.relative_to(PROJECT_ROOT)}…")
            g = nx.DiGraph()
            # add nodes
            for item in inventory_data:
                g.add_node(item["module_id"], label=item["module_id"], language=item["language"], loc=item["loc"])
            # add edges
            for src, imps in dependencies.items():
                for imp in imps:
                    # naive mapping: find first module that startswith imp
                    target = next((m for m in g.nodes if m.split('.', 1)[-1].startswith(imp)), None)
                    if target:
                        g.add_edge(src, target)
            try:
                nx.drawing.nx_pydot.write_dot(g, DOT_OUTPUT_FILE)
                print("DOT graph written successfully.")
            except Exception as e:
                print(f"Failed writing DOT graph: {e}")

    # Optionally write XLSX
    if args.classify:
        try:
            import pandas as pd  # type: ignore
            xlsx_path = OUTPUT_DIR / "inventory.xlsx"
            pd.DataFrame(inventory_data).to_excel(xlsx_path, index=False)
            print(f"Excel inventory written to {xlsx_path.relative_to(PROJECT_ROOT)}")
        except ImportError:
            print("pandas or openpyxl not installed; skipping Excel export. Run 'pip install pandas openpyxl' and re-run with --classify")

if __name__ == "__main__":
    main()
