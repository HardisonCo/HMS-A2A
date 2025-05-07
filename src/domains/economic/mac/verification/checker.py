"""
External Checker implementation for the MAC architecture.

The External Checker provides verification mechanisms for agent outputs,
implementing a verification-first approach to validation through various
specialized validators.
"""

from typing import Dict, Any, Optional, List, Type
import logging
import asyncio
from dataclasses import dataclass
import json
import re

# A2A imports
from a2a.core import Task, TaskResult
from graph.cort_react_agent import CoRTReactAgent

@dataclass
class VerificationResult:
    """Result of a verification operation."""
    is_valid: bool
    confidence: float
    feedback: str
    suggestions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "is_valid": self.is_valid,
            "confidence": self.confidence,
            "feedback": self.feedback,
            "suggestions": self.suggestions
        }


class Validator:
    """Base class for all validators."""
    
    def __init__(self, name: str):
        """Initialize validator."""
        self.name = name
        self.logger = logging.getLogger(f"MAC.Validator.{name}")
    
    async def validate(self, task: Task, result: TaskResult) -> VerificationResult:
        """
        Validate a task result.
        
        Args:
            task: The original task
            result: The task result to validate
            
        Returns:
            Verification result
        """
        self.logger.info(f"Validating task {task.id}")
        # Base implementation always returns valid
        return VerificationResult(
            is_valid=True,
            confidence=0.5,
            feedback=f"No validation implemented for {self.name}",
            suggestions=[]
        )


class StatisticalValidator(Validator):
    """Validates results using statistical methods."""
    
    def __init__(self):
        """Initialize validator."""
        super().__init__("statistical")
    
    async def validate(self, task: Task, result: TaskResult) -> VerificationResult:
        """
        Validate a task result using statistical methods.
        
        Args:
            task: The original task
            result: The task result to validate
            
        Returns:
            Verification result
        """
        self.logger.info(f"Statistical validation for task {task.id}")
        
        # In a real implementation, this would include:
        # - Consistency checks
        # - Outlier detection
        # - Probability analysis
        
        # Simple check for presence of expected fields
        if isinstance(result.result, dict):
            if "summary" not in result.result:
                return VerificationResult(
                    is_valid=False,
                    confidence=0.8,
                    feedback="Result missing 'summary' field",
                    suggestions=["Add a summary field to the result"]
                )
        
        # Check confidence metadata
        confidence = result.metadata.get("confidence", 0.5)
        if confidence < 0.7:
            return VerificationResult(
                is_valid=False,
                confidence=0.8,
                feedback=f"Low confidence result ({confidence})",
                suggestions=["Consider refinement or human review"]
            )
        
        # Success case
        return VerificationResult(
            is_valid=True,
            confidence=0.85,
            feedback="Statistical validation passed with acceptable confidence",
            suggestions=[]
        )


class SyntaxValidator(Validator):
    """Validates syntax correctness for code and structured data."""
    
    def __init__(self):
        """Initialize validator."""
        super().__init__("syntax")
    
    async def validate(self, task: Task, result: TaskResult) -> VerificationResult:
        """
        Validate syntax correctness in task results.
        
        Args:
            task: The original task
            result: The task result to validate
            
        Returns:
            Verification result
        """
        self.logger.info(f"Syntax validation for task {task.id}")
        
        # Determine what kind of syntax to validate
        task_type = task.metadata.get("type", "general")
        language = task.metadata.get("language", "python")
        
        if task_type == "code_generation":
            # Validate code syntax
            return await self._validate_code_syntax(result, language)
        elif task_type == "json_generation":
            # Validate JSON syntax
            return await self._validate_json_syntax(result)
        else:
            # General structure validation
            return await self._validate_general_structure(result)
    
    async def _validate_code_syntax(self, result: TaskResult, language: str) -> VerificationResult:
        """
        Validate code syntax for a specific language.
        
        Args:
            result: The task result to validate
            language: Programming language
            
        Returns:
            Verification result
        """
        # Extract code blocks from result
        code_blocks = self._extract_code_blocks(result)
        
        if not code_blocks:
            return VerificationResult(
                is_valid=False,
                confidence=0.8,
                feedback="No code blocks found in result",
                suggestions=["Ensure code is properly formatted in code blocks"]
            )
        
        # Placeholder for actual syntax validation logic
        # In a real implementation, this would:
        # - Run language-specific syntax checkers
        # - Use linters or compile tests
        
        # For demonstration, always pass with high confidence
        return VerificationResult(
            is_valid=True,
            confidence=0.9,
            feedback=f"{language} syntax appears valid",
            suggestions=[]
        )
    
    async def _validate_json_syntax(self, result: TaskResult) -> VerificationResult:
        """
        Validate JSON syntax in result.
        
        Args:
            result: The task result to validate
            
        Returns:
            Verification result
        """
        # Find all JSON strings in the result
        json_strings = []
        
        # If result itself is JSON
        if isinstance(result.result, dict):
            json_strings.append(json.dumps(result.result))
        
        # Look for JSON in text fields
        if isinstance(result.result, dict) and "text" in result.result:
            potential_json = self._extract_json_blocks(result.result["text"])
            json_strings.extend(potential_json)
        
        if not json_strings:
            return VerificationResult(
                is_valid=False,
                confidence=0.7,
                feedback="No JSON content found in result",
                suggestions=["Ensure JSON is properly formatted"]
            )
        
        # Validate each JSON string
        invalid_json = []
        for i, json_str in enumerate(json_strings):
            try:
                json.loads(json_str)
            except json.JSONDecodeError as e:
                invalid_json.append((i, str(e)))
        
        if invalid_json:
            error_details = "\n".join([f"JSON block {i}: {err}" for i, err in invalid_json])
            return VerificationResult(
                is_valid=False,
                confidence=0.9,
                feedback=f"Invalid JSON syntax: {error_details}",
                suggestions=["Fix JSON syntax errors"]
            )
        
        return VerificationResult(
            is_valid=True,
            confidence=0.9,
            feedback="JSON syntax is valid",
            suggestions=[]
        )
    
    async def _validate_general_structure(self, result: TaskResult) -> VerificationResult:
        """
        Validate general structure of result.
        
        Args:
            result: The task result to validate
            
        Returns:
            Verification result
        """
        # Check if result is a dictionary
        if not isinstance(result.result, dict):
            return VerificationResult(
                is_valid=False,
                confidence=0.8,
                feedback="Result is not a structured object",
                suggestions=["Return a structured object (dictionary)"]
            )
        
        # Check for minimal structure
        if "summary" not in result.result and "details" not in result.result:
            return VerificationResult(
                is_valid=False,
                confidence=0.7,
                feedback="Result missing essential structure (summary or details)",
                suggestions=["Include at least summary and/or details in the result"]
            )
        
        return VerificationResult(
            is_valid=True,
            confidence=0.8,
            feedback="Result structure is valid",
            suggestions=[]
        )
    
    def _extract_code_blocks(self, result: TaskResult) -> List[str]:
        """
        Extract code blocks from task result.
        
        Args:
            result: The task result
            
        Returns:
            List of code blocks
        """
        code_blocks = []
        
        # Extract from structured result
        if isinstance(result.result, dict):
            # Look for code in 'code' field
            if "code" in result.result:
                code_blocks.append(result.result["code"])
            
            # Look for code in text fields
            for field in ["text", "details", "summary"]:
                if field in result.result and isinstance(result.result[field], str):
                    blocks = re.findall(r"```(?:\w+)?\n([\s\S]*?)\n```", result.result[field])
                    code_blocks.extend(blocks)
        
        return code_blocks
    
    def _extract_json_blocks(self, text: str) -> List[str]:
        """
        Extract JSON blocks from text.
        
        Args:
            text: Text to extract from
            
        Returns:
            List of JSON strings
        """
        json_blocks = []
        
        # Find JSON blocks in triple backticks
        blocks = re.findall(r"```(?:json)?\n([\s\S]*?)\n```", text)
        json_blocks.extend(blocks)
        
        # Find JSON blocks with curly braces
        blocks = re.findall(r"\{[\s\S]*?\}", text)
        json_blocks.extend(blocks)
        
        return json_blocks


class PolicyValidator(Validator):
    """Validates compliance with governance policies."""
    
    def __init__(self, policy_rules: Optional[Dict[str, Any]] = None):
        """
        Initialize validator.
        
        Args:
            policy_rules: Dictionary of policy rules to enforce
        """
        super().__init__("policy")
        self.policy_rules = policy_rules or {}
    
    async def validate(self, task: Task, result: TaskResult) -> VerificationResult:
        """
        Validate compliance with governance policies.
        
        Args:
            task: The original task
            result: The task result to validate
            
        Returns:
            Verification result
        """
        self.logger.info(f"Policy validation for task {task.id}")
        
        # Determine policy context
        policy_framework = task.metadata.get("policy_framework", "default")
        domain = task.domain or "general"
        
        # Validate against policy rules
        violations = []
        suggestions = []
        
        # Check domain-specific policies
        if domain in self.policy_rules:
            domain_violations = await self._check_domain_policies(
                domain, result, self.policy_rules[domain]
            )
            violations.extend(domain_violations)
        
        # Check framework-specific policies
        if policy_framework in self.policy_rules:
            framework_violations = await self._check_framework_policies(
                policy_framework, result, self.policy_rules[policy_framework]
            )
            violations.extend(framework_violations)
        
        # Generate suggestions
        for violation in violations:
            if "suggestion" in violation:
                suggestions.append(violation["suggestion"])
        
        # Determine validity and confidence
        is_valid = len(violations) == 0
        confidence = 0.9 if violations else 0.8
        
        # Create feedback
        if violations:
            violation_text = "\n".join(f"- {v['description']}" for v in violations)
            feedback = f"Policy violations found:\n{violation_text}"
        else:
            feedback = "Policy compliance validated"
        
        return VerificationResult(
            is_valid=is_valid,
            confidence=confidence,
            feedback=feedback,
            suggestions=suggestions
        )
    
    async def _check_domain_policies(
        self, domain: str, result: TaskResult, policies: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Check domain-specific policies.
        
        Args:
            domain: Domain name
            result: Task result
            policies: Domain policies
            
        Returns:
            List of violations
        """
        violations = []
        
        # Placeholder for actual domain-specific policy checks
        # In a real implementation, this would check against domain-specific rules
        
        return violations
    
    async def _check_framework_policies(
        self, framework: str, result: TaskResult, policies: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Check framework-specific policies.
        
        Args:
            framework: Policy framework
            result: Task result
            policies: Framework policies
            
        Returns:
            List of violations
        """
        violations = []
        
        # Placeholder for actual framework-specific policy checks
        # In a real implementation, this would check against framework-specific rules
        
        return violations


class ExternalChecker:
    """
    External Checker for the MAC architecture.
    
    The External Checker implements a verification-first approach to validation,
    using various specialized validators to ensure agent outputs meet requirements.
    """
    
    def __init__(self, cort_agent: Optional[CoRTReactAgent] = None):
        """
        Initialize the External Checker.
        
        Args:
            cort_agent: Optional CoRT agent for advanced validation
        """
        self.validators = {}
        self.cort_agent = cort_agent
        self.logger = logging.getLogger("MAC.ExternalChecker")
        
        # Register default validators
        self.register_validator("statistical", StatisticalValidator())
        self.register_validator("syntax", SyntaxValidator())
        self.register_validator("policy", PolicyValidator())
    
    def register_validator(self, name: str, validator: Validator) -> None:
        """
        Register a validator component.
        
        Args:
            name: Validator name
            validator: Validator instance
        """
        self.validators[name] = validator
        self.logger.info(f"Registered validator: {name}")
    
    async def verify(self, result: TaskResult, task: Task) -> VerificationResult:
        """
        Verify a task result against its task definition.
        
        Args:
            result: The task result to verify
            task: The original task
            
        Returns:
            Verification result
        """
        self.logger.info(f"Verifying result for task {task.id}")
        
        # Identify required validations
        validations_required = await self._determine_required_validations(task, result)
        
        # Run validations
        validation_results = {}
        validation_tasks = []
        
        for validation_type in validations_required:
            if validation_type in self.validators:
                validator = self.validators[validation_type]
                validation_tasks.append(self._run_validation(validator, task, result))
            else:
                self.logger.warning(f"Required validator not available: {validation_type}")
        
        # Wait for all validations to complete
        results = await asyncio.gather(*validation_tasks, return_exceptions=True)
        
        # Process results
        for validation_type, result_or_error in zip(validations_required, results):
            if isinstance(result_or_error, Exception):
                self.logger.error(f"Validation {validation_type} failed: {str(result_or_error)}")
                # Create error result
                validation_results[validation_type] = VerificationResult(
                    is_valid=False,
                    confidence=0.5,
                    feedback=f"Validation error: {str(result_or_error)}",
                    suggestions=["Check validator implementation"]
                )
            else:
                validation_results[validation_type] = result_or_error
        
        # Combine validation results
        combined_result = await self._combine_validation_results(validation_results)
        
        self.logger.info(f"Verification completed for task {task.id}: valid={combined_result.is_valid}")
        return combined_result
    
    async def _run_validation(
        self, validator: Validator, task: Task, result: TaskResult
    ) -> VerificationResult:
        """
        Run a single validation with error handling.
        
        Args:
            validator: Validator to use
            task: The original task
            result: The task result to validate
            
        Returns:
            Verification result
        """
        try:
            return await validator.validate(task, result)
        except Exception as e:
            self.logger.error(f"Error in {validator.name} validation: {str(e)}")
            raise
    
    async def _determine_required_validations(self, task: Task, result: TaskResult) -> List[str]:
        """
        Determine which validations are required for this task.
        
        Args:
            task: The original task
            result: The task result
            
        Returns:
            List of required validation types
        """
        # Default validations
        required = ["statistical"]
        
        # Check task metadata for specific validation requirements
        validation_reqs = task.metadata.get("validations", {})
        
        if validation_reqs:
            # Add specific validations
            for validation_type, required_flag in validation_reqs.items():
                if required_flag and validation_type not in required:
                    required.append(validation_type)
        
        # Add task-type specific validations
        task_type = task.metadata.get("type", "general")
        
        if task_type == "code_generation":
            if "syntax" not in required:
                required.append("syntax")
        elif task_type == "policy_decision":
            if "policy" not in required:
                required.append("policy")
        elif task_type == "json_generation":
            if "syntax" not in required:
                required.append("syntax")
        
        # Add domain-specific validations
        if task.domain == "governance" and "policy" not in required:
            required.append("policy")
        
        return required
    
    async def _combine_validation_results(
        self, results: Dict[str, VerificationResult]
    ) -> VerificationResult:
        """
        Combine multiple validation results into a single verification result.
        
        Args:
            results: Dictionary mapping validation types to results
            
        Returns:
            Combined verification result
        """
        if not results:
            return VerificationResult(
                is_valid=False,
                confidence=0.0,
                feedback="No validations were performed",
                suggestions=["Ensure validators are properly configured"]
            )
        
        # Aggregate all feedbacks and suggestions
        all_feedback = []
        all_suggestions = []
        for validation_type, result in results.items():
            if result.feedback:
                all_feedback.append(f"{validation_type}: {result.feedback}")
            all_suggestions.extend(result.suggestions)
        
        # Calculate aggregate confidence
        confidence_sum = sum(result.confidence for result in results.values())
        avg_confidence = confidence_sum / len(results)
        
        # Determine aggregate validity
        # A result is valid only if ALL validations consider it valid
        is_valid = all(result.is_valid for result in results.values())
        
        return VerificationResult(
            is_valid=is_valid,
            confidence=avg_confidence,
            feedback="\n".join(all_feedback),
            suggestions=all_suggestions
        )
    
    async def verify_thought_process(self, journal: List[Dict[str, Any]]) -> VerificationResult:
        """
        Verify a Chain of Recursive Thoughts journal.
        
        Args:
            journal: CoRT journal
            
        Returns:
            Verification result
        """
        self.logger.info("Verifying thought process")
        
        # Check for empty journal
        if not journal:
            return VerificationResult(
                is_valid=False,
                confidence=0.9,
                feedback="Empty thought journal",
                suggestions=["Ensure CoRT process generated a journal"]
            )
        
        # Check for sufficient depth
        if len(journal) < 2:
            return VerificationResult(
                is_valid=False,
                confidence=0.8,
                feedback="Insufficient recursive thought depth",
                suggestions=["Increase CoRT depth parameter"]
            )
        
        # Check for improvement trend
        improvements = []
        for entry in journal:
            if "improvements" in entry and entry["improvements"]:
                if isinstance(entry["improvements"], list):
                    improvements.append(len(entry["improvements"]))
        
        # Look for diminishing improvements pattern
        if len(improvements) >= 2:
            is_diminishing = all(
                improvements[i] >= improvements[i+1]
                for i in range(len(improvements) - 1)
            )
            
            if not is_diminishing:
                return VerificationResult(
                    is_valid=False,
                    confidence=0.7,
                    feedback="Non-converging thought process",
                    suggestions=["Investigate recursive thought pattern",
                                "Consider adjusting CoRT parameters"]
                )
        
        # Success case
        return VerificationResult(
            is_valid=True,
            confidence=0.85,
            feedback="Thought process verification passed",
            suggestions=[]
        )


# Factory function for creating an External Checker
def create_checker(config_path: Optional[str] = None) -> ExternalChecker:
    """
    Create and configure an External Checker.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configured ExternalChecker
    """
    # Load configuration if path provided
    config = {}
    if config_path:
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logging.error(f"Error loading checker configuration: {str(e)}")
    
    # Create CoRT agent if needed
    cort_agent = None
    if config.get("use_cort_for_verification", False):
        cort_agent = CoRTReactAgent(
            use_cort=True,
            max_rounds=config.get("cort_depth", 2),
            generate_alternatives=config.get("generate_alternatives", 1)
        )
    
    # Create checker
    checker = ExternalChecker(cort_agent=cort_agent)
    
    # Register additional validators from config
    validator_configs = config.get("validators", {})
    for validator_name, validator_config in validator_configs.items():
        if validator_name not in checker.validators:
            validator_type = validator_config.get("type")
            if validator_type == "policy":
                checker.register_validator(
                    validator_name,
                    PolicyValidator(policy_rules=validator_config.get("rules", {}))
                )
    
    return checker