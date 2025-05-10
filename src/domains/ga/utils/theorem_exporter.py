"""
Enhanced Theorem Exporter for Genetic Theorem Proving

This module extends the original theorem_exporter.py to support genetic agent requirements,
providing functionality to extract and export theorems in formats suitable for the
genetic theorem proving system.
"""

import inspect
import ast
import json
import os
import importlib.util
import sys
from typing import Dict, List, Tuple, Any, Optional, Set, Union, Callable
import uuid
import logging
import re
from dataclasses import dataclass, field, asdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class TheoremMetadata:
    """Metadata for a theorem specification."""
    domain: str
    tags: List[str]
    priority: int = 3  # 1-5, where 1 is highest priority
    difficulty: int = 3  # 1-5, where 5 is most difficult
    importance: int = 3  # 1-5, where 5 is most important
    created_by: str = "theorem_exporter"
    verification_level: int = 0  # 0-3, where 3 is fully verified


@dataclass
class TheoremSpec:
    """Complete theorem specification for genetic theorem proving."""
    theorem_id: str
    natural_language: str
    formal_expression: str
    assumptions: List[str] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)
    metadata: TheoremMetadata = field(default_factory=lambda: TheoremMetadata(domain="economics", tags=["exported"]))
    source_module: Optional[str] = None
    source_function: Optional[str] = None
    source_line: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "theorem_id": self.theorem_id,
            "natural_language": self.natural_language,
            "formal_expression": self.formal_expression,
            "assumptions": self.assumptions,
            "variables": self.variables,
            "metadata": asdict(self.metadata),
            "source_module": self.source_module,
            "source_function": self.source_function,
            "source_line": self.source_line
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TheoremSpec':
        """Create from dictionary representation."""
        metadata = TheoremMetadata(
            domain=data["metadata"].get("domain", "economics"),
            tags=data["metadata"].get("tags", ["exported"]),
            priority=data["metadata"].get("priority", 3),
            difficulty=data["metadata"].get("difficulty", 3),
            importance=data["metadata"].get("importance", 3),
            created_by=data["metadata"].get("created_by", "theorem_exporter"),
            verification_level=data["metadata"].get("verification_level", 0)
        )
        
        return cls(
            theorem_id=data["theorem_id"],
            natural_language=data["natural_language"],
            formal_expression=data["formal_expression"],
            assumptions=data.get("assumptions", []),
            variables=data.get("variables", {}),
            metadata=metadata,
            source_module=data.get("source_module"),
            source_function=data.get("source_function"),
            source_line=data.get("source_line")
        )


class TheoremExtractor:
    """
    Enhanced extractor for theorems from Python code.
    
    This class analyzes Python code to extract theorem specifications,
    supporting a variety of formats including docstring annotations,
    code structure analysis, and specialized decorators.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize a theorem extractor.
        
        Args:
            output_dir: Optional directory to save extracted theorems
        """
        self.output_dir = output_dir
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
    
    def extract_from_function(self, func: Callable) -> Optional[TheoremSpec]:
        """
        Extract a theorem specification from a function.
        
        Args:
            func: The function to analyze
            
        Returns:
            Extracted theorem specification, or None if not found
        """
        docstring = inspect.getdoc(func)
        
        # Try docstring-based extraction first
        if docstring:
            # Check for @theorem_spec tag
            if "@theorem_spec" in docstring:
                return self._extract_from_theorem_spec_tag(func, docstring)
            
            # Check for @theorem tag
            if "@theorem" in docstring:
                return self._extract_from_theorem_tag(func, docstring)
        
        # Fall back to code structure analysis
        return self._extract_from_code_structure(func)
    
    def _extract_from_theorem_spec_tag(self, func: Callable, docstring: str) -> Optional[TheoremSpec]:
        """
        Extract theorem from @theorem_spec tag in docstring.
        
        Args:
            func: The function containing the theorem spec
            docstring: The function's docstring
            
        Returns:
            Extracted theorem specification, or None if extraction fails
        """
        try:
            # Extract JSON spec from docstring
            spec_pattern = r'@theorem_spec:\s*```(?:json)?\s*([\s\S]*?)\s*```'
            spec_match = re.search(spec_pattern, docstring)
            
            if not spec_match:
                # Try alternate format without code block
                spec_pattern = r'@theorem_spec:([\s\S]*?)(?:@|\Z)'
                spec_match = re.search(spec_pattern, docstring)
            
            if spec_match:
                spec_str = spec_match.group(1).strip()
                spec_data = json.loads(spec_str)
                
                # Get function info
                source_info = inspect.getsourcelines(func)
                source_line = source_info[1] if source_info else None
                
                # Create TheoremSpec
                theorem_spec = TheoremSpec.from_dict(spec_data)
                theorem_spec.source_function = func.__name__
                theorem_spec.source_module = func.__module__
                theorem_spec.source_line = source_line
                
                return theorem_spec
            
            return None
        except (json.JSONDecodeError, ValueError, AttributeError) as e:
            logger.error(f"Error extracting theorem spec from {func.__name__}: {e}")
            return None
    
    def _extract_from_theorem_tag(self, func: Callable, docstring: str) -> Optional[TheoremSpec]:
        """
        Extract theorem from @theorem tag in docstring.
        
        Args:
            func: The function containing the theorem
            docstring: The function's docstring
            
        Returns:
            Extracted theorem specification, or None if extraction fails
        """
        try:
            # Parse docstring for theorem components
            theorem_id = None
            natural_language = None
            formal_expression = None
            assumptions = []
            variables = {}
            domain = "economics"
            tags = ["exported"]
            priority = 3
            difficulty = 3
            importance = 3
            
            # Extract theorem ID
            id_match = re.search(r'@theorem\s+id:\s*([\w-]+)', docstring)
            if id_match:
                theorem_id = id_match.group(1)
            else:
                # Generate ID from function name if not specified
                theorem_id = f"T_{func.__name__}_{uuid.uuid4().hex[:6]}"
            
            # Extract natural language statement
            nl_match = re.search(r'@theorem\s+statement:\s*(.*?)(?:@|\Z)', docstring, re.DOTALL)
            if nl_match:
                natural_language = nl_match.group(1).strip()
            
            # Extract formal expression
            formal_match = re.search(r'@theorem\s+formal:\s*(.*?)(?:@|\Z)', docstring, re.DOTALL)
            if formal_match:
                formal_expression = formal_match.group(1).strip()
            
            # Extract assumptions
            assumptions_match = re.search(r'@theorem\s+assumptions:\s*(.*?)(?:@|\Z)', docstring, re.DOTALL)
            if assumptions_match:
                assumptions_text = assumptions_match.group(1).strip()
                assumptions = [a.strip() for a in assumptions_text.split('\n') if a.strip()]
            
            # Extract variables
            variables_match = re.search(r'@theorem\s+variables:\s*(.*?)(?:@|\Z)', docstring, re.DOTALL)
            if variables_match:
                variables_text = variables_match.group(1).strip()
                for line in variables_text.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        variables[parts[0].strip()] = parts[1].strip()
            
            # Extract domain
            domain_match = re.search(r'@theorem\s+domain:\s*([\w-]+)', docstring)
            if domain_match:
                domain = domain_match.group(1)
            
            # Extract tags
            tags_match = re.search(r'@theorem\s+tags:\s*(.*?)(?:@|\Z)', docstring)
            if tags_match:
                tags_text = tags_match.group(1).strip()
                tags = [t.strip() for t in tags_text.split(',')]
            
            # Extract priority
            priority_match = re.search(r'@theorem\s+priority:\s*(\d+)', docstring)
            if priority_match:
                priority = int(priority_match.group(1))
            
            # Extract difficulty
            difficulty_match = re.search(r'@theorem\s+difficulty:\s*(\d+)', docstring)
            if difficulty_match:
                difficulty = int(difficulty_match.group(1))
            
            # Extract importance
            importance_match = re.search(r'@theorem\s+importance:\s*(\d+)', docstring)
            if importance_match:
                importance = int(importance_match.group(1))
            
            # Check if required fields are present
            if not natural_language or not formal_expression:
                logger.warning(f"Missing required theorem fields in {func.__name__}")
                return None
            
            # Get function info
            source_info = inspect.getsourcelines(func)
            source_line = source_info[1] if source_info else None
            
            # Create metadata
            metadata = TheoremMetadata(
                domain=domain,
                tags=tags,
                priority=priority,
                difficulty=difficulty,
                importance=importance,
                created_by="theorem_exporter",
                verification_level=0
            )
            
            # Create TheoremSpec
            theorem_spec = TheoremSpec(
                theorem_id=theorem_id,
                natural_language=natural_language,
                formal_expression=formal_expression,
                assumptions=assumptions,
                variables=variables,
                metadata=metadata,
                source_function=func.__name__,
                source_module=func.__module__,
                source_line=source_line
            )
            
            return theorem_spec
            
        except (ValueError, AttributeError) as e:
            logger.error(f"Error extracting theorem from {func.__name__}: {e}")
            return None
    
    def _extract_from_code_structure(self, func: Callable) -> Optional[TheoremSpec]:
        """
        Extract theorem from code structure analysis.
        
        Args:
            func: The function to analyze
            
        Returns:
            Extracted theorem specification, or None if not identified as a theorem
        """
        try:
            # Get function source code
            source = inspect.getsource(func)
            source_info = inspect.getsourcelines(func)
            source_line = source_info[1] if source_info else None
            
            # Parse the function
            tree = ast.parse(source)
            func_node = None
            
            # Find the FunctionDef node
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == func.__name__:
                    func_node = node
                    break
            
            if not func_node:
                return None
            
            # Look for theorem-related patterns in the function
            
            # Pattern 1: Function returning a theorem verification assertion
            if self._is_theorem_verification_function(func_node):
                # Extract theorem details from the function
                theorem_id = f"T_{func.__name__}_{uuid.uuid4().hex[:6]}"
                
                # Extract natural language from function name and docstring
                docstring = ast.get_docstring(func_node)
                natural_language = docstring if docstring else f"Theorem from {func.__name__}"
                
                # Extract formal expression from return statement
                formal_expression = self._extract_formal_expression_from_returns(func_node)
                
                if formal_expression:
                    # Create metadata
                    metadata = TheoremMetadata(
                        domain="economics",
                        tags=["exported", "code_extracted"],
                        priority=3,
                        difficulty=3,
                        importance=3,
                        created_by="theorem_exporter",
                        verification_level=0
                    )
                    
                    # Create TheoremSpec
                    theorem_spec = TheoremSpec(
                        theorem_id=theorem_id,
                        natural_language=natural_language,
                        formal_expression=formal_expression,
                        assumptions=[],
                        variables={},
                        metadata=metadata,
                        source_function=func.__name__,
                        source_module=func.__module__,
                        source_line=source_line
                    )
                    
                    return theorem_spec
            
            return None
            
        except (ValueError, AttributeError, SyntaxError) as e:
            logger.error(f"Error analyzing code structure for {func.__name__}: {e}")
            return None
    
    def _is_theorem_verification_function(self, func_node: ast.FunctionDef) -> bool:
        """
        Check if a function appears to be a theorem verification function.
        
        Args:
            func_node: The function AST node
            
        Returns:
            True if the function appears to be a theorem verification function
        """
        # Check for theorem-related keywords in function name
        theorem_keywords = ["theorem", "prove", "lemma", "corollary", "assert", "verify", "check"]
        if any(keyword in func_node.name.lower() for keyword in theorem_keywords):
            return True
        
        # Check for assert statements or verification calls
        for node in ast.walk(func_node):
            if isinstance(node, ast.Assert):
                return True
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                
                verification_funcs = ["assert", "verify", "check", "prove", "validate"]
                if any(vf in func_name.lower() for vf in verification_funcs):
                    return True
        
        return False
    
    def _extract_formal_expression_from_returns(self, func_node: ast.FunctionDef) -> Optional[str]:
        """
        Extract formal expression from function return statements.
        
        Args:
            func_node: The function AST node
            
        Returns:
            Extracted formal expression, or None if not found
        """
        return_exprs = []
        
        # Find all return statements
        for node in ast.walk(func_node):
            if isinstance(node, ast.Return) and node.value:
                # Convert return expression to string
                return_exprs.append(ast.unparse(node.value))
        
        if return_exprs:
            # Join multiple returns with logical 'and'
            return " and ".join(return_exprs)
        
        return None
    
    def extract_from_module(self, module_path: str) -> List[TheoremSpec]:
        """
        Extract theorems from a Python module.
        
        Args:
            module_path: Path to the module file
            
        Returns:
            List of extracted theorem specifications
        """
        try:
            # Load the module
            if module_path.endswith('.py'):
                # Get absolute path
                abs_path = os.path.abspath(module_path)
                
                # Load module from file
                module_name = os.path.basename(module_path)[:-3]  # Remove .py
                spec = importlib.util.spec_from_file_location(module_name, abs_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                # Import module by name
                module = importlib.import_module(module_path)
            
            # Find all functions in the module
            theorem_specs = []
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj):
                    theorem_spec = self.extract_from_function(obj)
                    if theorem_spec:
                        theorem_specs.append(theorem_spec)
            
            return theorem_specs
            
        except (ImportError, ModuleNotFoundError, ValueError) as e:
            logger.error(f"Error loading module {module_path}: {e}")
            return []
    
    def save_theorem_spec(self, theorem_spec: TheoremSpec) -> str:
        """
        Save a theorem specification to file.
        
        Args:
            theorem_spec: The theorem specification to save
            
        Returns:
            Path to the saved file
        """
        if not self.output_dir:
            raise ValueError("Output directory not specified")
        
        filepath = os.path.join(self.output_dir, f"{theorem_spec.theorem_id}.json")
        
        with open(filepath, 'w') as f:
            json.dump(theorem_spec.to_dict(), f, indent=2)
        
        return filepath
    
    def extract_and_save_from_module(self, module_path: str) -> List[str]:
        """
        Extract theorems from a module and save them to files.
        
        Args:
            module_path: Path to the module file
            
        Returns:
            List of paths to saved theorem specification files
        """
        if not self.output_dir:
            raise ValueError("Output directory not specified")
        
        theorem_specs = self.extract_from_module(module_path)
        saved_paths = []
        
        for spec in theorem_specs:
            filepath = self.save_theorem_spec(spec)
            saved_paths.append(filepath)
            logger.info(f"Saved theorem spec {spec.theorem_id} to {filepath}")
        
        return saved_paths


# Decorator for explicitly marking functions as theorems
def theorem(id: Optional[str] = None, 
           statement: Optional[str] = None,
           formal: Optional[str] = None,
           assumptions: Optional[List[str]] = None,
           variables: Optional[Dict[str, str]] = None,
           domain: str = "economics",
           tags: Optional[List[str]] = None,
           priority: int = 3,
           difficulty: int = 3,
           importance: int = 3):
    """
    Decorator to mark a function as containing an economic theorem.
    
    Args:
        id: Optional theorem ID (generated if not provided)
        statement: Natural language statement of the theorem
        formal: Formal expression of the theorem
        assumptions: List of assumptions for the theorem
        variables: Dictionary of variables with types/descriptions
        domain: Domain of the theorem
        tags: List of tags for the theorem
        priority: Priority level (1-5, where 1 is highest)
        difficulty: Difficulty level (1-5, where 5 is most difficult)
        importance: Importance level (1-5, where 5 is most important)
    """
    def decorator(func):
        # Generate ID if not provided
        theorem_id = id or f"T_{func.__name__}_{uuid.uuid4().hex[:6]}"
        
        # Get statement from docstring if not provided
        nonlocal statement
        if not statement:
            docstring = inspect.getdoc(func)
            statement = docstring.split('\n')[0] if docstring else f"Theorem from {func.__name__}"
        
        # Get formal expression from function if not provided
        nonlocal formal
        if not formal:
            try:
                source = inspect.getsource(func)
                tree = ast.parse(source)
                func_node = None
                
                # Find the FunctionDef node
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == func.__name__:
                        func_node = node
                        break
                
                if func_node:
                    # Extract from return statements
                    extractor = TheoremExtractor()
                    formal = extractor._extract_formal_expression_from_returns(func_node)
            except:
                pass
        
        # If still no formal expression, use a placeholder
        if not formal:
            formal = f"formal_expression_for_{func.__name__}"
        
        # Create theorem spec in function's metadata
        func.__theorem_spec__ = {
            "theorem_id": theorem_id,
            "natural_language": statement,
            "formal_expression": formal,
            "assumptions": assumptions or [],
            "variables": variables or {},
            "metadata": {
                "domain": domain,
                "tags": tags or ["exported"],
                "priority": priority,
                "difficulty": difficulty,
                "importance": importance,
                "created_by": "theorem_decorator",
                "verification_level": 0
            }
        }
        
        return func
    
    return decorator


def find_and_extract_theorems(directory: str, output_dir: str, recursive: bool = True) -> Dict[str, List[str]]:
    """
    Find and extract theorems from Python files in a directory.
    
    Args:
        directory: Directory to search
        output_dir: Directory to save extracted theorem specifications
        recursive: Whether to search subdirectories
        
    Returns:
        Dictionary mapping module paths to lists of saved theorem specification paths
    """
    extractor = TheoremExtractor(output_dir=output_dir)
    results = {}
    
    # Get all Python files
    python_files = []
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            if file.endswith('.py'):
                python_files.append(os.path.join(directory, file))
    
    # Process each file
    for module_path in python_files:
        try:
            saved_paths = extractor.extract_and_save_from_module(module_path)
            if saved_paths:
                results[module_path] = saved_paths
        except Exception as e:
            logger.error(f"Error processing {module_path}: {e}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract economic theorems from Python code.")
    parser.add_argument("--dir", required=True, help="Directory to search for Python files")
    parser.add_argument("--output", required=True, help="Directory to save extracted theorem specifications")
    parser.add_argument("--non-recursive", action="store_true", help="Don't search subdirectories")
    
    args = parser.parse_args()
    
    results = find_and_extract_theorems(args.dir, args.output, not args.non_recursive)
    
    # Print summary
    total_theorems = sum(len(paths) for paths in results.values())
    print(f"Found {total_theorems} theorems in {len(results)} files")
    
    for module_path, saved_paths in results.items():
        print(f"{module_path}: {len(saved_paths)} theorems")
    
    print(f"All theorem specifications saved to {args.output}")