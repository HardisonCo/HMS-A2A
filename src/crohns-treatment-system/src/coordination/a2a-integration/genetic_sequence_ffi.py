"""
Foreign Function Interface (FFI) wrapper for the Crohn's genetic sequence analyzer.

This module provides Python bindings to the Rust-based genetic sequence analyzer,
enabling genetic sequence analysis for Crohn's disease patients and treatment optimization.
"""

import json
import ctypes
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

# Load the shared library
_lib_path = None

def _get_lib_path() -> Path:
    """Get the path to the shared library."""
    base_dir = Path(__file__).parent.parent.parent
    if (base_dir / "target" / "release").exists():
        return base_dir / "target" / "release" / "libcrohns_genetic.so"
    else:
        return base_dir / "target" / "debug" / "libcrohns_genetic.so"

def _load_library():
    """Load the shared library with the genetic sequence analyzer."""
    global _lib_path
    if _lib_path is None:
        _lib_path = _get_lib_path()
        
    try:
        lib = ctypes.CDLL(str(_lib_path))
        logger.info(f"Successfully loaded genetic sequence analyzer library from {_lib_path}")
        return lib
    except Exception as e:
        logger.error(f"Failed to load genetic sequence analyzer library: {e}")
        raise RuntimeError(f"Failed to load genetic sequence analyzer library: {e}")

# Define FFI result structure
class GeneticAnalysisResult(ctypes.Structure):
    _fields_ = [
        ("data", ctypes.c_char_p),
        ("error", ctypes.c_char_p),
        ("success", ctypes.c_bool),
    ]

# Define function signatures
def _setup_ffi_functions(lib):
    """Configure the FFI function signatures."""
    # Initialize sequence analyzer
    lib.initialize_sequence_analyzer.argtypes = []
    lib.initialize_sequence_analyzer.restype = ctypes.c_void_p
    
    # Analyze genetic sequences
    lib.analyze_genetic_sequences.argtypes = [ctypes.c_char_p]
    lib.analyze_genetic_sequences.restype = ctypes.POINTER(GeneticAnalysisResult)
    
    # Get variant significance
    lib.get_variant_significance.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.get_variant_significance.restype = ctypes.POINTER(GeneticAnalysisResult)
    
    # Free result memory
    lib.free_genetic_analysis_result.argtypes = [ctypes.POINTER(GeneticAnalysisResult)]
    lib.free_genetic_analysis_result.restype = None
    
    return lib

# Global library instance
_lib = None

def _get_lib():
    """Get or initialize the library."""
    global _lib
    if _lib is None:
        _lib = _setup_ffi_functions(_load_library())
    return _lib

class GeneticSequenceAnalyzer:
    """Python wrapper for the Rust genetic sequence analyzer."""
    
    def __init__(self):
        """Initialize the genetic sequence analyzer."""
        self._lib = _get_lib()
        self._analyzer = self._lib.initialize_sequence_analyzer()
        if not self._analyzer:
            raise RuntimeError("Failed to initialize genetic sequence analyzer")
        logger.info("Genetic sequence analyzer initialized successfully")
    
    async def analyze_sequences(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze genetic sequences for a patient.
        
        Args:
            patient_data: Dictionary containing patient data including genetic sequences
                Required fields:
                - patient_id: Unique identifier for the patient
                - sequences: Dictionary mapping gene names to sequences
                Optional fields:
                - demographic: Dictionary with age, sex, etc.
                - clinical: Dictionary with clinical data
        
        Returns:
            Dictionary containing analysis results including:
            - variants: List of identified genetic variants
            - risk_assessment: Overall risk assessment
            - treatment_recommendations: List of recommended treatments with efficacy scores
        """
        # Run in a thread pool to avoid blocking the event loop
        return await asyncio.get_event_loop().run_in_executor(
            None, self._analyze_sequences_sync, patient_data
        )
    
    def _analyze_sequences_sync(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version of analyze_sequences for thread pool execution."""
        # Convert input to JSON
        input_json = json.dumps(patient_data).encode('utf-8')
        
        # Call Rust function
        result_ptr = self._lib.analyze_genetic_sequences(input_json)
        if not result_ptr:
            raise RuntimeError("Failed to analyze genetic sequences: null result")
        
        try:
            result = result_ptr.contents
            
            # Check for error
            if not result.success:
                error_msg = result.error.decode('utf-8') if result.error else "Unknown error"
                raise RuntimeError(f"Genetic sequence analysis failed: {error_msg}")
            
            # Parse and return result
            if result.data:
                return json.loads(result.data.decode('utf-8'))
            else:
                return {}
        finally:
            # Free memory allocated by Rust
            if result_ptr:
                self._lib.free_genetic_analysis_result(result_ptr)
    
    async def get_variant_significance(self, gene: str, variant: str) -> Dict[str, Any]:
        """
        Get significance information for a specific genetic variant.
        
        Args:
            gene: Name of the gene (e.g., "NOD2")
            variant: Identifier of the variant (e.g., "R702W")
        
        Returns:
            Dictionary containing significance information including:
            - significance: Clinical significance (e.g., "pathogenic", "benign")
            - description: Description of the variant's effects
            - literature: References to scientific literature
        """
        # Run in a thread pool to avoid blocking the event loop
        return await asyncio.get_event_loop().run_in_executor(
            None, self._get_variant_significance_sync, gene, variant
        )
    
    def _get_variant_significance_sync(self, gene: str, variant: str) -> Dict[str, Any]:
        """Synchronous version of get_variant_significance for thread pool execution."""
        # Convert input to C strings
        gene_c = gene.encode('utf-8')
        variant_c = variant.encode('utf-8')
        
        # Call Rust function
        result_ptr = self._lib.get_variant_significance(gene_c, variant_c)
        if not result_ptr:
            raise RuntimeError("Failed to get variant significance: null result")
        
        try:
            result = result_ptr.contents
            
            # Check for error
            if not result.success:
                error_msg = result.error.decode('utf-8') if result.error else "Unknown error"
                raise RuntimeError(f"Failed to get variant significance: {error_msg}")
            
            # Parse and return result
            if result.data:
                return json.loads(result.data.decode('utf-8'))
            else:
                return {}
        finally:
            # Free memory allocated by Rust
            if result_ptr:
                self._lib.free_genetic_analysis_result(result_ptr)

# Singleton instance for reuse
_analyzer_instance = None

async def get_analyzer() -> GeneticSequenceAnalyzer:
    """Get or create a singleton instance of the genetic sequence analyzer."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = GeneticSequenceAnalyzer()
    return _analyzer_instance

async def analyze_patient_sequences(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to analyze genetic sequences for a patient.
    
    Args:
        patient_data: Dictionary containing patient data including genetic sequences
    
    Returns:
        Dictionary containing analysis results
    """
    analyzer = await get_analyzer()
    return await analyzer.analyze_sequences(patient_data)

async def get_crohns_variant_info(gene: str, variant: str) -> Dict[str, Any]:
    """
    Convenience function to get information about a Crohn's disease genetic variant.
    
    Args:
        gene: Name of the gene
        variant: Identifier of the variant
    
    Returns:
        Dictionary containing variant information
    """
    analyzer = await get_analyzer()
    return await analyzer.get_variant_significance(gene, variant)