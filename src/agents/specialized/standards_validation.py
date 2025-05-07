"""
Standards Validation Module

This module provides enhanced validation for standards-compliant agents
across various domains, ensuring compliance with relevant regulations.

It loads standards from the std.json file to provide comprehensive standards coverage
and implements a flexible, extensible validation framework for compliance checking.
"""

import os
import json
import logging
import importlib.resources
from typing import List, Dict, Any, Optional, Set, Union, Literal, Type, Protocol, Callable
from pydantic import BaseModel, Field, root_validator, validator

# Set up logging
logger = logging.getLogger(__name__)


class Standard(BaseModel):
    """Definition of a compliance standard or regulation."""
    
    id: str
    name: str
    description: str
    organization: Optional[str] = None
    version: Optional[str] = None
    requirements: List[str] = []
    domain: Optional[str] = None


class ValidationIssue(BaseModel):
    """Detailed description of a standards compliance issue."""
    
    standard_id: str
    severity: Literal["critical", "high", "medium", "low"]
    description: str
    recommendation: str
    location: Optional[str] = None
    confidence: float = 1.0
    rule_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """Validate that confidence is between 0 and 1."""
        if v < 0 or v > 1:
            raise ValueError('Confidence must be between 0 and 1')
        return v


class ValidationResult(BaseModel):
    """Result of a standards compliance validation."""
    
    valid: bool
    issues: List[ValidationIssue] = []
    standards_checked: List[str] = []
    confidence: float = 1.0
    
    def get_critical_issues(self) -> List[ValidationIssue]:
        """Get all critical validation issues."""
        return [issue for issue in self.issues if issue.severity == "critical"]
    
    def get_high_severity_issues(self) -> List[ValidationIssue]:
        """Get all high severity validation issues."""
        return [issue for issue in self.issues if issue.severity == "high"]


class IStandardsRegistry(Protocol):
    """Interface defining the contract for standards registries."""
    
    def register_standard(self, standard: Standard) -> None:
        """Register a compliance standard."""
        ...
    
    def get_standard(self, standard_id: str) -> Optional[Standard]:
        """Get a standard by ID."""
        ...
    
    def get_standards_for_domain(self, domain: str) -> List[Standard]:
        """Get all standards for a specific domain."""
        ...
    
    def get_all_standards(self) -> Dict[str, Standard]:
        """Get all registered standards."""
        ...


class StandardsRegistry(IStandardsRegistry):
    """Registry for compliance standards across domains."""
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super(StandardsRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry."""
        if getattr(self, '_initialized', False):
            return
            
        self.standards: Dict[str, Standard] = {}
        self.domain_standards: Dict[str, List[str]] = {}
        self.validation_rules: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.domain_metadata: Dict[str, Dict[str, Any]] = {}
        self.cross_domain_standards: List[str] = []
        self.cache: Dict[str, Any] = {}
        
        # Setup default caching
        self.cache_enabled = True
        self.cache_ttl = 3600  # 1 hour in seconds
        self.cache_timestamps: Dict[str, float] = {}
        
        self._initialized = True
        
        # Load standards from HMS-SME format if available
        self._load_standards_from_hms_sme()
    
    def register_standard(self, standard: Standard) -> None:
        """Register a compliance standard.
        
        Args:
            standard: The standard to register
        """
        self.standards[standard.id] = standard
        
        # Clear caches related to this standard
        self._clear_cache_for_standard(standard.id)
        
        # Register domain association
        if standard.domain:
            if standard.domain not in self.domain_standards:
                self.domain_standards[standard.domain] = []
            
            if standard.id not in self.domain_standards[standard.domain]:
                self.domain_standards[standard.domain].append(standard.id)
    
    def register_validation_rules(self, standard_id: str, rules: Dict[str, Dict[str, Any]]) -> None:
        """Register validation rules for a standard.
        
        Args:
            standard_id: ID of the standard
            rules: Dictionary of validation rules
        """
        self.validation_rules[standard_id] = rules
        self._clear_cache_for_standard(standard_id)
    
    def register_domain_metadata(self, domain: str, metadata: Dict[str, Any]) -> None:
        """Register metadata for a domain.
        
        Args:
            domain: Name of the domain
            metadata: Dictionary of domain metadata
        """
        self.domain_metadata[domain] = metadata
        
        # Clear domain-related caches
        cache_keys_to_remove = [k for k in self.cache if domain in k]
        for key in cache_keys_to_remove:
            del self.cache[key]
            if key in self.cache_timestamps:
                del self.cache_timestamps[key]
    
    def get_standard(self, standard_id: str) -> Optional[Standard]:
        """Get a standard by ID.
        
        Args:
            standard_id: The ID of the standard
            
        Returns:
            The standard, or None if not found
        """
        # Try cache first
        cache_key = f"standard:{standard_id}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Get from registry
        standard = self.standards.get(standard_id)
        
        # Cache result
        if standard:
            self._add_to_cache(cache_key, standard)
        
        return standard
    
    def get_standards_for_domain(self, domain: str) -> List[Standard]:
        """Get all standards for a specific domain.
        
        Args:
            domain: The industry domain
            
        Returns:
            List of standards for the domain
        """
        # Try cache first
        cache_key = f"domain_standards:{domain}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Get from registry
        standard_ids = self.domain_standards.get(domain, [])
        standards = [self.standards[standard_id] for standard_id in standard_ids 
                    if standard_id in self.standards]
        
        # Cache result
        self._add_to_cache(cache_key, standards)
        
        return standards
    
    def get_validation_rules(self, standard_id: str) -> Dict[str, Dict[str, Any]]:
        """Get validation rules for a standard.
        
        Args:
            standard_id: ID of the standard
            
        Returns:
            Dictionary of validation rules
        """
        # Try cache first
        cache_key = f"rules:{standard_id}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Get rules or empty dict if none
        rules = self.validation_rules.get(standard_id, {})
        
        # Cache result
        self._add_to_cache(cache_key, rules)
        
        return rules
    
    def get_domain_metadata(self, domain: str) -> Dict[str, Any]:
        """Get metadata for a domain.
        
        Args:
            domain: Name of the domain
            
        Returns:
            Dictionary of domain metadata
        """
        return self.domain_metadata.get(domain, {})
    
    def get_all_standards(self) -> Dict[str, Standard]:
        """Get all registered standards.
        
        Returns:
            Dictionary of all registered standards
        """
        return self.standards.copy()
    
    def get_cross_domain_standards(self) -> List[Standard]:
        """Get standards that apply across multiple domains.
        
        Returns:
            List of cross-domain standards
        """
        # Try cache first
        cache_key = "cross_domain_standards"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Identify cross-domain standards if not already populated
        if not self.cross_domain_standards:
            # Count domains per standard
            standard_domain_count = {}
            for domain, standard_ids in self.domain_standards.items():
                for std_id in standard_ids:
                    standard_domain_count[std_id] = standard_domain_count.get(std_id, 0) + 1
            
            # Standards that appear in more than one domain
            self.cross_domain_standards = [
                std_id for std_id, count in standard_domain_count.items() 
                if count > 1 or std_id in ["DATA_PRIVACY", "RESPONSIBLE_AI"]
            ]
        
        # Get full standard objects
        cross_domain_standards = [
            self.standards[std_id] for std_id in self.cross_domain_standards
            if std_id in self.standards
        ]
        
        # Cache result
        self._add_to_cache(cache_key, cross_domain_standards)
        
        return cross_domain_standards
    
    def get_all_domains(self) -> List[str]:
        """Get all domains with registered standards.
        
        Returns:
            List of domain names
        """
        return list(self.domain_standards.keys())
    
    def get_standards_by_requirement(self, requirement_text: str) -> List[Standard]:
        """Find standards that contain a specific requirement.
        
        Args:
            requirement_text: Text to search for in requirements
            
        Returns:
            List of standards containing the requirement
        """
        requirement_text = requirement_text.lower()
        matching_standards = []
        
        for std_id, standard in self.standards.items():
            for req in standard.requirements:
                if requirement_text in req.lower():
                    matching_standards.append(standard)
                    break
        
        return matching_standards
    
    def _load_standards_from_hms_sme(self) -> None:
        """Load standards from HMS-SME format."""
        try:
            # Get path to std.json
            data_dir = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                "data"
            ))
            std_file = os.path.join(data_dir, "std.json")
            
            # Check if file exists and load it
            if os.path.exists(std_file):
                with open(std_file, 'r') as f:
                    data = json.load(f)
                
                # Process standards
                if "standards" in data:
                    for std_id, std_info in data["standards"].items():
                        # Create requirements from validations
                        requirements = []
                        if "validations" in std_info:
                            for rule_id, rule in std_info["validations"].items():
                                requirements.append(rule["description"])
                        
                        # Get domain
                        domain = None
                        if "domains" in std_info and std_info["domains"]:
                            domain = std_info["domains"][0]  # Primary domain
                        
                        # Create and register the standard
                        standard = Standard(
                            id=std_id,
                            name=std_info.get("name", std_id),
                            description=std_info.get("description", ""),
                            domain=domain,
                            requirements=requirements
                        )
                        self.register_standard(standard)
                        
                        # Register validation rules
                        if "validations" in std_info:
                            self.register_validation_rules(std_id, std_info["validations"])
                
                # Process domain metadata
                if "domains" in data:
                    for domain_name, domain_info in data["domains"].items():
                        self.register_domain_metadata(domain_name, domain_info)
                
                logger.info(f"Loaded {len(data.get('standards', {}))} standards from HMS-SME format")
            else:
                logger.warning(f"HMS-SME standards file not found at {std_file}")
        except Exception as e:
            logger.error(f"Error loading HMS-SME standards: {str(e)}")
            # Continue without HMS-SME standards - fallback standards will be registered
    
    def _add_to_cache(self, key: str, value: Any) -> None:
        """Add a value to the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        if not self.cache_enabled:
            return
            
        self.cache[key] = value
        self.cache_timestamps[key] = time.time()
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value, or None if not found or expired
        """
        if not self.cache_enabled or key not in self.cache:
            return None
            
        # Check if expired
        timestamp = self.cache_timestamps.get(key, 0)
        if time.time() - timestamp > self.cache_ttl:
            # Expired
            del self.cache[key]
            del self.cache_timestamps[key]
            return None
            
        return self.cache[key]
    
    def _clear_cache_for_standard(self, standard_id: str) -> None:
        """Clear all cache entries related to a standard.
        
        Args:
            standard_id: ID of the standard
        """
        if not self.cache_enabled:
            return
            
        # Remove direct standard cache
        direct_keys = [f"standard:{standard_id}", f"rules:{standard_id}"]
        for key in direct_keys:
            if key in self.cache:
                del self.cache[key]
                if key in self.cache_timestamps:
                    del self.cache_timestamps[key]
        
        # Clear related caches that might contain this standard
        related_keys = ["cross_domain_standards"]
        for domain in self.domain_standards:
            if standard_id in self.domain_standards[domain]:
                related_keys.append(f"domain_standards:{domain}")
        
        for key in related_keys:
            if key in self.cache:
                del self.cache[key]
                if key in self.cache_timestamps:
                    del self.cache_timestamps[key]
    
    def configure_cache(self, enabled: bool = True, ttl: int = 3600) -> None:
        """Configure the cache settings.
        
        Args:
            enabled: Whether to enable caching
            ttl: Time-to-live for cache entries in seconds
        """
        self.cache_enabled = enabled
        self.cache_ttl = ttl
        
        # Clear cache if disabling
        if not enabled:
            self.cache.clear()
            self.cache_timestamps.clear()
            
    def get_standard_validation_severity(self, standard_id: str, rule_id: str) -> str:
        """Get the severity level for a standard's validation rule.
        
        Args:
            standard_id: ID of the standard
            rule_id: ID of the validation rule
            
        Returns:
            Severity level or "medium" if not found
        """
        rules = self.get_validation_rules(standard_id)
        if rule_id in rules:
            return rules[rule_id].get("severity", "medium")
        return "medium"
    
    def get_severity_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Get metadata about severity levels.
        
        Returns:
            Dictionary of severity metadata
        """
        # Try to load from std.json first
        data_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "data"
        ))
        std_file = os.path.join(data_dir, "std.json")
        
        if os.path.exists(std_file):
            try:
                with open(std_file, 'r') as f:
                    data = json.load(f)
                if "validation_severity" in data:
                    return data["validation_severity"]
            except Exception as e:
                logger.error(f"Error loading severity metadata: {str(e)}")
        
        # Fallback to default severity levels
        return {
            "critical": {
                "description": "Violations may cause significant harm or legal consequences",
                "requires_human_review": True,
                "blocks_execution": True
            },
            "high": {
                "description": "Serious violations that should be addressed promptly",
                "requires_human_review": True,
                "blocks_execution": False
            },
            "medium": {
                "description": "Notable issues that should be flagged for attention",
                "requires_human_review": False,
                "blocks_execution": False
            },
            "low": {
                "description": "Minor issues that represent opportunities for improvement",
                "requires_human_review": False,
                "blocks_execution": False
            }
        }


class ValidationRule(Protocol):
    """Protocol defining a validation rule for standards compliance."""
    
    def validate(self, content: Any, standard: Standard) -> List[ValidationIssue]:
        """Validate content against a standard and return any issues found."""
        ...


class KeywordMatchRule:
    """A simple rule that checks for the presence or absence of keywords."""
    
    def __init__(self, 
                 trigger_words: List[str], 
                 required_words: List[str] = None, 
                 forbidden_words: List[str] = None,
                 severity: str = "medium",
                 rule_id: str = None):
        """Initialize the keyword match rule.
        
        Args:
            trigger_words: Words that trigger this rule to be applied
            required_words: Words that must be present when trigger words are found
            forbidden_words: Words that must not be present when trigger words are found
            severity: The severity level for violations of this rule
            rule_id: Optional identifier for this rule
        """
        self.trigger_words = [w.lower() for w in trigger_words]
        self.required_words = [w.lower() for w in (required_words or [])]
        self.forbidden_words = [w.lower() for w in (forbidden_words or [])]
        self.severity = severity
        self.rule_id = rule_id or f"keyword-{'-'.join(trigger_words)}"
    
    def validate(self, content: Any, standard: Standard) -> List[ValidationIssue]:
        """Check content for keyword patterns and return any issues found."""
        issues = []
        
        # Convert content to string if needed
        content_str = content if isinstance(content, str) else str(content)
        content_lower = content_str.lower()
        
        # Check if any trigger words are present
        trigger_found = any(word in content_lower for word in self.trigger_words)
        
        if trigger_found:
            # Check for required words
            if self.required_words and not any(word in content_lower for word in self.required_words):
                issues.append(ValidationIssue(
                    standard_id=standard.id,
                    severity=self.severity,
                    description=f"Missing required elements for {', '.join(self.trigger_words)} in {standard.name}",
                    recommendation=f"Include elements related to {', '.join(self.required_words)} when discussing {', '.join(self.trigger_words)}",
                    rule_id=self.rule_id,
                    confidence=0.8  # Keyword matching has moderate confidence
                ))
            
            # Check for forbidden words
            if self.forbidden_words and any(word in content_lower for word in self.forbidden_words):
                issues.append(ValidationIssue(
                    standard_id=standard.id,
                    severity=self.severity,
                    description=f"Found potentially non-compliant content with {', '.join(self.trigger_words)} in {standard.name}",
                    recommendation=f"Review usage of terms like {', '.join([w for w in self.forbidden_words if w in content_lower])}",
                    rule_id=self.rule_id,
                    confidence=0.8  # Keyword matching has moderate confidence
                ))
        
        return issues


class HarmfulPatternRule:
    """A rule that checks for harmful content patterns."""
    
    def __init__(self, 
                 patterns: Dict[str, str],
                 severity: str = "critical",
                 rule_id: str = "harmful-content"):
        """Initialize the harmful pattern rule.
        
        Args:
            patterns: Dictionary mapping patterns to their descriptions
            severity: The severity level for violations
            rule_id: Identifier for this rule
        """
        self.patterns = {p.lower(): desc for p, desc in patterns.items()}
        self.severity = severity
        self.rule_id = rule_id
    
    def validate(self, content: Any, standard: Standard) -> List[ValidationIssue]:
        """Check content for harmful patterns and return any issues found."""
        issues = []
        
        # Convert content to string if needed
        content_str = content if isinstance(content, str) else str(content)
        content_lower = content_str.lower()
        
        # Check for harmful patterns
        for pattern, description in self.patterns.items():
            if pattern in content_lower:
                issues.append(ValidationIssue(
                    standard_id=standard.id,
                    severity=self.severity,
                    description=f"{description} which violates {standard.name}",
                    recommendation="Remove all references to illegal or harmful activities",
                    rule_id=self.rule_id,
                    confidence=0.9  # Higher confidence for clearly harmful content
                ))
        
        return issues


class StandardsValidator:
    """
    Standards validation framework for ensuring compliance with domain-specific standards.
    
    This validator provides comprehensive standards validation with customizable rule sets,
    context-aware validation, extensible architecture, and support for rule-based compliance checking.
    It supports a wide range of validation techniques including keyword matching, pattern analysis,
    requirement verification, and structural validation.
    """
    
    def __init__(
        self, 
        domain: str = None, 
        supported_standards: Optional[List[str]] = None, 
        registry_instance: IStandardsRegistry = None,
        validation_context: Optional[Dict[str, Any]] = None
    ):
        """Initialize the validator.
        
        Args:
            domain: The industry domain (optional if supported_standards is provided)
            supported_standards: Optional list of supported standard IDs
            registry_instance: Optional registry instance to use. If None, the default registry is used.
            validation_context: Optional context information for validation
        """
        self.domain = domain
        self.registry = registry_instance or registry
        self.validation_context = validation_context or {}
        self.validation_issues: List[ValidationIssue] = []
        self.current_validation_targets: List[Dict[str, Any]] = []
        
        # If supported standards are provided, use them
        if supported_standards:
            self.supported_standards = supported_standards
        elif domain:
            # Get standards for the domain
            domain_standards = self.registry.get_standards_for_domain(domain)
            self.supported_standards = [std.id for std in domain_standards]
            
            # Add essential cross-domain standards
            cross_domain_standards = self.registry.get_cross_domain_standards()
            for std in cross_domain_standards:
                if std.id not in self.supported_standards:
                    self.supported_standards.append(std.id)
        else:
            # No domain or standards specified, use cross-domain standards only
            cross_domain_standards = self.registry.get_cross_domain_standards()
            self.supported_standards = [std.id for std in cross_domain_standards]
            
        # Load validation rules from registry
        self.dynamic_rules: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._load_dynamic_rules()
        
        # Initialize rule factories for each standard
        self.rule_factories: Dict[str, List[Callable]] = {}
        self._initialize_rule_factories()
        
        # Static rules as a fallback
        self.static_rules: Dict[str, List[ValidationRule]] = {}
        self._initialize_static_rules()
    
    def _load_dynamic_rules(self) -> None:
        """Load dynamic validation rules from registry."""
        # Load rules for each supported standard
        for std_id in self.supported_standards:
            # Get validation rules from registry
            rules = self.registry.get_validation_rules(std_id)
            if rules:
                self.dynamic_rules[std_id] = rules
    
    def _initialize_rule_factories(self) -> None:
        """Initialize rule factories for creating dynamic validation rules."""
        # Rule factory for keyword matching rules
        def create_keyword_rules(standard_id: str) -> List[ValidationRule]:
            """Create keyword matching rules from dynamic rules."""
            rules = []
            
            # Get dynamic rules for this standard
            standard_rules = self.dynamic_rules.get(standard_id, {})
            
            for rule_id, rule_info in standard_rules.items():
                # Extract rule metadata
                description = rule_info.get("description", "")
                severity = rule_info.get("severity", "medium")
                
                # Extract keywords from description
                words = description.lower().split()
                important_words = [w for w in words if len(w) > 4 and w.isalpha()]
                
                # Skip if not enough keywords
                if len(important_words) < 2:
                    continue
                
                # Create trigger words from most specific terms
                trigger_words = important_words[:3] if len(important_words) >= 3 else important_words
                
                # Create required words from remaining terms
                required_words = important_words[3:8] if len(important_words) > 3 else []
                
                # Create rule if we have enough terms
                if trigger_words:
                    rules.append(KeywordMatchRule(
                        trigger_words=trigger_words,
                        required_words=required_words,
                        severity=severity,
                        rule_id=f"{standard_id}:{rule_id}"
                    ))
            
            return rules
        
        # Register rule factories for each standard
        for std_id in self.supported_standards:
            self.rule_factories[std_id] = [create_keyword_rules]
    
    def _initialize_static_rules(self) -> None:
        """Initialize static validation rules as a fallback."""
        # Common rules for all standards
        common_rules = [
            HarmfulPatternRule({
                "illegally": "Contains references to illegal activities",
                "illegal activity": "Contains references to illegal activities",
                "hack": "Contains potentially harmful hacking-related content",
                "bypass security": "Contains instructions to bypass security measures",
                "steal": "Contains references to theft or unauthorized access",
                "violate": "Contains references to violating rules or regulations"
            })
        ]
        
        # Standard-specific rules
        self.static_rules["DATA_PRIVACY"] = common_rules + [
            KeywordMatchRule(
                trigger_words=["data", "information", "personal", "pii"],
                required_words=["privacy", "protect", "secure", "confidential", "consent", "policy"],
                rule_id="data-privacy-disclosure"
            ),
            KeywordMatchRule(
                trigger_words=["share", "disclose", "reveal", "publish", "transfer"],
                required_words=["consent", "permission", "authorized", "anonymized", "encrypted"],
                severity="high",
                rule_id="data-sharing-compliance"
            )
        ]
        
        self.static_rules["RESPONSIBLE_AI"] = common_rules + [
            KeywordMatchRule(
                trigger_words=["ai", "algorithm", "model", "prediction", "decision"],
                required_words=["transparent", "explainable", "fair", "accountable", "ethical"],
                rule_id="ai-transparency"
            ),
            KeywordMatchRule(
                trigger_words=["bias", "fairness", "discrimination"],
                required_words=["prevent", "mitigate", "reduce", "avoid", "test"],
                severity="high",
                rule_id="ai-bias"
            )
        ]
        
        self.static_rules["HIPAA"] = common_rules + [
            KeywordMatchRule(
                trigger_words=["patient", "medical", "health", "treatment", "diagnosis"],
                required_words=["protected", "confidential", "secure", "authorized", "consent"],
                severity="high",
                rule_id="phi-protection"
            ),
            KeywordMatchRule(
                trigger_words=["share", "disclose", "access", "release"],
                forbidden_words=["unauthorized", "public", "unrestricted", "all"],
                severity="critical",
                rule_id="hipaa-disclosure"
            )
        ]
        
        # Add more specific rules based on domain
        if self.domain == "accounting":
            self.static_rules["GAAP"] = common_rules + [
                KeywordMatchRule(
                    trigger_words=["financial statement", "balance sheet", "income statement", "cash flow"],
                    required_words=["consistent", "accurate", "complete", "accrual", "standards"],
                    rule_id="gaap-financial-reporting"
                ),
                KeywordMatchRule(
                    trigger_words=["estimate", "judgment", "assumption"],
                    required_words=["reasonable", "disclosed", "documented", "supported"],
                    rule_id="accounting-estimates"
                )
            ]
            
            self.static_rules["IFRS"] = common_rules + [
                KeywordMatchRule(
                    trigger_words=["financial statement", "reporting", "disclosure"],
                    required_words=["fair", "transparent", "complete", "accurate", "international"],
                    rule_id="ifrs-reporting"
                ),
                KeywordMatchRule(
                    trigger_words=["asset", "liability", "revenue", "expense"],
                    required_words=["recognition", "measurement", "disclosure", "criteria"],
                    rule_id="ifrs-recognition"
                )
            ]
        
        elif self.domain == "socialwork":
            self.static_rules["NASW_CODE_OF_ETHICS"] = common_rules + [
                KeywordMatchRule(
                    trigger_words=["client", "service", "case", "assessment"],
                    required_words=["ethical", "dignity", "worth", "respect", "self-determination", "informed consent"],
                    severity="high",
                    rule_id="client-dignity-respect"
                ),
                KeywordMatchRule(
                    trigger_words=["confidential", "privacy", "information", "record"],
                    required_words=["protect", "secure", "consent", "limits", "authorized"],
                    severity="critical",
                    rule_id="confidentiality-protection"
                )
            ]
            
            self.static_rules["CLIENT_CONFIDENTIALITY"] = common_rules + [
                KeywordMatchRule(
                    trigger_words=["client", "information", "case", "history", "details"],
                    required_words=["confidential", "private", "protected", "secure", "limited"],
                    severity="critical",
                    rule_id="client-privacy"
                )
            ]
        
        elif self.domain == "government":
            self.static_rules["PUBLIC_SECTOR_ETHICS"] = common_rules + [
                KeywordMatchRule(
                    trigger_words=["public servant", "government employee", "official", "civil servant"],
                    required_words=["ethical", "integrity", "impartial", "public interest", "responsibility"],
                    severity="high",
                    rule_id="public-service-ethics"
                )
            ]
            
            self.static_rules["GOVERNMENT_TRANSPARENCY_STANDARDS"] = common_rules + [
                KeywordMatchRule(
                    trigger_words=["information", "data", "decision", "process", "meeting"],
                    required_words=["transparent", "public", "available", "accessible", "open"],
                    rule_id="transparency-requirements"
                )
            ]
        
        # Use common rules as default
        self.static_rules["DEFAULT"] = common_rules
        
        # Add Deal Framework rules if supported
        if "DealFramework" in self.supported_standards:
            self.static_rules["DealFramework"] = common_rules + [
                KeywordMatchRule(
                    trigger_words=["problem", "challenge", "issue", "difficulty"],
                    required_words=["defined", "specific", "clear", "constraints", "criteria"],
                    severity="high",
                    rule_id="problem-definition"
                ),
                KeywordMatchRule(
                    trigger_words=["solution", "approach", "resolve", "address"],
                    required_words=["validated", "tested", "evaluated", "verified", "meets"],
                    severity="high",
                    rule_id="solution-validation"
                ),
                KeywordMatchRule(
                    trigger_words=["transaction", "exchange", "transfer", "deal"],
                    required_words=["complete", "successful", "verified", "agreed", "participants"],
                    severity="medium",
                    rule_id="transaction-completion"
                ),
                KeywordMatchRule(
                    trigger_words=["risk", "high-stakes", "consequential", "impact"],
                    required_words=["human", "review", "oversight", "approval", "verification"],
                    severity="critical",
                    rule_id="human-review"
                )
            ]
    
    def validate(self, content: Any, standard_id: str = None) -> ValidationResult:
        """
        Validate content against a specific standard or all supported standards.
        
        Args:
            content: The content to validate (string, dictionary, or object)
            standard_id: Optional specific standard to validate against
                         If None, validates against all supported standards
                         
        Returns:
            ValidationResult containing validation status and issues
        """
        # Clear previous validation issues
        self.validation_issues = []
        
        # Determine which standards to check
        standards_to_check = []
        if standard_id:
            if standard_id in self.supported_standards:
                standards_to_check = [standard_id]
            else:
                logger.warning(f"Standard {standard_id} not supported, skipping validation")
                return ValidationResult(
                    valid=True,
                    issues=[],
                    standards_checked=[]
                )
        else:
            standards_to_check = self.supported_standards
        
        # Validate against each standard
        for std_id in standards_to_check:
            standard = self.registry.get_standard(std_id)
            if not standard:
                logger.warning(f"Standard {std_id} not found in registry, skipping validation")
                continue
            
            # Validate content against this standard
            self._validate_against_standard(content, standard)
        
        # Create result
        return ValidationResult(
            valid=len(self.validation_issues) == 0,
            issues=self.validation_issues.copy(),
            standards_checked=standards_to_check,
            confidence=self._calculate_overall_confidence()
        )
    
    def _validate_against_standard(self, content: Any, standard: Standard) -> None:
        """
        Validate content against a specific standard.
        
        Args:
            content: The content to validate
            standard: The standard to validate against
        """
        # Apply dynamic rules first
        self._apply_dynamic_rules(content, standard)
        
        # If no issues found, apply static rules
        if not any(issue.standard_id == standard.id for issue in self.validation_issues):
            self._apply_static_rules(content, standard)
        
        # Apply requirement-based validation as a fallback
        if not any(issue.standard_id == standard.id for issue in self.validation_issues):
            self._validate_requirements(content, standard)
    
    def _apply_dynamic_rules(self, content: Any, standard: Standard) -> None:
        """
        Apply dynamically generated rules for a standard.
        
        Args:
            content: The content to validate
            standard: The standard to validate against
        """
        # Get rule factories for this standard
        factories = self.rule_factories.get(standard.id, [])
        
        # Apply each factory to generate and apply rules
        for factory in factories:
            rules = factory(standard.id)
            
            for rule in rules:
                issues = rule.validate(content, standard)
                self.validation_issues.extend(issues)
    
    def _apply_static_rules(self, content: Any, standard: Standard) -> None:
        """
        Apply static rules for a standard.
        
        Args:
            content: The content to validate
            standard: The standard to validate against
        """
        # Get static rules for this standard (or use defaults)
        rules = self.static_rules.get(standard.id, self.static_rules.get("DEFAULT", []))
        
        # Apply each rule
        for rule in rules:
            issues = rule.validate(content, standard)
            self.validation_issues.extend(issues)
    
    def _validate_requirements(self, content: Any, standard: Standard) -> None:
        """
        Validate content against a standard's requirements.
        
        Args:
            content: The content to validate
            standard: The standard to validate against
        """
        # Skip if no requirements
        if not standard.requirements:
            return
        
        # Convert content to string if it's not already
        content_str = str(content) if not isinstance(content, str) else content
        content_lower = content_str.lower()
        
        # Check each requirement
        for requirement in standard.requirements:
            requirement_text = requirement.lower()
            
            # Skip very short requirements or those that are too vague
            if len(requirement_text.split()) < 3:
                continue
                
            # Extract important terms from the requirement
            words = requirement_text.split()
            important_terms = [w for w in words if len(w) > 4 and w not in 
                              ["should", "would", "could", "must", "shall", "may", "about", "these", "those"]]
            
            # Skip if not enough important terms
            if len(important_terms) < 2:
                continue
            
            # Check if important terms from requirement are mentioned in content
            req_terms_present = sum(1 for term in important_terms if term in content_lower)
            relevance_ratio = req_terms_present / len(important_terms) if important_terms else 0
            
            # If content seems relevant to this requirement (some key terms present)
            # but not fully addressing it (not all terms present)
            if 0.2 < relevance_ratio < 0.7:
                self.validation_issues.append(ValidationIssue(
                    standard_id=standard.id,
                    severity="medium",
                    description=f"May not fully address requirement in {standard.name}",
                    recommendation=f"Review for compliance with: '{requirement}'",
                    confidence=0.6  # Lower confidence for this type of check
                ))
    
    def _calculate_overall_confidence(self) -> float:
        """
        Calculate the overall confidence score for validation results.
        
        Returns:
            Confidence score between 0 and 1
        """
        if not self.validation_issues:
            return 1.0
            
        # Average confidence of all issues
        confidences = [issue.confidence for issue in self.validation_issues]
        return sum(confidences) / len(confidences)
    
    def validate_structure(self, entity: Any, standard_id: str = None) -> ValidationResult:
        """
        Validate the structure of an entity against standards.
        
        This is particularly useful for validating Deal components against the DealFramework standard.
        
        Args:
            entity: The entity to validate (e.g., Deal, Problem, Solution)
            standard_id: Optional specific standard to validate against
                
        Returns:
            ValidationResult containing validation status and issues
        """
        # Get entity type for specialized validation
        entity_type = type(entity).__name__
        
        # Convert entity to dictionary if it has a to_dict method
        try:
            if hasattr(entity, "to_dict") and callable(entity.to_dict):
                entity_dict = entity.to_dict()
            else:
                # Try to convert to dict directly
                entity_dict = dict(entity)
        except (TypeError, ValueError):
            # If conversion fails, validate the entity as is
            return self.validate(entity, standard_id)
        
        # Add entity type to validation context
        context = self.validation_context.copy()
        context["entity_type"] = entity_type
        
        # Special handling for Deal Framework validation
        if standard_id is None or standard_id == "DealFramework":
            # Validate Deal structure
            if entity_type == "Deal":
                return self._validate_deal_structure(entity_dict)
            # Validate Problem structure
            elif entity_type == "Problem":
                return self._validate_problem_structure(entity_dict)
            # Validate Solution structure
            elif entity_type == "Solution":
                return self._validate_solution_structure(entity_dict)
            # Validate Player structure
            elif entity_type == "Player":
                return self._validate_player_structure(entity_dict)
            # Validate Transaction structure
            elif entity_type == "Transaction":
                return self._validate_transaction_structure(entity_dict)
        
        # Default validation for other cases
        return self.validate(entity_dict, standard_id)
    
    def _validate_deal_structure(self, deal_dict: Dict[str, Any]) -> ValidationResult:
        """
        Validate a Deal structure against the DealFramework standard.
        
        Args:
            deal_dict: Dictionary representation of a Deal
            
        Returns:
            ValidationResult containing validation status and issues
        """
        issues = []
        
        # Check for required fields
        required_fields = ["id", "name", "description", "participants", "status"]
        for field in required_fields:
            if field not in deal_dict or not deal_dict[field]:
                issues.append(ValidationIssue(
                    standard_id="DealFramework",
                    severity="high",
                    description=f"Missing required Deal field: {field}",
                    recommendation=f"Add a valid {field} to the Deal",
                    confidence=1.0
                ))
        
        # Check for problems if deal is not in draft status
        if deal_dict.get("status") != "draft" and not deal_dict.get("problems"):
            issues.append(ValidationIssue(
                standard_id="DealFramework",
                severity="high",
                description="Deal has no problems defined",
                recommendation="Add at least one Problem to the Deal",
                confidence=0.9
            ))
        
        # Check for players
        if not deal_dict.get("players"):
            issues.append(ValidationIssue(
                standard_id="DealFramework",
                severity="high",
                description="Deal has no players defined",
                recommendation="Add players for all participants",
                confidence=0.9
            ))
        elif len(deal_dict.get("players", {})) < len(deal_dict.get("participants", [])):
            issues.append(ValidationIssue(
                standard_id="DealFramework",
                severity="medium",
                description="Not all participants have corresponding players",
                recommendation="Add players for all participants",
                confidence=0.8
            ))
        
        # Check for completed deals
        if deal_dict.get("status") == "completed":
            # Verify that all problems have solutions
            problems = deal_dict.get("problems", {})
            solutions = deal_dict.get("solutions", {})
            
            problem_ids = set(problems.keys())
            solution_problem_ids = set()
            
            for sol_id, solution in solutions.items():
                if solution.get("problem_id"):
                    solution_problem_ids.add(solution.get("problem_id"))
            
            unresolved_problems = problem_ids - solution_problem_ids
            if unresolved_problems:
                issues.append(ValidationIssue(
                    standard_id="DealFramework",
                    severity="critical",
                    description=f"Completed deal has {len(unresolved_problems)} unresolved problems",
                    recommendation="Add solutions for all problems before completing the deal",
                    confidence=1.0
                ))
        
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues,
            standards_checked=["DealFramework"],
            confidence=1.0
        )
    
    def _validate_problem_structure(self, problem_dict: Dict[str, Any]) -> ValidationResult:
        """
        Validate a Problem structure against the DealFramework standard.
        
        Args:
            problem_dict: Dictionary representation of a Problem
            
        Returns:
            ValidationResult containing validation status and issues
        """
        issues = []
        
        # Check for required fields
        required_fields = ["id", "name", "description"]
        for field in required_fields:
            if field not in problem_dict or not problem_dict[field]:
                issues.append(ValidationIssue(
                    standard_id="DealFramework",
                    severity="high",
                    description=f"Missing required Problem field: {field}",
                    recommendation=f"Add a valid {field} to the Problem",
                    confidence=1.0
                ))
        
        # Check for success criteria
        if not problem_dict.get("success_criteria"):
            issues.append(ValidationIssue(
                standard_id="DealFramework",
                severity="medium",
                description="Problem has no success criteria defined",
                recommendation="Add success criteria to clarify when the problem is solved",
                confidence=0.9
            ))
        
        # Check for constraints
        if not problem_dict.get("constraints"):
            issues.append(ValidationIssue(
                standard_id="DealFramework",
                severity="low",
                description="Problem has no constraints defined",
                recommendation="Consider adding constraints to define problem boundaries",
                confidence=0.7
            ))
        
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues,
            standards_checked=["DealFramework"],
            confidence=1.0
        )
    
    def _validate_solution_structure(self, solution_dict: Dict[str, Any]) -> ValidationResult:
        """
        Validate a Solution structure against the DealFramework standard.
        
        Args:
            solution_dict: Dictionary representation of a Solution
            
        Returns:
            ValidationResult containing validation status and issues
        """
        issues = []
        
        # Check for required fields
        required_fields = ["id", "name", "description"]
        for field in required_fields:
            if field not in solution_dict or not solution_dict[field]:
                issues.append(ValidationIssue(
                    standard_id="DealFramework",
                    severity="high",
                    description=f"Missing required Solution field: {field}",
                    recommendation=f"Add a valid {field} to the Solution",
                    confidence=1.0
                ))
        
        # Check for problem ID
        if not solution_dict.get("problem_id"):
            issues.append(ValidationIssue(
                standard_id="DealFramework",
                severity="high",
                description="Solution is not linked to a problem",
                recommendation="Link the solution to a specific problem",
                confidence=0.9
            ))
        
        # Check for approach
        if not solution_dict.get("approach"):
            issues.append(ValidationIssue(
                standard_id="DealFramework",
                severity="medium",
                description="Solution has no approach defined",
                recommendation="Add an approach description to the solution",
                confidence=0.8
            ))
        
        # Check for implementation steps
        if not solution_dict.get("implementation_steps"):
            issues.append(ValidationIssue(
                standard_id="DealFramework",
                severity="medium",
                description="Solution has no implementation steps defined",
                recommendation="Add implementation steps to the solution",
                confidence=0.8
            ))
        
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues,
            standards_checked=["DealFramework"],
            confidence=1.0
        )
    
    def _validate_player_structure(self, player_dict: Dict[str, Any]) -> ValidationResult:
        """
        Validate a Player structure against the DealFramework standard.
        
        Args:
            player_dict: Dictionary representation of a Player
            
        Returns:
            ValidationResult containing validation status and issues
        """
        issues = []
        
        # Check for required fields
        required_fields = ["id", "name", "role", "agent_id"]
        for field in required_fields:
            if field not in player_dict or not player_dict[field]:
                issues.append(ValidationIssue(
                    standard_id="DealFramework",
                    severity="high",
                    description=f"Missing required Player field: {field}",
                    recommendation=f"Add a valid {field} to the Player",
                    confidence=1.0
                ))
        
        # Check for capabilities
        if not player_dict.get("capabilities"):
            issues.append(ValidationIssue(
                standard_id="DealFramework",
                severity="low",
                description="Player has no capabilities defined",
                recommendation="Add capabilities to clarify player roles and expertise",
                confidence=0.7
            ))
        
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues,
            standards_checked=["DealFramework"],
            confidence=1.0
        )
    
    def _validate_transaction_structure(self, transaction_dict: Dict[str, Any]) -> ValidationResult:
        """
        Validate a Transaction structure against the DealFramework standard.
        
        Args:
            transaction_dict: Dictionary representation of a Transaction
            
        Returns:
            ValidationResult containing validation status and issues
        """
        issues = []
        
        # Check for required fields
        required_fields = ["id", "name", "transaction_type", "from_player", "to_player", "status"]
        for field in required_fields:
            if field not in transaction_dict or not transaction_dict[field]:
                issues.append(ValidationIssue(
                    standard_id="DealFramework",
                    severity="high",
                    description=f"Missing required Transaction field: {field}",
                    recommendation=f"Add a valid {field} to the Transaction",
                    confidence=1.0
                ))
        
        # Check for completed transactions without approvals
        if (transaction_dict.get("status") == "completed" and 
            transaction_dict.get("approval_requirements") and 
            not transaction_dict.get("approval_history")):
            issues.append(ValidationIssue(
                standard_id="DealFramework",
                severity="critical",
                description="Transaction marked completed without required approvals",
                recommendation="Obtain all required approvals before completing transaction",
                confidence=1.0
            ))
        
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues,
            standards_checked=["DealFramework"],
            confidence=1.0
        )
    
    def validate_field(self, field_name: str, value: Any, standards: List[str] = None) -> ValidationResult:
        """
        Validate a specific field against standards.
        
        Args:
            field_name: Name of the field being validated
            value: Value to validate
            standards: List of standard IDs to validate against (defaults to all supported standards)
            
        Returns:
            ValidationResult containing validation status and issues
        """
        # Setup validation context
        context = self.validation_context.copy()
        context["field_name"] = field_name
        
        # Set standards to validate against
        standards_to_check = standards or self.supported_standards
        
        # Validate the field
        issues = []
        for std_id in standards_to_check:
            if std_id not in self.supported_standards:
                continue
                
            standard = self.registry.get_standard(std_id)
            if not standard:
                continue
            
            # Use field-specific validation logic
            field_issues = self._validate_field_against_standard(field_name, value, standard)
            issues.extend(field_issues)
        
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues,
            standards_checked=standards_to_check,
            confidence=self._calculate_overall_confidence()
        )
    
    def _validate_field_against_standard(self, field_name: str, value: Any, standard: Standard) -> List[ValidationIssue]:
        """
        Validate a field against a specific standard.
        
        Args:
            field_name: Name of the field being validated
            value: Value to validate
            standard: The standard to validate against
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Convert value to string for text-based validation
        if not isinstance(value, str):
            value_str = str(value)
        else:
            value_str = value
        
        # Check field against standard requirements
        for requirement in standard.requirements:
            requirement_text = requirement.lower()
            
            # Skip requirements not relevant to this field
            if field_name.lower() not in requirement_text:
                continue
            
            # Check if requirement is addressed
            value_lower = value_str.lower()
            
            # Extract key terms from requirement
            words = requirement_text.split()
            important_terms = [w for w in words if len(w) > 4 and w not in 
                              ["should", "would", "could", "must", "shall", "may", "about", "these", "those"]]
            
            # Check if key terms are present in value
            terms_present = [term for term in important_terms if term in value_lower]
            
            # If some but not all terms are present
            if terms_present and len(terms_present) < len(important_terms) / 2:
                issues.append(ValidationIssue(
                    standard_id=standard.id,
                    severity="medium",
                    description=f"Field '{field_name}' may not fully comply with {standard.name}",
                    recommendation=f"Review field against requirement: '{requirement}'",
                    confidence=0.7
                ))
        
        # Check for field-specific issues
        if field_name.lower() in ["password", "credential", "token", "secret", "key"]:
            # Check for lack of protection terms
            protection_terms = ["encrypted", "secured", "protected", "hashed"]
            if not any(term in value_str.lower() for term in protection_terms):
                issues.append(ValidationIssue(
                    standard_id=standard.id,
                    severity="high",
                    description=f"Sensitive field '{field_name}' lacks security protection",
                    recommendation="Ensure sensitive data is properly protected",
                    confidence=0.9
                ))
        
        return issues
    
    def get_violations(self) -> List[ValidationIssue]:
        """
        Get all validation issues from the most recent validation.
        
        Returns:
            List of validation issues
        """
        return self.validation_issues.copy()
    
    def get_critical_violations(self) -> List[ValidationIssue]:
        """
        Get critical validation issues from the most recent validation.
        
        Returns:
            List of critical validation issues
        """
        return [issue for issue in self.validation_issues if issue.severity == "critical"]
    
    def get_supported_standards_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all supported standards.
        
        Returns:
            List of dictionaries with standard information
        """
        standards_info = []
        
        for std_id in self.supported_standards:
            std = self.registry.get_standard(std_id)
            if std:
                standards_info.append({
                    "id": std.id,
                    "name": std.name,
                    "description": std.description,
                    "organization": std.organization,
                    "domain": std.domain,
                    "requirement_count": len(std.requirements)
                })
        
        return standards_info
    
    def validate_content(self, content: Union[str, Dict], standards_metadata: Optional[Dict[str, Any]] = None,
                       max_standards: int = None) -> ValidationResult:
        """
        Legacy method for backwards compatibility.
        
        Args:
            content: The content to validate
            standards_metadata: Optional metadata about which standards to check
            max_standards: Optional maximum number of standards to check
            
        Returns:
            ValidationResult containing validation status and issues
        """
        # Determine standards to check
        if standards_metadata and "standards" in standards_metadata:
            standards_to_validate = [
                std_id for std_id in standards_metadata["standards"].keys() 
                if std_id in self.supported_standards
            ]
        else:
            standards_to_validate = self.supported_standards
            
            # Apply limit if specified
            if max_standards is not None and max_standards < len(standards_to_validate):
                standards_to_validate = standards_to_validate[:max_standards]
        
        # Update validation context with metadata
        if standards_metadata:
            self.validation_context.update(standards_metadata)
        
        # Validate content against standards
        return self.validate(content, None)


# Create the default registry instance
registry = StandardsRegistry()

# Load standards from std.json file
def load_standards_from_file(registry_instance: IStandardsRegistry = None):
    """Load standards from the std.json file.
    
    Args:
        registry_instance: Optional registry instance to use.
            If None, the default registry is used.
    
    Raises:
        FileNotFoundError: If the std.json file cannot be found.
        json.JSONDecodeError: If the std.json file is not valid JSON.
        ValueError: If the std.json file has an unexpected format.
    """
    registry_to_use = registry_instance or registry
    
    try:
        # Find the path to the std.json file
        data_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "data"
        ))
        std_file = os.path.join(data_dir, "std.json")
        
        # Check if file exists
        if not os.path.exists(std_file):
            error_msg = f"Standards file not found: {std_file}"
            logger.critical(error_msg)
            raise FileNotFoundError(error_msg)
        
        # Load the standards data
        try:
            with open(std_file, "r") as f:
                standards_data = json.load(f)
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in standards file: {e}"
            logger.critical(error_msg)
            raise
            
        # Validate expected format
        if not isinstance(standards_data, dict):
            error_msg = f"Unexpected format in std.json: expected dict, got {type(standards_data)}"
            logger.critical(error_msg)
            raise ValueError(error_msg)
        
        # Process and register each standard
        for std_id, std_info in standards_data.items():
            try:
                # Extract the requirements if available
                requirements = []
                if "resources" in std_info:
                    for resource_type, resource_list in std_info["resources"].items():
                        if isinstance(resource_list, list):
                            requirements.extend(resource_list)
                
                # Extract organization info if available
                organization = None
                if "organization" in std_info and "name" in std_info["organization"]:
                    organization = std_info["organization"]["name"]
                
                # Extract version info if available
                version = None
                if "specification" in std_info and "version" in std_info["specification"]:
                    version = std_info["specification"]["version"]
                
                # Extract domain directly if available
                domain = None
                if "domain" in std_info:
                    domain = std_info["domain"]
                else:
                    domain = get_domain_for_standard(std_id, std_info)
                
                # Create and register the standard
                standard = Standard(
                    id=std_id,
                    name=std_info.get("name", std_id),  # Use the ID as name if not explicitly provided
                    description=std_info.get("description", ""),
                    organization=organization,
                    version=version,
                    requirements=requirements,  # Use all requirements, no arbitrary limit
                    domain=domain
                )
                
                registry_to_use.register_standard(standard)
            except Exception as e:
                # Log error but continue processing other standards
                logger.error(f"Error processing standard {std_id}: {e}")
        
        logger.info(f"Loaded {len(standards_data)} standards from std.json")
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        # Log the specific error with traceback
        logger.critical(f"Failed to load standards from file: {e}", exc_info=True)
        
        # Register fallback standards to allow system to continue in degraded mode
        logger.warning("Loading fallback standards due to configuration error")
        register_essential_standards(registry_to_use)
        
        # Re-raise for proper error handling by caller
        raise

def get_domain_for_standard(std_id: str, std_info: Dict) -> Optional[str]:
    """Determine the domain for a standard based on its ID and info."""
    # Map standard IDs to domains (this is a simplified approach)
    domain_mappings = {
        "HIPAA": "healthcare",
        "HITECH": "healthcare",
        "ATA": "healthcare",
        "ISO_13131": "healthcare",
        "HL7": "healthcare",
        "FHIR": "healthcare",
        "DICOM": "healthcare",
        
        "SEC": "finance",
        "FINRA": "finance",
        "BASEL": "finance",
        "SOX": "finance",
        "AML": "finance",
        "KYC": "finance",
        "GDPR": "data_privacy",
        "CCPA": "data_privacy",
        
        "ISO_27001": "security",
        "NIST": "security",
        "SOC2": "security",
        "PCI_DSS": "security",
        
        "FDA": "agriculture",
        "FSMA": "agriculture",
        "HACCP": "agriculture",
        "USDA": "agriculture",
        
        "ISO_9001": "quality",
        "CMMI": "technology",
        "OWASP": "technology"
    }
    
    # Check for direct matches
    for key, domain in domain_mappings.items():
        if key in std_id:
            return domain
    
    # Check description for keywords
    description = std_info.get("description", "").lower()
    keyword_domain_map = {
        "healthcare": ["health", "medical", "patient", "clinical", "hospital"],
        "finance": ["financial", "banking", "investment", "trading", "money"],
        "agriculture": ["agriculture", "farm", "food", "crop", "livestock"],
        "technology": ["software", "technology", "computing", "data", "digital"],
        "security": ["security", "privacy", "protection", "cyber", "threat"],
        "energy": ["energy", "power", "electricity", "renewable", "grid"]
    }
    
    for domain, keywords in keyword_domain_map.items():
        if any(keyword in description for keyword in keywords):
            return domain
    
    return None

def register_essential_standards(registry_instance: IStandardsRegistry = None):
    """Register essential standards that should always be available.
    
    Args:
        registry_instance: Optional registry instance to use.
            If None, the default registry is used.
    """
    registry_to_use = registry_instance or registry
    
    # Register common cross-domain standards
    registry_to_use.register_standard(Standard(
        id="DATA_PRIVACY",
        name="Data Privacy Standard",
        description="General data privacy requirements applicable across domains",
        domain="data_privacy",
        requirements=[
            "Personal data must be processed lawfully, fairly, and transparently",
            "Personal data must be collected for specified, explicit, and legitimate purposes",
            "Personal data must be adequate, relevant, and limited to what is necessary",
            "Personal data must be accurate and kept up to date",
            "Personal data must be stored securely"
        ]
    ))

    registry_to_use.register_standard(Standard(
        id="RESPONSIBLE_AI",
        name="Responsible AI Guidelines",
        description="Guidelines for responsible AI development and deployment",
        domain="artificial_intelligence",
        requirements=[
            "AI systems should be transparent in their operation",
            "AI systems should avoid creating or reinforcing bias",
            "AI systems should respect user privacy and data rights",
            "AI systems should be robust and secure",
            "AI systems should be accountable and auditable"
        ]
    ))

    # Register healthcare-specific standards
    registry_to_use.register_standard(Standard(
        id="HIPAA",
        name="Health Insurance Portability and Accountability Act",
        organization="U.S. Department of Health and Human Services",
        description="Regulations to protect sensitive patient health information",
        domain="healthcare",
        requirements=[
            "Implement safeguards to protect patient health information",
            "Limit disclosure of protected health information to the minimum necessary",
            "Patients have the right to access their health information",
            "Maintain audit controls and activity logs",
            "Conduct risk assessments and management"
        ]
    ))

    # Register finance-specific standards
    registry_to_use.register_standard(Standard(
        id="FINANCIAL_ADVICE",
        name="Financial Advice Standards",
        description="Standards for providing financial advice",
        domain="finance",
        requirements=[
            "Disclose relevant risks and limitations",
            "Consider client's specific financial situation",
            "Avoid conflicts of interest",
            "Present balanced view of investment opportunities",
            "Maintain current knowledge of financial markets and regulations"
        ]
    ))
    
    # Register accounting-specific standards
    registry_to_use.register_standard(Standard(
        id="GAAP",
        name="Generally Accepted Accounting Principles",
        organization="Financial Accounting Standards Board",
        description="A set of accounting standards for financial reporting",
        domain="accounting",
        requirements=[
            "Present financial information fairly and consistently",
            "Follow accrual accounting principles",
            "Maintain proper documentation for financial transactions",
            "Apply consistent accounting methods across reporting periods",
            "Disclose significant accounting policies"
        ]
    ))
    
    registry_to_use.register_standard(Standard(
        id="IFRS",
        name="International Financial Reporting Standards",
        organization="International Accounting Standards Board",
        description="International accounting standards for financial statements",
        domain="accounting",
        requirements=[
            "Present fair view of financial position and performance",
            "Prepare financial statements on accrual basis",
            "Apply materiality concept to financial reporting",
            "Ensure financial statements are understandable, relevant, reliable and comparable",
            "Disclose significant judgments and estimates"
        ]
    ))
    
    # Register social work-specific standards
    registry_to_use.register_standard(Standard(
        id="NASW_CODE_OF_ETHICS",
        name="NASW Code of Ethics",
        organization="National Association of Social Workers",
        description="Ethical principles and standards that guide social work practice",
        domain="socialwork",
        requirements=[
            "Respect the dignity and worth of the person",
            "Maintain client confidentiality and privacy",
            "Prioritize client self-determination",
            "Ensure informed consent for all interventions",
            "Maintain clear professional boundaries",
            "Promote social justice and advocate for vulnerable populations",
            "Practice cultural competence and respect diversity",
            "Use evidence-based practices and maintain professional competence",
            "Uphold integrity and trustworthiness in professional practice",
            "Fulfill obligations to the broader society and specific vulnerable populations"
        ]
    ))
    
    registry_to_use.register_standard(Standard(
        id="CLIENT_CONFIDENTIALITY",
        name="Client Confidentiality Standards",
        description="Standards for maintaining client confidentiality and privacy",
        domain="socialwork",
        requirements=[
            "Protect client information from unauthorized disclosure",
            "Inform clients about limits of confidentiality",
            "Only share information with appropriate consent",
            "Maintain secure records and communications",
            "Follow mandatory reporting requirements while minimizing disclosure",
            "Ensure confidentiality in electronic communications and records"
        ]
    ))
    
    registry_to_use.register_standard(Standard(
        id="CULTURAL_COMPETENCE",
        name="Cultural Competence Standards",
        description="Standards for culturally competent social work practice",
        domain="socialwork",
        requirements=[
            "Acknowledge the importance of culture in human experience",
            "Recognize the strengths in all cultures",
            "Practice cultural humility and ongoing self-reflection",
            "Obtain knowledge about different cultural groups",
            "Develop culturally appropriate intervention strategies",
            "Avoid imposing values that may conflict with client cultural identity",
            "Consider historical oppression and discrimination in assessment and intervention"
        ]
    ))
    
    # Register government administration-specific standards
    registry_to_use.register_standard(Standard(
        id="PUBLIC_SECTOR_ETHICS",
        name="Public Sector Ethics Standards",
        description="Ethical principles for public service",
        domain="government",
        requirements=[
            "Place public interest above personal, political, or organizational interests",
            "Maintain high standards of integrity and ethical conduct",
            "Avoid conflicts of interest or appearances of impropriety",
            "Ensure proper use and management of public resources",
            "Promote equality and non-discrimination in public service delivery",
            "Report misconduct and protect whistleblowers",
            "Uphold professional standards and competence in public service"
        ]
    ))
    
    registry_to_use.register_standard(Standard(
        id="GOVERNMENT_TRANSPARENCY_STANDARDS",
        name="Government Transparency Standards",
        description="Standards for transparency in government operations",
        domain="government",
        requirements=[
            "Provide timely access to government information and data",
            "Hold open meetings for public business",
            "Make decision-making processes visible to the public",
            "Proactively share information with stakeholders",
            "Document and preserve government records",
            "Make information accessible in usable formats",
            "Balance transparency with legitimate privacy and security concerns"
        ]
    ))
    
    registry_to_use.register_standard(Standard(
        id="PUBLIC_RECORDS_MANAGEMENT",
        name="Public Records Management Standards",
        description="Standards for managing government records",
        domain="government",
        requirements=[
            "Maintain records according to retention schedules",
            "Document activities, decisions, and transactions",
            "Preserve records in accessible formats",
            "Implement secure storage and retrieval systems",
            "Follow proper procedures for records disposal",
            "Comply with public records access laws",
            "Protect confidential and personally identifiable information"
        ]
    ))
    
    registry_to_use.register_standard(Standard(
        id="ADMINISTRATIVE_PROCEDURE_RULES",
        name="Administrative Procedure Rules",
        description="Rules governing administrative processes",
        domain="government",
        requirements=[
            "Follow due process in administrative actions",
            "Provide notice and opportunity to be heard",
            "Apply rules and procedures consistently",
            "Document reasoning for administrative decisions",
            "Allow for review of administrative determinations",
            "Follow established timelines and deadlines",
            "Ensure administrative actions fall within legal authority"
        ]
    ))
    
    registry_to_use.register_standard(Standard(
        id="PUBLIC_PROCUREMENT_PROTOCOLS",
        name="Public Procurement Protocols",
        description="Protocols for government purchasing and contracting",
        domain="government",
        requirements=[
            "Ensure open competition in procurement processes",
            "Maintain vendor-neutral specifications",
            "Follow transparent selection procedures",
            "Document procurement decisions and rationales",
            "Prevent conflicts of interest in contracting",
            "Apply value-for-money principles",
            "Include proper oversight and accountability measures"
        ]
    ))
    
    registry_to_use.register_standard(Standard(
        id="GOVERNMENT_ACCOUNTABILITY_FRAMEWORKS",
        name="Government Accountability Frameworks",
        description="Frameworks for accountability in public administration",
        domain="government",
        requirements=[
            "Establish clear responsibilities and performance expectations",
            "Monitor and report on program outcomes",
            "Implement internal controls and risk management",
            "Respond to audit and oversight findings",
            "Provide transparent reporting on government activities",
            "Hold officials accountable for decisions and actions",
            "Address and correct identified deficiencies"
        ]
    ))
    
    registry_to_use.register_standard(Standard(
        id="PUBLIC_SERVICE_DELIVERY_STANDARDS",
        name="Public Service Delivery Standards",
        description="Standards for effective government service delivery",
        domain="government",
        requirements=[
            "Provide timely and responsive service",
            "Ensure accessibility for all constituents",
            "Deliver services with professionalism and courtesy",
            "Establish and meet clear service level standards",
            "Collect and respond to feedback on service quality",
            "Continuously improve service delivery processes",
            "Provide equitable service regardless of constituent characteristics"
        ]
    ))
    
    registry_to_use.register_standard(Standard(
        id="PUBLIC_PARTICIPATION_GUIDELINES",
        name="Public Participation Guidelines",
        description="Guidelines for engaging the public in government",
        domain="government",
        requirements=[
            "Provide meaningful opportunities for public input",
            "Involve stakeholders early in decision-making processes",
            "Consider diverse perspectives and needs in policy development",
            "Communicate how public input influences decisions",
            "Use multiple methods to reach different stakeholder groups",
            "Provide sufficient information for informed participation",
            "Make participation processes accessible to all"
        ]
    ))
    
    registry_to_use.register_standard(Standard(
        id="GOVERNMENT_DATA_GOVERNANCE",
        name="Government Data Governance Standards",
        description="Standards for managing government data",
        domain="government",
        requirements=[
            "Establish data quality and integrity controls",
            "Implement data security and privacy protections",
            "Define data ownership and stewardship responsibilities",
            "Document metadata and data dictionaries",
            "Follow data sharing and interoperability standards",
            "Maintain data as a strategic asset",
            "Ensure data is fit for its intended purposes"
        ]
    ))
    
    registry_to_use.register_standard(Standard(
        id="PUBLIC_SECTOR_PERFORMANCE_METRICS",
        name="Public Sector Performance Metrics",
        description="Standards for measuring government performance",
        domain="government",
        requirements=[
            "Establish relevant and measurable performance indicators",
            "Collect and analyze performance data",
            "Report performance results transparently",
            "Use performance information to improve operations",
            "Balance quantitative and qualitative measures",
            "Focus on outcomes rather than just outputs",
            "Compare performance against established targets"
        ]
    ))
    
    logger.info("Essential standards have been registered")


# Try to load standards from file, falling back to essential standards if needed
try:
    load_standards_from_file()
except Exception:
    logger.warning("Failed to load standards from file - system running with fallback standards only")
    # The error has already been logged by load_standards_from_file