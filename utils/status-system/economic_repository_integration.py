#!/usr/bin/env python3
"""
Economic Repository Integration

This module integrates the economic domain formalization with repository analysis,
allowing the system to track, monitor, and optimize economic theorems and proofs
within the repository structure. It provides the bridge between the economic domain
model and the genetic agent system for repository analysis.

Key Components:
- TheoremRepository: Manages theorems and proofs within the repository
- EconomicRepositoryAnalyzer: Analyzes repository status related to economic theorems
- ProofStatusTracker: Tracks the status of theorem proofs
- TheoremOptimizer: Optimizes theorem statements and proofs
"""

import os
import re
import json
import time
import shutil
import logging
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from economic_domain_model import (
    ConceptType, DomainAxiom, DomainModelManager, DomainTheorem, 
    EconomicConcept, FormalDefinition, FormalizationLanguage,
    Proof, ProofStep, TheoremStatus
)

from economic_formal_translator import (
    LeanTranslator, FormalStructureGenerator, ProofGenerator, EconomicInterpreter
)

from economic_theorem_prover import (
    TheoremProver, ProofStrategy, SubgoalDecomposer, ProofVerifier, DeepSeekProverInterface
)

from repository_analyzer import RepositoryAnalyzer, RepositoryIssue, IssueSeverity
from genetic_agent_system import GeneticAgentSystem, Agent, AgentTask


@dataclass
class TheoremRepositoryConfig:
    """Configuration for the theorem repository."""
    root_path: str
    lean_export_path: str
    backup_interval: timedelta = field(default_factory=lambda: timedelta(hours=24))
    max_backups: int = 5
    auto_export: bool = True
    organize_by_concept_type: bool = True


class TheoremRepository:
    """Manages theorems and proofs within the repository structure."""
    
    def __init__(self, 
                 domain_manager: DomainModelManager, 
                 config: TheoremRepositoryConfig):
        """Initialize the theorem repository.
        
        Args:
            domain_manager: The domain model manager
            config: Repository configuration
        """
        self.domain_manager = domain_manager
        self.config = config
        self.logger = logging.getLogger("TheoremRepository")
        
        # Create repository directories
        os.makedirs(self.config.root_path, exist_ok=True)
        os.makedirs(self.config.lean_export_path, exist_ok=True)
        
        # Initialize concept type directories if needed
        if self.config.organize_by_concept_type:
            for concept_type in ConceptType:
                concept_dir = os.path.join(self.config.root_path, concept_type.value)
                os.makedirs(concept_dir, exist_ok=True)
        
        # Last backup timestamp
        self.last_backup = datetime.now() - self.config.backup_interval
    
    def export_all_theorems(self) -> None:
        """Export all theorems to the repository structure."""
        # Check if backup is needed
        if datetime.now() - self.last_backup > self.config.backup_interval:
            self._create_backup()
        
        # Export theorems organized by concept type
        if self.config.organize_by_concept_type:
            for concept_type in ConceptType:
                theorems = self.domain_manager.get_concepts_by_type(concept_type)
                
                for concept in theorems:
                    if isinstance(concept, DomainTheorem):
                        self._export_theorem(concept)
        else:
            # Export all theorems in a flat structure
            for theorem_id, theorem in self.domain_manager.theorems.items():
                self._export_theorem(theorem)
        
        # Export to Lean format if configured
        if self.config.auto_export:
            self._export_to_lean()
    
    def _export_theorem(self, theorem: DomainTheorem) -> None:
        """Export a theorem to the repository structure."""
        if self.config.organize_by_concept_type:
            # Determine the destination directory
            dest_dir = os.path.join(self.config.root_path, theorem.concept_type.value)
        else:
            dest_dir = self.config.root_path
        
        # Create theorem filename
        filename = f"{theorem.id}.json"
        filepath = os.path.join(dest_dir, filename)
        
        # Export the theorem data
        with open(filepath, 'w') as f:
            json.dump(theorem.to_dict(), f, indent=2)
        
        # Export proofs if any
        if theorem.proofs:
            proofs_dir = os.path.join(dest_dir, f"{theorem.id}_proofs")
            os.makedirs(proofs_dir, exist_ok=True)
            
            for proof in theorem.proofs:
                proof_filename = f"{proof.proof_id}.json"
                proof_filepath = os.path.join(proofs_dir, proof_filename)
                
                with open(proof_filepath, 'w') as f:
                    json.dump(proof.to_dict(), f, indent=2)
    
    def _export_to_lean(self) -> None:
        """Export all theorems to Lean format."""
        # Export to Lean
        self.domain_manager.export_to_lean(self.config.lean_export_path)
        
        # Also export by concept type if configured
        if self.config.organize_by_concept_type:
            for concept_type in ConceptType:
                # Get concepts of this type
                concepts = self.domain_manager.get_concepts_by_type(concept_type)
                
                if concepts:
                    # Create concept type export directory
                    concept_export_dir = os.path.join(self.config.lean_export_path, concept_type.value)
                    os.makedirs(concept_export_dir, exist_ok=True)
                    
                    # Create a specialized manager for this concept type
                    specialized_manager = DomainModelManager(concept_export_dir)
                    
                    # Add concepts
                    for concept in concepts:
                        if isinstance(concept, DomainAxiom):
                            specialized_manager.add_axiom(concept)
                        elif isinstance(concept, DomainTheorem):
                            specialized_manager.add_theorem(concept)
                        else:
                            specialized_manager.add_concept(concept)
                    
                    # Export
                    specialized_manager.export_to_lean(concept_export_dir)
    
    def _create_backup(self) -> None:
        """Create a backup of the repository."""
        # Create backup directory
        backup_dir = os.path.join(self.config.root_path, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
        
        # Copy domain model files
        if os.path.exists(self.domain_manager.storage_dir):
            shutil.copytree(self.domain_manager.storage_dir, backup_path)
        
        # Clean up old backups if needed
        backup_dirs = sorted([d for d in os.listdir(backup_dir) if d.startswith("backup_")])
        if len(backup_dirs) > self.config.max_backups:
            for old_backup in backup_dirs[:-self.config.max_backups]:
                old_backup_path = os.path.join(backup_dir, old_backup)
                if os.path.isdir(old_backup_path):
                    shutil.rmtree(old_backup_path)
        
        # Update last backup timestamp
        self.last_backup = datetime.now()
        self.logger.info(f"Created backup at {backup_path}")
    
    def import_from_repository(self) -> None:
        """Import theorems from the repository structure."""
        # Import from the repository structure
        if self.config.organize_by_concept_type:
            for concept_type in ConceptType:
                concept_dir = os.path.join(self.config.root_path, concept_type.value)
                if os.path.isdir(concept_dir):
                    self._import_from_directory(concept_dir)
        else:
            self._import_from_directory(self.config.root_path)
    
    def _import_from_directory(self, directory: str) -> None:
        """Import theorems from a directory."""
        if not os.path.isdir(directory):
            return
        
        # Import theorem files
        for filename in os.listdir(directory):
            if filename.endswith(".json") and not filename.startswith("._"):
                filepath = os.path.join(directory, filename)
                
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    
                    # Determine if it's a theorem, axiom, or concept
                    if "proofs" in data:
                        # It's a theorem
                        theorem = DomainTheorem.from_dict(data)
                        
                        # Import proofs if they exist
                        proofs_dir = os.path.join(directory, f"{theorem.id}_proofs")
                        if os.path.isdir(proofs_dir):
                            for proof_file in os.listdir(proofs_dir):
                                if proof_file.endswith(".json") and not proof_file.startswith("._"):
                                    proof_path = os.path.join(proofs_dir, proof_file)
                                    
                                    with open(proof_path, 'r') as f:
                                        proof_data = json.load(f)
                                    
                                    proof = Proof.from_dict(proof_data)
                                    theorem.proofs.append(proof)
                        
                        # Add to domain manager
                        self.domain_manager.add_theorem(theorem)
                    
                    elif "is_primitive" in data:
                        # It's an axiom
                        axiom = DomainAxiom.from_dict(data)
                        self.domain_manager.add_axiom(axiom)
                    
                    else:
                        # It's a regular concept
                        concept = EconomicConcept.from_dict(data)
                        self.domain_manager.add_concept(concept)
                
                except Exception as e:
                    self.logger.error(f"Error importing {filepath}: {str(e)}")
    
    def get_theorem_file_path(self, theorem_id: str) -> Optional[str]:
        """Get the file path for a theorem in the repository.
        
        Args:
            theorem_id: ID of the theorem
            
        Returns:
            Path to the theorem file, or None if not found
        """
        theorem = self.domain_manager.get_theorem(theorem_id)
        if not theorem:
            return None
        
        if self.config.organize_by_concept_type:
            # Look in the concept type directory
            filepath = os.path.join(
                self.config.root_path, 
                theorem.concept_type.value, 
                f"{theorem_id}.json"
            )
        else:
            # Look in the root directory
            filepath = os.path.join(self.config.root_path, f"{theorem_id}.json")
        
        if os.path.exists(filepath):
            return filepath
        
        return None
    
    def get_theorem_proof_path(self, theorem_id: str, proof_id: str) -> Optional[str]:
        """Get the file path for a theorem proof in the repository.
        
        Args:
            theorem_id: ID of the theorem
            proof_id: ID of the proof
            
        Returns:
            Path to the proof file, or None if not found
        """
        theorem = self.domain_manager.get_theorem(theorem_id)
        if not theorem:
            return None
        
        if self.config.organize_by_concept_type:
            # Look in the concept type directory
            proofs_dir = os.path.join(
                self.config.root_path, 
                theorem.concept_type.value, 
                f"{theorem_id}_proofs"
            )
        else:
            # Look in the root directory
            proofs_dir = os.path.join(self.config.root_path, f"{theorem_id}_proofs")
        
        proof_path = os.path.join(proofs_dir, f"{proof_id}.json")
        if os.path.exists(proof_path):
            return proof_path
        
        return None


@dataclass
class TheoremRepositoryIssue(RepositoryIssue):
    """Issues related to economic theorems in the repository."""
    
    @classmethod
    def incomplete_proof(cls, theorem_id: str, message: str) -> 'TheoremRepositoryIssue':
        """Create an issue for an incomplete proof."""
        return cls(
            issue_id=f"incomplete_proof_{theorem_id}_{int(time.time())}",
            title=f"Incomplete proof for theorem {theorem_id}",
            description=message,
            severity=IssueSeverity.MEDIUM,
            location=f"theorem:{theorem_id}",
            tags=["proof", "incomplete"]
        )
    
    @classmethod
    def unverified_proof(cls, theorem_id: str, proof_id: str) -> 'TheoremRepositoryIssue':
        """Create an issue for an unverified proof."""
        return cls(
            issue_id=f"unverified_proof_{theorem_id}_{proof_id}_{int(time.time())}",
            title=f"Unverified proof {proof_id} for theorem {theorem_id}",
            description="The proof has not been verified by the proof checker.",
            severity=IssueSeverity.MEDIUM,
            location=f"theorem:{theorem_id}:proof:{proof_id}",
            tags=["proof", "unverified"]
        )
    
    @classmethod
    def missing_decomposition(cls, theorem_id: str) -> 'TheoremRepositoryIssue':
        """Create an issue for a complex theorem without decomposition."""
        return cls(
            issue_id=f"missing_decomposition_{theorem_id}_{int(time.time())}",
            title=f"Complex theorem {theorem_id} without decomposition",
            description="This complex theorem could benefit from decomposition into simpler subgoals.",
            severity=IssueSeverity.LOW,
            location=f"theorem:{theorem_id}",
            tags=["theorem", "decomposition"]
        )
    
    @classmethod
    def inconsistent_dependencies(cls, theorem_id: str, dependencies: List[str]) -> 'TheoremRepositoryIssue':
        """Create an issue for inconsistent dependencies."""
        return cls(
            issue_id=f"inconsistent_deps_{theorem_id}_{int(time.time())}",
            title=f"Inconsistent dependencies for theorem {theorem_id}",
            description=f"The theorem has dependencies that are not consistent: {', '.join(dependencies)}",
            severity=IssueSeverity.HIGH,
            location=f"theorem:{theorem_id}",
            tags=["theorem", "dependencies", "inconsistency"]
        )
    
    @classmethod
    def code_style_issue(cls, theorem_id: str, message: str) -> 'TheoremRepositoryIssue':
        """Create an issue for code style problems."""
        return cls(
            issue_id=f"code_style_{theorem_id}_{int(time.time())}",
            title=f"Code style issue in theorem {theorem_id}",
            description=message,
            severity=IssueSeverity.LOW,
            location=f"theorem:{theorem_id}",
            tags=["theorem", "code_style"]
        )
    
    @classmethod
    def optimization_opportunity(cls, theorem_id: str, message: str) -> 'TheoremRepositoryIssue':
        """Create an issue for optimization opportunities."""
        return cls(
            issue_id=f"optimization_{theorem_id}_{int(time.time())}",
            title=f"Optimization opportunity for theorem {theorem_id}",
            description=message,
            severity=IssueSeverity.LOW,
            location=f"theorem:{theorem_id}",
            tags=["theorem", "optimization"]
        )


class EconomicRepositoryAnalyzer:
    """Analyzes repository status related to economic theorems."""
    
    def __init__(self, 
                 domain_manager: DomainModelManager,
                 theorem_repository: TheoremRepository,
                 repo_analyzer: RepositoryAnalyzer):
        """Initialize the economic repository analyzer.
        
        Args:
            domain_manager: The domain model manager
            theorem_repository: The theorem repository
            repo_analyzer: The general repository analyzer
        """
        self.domain_manager = domain_manager
        self.theorem_repository = theorem_repository
        self.repo_analyzer = repo_analyzer
        self.logger = logging.getLogger("EconomicRepositoryAnalyzer")
    
    def analyze_repository(self) -> List[TheoremRepositoryIssue]:
        """Analyze the theorem repository for issues.
        
        Returns:
            List of repository issues
        """
        issues = []
        
        # Analyze all theorems
        for theorem_id, theorem in self.domain_manager.theorems.items():
            # Check for incomplete proofs
            if theorem.status == TheoremStatus.PARTIALLY_PROVEN:
                issues.append(TheoremRepositoryIssue.incomplete_proof(
                    theorem_id=theorem_id,
                    message="Theorem has partial proofs but is not fully proven."
                ))
            
            # Check for unverified proofs
            for proof in theorem.proofs:
                if not proof.verified:
                    issues.append(TheoremRepositoryIssue.unverified_proof(
                        theorem_id=theorem_id,
                        proof_id=proof.proof_id
                    ))
            
            # Check for complex theorems without decomposition
            if theorem.difficulty >= 5 and not theorem.decomposition:
                issues.append(TheoremRepositoryIssue.missing_decomposition(
                    theorem_id=theorem_id
                ))
            
            # Check for inconsistent dependencies
            issues.extend(self._check_dependencies(theorem))
            
            # Check for code style issues
            issues.extend(self._check_code_style(theorem))
            
            # Check for optimization opportunities
            issues.extend(self._check_optimization_opportunities(theorem))
        
        return issues
    
    def _check_dependencies(self, theorem: DomainTheorem) -> List[TheoremRepositoryIssue]:
        """Check theorem dependencies for issues."""
        issues = []
        
        # Get formal definition
        lean_def = theorem.get_formal_definition(FormalizationLanguage.LEAN4)
        if not lean_def:
            return issues
        
        # Check if all dependencies exist
        missing_deps = []
        for dep_id in lean_def.dependencies:
            if not (self.domain_manager.get_axiom(dep_id) or self.domain_manager.get_theorem(dep_id)):
                missing_deps.append(dep_id)
        
        if missing_deps:
            issues.append(TheoremRepositoryIssue.inconsistent_dependencies(
                theorem_id=theorem.id,
                dependencies=missing_deps
            ))
        
        return issues
    
    def _check_code_style(self, theorem: DomainTheorem) -> List[TheoremRepositoryIssue]:
        """Check theorem code style for issues."""
        issues = []
        
        # Get formal definition
        lean_def = theorem.get_formal_definition(FormalizationLanguage.LEAN4)
        if not lean_def:
            return issues
        
        code = lean_def.code
        
        # Check for basic style issues
        if not code.strip():
            issues.append(TheoremRepositoryIssue.code_style_issue(
                theorem_id=theorem.id,
                message="Empty formal definition."
            ))
            return issues
        
        # Check for "sorry" in a supposedly complete proof
        if theorem.status == TheoremStatus.PROVEN and "sorry" in code:
            issues.append(TheoremRepositoryIssue.code_style_issue(
                theorem_id=theorem.id,
                message="Proven theorem still contains 'sorry' in the formal definition."
            ))
        
        # Check for inconsistent naming
        theorem_name = theorem.name.lower().replace(" ", "_").replace("-", "_")
        identifier_pattern = r'theorem\s+(\w+)'
        match = re.search(identifier_pattern, code)
        if match:
            identifier = match.group(1).lower()
            if not (identifier in theorem_name or theorem_name in identifier):
                issues.append(TheoremRepositoryIssue.code_style_issue(
                    theorem_id=theorem.id,
                    message=f"Theorem identifier '{identifier}' doesn't match theorem name '{theorem.name}'."
                ))
        
        # Check for missing documentation comments
        if not re.search(r'/--.*--/', code, re.DOTALL):
            issues.append(TheoremRepositoryIssue.code_style_issue(
                theorem_id=theorem.id,
                message="Missing documentation comments."
            ))
        
        return issues
    
    def _check_optimization_opportunities(self, theorem: DomainTheorem) -> List[TheoremRepositoryIssue]:
        """Check for theorem optimization opportunities."""
        issues = []
        
        # Get formal definition
        lean_def = theorem.get_formal_definition(FormalizationLanguage.LEAN4)
        if not lean_def:
            return issues
        
        code = lean_def.code
        
        # Check for long or complex proofs that could be optimized
        for proof in theorem.proofs:
            if len(proof.steps) > 15:
                issues.append(TheoremRepositoryIssue.optimization_opportunity(
                    theorem_id=theorem.id,
                    message=f"Proof '{proof.proof_id}' has {len(proof.steps)} steps and might benefit from refactoring."
                ))
        
        # Check for theorems with multiple proofs (potential for consolidation)
        if len(theorem.proofs) > 1:
            issues.append(TheoremRepositoryIssue.optimization_opportunity(
                theorem_id=theorem.id,
                message=f"Theorem has {len(theorem.proofs)} proofs. Consider consolidating to the best one."
            ))
        
        # Check for complex dependencies that might be simplified
        if lean_def.dependencies and len(lean_def.dependencies) > 5:
            issues.append(TheoremRepositoryIssue.optimization_opportunity(
                theorem_id=theorem.id,
                message=f"Theorem depends on {len(lean_def.dependencies)} other concepts. Consider simplifying dependencies."
            ))
        
        return issues
    
    def create_reports(self, output_dir: str) -> Dict[str, str]:
        """Create analysis reports for the economic repository.
        
        Args:
            output_dir: Directory to write reports to
            
        Returns:
            Dictionary mapping report names to file paths
        """
        os.makedirs(output_dir, exist_ok=True)
        reports = {}
        
        # Create issues report
        issues = self.analyze_repository()
        issues_path = os.path.join(output_dir, "theorem_issues.json")
        with open(issues_path, 'w') as f:
            json.dump([issue.to_dict() for issue in issues], f, indent=2)
        reports["issues"] = issues_path
        
        # Create theorem status report
        status_report = self._generate_theorem_status_report()
        status_path = os.path.join(output_dir, "theorem_status.json")
        with open(status_path, 'w') as f:
            json.dump(status_report, f, indent=2)
        reports["status"] = status_path
        
        # Create progress report
        progress_report = self._generate_progress_report()
        progress_path = os.path.join(output_dir, "theorem_progress.json")
        with open(progress_path, 'w') as f:
            json.dump(progress_report, f, indent=2)
        reports["progress"] = progress_path
        
        # Create statistics report
        stats_report = self._generate_statistics_report()
        stats_path = os.path.join(output_dir, "theorem_statistics.json")
        with open(stats_path, 'w') as f:
            json.dump(stats_report, f, indent=2)
        reports["statistics"] = stats_path
        
        return reports
    
    def _generate_theorem_status_report(self) -> Dict[str, Any]:
        """Generate a report on theorem status."""
        # Organize theorems by status
        status_counts = {status.value: 0 for status in TheoremStatus}
        theorems_by_status = {status.value: [] for status in TheoremStatus}
        
        for theorem_id, theorem in self.domain_manager.theorems.items():
            status_counts[theorem.status.value] += 1
            theorems_by_status[theorem.status.value].append({
                "id": theorem_id,
                "name": theorem.name,
                "concept_type": theorem.concept_type.value,
                "difficulty": theorem.difficulty,
                "importance": theorem.importance,
                "num_proofs": len(theorem.proofs),
                "verified_proofs": sum(1 for p in theorem.proofs if p.verified)
            })
        
        # Organize by concept type
        type_counts = {ct.value: 0 for ct in ConceptType}
        theorems_by_type = {ct.value: [] for ct in ConceptType}
        
        for theorem_id, theorem in self.domain_manager.theorems.items():
            type_counts[theorem.concept_type.value] += 1
            theorems_by_type[theorem.concept_type.value].append({
                "id": theorem_id,
                "name": theorem.name,
                "status": theorem.status.value,
                "difficulty": theorem.difficulty,
                "importance": theorem.importance
            })
        
        return {
            "total_theorems": len(self.domain_manager.theorems),
            "status_counts": status_counts,
            "theorems_by_status": theorems_by_status,
            "type_counts": type_counts,
            "theorems_by_type": theorems_by_type,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_progress_report(self) -> Dict[str, Any]:
        """Generate a report on theorem proving progress."""
        # Calculate overall progress
        total_theorems = len(self.domain_manager.theorems)
        if total_theorems == 0:
            return {"progress": 0, "theorems": {}}
        
        # Define progress weights by status
        status_weights = {
            TheoremStatus.CONJECTURED.value: 0.0,
            TheoremStatus.PARTIALLY_PROVEN.value: 0.5,
            TheoremStatus.PROVEN.value: 1.0,
            TheoremStatus.DISPROVEN.value: 1.0,
            TheoremStatus.UNDECIDABLE.value: 1.0
        }
        
        # Calculate progress for each theorem and overall
        theorem_progress = {}
        total_progress = 0.0
        
        for theorem_id, theorem in self.domain_manager.theorems.items():
            # Base progress on status
            status_progress = status_weights[theorem.status.value]
            
            # Adjust by proof completeness
            if theorem.proofs:
                proof_progress = sum(
                    (1.0 if p.complete else 0.5) * (1.0 if p.verified else 0.5)
                    for p in theorem.proofs
                ) / len(theorem.proofs)
                
                # Combine status and proof progress
                progress = (status_progress + proof_progress) / 2
            else:
                progress = status_progress * 0.8  # Penalize for no proofs
            
            # Weight by importance
            weighted_progress = progress * (theorem.importance / 10.0)
            
            # Store theorem progress
            theorem_progress[theorem_id] = {
                "raw_progress": progress,
                "weighted_progress": weighted_progress,
                "importance": theorem.importance,
                "status": theorem.status.value,
                "proof_count": len(theorem.proofs),
                "verified_count": sum(1 for p in theorem.proofs if p.verified)
            }
            
            # Add to total progress
            total_progress += weighted_progress * (theorem.importance / 10.0)
        
        # Normalize total progress
        if total_theorems > 0:
            total_importance = sum(t.importance for t in self.domain_manager.theorems.values())
            normalized_progress = total_progress * 10.0 / total_importance if total_importance > 0 else 0
        else:
            normalized_progress = 0
        
        return {
            "overall_progress": normalized_progress,
            "progress_by_theorem": theorem_progress,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_statistics_report(self) -> Dict[str, Any]:
        """Generate a statistical report on the theorem repository."""
        # Basic statistics
        theorems = self.domain_manager.theorems
        
        if not theorems:
            return {"timestamp": datetime.now().isoformat()}
        
        # Calculate statistics
        avg_difficulty = sum(t.difficulty for t in theorems.values()) / len(theorems)
        avg_importance = sum(t.importance for t in theorems.values()) / len(theorems)
        
        max_difficulty_theorem = max(theorems.values(), key=lambda t: t.difficulty)
        max_importance_theorem = max(theorems.values(), key=lambda t: t.importance)
        
        proof_counts = [len(t.proofs) for t in theorems.values()]
        avg_proofs = sum(proof_counts) / len(theorems)
        
        step_counts = [
            len(p.steps) for t in theorems.values() 
            for p in t.proofs if p.steps
        ]
        avg_steps = sum(step_counts) / len(step_counts) if step_counts else 0
        
        # Complexity metrics
        complexity_metrics = {
            "avg_difficulty": avg_difficulty,
            "avg_importance": avg_importance,
            "max_difficulty": {
                "value": max_difficulty_theorem.difficulty,
                "theorem": max_difficulty_theorem.id,
                "theorem_name": max_difficulty_theorem.name
            },
            "max_importance": {
                "value": max_importance_theorem.importance,
                "theorem": max_importance_theorem.id,
                "theorem_name": max_importance_theorem.name
            },
            "avg_proofs_per_theorem": avg_proofs,
            "avg_steps_per_proof": avg_steps,
            "theorems_with_no_proofs": sum(1 for t in theorems.values() if not t.proofs),
            "theorems_with_decomposition": sum(1 for t in theorems.values() if t.decomposition)
        }
        
        # Concept type distribution
        type_distribution = {ct.value: 0 for ct in ConceptType}
        for theorem in theorems.values():
            type_distribution[theorem.concept_type.value] += 1
        
        # Status distribution
        status_distribution = {status.value: 0 for status in TheoremStatus}
        for theorem in theorems.values():
            status_distribution[theorem.status.value] += 1
        
        return {
            "total_theorems": len(theorems),
            "total_proofs": sum(len(t.proofs) for t in theorems.values()),
            "verified_proofs": sum(sum(1 for p in t.proofs if p.verified) for t in theorems.values()),
            "complexity_metrics": complexity_metrics,
            "concept_type_distribution": type_distribution,
            "status_distribution": status_distribution,
            "timestamp": datetime.now().isoformat()
        }


class ProofStatusTracker:
    """Tracks the status of theorem proofs."""
    
    def __init__(self, 
                 domain_manager: DomainModelManager,
                 theorem_repository: TheoremRepository,
                 prover: TheoremProver):
        """Initialize the proof status tracker.
        
        Args:
            domain_manager: The domain model manager
            theorem_repository: The theorem repository
            prover: The theorem prover
        """
        self.domain_manager = domain_manager
        self.theorem_repository = theorem_repository
        self.prover = prover
        self.logger = logging.getLogger("ProofStatusTracker")
        
        # Status change history
        self.status_history = {}
    
    def track_theorem_status(self, theorem_id: str) -> Dict[str, Any]:
        """Track the status of a theorem.
        
        Args:
            theorem_id: ID of the theorem to track
            
        Returns:
            Dictionary with status information
        """
        theorem = self.domain_manager.get_theorem(theorem_id)
        if not theorem:
            return {"error": f"Theorem not found: {theorem_id}"}
        
        # Get current status
        current_status = {
            "id": theorem_id,
            "name": theorem.name,
            "status": theorem.status.value,
            "proofs": [{
                "id": p.proof_id,
                "complete": p.complete,
                "verified": p.verified,
                "steps": len(p.steps)
            } for p in theorem.proofs],
            "decomposition": theorem.decomposition,
            "timestamp": datetime.now().isoformat()
        }
        
        # Update history
        if theorem_id not in self.status_history:
            self.status_history[theorem_id] = []
        
        # Check if status has changed
        if (not self.status_history[theorem_id] or 
            self.status_history[theorem_id][-1]["status"] != current_status["status"] or
            len(self.status_history[theorem_id][-1]["proofs"]) != len(current_status["proofs"])):
            self.status_history[theorem_id].append(current_status)
        
        return current_status
    
    def track_all_theorems(self) -> Dict[str, Dict[str, Any]]:
        """Track the status of all theorems.
        
        Returns:
            Dictionary mapping theorem IDs to status information
        """
        statuses = {}
        for theorem_id in self.domain_manager.theorems:
            statuses[theorem_id] = self.track_theorem_status(theorem_id)
        return statuses
    
    def get_status_history(self, theorem_id: str) -> List[Dict[str, Any]]:
        """Get the status history for a theorem.
        
        Args:
            theorem_id: ID of the theorem
            
        Returns:
            List of status entries in chronological order
        """
        return self.status_history.get(theorem_id, [])
    
    def export_status_history(self, output_dir: str) -> None:
        """Export status history to JSON files.
        
        Args:
            output_dir: Directory to export to
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Export overall status
        status_file = os.path.join(output_dir, "theorem_status_history.json")
        with open(status_file, 'w') as f:
            json.dump(self.status_history, f, indent=2)
        
        # Export individual theorem histories
        history_dir = os.path.join(output_dir, "theorem_histories")
        os.makedirs(history_dir, exist_ok=True)
        
        for theorem_id, history in self.status_history.items():
            theorem_file = os.path.join(history_dir, f"{theorem_id}_history.json")
            with open(theorem_file, 'w') as f:
                json.dump(history, f, indent=2)


class TheoremOptimizer:
    """Optimizes theorem statements and proofs."""
    
    def __init__(self, 
                 domain_manager: DomainModelManager,
                 translator: LeanTranslator,
                 prover: TheoremProver):
        """Initialize the theorem optimizer.
        
        Args:
            domain_manager: The domain model manager
            translator: The Lean translator
            prover: The theorem prover
        """
        self.domain_manager = domain_manager
        self.translator = translator
        self.prover = prover
        self.logger = logging.getLogger("TheoremOptimizer")
    
    def optimize_theorem_statement(self, theorem_id: str) -> Tuple[bool, str]:
        """Optimize a theorem statement.
        
        Args:
            theorem_id: ID of the theorem to optimize
            
        Returns:
            Tuple of (success, message)
        """
        theorem = self.domain_manager.get_theorem(theorem_id)
        if not theorem:
            return False, f"Theorem not found: {theorem_id}"
        
        # Get formal definition
        lean_def = theorem.get_formal_definition(FormalizationLanguage.LEAN4)
        if not lean_def:
            return False, "No formal definition found"
        
        # Analyze the formal definition
        optimized_code = self._optimize_lean_code(lean_def.code)
        
        if optimized_code == lean_def.code:
            return False, "No optimizations found"
        
        # Update the formal definition
        theorem.add_formal_definition(FormalDefinition(
            language=FormalizationLanguage.LEAN4,
            code=optimized_code,
            imports=lean_def.imports,
            dependencies=lean_def.dependencies
        ))
        
        # Update the theorem
        self.domain_manager.add_theorem(theorem)
        
        return True, "Theorem statement optimized"
    
    def optimize_proof(self, theorem_id: str, proof_id: str) -> Tuple[bool, str]:
        """Optimize a theorem proof.
        
        Args:
            theorem_id: ID of the theorem
            proof_id: ID of the proof to optimize
            
        Returns:
            Tuple of (success, message)
        """
        theorem = self.domain_manager.get_theorem(theorem_id)
        if not theorem:
            return False, f"Theorem not found: {theorem_id}"
        
        # Find the proof
        proof = None
        for p in theorem.proofs:
            if p.proof_id == proof_id:
                proof = p
                break
        
        if not proof:
            return False, f"Proof not found: {proof_id}"
        
        # Check if there are steps to optimize
        if not proof.steps:
            return False, "No proof steps to optimize"
        
        # Optimize the proof steps
        optimized_steps = self._optimize_proof_steps(proof.steps)
        
        if len(optimized_steps) == len(proof.steps):
            # No step reduction, check for code optimization
            optimized = False
            for i, (orig, opt) in enumerate(zip(proof.steps, optimized_steps)):
                if orig.formal_code != opt.formal_code:
                    optimized = True
                    break
            
            if not optimized:
                return False, "No optimizations found"
        
        # Create a new optimized proof
        new_proof_id = f"{proof_id}_optimized_{int(time.time())}"
        optimized_proof = Proof(
            proof_id=new_proof_id,
            language=proof.language,
            steps=optimized_steps,
            complete=proof.complete,
            verified=False,  # Reset verification since we modified the proof
            created_by=f"optimizer_{int(time.time())}",
            created_at=datetime.now().isoformat(),
            metadata={
                "original_proof_id": proof_id,
                "optimization_timestamp": datetime.now().isoformat()
            }
        )
        
        # Add the optimized proof to the theorem
        theorem.proofs.append(optimized_proof)
        self.domain_manager.add_theorem(theorem)
        
        # Try to verify the optimized proof
        verified, _ = self.prover.verifier.verify_proof(theorem, optimized_proof)
        if verified:
            # Update proof verification status
            for p in theorem.proofs:
                if p.proof_id == new_proof_id:
                    p.verified = True
                    break
            self.domain_manager.add_theorem(theorem)
            
            return True, f"Proof optimized and verified: {new_proof_id}"
        
        return True, f"Proof optimized but not verified: {new_proof_id}"
    
    def _optimize_lean_code(self, code: str) -> str:
        """Optimize Lean code by applying heuristic rules."""
        # Example optimization rules (in a real implementation, these would be more sophisticated)
        
        # Remove unnecessary parentheses
        code = re.sub(r'\(\s*([a-zA-Z0-9_]+)\s*\)', r'\1', code)
        
        # Simplify nested implications: (A → (B → C)) to (A → B → C)
        code = re.sub(r'(\([^()]*?)\s*→\s*\(([^()]*?)\s*→\s*([^()]*?)\)', r'\1 → \2 → \3', code)
        
        # Simplify nested conjunctions: (A ∧ (B ∧ C)) to (A ∧ B ∧ C)
        code = re.sub(r'(\([^()]*?)\s*∧\s*\(([^()]*?)\s*∧\s*([^()]*?)\)', r'\1 ∧ \2 ∧ \3', code)
        
        # Clean up whitespace
        code = re.sub(r'\s+', ' ', code)
        code = re.sub(r'\s*:\s*', ': ', code)
        code = re.sub(r'\s*→\s*', ' → ', code)
        code = re.sub(r'\s*∧\s*', ' ∧ ', code)
        code = re.sub(r'\s*∨\s*', ' ∨ ', code)
        
        # Ensure consistent indentation
        lines = code.split('\n')
        indented_lines = []
        for line in lines:
            if line.strip().startswith('theorem'):
                indented_lines.append(line.strip())
            elif line.strip().startswith('--'):
                indented_lines.append(line.strip())
            else:
                indented_lines.append('  ' + line.strip())
        
        return '\n'.join(indented_lines)
    
    def _optimize_proof_steps(self, steps: List[ProofStep]) -> List[ProofStep]:
        """Optimize proof steps by removing redundancies and simplifying."""
        if not steps:
            return []
        
        optimized_steps = []
        
        # Copy the first step
        optimized_steps.append(ProofStep(
            step_id=steps[0].step_id,
            description=steps[0].description,
            formal_code=self._optimize_lean_code(steps[0].formal_code),
            depends_on=steps[0].depends_on,
            confidence=steps[0].confidence
        ))
        
        # Process remaining steps
        for i in range(1, len(steps)):
            current_step = steps[i]
            prev_step = steps[i-1]
            
            # Skip redundant steps (e.g., repeated assumptions)
            if current_step.formal_code.strip() == prev_step.formal_code.strip():
                continue
            
            # Skip trivial steps
            if current_step.formal_code.strip() in ('assumption', 'refl', 'trivial'):
                # Only keep if it's the concluding step
                if i == len(steps) - 1:
                    optimized_steps.append(ProofStep(
                        step_id=f"step_{len(optimized_steps)+1}",
                        description=current_step.description,
                        formal_code=current_step.formal_code,
                        depends_on=[optimized_steps[-1].step_id],
                        confidence=current_step.confidence
                    ))
                continue
            
            # Combine similar consecutive steps (e.g., multiple rw steps)
            if (current_step.formal_code.startswith('rw') and 
                prev_step.formal_code.startswith('rw')):
                # Extract the rewrite targets
                prev_rw = re.findall(r'rw\s+\[(.*?)\]', prev_step.formal_code)
                curr_rw = re.findall(r'rw\s+\[(.*?)\]', current_step.formal_code)
                
                if prev_rw and curr_rw:
                    # Combine the rewrite targets
                    combined_rw = f"rw [{prev_rw[0]}, {curr_rw[0]}]"
                    
                    # Replace the last step with the combined one
                    optimized_steps[-1] = ProofStep(
                        step_id=optimized_steps[-1].step_id,
                        description=f"Combined rewrite: {prev_step.description} and {current_step.description}",
                        formal_code=combined_rw,
                        depends_on=optimized_steps[-1].depends_on,
                        confidence=min(prev_step.confidence, current_step.confidence)
                    )
                    continue
            
            # Otherwise add the optimized step
            optimized_steps.append(ProofStep(
                step_id=f"step_{len(optimized_steps)+1}",
                description=current_step.description,
                formal_code=self._optimize_lean_code(current_step.formal_code),
                depends_on=[optimized_steps[-1].step_id],
                confidence=current_step.confidence
            ))
        
        return optimized_steps


class EconomicGeneticAgent(Agent):
    """Specialized genetic agent for economic theorem proving."""
    
    def __init__(self, 
                 agent_id: str, 
                 name: str,
                 domain_manager: DomainModelManager,
                 prover: TheoremProver,
                 optimizer: TheoremOptimizer,
                 concept_type: Optional[ConceptType] = None,
                 specialization: Optional[str] = None):
        """Initialize the economic genetic agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Name of the agent
            domain_manager: The domain model manager
            prover: The theorem prover
            optimizer: The theorem optimizer
            concept_type: The concept type this agent specializes in (optional)
            specialization: The agent's specialization (e.g., "decomposition", "proving") (optional)
        """
        super().__init__(agent_id, name)
        self.domain_manager = domain_manager
        self.prover = prover
        self.optimizer = optimizer
        self.concept_type = concept_type
        self.specialization = specialization
        
        # Agent genome characteristics
        self.theorem_selection_preference = 0.5  # From random to importance-based
        self.risk_tolerance = 0.5  # From conservative to aggressive
        self.optimization_frequency = 0.3  # How often to attempt optimizations
        self.decomposition_threshold = 5  # Complexity threshold for decomposition
        self.proof_style_preference = 0.5  # From direct to complex proofs
        
        # Performance tracking
        self.theorems_attempted = []
        self.theorems_proven = []
        self.optimizations_attempted = []
        self.optimizations_successful = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "concept_type": self.concept_type.value if self.concept_type else None,
            "specialization": self.specialization,
            "genome": {
                "theorem_selection_preference": self.theorem_selection_preference,
                "risk_tolerance": self.risk_tolerance,
                "optimization_frequency": self.optimization_frequency,
                "decomposition_threshold": self.decomposition_threshold,
                "proof_style_preference": self.proof_style_preference
            },
            "performance": {
                "theorems_attempted": len(self.theorems_attempted),
                "theorems_proven": len(self.theorems_proven),
                "optimizations_attempted": len(self.optimizations_attempted),
                "optimizations_successful": len(self.optimizations_successful)
            }
        })
        return data
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a task based on agent's genome and specialization.
        
        Args:
            task: The task to execute
            
        Returns:
            Result of the task execution
        """
        task_type = task.task_type
        
        if task_type == "prove_theorem":
            return await self._execute_prove_theorem(task)
        elif task_type == "optimize_theorem":
            return await self._execute_optimize_theorem(task)
        elif task_type == "analyze_theorems":
            return await self._execute_analyze_theorems(task)
        else:
            return {"error": f"Unsupported task type: {task_type}"}
    
    async def _execute_prove_theorem(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a theorem proving task."""
        # Extract parameters
        theorem_id = task.parameters.get("theorem_id")
        if not theorem_id:
            return {"error": "No theorem_id provided"}
        
        # Track attempt
        self.theorems_attempted.append(theorem_id)
        
        # Determine whether to decompose based on agent's genome
        theorem = self.domain_manager.get_theorem(theorem_id)
        if not theorem:
            return {"error": f"Theorem not found: {theorem_id}"}
        
        decompose = theorem.difficulty >= self.decomposition_threshold
        
        # Select a proof strategy based on agent's genome
        strategy_preference = "direct" if self.proof_style_preference < 0.3 else (
            "contradiction" if self.proof_style_preference < 0.6 else "construction"
        )
        
        strategy_id = None
        for sid, strategy in self.prover.strategies.items():
            if strategy_preference in strategy.name.lower():
                strategy_id = sid
                break
        
        # Attempt to prove the theorem
        success, message, proof = await self.prover.prove_theorem(
            theorem_id=theorem_id,
            strategy_id=strategy_id,
            decompose=decompose
        )
        
        # Track success
        if success:
            self.theorems_proven.append(theorem_id)
        
        return {
            "success": success,
            "message": message,
            "proof_id": proof.proof_id if proof else None,
            "strategy_used": strategy_id,
            "decomposition_used": decompose
        }
    
    async def _execute_optimize_theorem(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a theorem optimization task."""
        # Extract parameters
        theorem_id = task.parameters.get("theorem_id")
        proof_id = task.parameters.get("proof_id")
        
        if not theorem_id:
            return {"error": "No theorem_id provided"}
        
        # Track attempt
        self.optimizations_attempted.append(theorem_id)
        
        # Determine whether to optimize statement, proof, or both
        optimize_statement = task.parameters.get("optimize_statement", True)
        optimize_proof = task.parameters.get("optimize_proof", True) and proof_id is not None
        
        results = {}
        
        if optimize_statement:
            # Optimize the theorem statement
            success, message = self.optimizer.optimize_theorem_statement(theorem_id)
            results["statement_optimization"] = {
                "success": success,
                "message": message
            }
        
        if optimize_proof and proof_id:
            # Optimize the proof
            success, message = self.optimizer.optimize_proof(theorem_id, proof_id)
            results["proof_optimization"] = {
                "success": success,
                "message": message
            }
            
            # Track success
            if success:
                self.optimizations_successful.append(theorem_id)
        
        return results
    
    async def _execute_analyze_theorems(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a theorem analysis task."""
        # Filter theorems based on agent's specialization
        theorems = []
        
        if self.concept_type:
            # Filter by concept type
            for theorem_id, theorem in self.domain_manager.theorems.items():
                if theorem.concept_type == self.concept_type:
                    theorems.append(theorem)
        else:
            # Use all theorems
            theorems = list(self.domain_manager.theorems.values())
        
        # Sort theorems based on agent's preferences
        if self.theorem_selection_preference < 0.3:
            # Random selection
            import random
            random.shuffle(theorems)
        elif self.theorem_selection_preference < 0.6:
            # Sort by difficulty
            theorems.sort(key=lambda t: t.difficulty)
        else:
            # Sort by importance
            theorems.sort(key=lambda t: t.importance, reverse=True)
        
        # Analyze theorem properties and identify opportunities
        opportunities = []
        
        for theorem in theorems[:10]:  # Limit analysis to top 10 theorems
            # Check if theorem needs proving
            if theorem.status != TheoremStatus.PROVEN:
                opportunities.append({
                    "theorem_id": theorem.id,
                    "type": "proving",
                    "importance": theorem.importance,
                    "difficulty": theorem.difficulty,
                    "description": f"Theorem '{theorem.name}' needs to be proven."
                })
            
            # Check if theorem could benefit from optimization
            lean_def = theorem.get_formal_definition(FormalizationLanguage.LEAN4)
            if lean_def and len(lean_def.code) > 500:
                opportunities.append({
                    "theorem_id": theorem.id,
                    "type": "optimization",
                    "importance": theorem.importance,
                    "complexity": len(lean_def.code),
                    "description": f"Theorem '{theorem.name}' has a complex formal definition that might benefit from optimization."
                })
            
            # Check if theorem has unverified proofs
            for proof in theorem.proofs:
                if not proof.verified:
                    opportunities.append({
                        "theorem_id": theorem.id,
                        "proof_id": proof.proof_id,
                        "type": "verification",
                        "importance": theorem.importance,
                        "description": f"Proof '{proof.proof_id}' for theorem '{theorem.name}' needs verification."
                    })
        
        return {
            "theorems_analyzed": len(theorems),
            "opportunities": opportunities
        }


class EconomicGeneticAgentSystem(GeneticAgentSystem):
    """Genetic agent system specialized for economic theorem proving."""
    
    def __init__(self, 
                 domain_manager: DomainModelManager,
                 theorem_repository: TheoremRepository,
                 repo_analyzer: EconomicRepositoryAnalyzer,
                 prover: TheoremProver,
                 optimizer: TheoremOptimizer):
        """Initialize the economic genetic agent system.
        
        Args:
            domain_manager: The domain model manager
            theorem_repository: The theorem repository
            repo_analyzer: The economic repository analyzer
            prover: The theorem prover
            optimizer: The theorem optimizer
        """
        super().__init__()
        self.domain_manager = domain_manager
        self.theorem_repository = theorem_repository
        self.repo_analyzer = repo_analyzer
        self.prover = prover
        self.optimizer = optimizer
        
        # Create specialized agents
        self._create_specialized_agents()
    
    def _create_specialized_agents(self) -> None:
        """Create specialized agents for different economic theorem proving tasks."""
        # Create agents for each concept type
        for concept_type in ConceptType:
            # Generic prover for this concept type
            agent = EconomicGeneticAgent(
                agent_id=f"prover_{concept_type.value}",
                name=f"{concept_type.value.capitalize()} Theorem Prover",
                domain_manager=self.domain_manager,
                prover=self.prover,
                optimizer=self.optimizer,
                concept_type=concept_type,
                specialization="proving"
            )
            self.add_agent(agent)
            
            # Optimizer for this concept type
            agent = EconomicGeneticAgent(
                agent_id=f"optimizer_{concept_type.value}",
                name=f"{concept_type.value.capitalize()} Theorem Optimizer",
                domain_manager=self.domain_manager,
                prover=self.prover,
                optimizer=self.optimizer,
                concept_type=concept_type,
                specialization="optimization"
            )
            self.add_agent(agent)
        
        # Create specialized agents for specific tasks
        for specialization, name in [
            ("decomposition", "Theorem Decomposer"),
            ("verification", "Proof Verifier"),
            ("analysis", "Theorem Analyzer")
        ]:
            agent = EconomicGeneticAgent(
                agent_id=f"{specialization}_agent",
                name=name,
                domain_manager=self.domain_manager,
                prover=self.prover,
                optimizer=self.optimizer,
                specialization=specialization
            )
            self.add_agent(agent)
    
    async def run_genetic_evolution(self, generations: int = 5, tasks_per_generation: int = 10) -> List[Dict[str, Any]]:
        """Run genetic evolution of agents through multiple generations.
        
        Args:
            generations: Number of generations to evolve
            tasks_per_generation: Number of tasks per generation
            
        Returns:
            List of evolution statistics by generation
        """
        evolution_stats = []
        
        for generation in range(generations):
            # Generate tasks
            tasks = self._generate_tasks(tasks_per_generation)
            
            # Execute tasks with current agents
            results = await self.execute_tasks(tasks)
            
            # Evaluate agent fitness
            fitness_scores = self._evaluate_agent_fitness(results)
            
            # Track statistics
            stats = {
                "generation": generation + 1,
                "agents": len(self.agents),
                "tasks": len(tasks),
                "successful_tasks": sum(1 for r in results if r.get("success", False)),
                "fitness_scores": fitness_scores
            }
            evolution_stats.append(stats)
            
            # Skip evolution for the last generation
            if generation == generations - 1:
                break
            
            # Evolve agents
            self._evolve_agents(fitness_scores)
        
        return evolution_stats
    
    def _generate_tasks(self, count: int) -> List[AgentTask]:
        """Generate theorem proving and optimization tasks.
        
        Args:
            count: Number of tasks to generate
            
        Returns:
            List of agent tasks
        """
        tasks = []
        theorems = list(self.domain_manager.theorems.values())
        
        if not theorems:
            return tasks
        
        # Prioritize theorems that need work
        unproven_theorems = [t for t in theorems if t.status != TheoremStatus.PROVEN]
        optimizable_theorems = [t for t in theorems if t.proofs and any(not p.verified for p in t.proofs)]
        
        # Determine task distribution
        proving_count = int(count * 0.6)  # 60% proving tasks
        optimization_count = int(count * 0.3)  # 30% optimization tasks
        analysis_count = count - proving_count - optimization_count  # Remaining for analysis
        
        # Generate proving tasks
        for i in range(proving_count):
            if unproven_theorems:
                theorem = unproven_theorems[i % len(unproven_theorems)]
                tasks.append(AgentTask(
                    task_id=f"prove_{theorem.id}_{int(time.time())}_{i}",
                    task_type="prove_theorem",
                    parameters={"theorem_id": theorem.id},
                    priority="high"
                ))
            elif theorems:
                # If no unproven theorems, just use any theorem
                theorem = theorems[i % len(theorems)]
                tasks.append(AgentTask(
                    task_id=f"prove_{theorem.id}_{int(time.time())}_{i}",
                    task_type="prove_theorem",
                    parameters={"theorem_id": theorem.id},
                    priority="medium"
                ))
        
        # Generate optimization tasks
        for i in range(optimization_count):
            if optimizable_theorems:
                theorem = optimizable_theorems[i % len(optimizable_theorems)]
                proof_id = theorem.proofs[0].proof_id if theorem.proofs else None
                
                tasks.append(AgentTask(
                    task_id=f"optimize_{theorem.id}_{int(time.time())}_{i}",
                    task_type="optimize_theorem",
                    parameters={
                        "theorem_id": theorem.id,
                        "proof_id": proof_id,
                        "optimize_statement": True,
                        "optimize_proof": proof_id is not None
                    },
                    priority="medium"
                ))
            elif theorems:
                # If no optimizable theorems, just use any theorem
                theorem = theorems[i % len(theorems)]
                tasks.append(AgentTask(
                    task_id=f"optimize_{theorem.id}_{int(time.time())}_{i}",
                    task_type="optimize_theorem",
                    parameters={"theorem_id": theorem.id, "optimize_statement": True},
                    priority="low"
                ))
        
        # Generate analysis tasks
        for i in range(analysis_count):
            tasks.append(AgentTask(
                task_id=f"analyze_theorems_{int(time.time())}_{i}",
                task_type="analyze_theorems",
                parameters={},
                priority="low"
            ))
        
        return tasks
    
    def _evaluate_agent_fitness(self, task_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Evaluate fitness of each agent based on task results.
        
        Args:
            task_results: Results of executed tasks
            
        Returns:
            Dictionary mapping agent IDs to fitness scores
        """
        fitness_scores = {agent.id: 0.0 for agent in self.agents}
        tasks_by_agent = {agent.id: 0 for agent in self.agents}
        
        for result in task_results:
            agent_id = result.get("agent_id")
            if not agent_id or agent_id not in fitness_scores:
                continue
            
            # Count task
            tasks_by_agent[agent_id] += 1
            
            # Base score on success
            if result.get("success", False):
                fitness_scores[agent_id] += 1.0
            
            # Additional points based on task difficulty
            theorem_id = result.get("parameters", {}).get("theorem_id")
            if theorem_id:
                theorem = self.domain_manager.get_theorem(theorem_id)
                if theorem:
                    difficulty_bonus = theorem.difficulty / 10.0
                    fitness_scores[agent_id] += difficulty_bonus
            
            # Points for optimizations
            if result.get("task_type") == "optimize_theorem":
                if result.get("statement_optimization", {}).get("success", False):
                    fitness_scores[agent_id] += 0.5
                if result.get("proof_optimization", {}).get("success", False):
                    fitness_scores[agent_id] += 0.5
            
            # Points for analysis insights
            if result.get("task_type") == "analyze_theorems":
                opportunities = result.get("opportunities", [])
                fitness_scores[agent_id] += min(len(opportunities) * 0.1, 1.0)
        
        # Normalize by number of tasks
        for agent_id in fitness_scores:
            if tasks_by_agent[agent_id] > 0:
                fitness_scores[agent_id] /= tasks_by_agent[agent_id]
        
        return fitness_scores
    
    def _evolve_agents(self, fitness_scores: Dict[str, float]) -> None:
        """Evolve agents based on fitness scores.
        
        Args:
            fitness_scores: Dictionary mapping agent IDs to fitness scores
        """
        # Convert to list of (agent_id, fitness) pairs and sort by fitness
        fitness_pairs = [(agent_id, score) for agent_id, score in fitness_scores.items()]
        fitness_pairs.sort(key=lambda pair: pair[1], reverse=True)
        
        # Get agents by ID
        agents_by_id = {agent.id: agent for agent in self.agents}
        
        # Keep top performers (elite selection)
        elite_count = max(1, len(self.agents) // 4)
        elite_agents = [agents_by_id[agent_id] for agent_id, _ in fitness_pairs[:elite_count]]
        
        # Create new agents through mutation and crossover
        new_agents = list(elite_agents)  # Start with elite agents
        
        # Create new agents until we reach the original population size
        while len(new_agents) < len(self.agents):
            # Determine whether to do mutation or crossover
            if len(new_agents) == 1 or random.random() < 0.7:  # 70% chance of mutation
                # Select a parent
                parent_idx = random.choices(
                    range(len(new_agents)),
                    weights=[fitness_scores.get(agent.id, 0.1) for agent in new_agents],
                    k=1
                )[0]
                parent = new_agents[parent_idx]
                
                # Create mutated agent
                child = self._mutate_agent(parent)
                new_agents.append(child)
            else:
                # Select two parents
                parent_indices = random.choices(
                    range(len(new_agents)),
                    weights=[fitness_scores.get(agent.id, 0.1) for agent in new_agents],
                    k=2
                )
                parent1 = new_agents[parent_indices[0]]
                parent2 = new_agents[parent_indices[1]]
                
                # Create child through crossover
                child = self._crossover_agents(parent1, parent2)
                new_agents.append(child)
        
        # Replace the agent population
        self.agents = new_agents
    
    def _mutate_agent(self, agent: EconomicGeneticAgent) -> EconomicGeneticAgent:
        """Create a mutated version of an agent.
        
        Args:
            agent: The agent to mutate
            
        Returns:
            A new mutated agent
        """
        # Create a new agent with the same basic properties
        new_agent = EconomicGeneticAgent(
            agent_id=f"{agent.id}_mutated_{int(time.time())}",
            name=f"Mutated {agent.name}",
            domain_manager=self.domain_manager,
            prover=self.prover,
            optimizer=self.optimizer,
            concept_type=agent.concept_type,
            specialization=agent.specialization
        )
        
        # Mutate genome characteristics
        mutation_scale = 0.2  # Maximum change is ±20%
        
        new_agent.theorem_selection_preference = max(0.0, min(1.0, 
            agent.theorem_selection_preference + (random.random() - 0.5) * mutation_scale * 2
        ))
        
        new_agent.risk_tolerance = max(0.0, min(1.0,
            agent.risk_tolerance + (random.random() - 0.5) * mutation_scale * 2
        ))
        
        new_agent.optimization_frequency = max(0.0, min(1.0,
            agent.optimization_frequency + (random.random() - 0.5) * mutation_scale * 2
        ))
        
        new_agent.decomposition_threshold = max(1, min(10,
            agent.decomposition_threshold + int((random.random() - 0.5) * mutation_scale * 10)
        ))
        
        new_agent.proof_style_preference = max(0.0, min(1.0,
            agent.proof_style_preference + (random.random() - 0.5) * mutation_scale * 2
        ))
        
        return new_agent
    
    def _crossover_agents(self, agent1: EconomicGeneticAgent, agent2: EconomicGeneticAgent) -> EconomicGeneticAgent:
        """Create a new agent by crossing over two parent agents.
        
        Args:
            agent1: First parent agent
            agent2: Second parent agent
            
        Returns:
            A new agent created through crossover
        """
        # Create a new agent with the same basic properties
        new_agent = EconomicGeneticAgent(
            agent_id=f"crossover_{int(time.time())}",
            name=f"Crossover of {agent1.name} and {agent2.name}",
            domain_manager=self.domain_manager,
            prover=self.prover,
            optimizer=self.optimizer,
            concept_type=agent1.concept_type,  # Inherit from first parent
            specialization=agent1.specialization  # Inherit from first parent
        )
        
        # Crossover genome characteristics
        crossover_point = random.randint(0, 4)  # 5 genome characteristics
        
        # First characteristics come from parent 1
        if crossover_point >= 0:
            new_agent.theorem_selection_preference = agent1.theorem_selection_preference
        else:
            new_agent.theorem_selection_preference = agent2.theorem_selection_preference
        
        if crossover_point >= 1:
            new_agent.risk_tolerance = agent1.risk_tolerance
        else:
            new_agent.risk_tolerance = agent2.risk_tolerance
        
        if crossover_point >= 2:
            new_agent.optimization_frequency = agent1.optimization_frequency
        else:
            new_agent.optimization_frequency = agent2.optimization_frequency
        
        if crossover_point >= 3:
            new_agent.decomposition_threshold = agent1.decomposition_threshold
        else:
            new_agent.decomposition_threshold = agent2.decomposition_threshold
        
        if crossover_point >= 4:
            new_agent.proof_style_preference = agent1.proof_style_preference
        else:
            new_agent.proof_style_preference = agent2.proof_style_preference
        
        return new_agent


if __name__ == "__main__":
    # Basic usage example
    from economic_domain_model import DomainModelManager
    from economic_formal_translator import LeanTranslator
    from economic_theorem_prover import (
        TheoremProver, SubgoalDecomposer, ProofVerifier, DeepSeekProverInterface
    )
    from repository_analyzer import RepositoryAnalyzer
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create domain manager
    domain_manager = DomainModelManager("./domain_model")
    
    # Set up repository config
    repo_config = TheoremRepositoryConfig(
        root_path="./theorem_repository",
        lean_export_path="./lean_export"
    )
    
    # Create theorem repository
    theorem_repo = TheoremRepository(domain_manager, repo_config)
    
    # Create translator and prover components
    translator = LeanTranslator(domain_manager)
    decomposer = SubgoalDecomposer(domain_manager)
    verifier = ProofVerifier(domain_manager, translator)
    deepseek = DeepSeekProverInterface()
    
    # Create theorem prover
    prover = TheoremProver(
        domain_manager=domain_manager,
        decomposer=decomposer,
        translator=translator,
        verifier=verifier,
        deepseek=deepseek
    )
    
    # Create repository analyzer
    repo_analyzer = RepositoryAnalyzer()
    
    # Create economic repository analyzer
    econ_repo_analyzer = EconomicRepositoryAnalyzer(
        domain_manager=domain_manager,
        theorem_repository=theorem_repo,
        repo_analyzer=repo_analyzer
    )
    
    # Create theorem optimizer
    optimizer = TheoremOptimizer(
        domain_manager=domain_manager,
        translator=translator,
        prover=prover
    )
    
    # Create economic genetic agent system
    genetic_system = EconomicGeneticAgentSystem(
        domain_manager=domain_manager,
        theorem_repository=theorem_repo,
        repo_analyzer=econ_repo_analyzer,
        prover=prover,
        optimizer=optimizer
    )
    
    # Print available agents
    print(f"Created {len(genetic_system.agents)} specialized genetic agents:")
    for agent in genetic_system.agents:
        print(f"- {agent.name} ({agent.id})")
        if hasattr(agent, "concept_type") and agent.concept_type:
            print(f"  Concept type: {agent.concept_type.value}")
        if hasattr(agent, "specialization") and agent.specialization:
            print(f"  Specialization: {agent.specialization}")
    
    # Run genetic evolution (in an async context)
    import asyncio
    
    async def test_genetic_evolution():
        stats = await genetic_system.run_genetic_evolution(generations=2, tasks_per_generation=3)
        print("\nGenetic evolution results:")
        for gen_stats in stats:
            print(f"Generation {gen_stats['generation']}:")
            print(f"  Agents: {gen_stats['agents']}")
            print(f"  Tasks: {gen_stats['tasks']}")
            print(f"  Successful tasks: {gen_stats['successful_tasks']}")
            print(f"  Average fitness: {sum(gen_stats['fitness_scores'].values()) / len(gen_stats['fitness_scores']):.4f}")
    
    # Run the test
    asyncio.run(test_genetic_evolution())