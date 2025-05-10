"""
Lean Theorem Extractor

This module extracts theorem definitions from Lean files to enable automated proving
with the DeepSeek-Prover-V2 system.
"""

import re
import os
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class LeanVariable:
    """Representation of a variable in a Lean theorem."""
    name: str
    type_: str
    implicit: bool = False


@dataclass
class LeanHypothesis:
    """Representation of a hypothesis in a Lean theorem."""
    name: str
    expression: str


@dataclass
class LeanTheorem:
    """Representation of a theorem in Lean."""
    theorem_id: str
    formal_expression: str
    variables: List[LeanVariable] = field(default_factory=list)
    hypotheses: List[LeanHypothesis] = field(default_factory=list)
    namespace: Optional[str] = None
    proof_outline: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    file_path: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class LeanLibrary:
    """Representation of a Lean library with theorems."""
    file_path: str
    theorems: Dict[str, LeanTheorem] = field(default_factory=dict)
    namespaces: Dict[str, Set[str]] = field(default_factory=dict)
    imports: List[str] = field(default_factory=list)


class LeanTheoremExtractor:
    """
    Extracts theorems from Lean files for use with the DeepSeek-Prover-V2 system.
    """
    
    def __init__(self, lean_lib_path: str):
        """
        Initialize the theorem extractor.
        
        Args:
            lean_lib_path: Path to the Lean library
        """
        self.lean_lib_path = lean_lib_path
        
        # Regular expressions for extracting Lean elements
        self.theorem_pattern = re.compile(r'theorem\s+([a-zA-Z0-9_]+)(?:\s*\{[^}]*\})?\s*(?:\([^)]*\))?\s*:(?:[^:=]+)(?::\=|:=)(?:[^-]|-[^-])*?((?:--.*$)|(?:/-[\s\S]*?-/)|\Z)', re.MULTILINE)
        self.namespace_pattern = re.compile(r'namespace\s+([a-zA-Z0-9_]+)')
        self.end_namespace_pattern = re.compile(r'end\s+([a-zA-Z0-9_]+)')
        self.import_pattern = re.compile(r'import\s+([a-zA-Z0-9_\.]+)')
        self.variable_pattern = re.compile(r'(?:\{([^}]*)\})|(?:\(([^)]*)\))')
        self.hypothesis_pattern = re.compile(r'\((h_[a-zA-Z0-9_]+)\s*:\s*([^)]+)\)')
        self.proof_outline_pattern = re.compile(r'/\*\s*proof_outline:([\s\S]*?)\*/')
        self.inline_proof_outline_pattern = re.compile(r'--\s*proof_outline:\s*(.*?)(?:\n|$)')
        self.multi_proof_outline_pattern = re.compile(r'/-\s*proof_outline:([\s\S]*?)-/')
        
    def extract_theorems_from_file(self, file_path: str) -> LeanLibrary:
        """
        Extract theorems from a Lean file.
        
        Args:
            file_path: Path to the Lean file
            
        Returns:
            LeanLibrary containing extracted theorems
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            library = LeanLibrary(file_path=file_path)
            
            # Extract imports
            imports = self.import_pattern.findall(content)
            library.imports = imports
            
            # Track current namespace
            current_namespace = None
            namespace_stack = []
            
            # Find all namespace declarations and endings
            namespace_matches = [(m.start(), "start", m.group(1)) 
                               for m in self.namespace_pattern.finditer(content)]
            end_namespace_matches = [(m.start(), "end", m.group(1)) 
                                   for m in self.end_namespace_pattern.finditer(content)]
            
            # Combine and sort by position
            namespace_events = sorted(namespace_matches + end_namespace_matches, key=lambda x: x[0])
            
            # Find all theorems
            theorem_matches = list(self.theorem_pattern.finditer(content))
            
            # For each theorem, determine its namespace
            for match in theorem_matches:
                position = match.start()
                
                # Update namespace based on position
                current_namespace = self._get_namespace_at_position(position, namespace_events, namespace_stack)
                
                # Extract theorem details
                theorem_id = match.group(1)
                full_match = match.group(0)
                
                # Find line number
                line_number = content[:position].count('\n') + 1
                
                # Extract variables and hypotheses
                variables = self._extract_variables(full_match)
                hypotheses = self._extract_hypotheses(full_match)
                
                # Extract formal expression (between ":" and ":=")
                formal_expr_match = re.search(r':\s*([^:=]+)(?::\=|:=)', full_match)
                formal_expression = formal_expr_match.group(1).strip() if formal_expr_match else ""
                
                # Extract proof outline
                proof_outline = self._extract_proof_outline(match.group(2) if match.group(2) else "")
                
                # Create theorem object
                theorem = LeanTheorem(
                    theorem_id=theorem_id,
                    formal_expression=formal_expression,
                    variables=variables,
                    hypotheses=hypotheses,
                    namespace=current_namespace,
                    proof_outline=proof_outline,
                    file_path=file_path,
                    line_number=line_number
                )
                
                # Add to library
                library.theorems[theorem_id] = theorem
                
                # Add to namespace mapping
                full_id = f"{current_namespace}.{theorem_id}" if current_namespace else theorem_id
                if current_namespace not in library.namespaces:
                    library.namespaces[current_namespace] = set()
                library.namespaces[current_namespace].add(theorem_id)
            
            return library
                
        except Exception as e:
            logger.error(f"Error extracting theorems from {file_path}: {e}")
            return LeanLibrary(file_path=file_path)
    
    def extract_theorems_from_directory(self, directory: Optional[str] = None) -> Dict[str, LeanLibrary]:
        """
        Extract theorems from all Lean files in a directory.
        
        Args:
            directory: Directory to search for Lean files (defaults to lean_lib_path)
            
        Returns:
            Dictionary mapping file paths to LeanLibrary objects
        """
        directory = directory or self.lean_lib_path
        libraries = {}
        
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith('.lean'):
                        file_path = os.path.join(root, file)
                        library = self.extract_theorems_from_file(file_path)
                        libraries[file_path] = library
                        logger.info(f"Extracted {len(library.theorems)} theorems from {file_path}")
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
        
        return libraries
    
    def find_theorem(self, theorem_id: str, namespace: Optional[str] = None) -> Optional[LeanTheorem]:
        """
        Find a theorem by ID and optional namespace.
        
        Args:
            theorem_id: ID of the theorem to find
            namespace: Optional namespace to search in
            
        Returns:
            LeanTheorem if found, None otherwise
        """
        libraries = self.extract_theorems_from_directory()
        
        # Search in all libraries
        for library in libraries.values():
            # Check if the theorem exists directly
            if theorem_id in library.theorems:
                theorem = library.theorems[theorem_id]
                # If namespace is specified, check that it matches
                if namespace is None or theorem.namespace == namespace:
                    return theorem
            
            # Check for namespaced theorem
            if namespace in library.namespaces and theorem_id in library.namespaces[namespace]:
                return library.theorems[theorem_id]
        
        return None
    
    def _get_namespace_at_position(self, position: int, namespace_events: List[Tuple[int, str, str]], 
                                  namespace_stack: List[str]) -> Optional[str]:
        """
        Determine the namespace at a given position in the file.
        
        Args:
            position: Position in the file
            namespace_events: List of namespace events (start/end) with positions
            namespace_stack: Stack to track namespace nesting
            
        Returns:
            Current namespace at the position
        """
        namespace_stack.clear()
        
        for event_pos, event_type, namespace in namespace_events:
            if event_pos > position:
                break
                
            if event_type == "start":
                namespace_stack.append(namespace)
            elif event_type == "end" and namespace_stack and namespace_stack[-1] == namespace:
                namespace_stack.pop()
        
        return namespace_stack[-1] if namespace_stack else None
    
    def _extract_variables(self, theorem_text: str) -> List[LeanVariable]:
        """
        Extract variables from a theorem definition.
        
        Args:
            theorem_text: Text of the theorem definition
            
        Returns:
            List of LeanVariable objects
        """
        variables = []
        
        # Find all variable blocks
        for implicit_match, explicit_match in self.variable_pattern.findall(theorem_text):
            is_implicit = bool(implicit_match)
            var_text = implicit_match if is_implicit else explicit_match
            
            # Skip empty matches
            if not var_text.strip():
                continue
            
            # Handle multiple variables in one declaration
            var_parts = var_text.split(',')
            
            for part in var_parts:
                # Skip empty parts
                if not part.strip():
                    continue
                
                # Extract name and type
                name_type_parts = part.split(':')
                if len(name_type_parts) >= 2:
                    name = name_type_parts[0].strip()
                    type_ = ':'.join(name_type_parts[1:]).strip()
                    
                    variables.append(LeanVariable(name=name, type_=type_, implicit=is_implicit))
        
        return variables
    
    def _extract_hypotheses(self, theorem_text: str) -> List[LeanHypothesis]:
        """
        Extract hypotheses from a theorem definition.
        
        Args:
            theorem_text: Text of the theorem definition
            
        Returns:
            List of LeanHypothesis objects
        """
        hypotheses = []
        
        # Find all hypothesis declarations
        for name, expression in self.hypothesis_pattern.findall(theorem_text):
            hypotheses.append(LeanHypothesis(name=name, expression=expression.strip()))
        
        return hypotheses
    
    def _extract_proof_outline(self, comment_text: str) -> Optional[str]:
        """
        Extract proof outline from comments.
        
        Args:
            comment_text: Comment text after the theorem
            
        Returns:
            Proof outline if found, None otherwise
        """
        # Check for multi-line proof outline
        multi_match = self.multi_proof_outline_pattern.search(comment_text)
        if multi_match:
            return multi_match.group(1).strip()
        
        # Check for inline proof outline
        inline_matches = self.inline_proof_outline_pattern.findall(comment_text)
        if inline_matches:
            return ' '.join(inline_matches).strip()
        
        # Check for any proof outline format
        outline_match = self.proof_outline_pattern.search(comment_text)
        if outline_match:
            return outline_match.group(1).strip()
        
        # Check for comment lines after "sorry"
        sorry_comments = []
        in_comment = False
        
        for line in comment_text.split('\n'):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Look for comment indicators
            if line.startswith('--'):
                sorry_comments.append(line[2:].strip())
                in_comment = True
            elif line.startswith('/-'):
                in_comment = True
                sorry_comments.append(line[2:].strip())
            elif line.endswith('-/'):
                if in_comment:
                    sorry_comments.append(line[:-2].strip())
                    in_comment = False
            elif in_comment:
                sorry_comments.append(line)
        
        return '\n'.join(sorry_comments) if sorry_comments else None


def create_theorem_request(theorem: LeanTheorem) -> Dict[str, Any]:
    """
    Create a theorem proving request from a LeanTheorem.
    
    Args:
        theorem: LeanTheorem to create request for
        
    Returns:
        Dictionary with request parameters
    """
    # Convert variables to dictionary format expected by prover
    variables = {var.name: var.type_ for var in theorem.variables}
    
    # Convert hypotheses to list format expected by prover
    assumptions = [f"{h.name}: {h.expression}" for h in theorem.hypotheses]
    
    # Create request
    request = {
        "theorem_id": theorem.theorem_id,
        "formal_expression": theorem.formal_expression,
        "variables": variables,
        "assumptions": assumptions,
        "context": f"Namespace: {theorem.namespace}" if theorem.namespace else "",
        "proof_outline": theorem.proof_outline
    }
    
    return request