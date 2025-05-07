"""
Core interfaces for the Trade Balance System.

This module defines the essential interfaces for the Trade Balance System,
establishing the contract between different components and enabling
parallel development of implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any, Protocol, TypeVar, Generic


# ===== Value Translation & Win-Win Framework Interfaces =====

class EntityType(Enum):
    """Entity types supported by the Win-Win framework."""
    GOVERNMENT = "government"
    CORPORATE = "corporate"
    NGO = "ngo"
    CIVILIAN = "civilian"


@dataclass
class EntityProfile:
    """Profile for an entity participating in a deal."""
    id: str
    name: str
    type: EntityType
    dimensions: Dict[str, float]  # Value dimension weights
    time_preference: float  # Discount rate for time
    risk_preference: float  # Risk aversion factor
    resource_constraints: Dict[str, float]  # Constraints on resources
    performance_metrics: Dict[str, List[float]]  # Historical performance


@dataclass
class ValueComponent:
    """Component of value for an entity."""
    dimension: str
    amount: float
    timeline: List[Tuple[int, float]]  # List of (period, amount) tuples
    probability: float
    verification_method: str
    is_quantifiable: bool
    network_effects: Dict[str, float]  # Impact on other dimensions


@dataclass
class EntityValue:
    """Total value assessment for an entity."""
    entity_id: str
    entity_type: EntityType
    components: Dict[str, ValueComponent]
    total_value: float
    time_adjusted_value: float
    risk_adjusted_value: float
    is_win: bool
    confidence: float


class IValueTranslator(Protocol):
    """Protocol for value translation between domains."""
    
    def translate_value(
        self, 
        value_components: Dict[str, ValueComponent],
        entity_profile: EntityProfile
    ) -> Tuple[float, Dict[str, float]]:
        """
        Translate value components into entity-specific value.
        
        Args:
            value_components: Dictionary of value components
            entity_profile: Entity profile
            
        Returns:
            Tuple of (total value, component values dictionary)
        """
        ...


class IWinWinCalculator(Protocol):
    """Protocol for Win-Win calculation and optimization."""
    
    def calculate_entity_value(
        self,
        entity_profile: EntityProfile,
        value_components: Dict[str, ValueComponent],
        historical_data: Optional[Dict[str, List[float]]] = None,
        superset_data: Optional[Dict[str, List[float]]] = None
    ) -> EntityValue:
        """
        Calculate the total value for an entity.
        
        Args:
            entity_profile: Entity profile
            value_components: Dictionary of value components
            historical_data: Historical value data for this entity
            superset_data: Value data for the superset of entities
            
        Returns:
            EntityValue object
        """
        ...
    
    def is_win_win(
        self,
        entity_values: Dict[str, EntityValue]
    ) -> bool:
        """
        Determine if a deal satisfies the win-win condition for all entities.
        
        Args:
            entity_values: Dictionary of EntityValue objects by entity ID
            
        Returns:
            True if the deal is win-win, False otherwise
        """
        ...
    
    def optimize_value_distribution(
        self,
        entity_profiles: Dict[str, EntityProfile],
        initial_value_components: Dict[str, Dict[str, ValueComponent]],
        constraints: Dict[str, Any]
    ) -> Dict[str, Dict[str, ValueComponent]]:
        """
        Optimize the distribution of value among entities to ensure win-win.
        
        Args:
            entity_profiles: Dictionary of entity profiles by entity ID
            initial_value_components: Dictionary of value components by entity ID
            constraints: Dictionary of optimization constraints
            
        Returns:
            Optimized value components by entity ID
        """
        ...
    
    def analyze_win_win_deal(
        self,
        entity_profiles: Dict[str, EntityProfile],
        value_components: Dict[str, Dict[str, ValueComponent]]
    ) -> Dict[str, Any]:
        """
        Analyze a deal for win-win status and suggest improvements.
        
        Args:
            entity_profiles: Dictionary of entity profiles by entity ID
            value_components: Dictionary of value components by entity ID
            
        Returns:
            Dictionary with analysis results
        """
        ...


# ===== Market Network Interfaces =====

class MarketMechanism(Enum):
    """Market mechanisms supported by the system."""
    CONTINUOUS_DOUBLE_AUCTION = "continuous_double_auction"
    CALL_MARKET = "call_market"
    MARKET_MAKER = "market_maker"


class OrderType(Enum):
    """Order types for market transactions."""
    BUY = "buy"
    SELL = "sell"


@dataclass
class Order:
    """Market order representation."""
    order_id: str
    agent_id: str
    order_type: OrderType
    resource_type: str
    quantity: float
    price: float
    timestamp: datetime
    expiration: Optional[datetime] = None
    conditions: Dict[str, Any] = None


@dataclass
class Transaction:
    """Market transaction representation."""
    transaction_id: str
    buy_order_id: str
    sell_order_id: str
    buyer_id: str
    seller_id: str
    resource_type: str
    quantity: float
    price: float
    timestamp: datetime
    fees: Dict[str, float] = None


class NetworkType(Enum):
    """Network types supported by the system."""
    SOCIAL = "social"
    COMMERCIAL = "commercial"
    KNOWLEDGE = "knowledge"
    COMPOSITE = "composite"


class EffectType(Enum):
    """Network effect types."""
    DIRECT = "direct"
    INDIRECT = "indirect"
    LOCAL = "local"
    GLOBAL = "global"


class IMarket(Protocol):
    """Protocol for market implementations."""
    
    @property
    def market_id(self) -> str:
        """Get market ID."""
        ...
    
    @property
    def mechanism(self) -> MarketMechanism:
        """Get market mechanism."""
        ...
    
    def place_order(self, order: Order) -> bool:
        """
        Place an order in the market.
        
        Args:
            order: Order to place
            
        Returns:
            True if order was placed successfully, False otherwise
        """
        ...
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order in the market.
        
        Args:
            order_id: ID of order to cancel
            
        Returns:
            True if order was cancelled successfully, False otherwise
        """
        ...
    
    def get_transactions(self, 
                         agent_id: Optional[str] = None,
                         resource_type: Optional[str] = None,
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None
                        ) -> List[Transaction]:
        """
        Get transactions matching the specified criteria.
        
        Args:
            agent_id: Filter by agent ID
            resource_type: Filter by resource type
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            List of matching transactions
        """
        ...
    
    def get_market_price(self, resource_type: str) -> float:
        """
        Get current market price for a resource.
        
        Args:
            resource_type: Resource type
            
        Returns:
            Current market price
        """
        ...
    
    def get_order_book(self, resource_type: str) -> Dict[str, List[Order]]:
        """
        Get order book for a resource.
        
        Args:
            resource_type: Resource type
            
        Returns:
            Dictionary with 'buy' and 'sell' keys mapping to lists of orders
        """
        ...


class IAgentNetwork(Protocol):
    """Protocol for agent network implementations."""
    
    @property
    def network_id(self) -> str:
        """Get network ID."""
        ...
    
    @property
    def network_type(self) -> NetworkType:
        """Get network type."""
        ...
    
    def add_agent(self, agent_id: str, attributes: Dict[str, Any]) -> bool:
        """
        Add an agent to the network.
        
        Args:
            agent_id: Agent ID
            attributes: Agent attributes
            
        Returns:
            True if agent was added successfully, False otherwise
        """
        ...
    
    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the network.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            True if agent was removed successfully, False otherwise
        """
        ...
    
    def add_edge(self, agent_id_1: str, agent_id_2: str, weight: float = 1.0) -> bool:
        """
        Add an edge between agents.
        
        Args:
            agent_id_1: First agent ID
            agent_id_2: Second agent ID
            weight: Edge weight
            
        Returns:
            True if edge was added successfully, False otherwise
        """
        ...
    
    def remove_edge(self, agent_id_1: str, agent_id_2: str) -> bool:
        """
        Remove an edge between agents.
        
        Args:
            agent_id_1: First agent ID
            agent_id_2: Second agent ID
            
        Returns:
            True if edge was removed successfully, False otherwise
        """
        ...
    
    def calculate_network_value(self) -> float:
        """
        Calculate the total network value.
        
        Returns:
            Network value
        """
        ...
    
    def calculate_agent_centrality(self, agent_id: str) -> float:
        """
        Calculate centrality for an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Centrality score
        """
        ...


# ===== Certificate System Interfaces =====

class CertificateStatus(Enum):
    """Certificate status values."""
    ACTIVE = "active"
    USED = "used"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class CertificateAction:
    """Record of action taken on a certificate."""
    timestamp: str
    action: str  # "issued", "used", "transferred", "expired", "revoked"
    value: float  # Certificate value at time of action
    details: Optional[Dict[str, Any]] = None


@dataclass
class Certificate:
    """Import certificate representation."""
    id: str
    owner: str
    value: float
    issued_date: str
    expiry_date: str
    issuing_authority: str
    status: CertificateStatus
    history: List[CertificateAction]


class ICertificateSystem(Protocol):
    """Protocol for certificate system implementations."""
    
    def issue_certificate(
        self,
        owner: str,
        value: float,
        duration_days: int = 180
    ) -> Certificate:
        """
        Issue a new certificate.
        
        Args:
            owner: Certificate owner
            value: Certificate value
            duration_days: Certificate validity duration in days
            
        Returns:
            Issued certificate
        """
        ...
    
    def verify_certificate(self, certificate_id: str) -> bool:
        """
        Verify a certificate is valid.
        
        Args:
            certificate_id: Certificate ID
            
        Returns:
            True if certificate is valid, False otherwise
        """
        ...
    
    def transfer_certificate(
        self,
        certificate_id: str,
        new_owner: str
    ) -> Certificate:
        """
        Transfer a certificate to a new owner.
        
        Args:
            certificate_id: Certificate ID
            new_owner: New owner ID
            
        Returns:
            Updated certificate
        """
        ...
    
    def use_certificate(
        self,
        certificate_id: str,
        amount: float,
        transaction_id: Optional[str] = None
    ) -> bool:
        """
        Use some or all of a certificate's value.
        
        Args:
            certificate_id: Certificate ID
            amount: Amount to use
            transaction_id: Associated transaction ID
            
        Returns:
            True if certificate was used successfully, False otherwise
        """
        ...
    
    def get_certificate(self, certificate_id: str) -> Optional[Certificate]:
        """
        Get a certificate by ID.
        
        Args:
            certificate_id: Certificate ID
            
        Returns:
            Certificate if found, None otherwise
        """
        ...
    
    def get_certificates_by_owner(self, owner: str) -> List[Certificate]:
        """
        Get all certificates for an owner.
        
        Args:
            owner: Owner ID
            
        Returns:
            List of certificates
        """
        ...
    
    def get_available_value(self, owner: str) -> float:
        """
        Get total available certificate value for an owner.
        
        Args:
            owner: Owner ID
            
        Returns:
            Total available value
        """
        ...


# ===== Agency Interfaces =====

class PolicyType(Enum):
    """Policy types supported by the system."""
    IMPORT_CERTIFICATE = "import_certificate"
    TARIFF = "tariff"
    REGULATORY = "regulatory"
    SUBSIDY = "subsidy"


class PolicyStatus(Enum):
    """Policy status values."""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


@dataclass
class PolicyHistoryEntry:
    """Entry in a policy's legislative history."""
    timestamp: str
    from_status: PolicyStatus
    to_status: PolicyStatus
    comment: str


@dataclass
class GovernancePolicy:
    """Trade policy within the governance framework."""
    policy_id: str
    title: str
    description: str
    policy_type: PolicyType
    status: PolicyStatus
    version: str
    created_at: str
    updated_at: str
    parameters: Dict[str, Any]
    legislative_history: List[PolicyHistoryEntry]


class ProgramStatus(Enum):
    """Program status values."""
    SETUP = "setup"
    ACTIVE = "active"
    COMPLETED = "completed"
    SUSPENDED = "suspended"


@dataclass
class ProgramMetrics:
    """Metrics for a trade program."""
    trade_flows: int
    total_volume: float
    balance: float
    war_score: float
    start_date: Optional[str]
    last_updated: Optional[str]
    custom_metrics: Dict[str, Any] = None


@dataclass
class ProgramActivity:
    """Program implementation for a trade initiative."""
    program_id: str
    title: str
    description: str
    country_a: str
    country_b: str
    created_at: str
    updated_at: str
    status: ProgramStatus
    metrics: ProgramMetrics
    activity_log: List[Dict[str, Any]]


class ModelType(Enum):
    """Economic model types."""
    GENERAL_EQUILIBRIUM = "general_equilibrium"
    ECONOMETRIC = "econometric"
    INPUT_OUTPUT = "input_output"
    SECTOR_SPECIFIC = "sector_specific"


@dataclass
class EconomicModel:
    """Economic model for trade policy analysis."""
    model_id: str
    title: str
    description: str
    model_type: ModelType
    version: str
    created_at: str
    updated_at: str
    parameters: Dict[str, Any]


class AssessmentStatus(Enum):
    """Assessment status values."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AssessmentMetrics:
    """Metrics for a trade impact assessment."""
    gdp_impact: float
    job_creation: int
    trade_balance_effect: float
    confidence_level: float
    custom_metrics: Dict[str, Any] = None


@dataclass
class TradeImpactAssessment:
    """Economic impact assessment for a trade deal."""
    assessment_id: str
    deal_id: str
    title: str
    model_id: str
    created_at: str
    status: AssessmentStatus
    results: Dict[str, Any]
    metrics: AssessmentMetrics


class IUSTDAAgent(Protocol):
    """Protocol for USTDA agent implementation."""
    
    @property
    def agent_id(self) -> str:
        """Get agent ID."""
        ...
    
    @property
    def capabilities(self) -> List[str]:
        """Get agent capabilities."""
        ...
    
    def create_policy(self, policy_data: Dict[str, Any]) -> GovernancePolicy:
        """
        Create a new policy.
        
        Args:
            policy_data: Policy data
            
        Returns:
            Created policy
        """
        ...
    
    def update_policy(self, policy_id: str, updates: Dict[str, Any]) -> GovernancePolicy:
        """
        Update an existing policy.
        
        Args:
            policy_id: Policy ID
            updates: Updates to apply
            
        Returns:
            Updated policy
        """
        ...
    
    def get_policy(self, policy_id: str) -> Optional[GovernancePolicy]:
        """
        Get a policy by ID.
        
        Args:
            policy_id: Policy ID
            
        Returns:
            Policy if found, None otherwise
        """
        ...
    
    def list_policies(self, filters: Dict[str, Any] = None) -> List[GovernancePolicy]:
        """
        List policies matching the specified filters.
        
        Args:
            filters: Filters to apply
            
        Returns:
            List of matching policies
        """
        ...
    
    def create_program(self, program_data: Dict[str, Any]) -> ProgramActivity:
        """
        Create a new program.
        
        Args:
            program_data: Program data
            
        Returns:
            Created program
        """
        ...
    
    def update_program(self, program_id: str, updates: Dict[str, Any]) -> ProgramActivity:
        """
        Update an existing program.
        
        Args:
            program_id: Program ID
            updates: Updates to apply
            
        Returns:
            Updated program
        """
        ...
    
    def get_program(self, program_id: str) -> Optional[ProgramActivity]:
        """
        Get a program by ID.
        
        Args:
            program_id: Program ID
            
        Returns:
            Program if found, None otherwise
        """
        ...
    
    def list_programs(self, filters: Dict[str, Any] = None) -> List[ProgramActivity]:
        """
        List programs matching the specified filters.
        
        Args:
            filters: Filters to apply
            
        Returns:
            List of matching programs
        """
        ...
    
    def create_trade_deal(
        self,
        title: str,
        description: str,
        country_a: str,
        country_b: str
    ) -> Dict[str, Any]:
        """
        Create a new trade deal between countries.
        
        Args:
            title: Deal title
            description: Deal description
            country_a: First country
            country_b: Second country
            
        Returns:
            Dictionary with deal details
        """
        ...
    
    def issue_import_certificate(self, owner: str, value: float) -> Certificate:
        """
        Issue an import certificate to an entity.
        
        Args:
            owner: Entity receiving the certificate
            value: Certificate value
            
        Returns:
            Created ImportCertificate
        """
        ...
    
    def get_moneyball_opportunities(self) -> List[Dict[str, Any]]:
        """
        Generate Moneyball-style opportunities.
        
        Returns:
            List of undervalued opportunities
        """
        ...


class IUSITCAgent(Protocol):
    """Protocol for USITC agent implementation."""
    
    @property
    def agent_id(self) -> str:
        """Get agent ID."""
        ...
    
    @property
    def capabilities(self) -> List[str]:
        """Get agent capabilities."""
        ...
    
    def create_model(self, model_data: Dict[str, Any]) -> EconomicModel:
        """
        Create a new economic model.
        
        Args:
            model_data: Model data
            
        Returns:
            Created model
        """
        ...
    
    def update_model(self, model_id: str, updates: Dict[str, Any]) -> EconomicModel:
        """
        Update an existing model.
        
        Args:
            model_id: Model ID
            updates: Updates to apply
            
        Returns:
            Updated model
        """
        ...
    
    def get_model(self, model_id: str) -> Optional[EconomicModel]:
        """
        Get a model by ID.
        
        Args:
            model_id: Model ID
            
        Returns:
            Model if found, None otherwise
        """
        ...
    
    def list_models(self, filters: Dict[str, Any] = None) -> List[EconomicModel]:
        """
        List models matching the specified filters.
        
        Args:
            filters: Filters to apply
            
        Returns:
            List of matching models
        """
        ...
    
    def run_model(self, model_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run an economic model with given inputs.
        
        Args:
            model_id: Model ID
            inputs: Model inputs
            
        Returns:
            Model outputs
        """
        ...
    
    def create_assessment(self, assessment_data: Dict[str, Any]) -> TradeImpactAssessment:
        """
        Create a new trade impact assessment.
        
        Args:
            assessment_data: Assessment data
            
        Returns:
            Created assessment
        """
        ...
    
    def get_assessment(self, assessment_id: str) -> Optional[TradeImpactAssessment]:
        """
        Get an assessment by ID.
        
        Args:
            assessment_id: Assessment ID
            
        Returns:
            Assessment if found, None otherwise
        """
        ...
    
    def list_assessments(self, filters: Dict[str, Any] = None) -> List[TradeImpactAssessment]:
        """
        List assessments matching the specified filters.
        
        Args:
            filters: Filters to apply
            
        Returns:
            List of matching assessments
        """
        ...
    
    def analyze_trade_program(self, program_id: str) -> Dict[str, Any]:
        """
        Analyze economic impacts of a trade program.
        
        Args:
            program_id: Program ID
            
        Returns:
            Dictionary with analysis results
        """
        ...
    
    def optimize_trade_policy(
        self,
        program_id: str,
        optimization_goal: str
    ) -> Dict[str, Any]:
        """
        Optimize trade policy parameters for a specific goal.
        
        Args:
            program_id: Program ID
            optimization_goal: Goal to optimize for
            
        Returns:
            Dictionary with optimized policy parameters
        """
        ...


# ===== Integration Interfaces =====

class IAgencyNetworkExtension(Protocol):
    """Protocol for agency network extension implementation."""
    
    @property
    def integrator(self):
        """Get market network integrator."""
        ...
    
    @property
    def ustda_agent(self) -> IUSTDAAgent:
        """Get USTDA agent."""
        ...
    
    @property
    def usitc_agent(self) -> IUSITCAgent:
        """Get USITC agent."""
        ...
    
    async def register_agency(
        self,
        agency_id: str,
        agency_type: str,
        capabilities: List[str],
        value_dimensions: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Register a government agency with the market network.
        
        Args:
            agency_id: ID of the agency
            agency_type: Type of agency
            capabilities: List of agency capabilities
            value_dimensions: Value dimension weights
            
        Returns:
            Registration result
        """
        ...
    
    async def apply_policy_to_market(
        self,
        policy_id: str,
        market_id: str
    ) -> Dict[str, Any]:
        """
        Apply a government policy to a specific market.
        
        Args:
            policy_id: ID of the policy to apply
            market_id: ID of the market to apply the policy to
            
        Returns:
            Policy application results
        """
        ...
    
    async def evaluate_deal_economic_impact(
        self,
        deal_id: str,
        model_id: str
    ) -> Dict[str, Any]:
        """
        Evaluate the economic impact of a deal using an economic model.
        
        Args:
            deal_id: ID of the deal to evaluate
            model_id: ID of the economic model to use
            
        Returns:
            Economic impact assessment
        """
        ...
    
    async def calculate_win_win_status(
        self,
        deal_id: str,
        apply_adjustments: bool = False
    ) -> Dict[str, Any]:
        """
        Apply the win-win calculation framework to a deal.
        
        Args:
            deal_id: ID of the deal to evaluate
            apply_adjustments: Whether to apply automatic adjustments if not win-win
            
        Returns:
            Win-win calculation results
        """
        ...
    
    async def create_policy_based_deal(
        self,
        agency_id: str,
        problem_statement: str,
        stakeholder_ids: List[str],
        policy_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a deal based on agency policy priorities.
        
        Args:
            agency_id: ID of the agency creating the deal
            problem_statement: Problem statement for the deal
            stakeholder_ids: List of stakeholder IDs to include
            policy_id: Optional policy ID to apply to the deal
            
        Returns:
            Deal creation results
        """
        ...


# ===== Type Variables for Generic Functions =====

T = TypeVar('T')
U = TypeVar('U')


# ===== Result Types =====

@dataclass
class Result(Generic[T]):
    """Generic result type with success/failure status."""
    success: bool
    value: Optional[T] = None
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None