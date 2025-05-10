"""
trade_base.py

Base classes and data structures for a Moneyball-style dynamic trade system.
Implements the core abstractions for trade deal analysis and management.

MONEYBALL FINANCING: INTERNATIONAL DEVELOPMENT

The TradeBase module defines core abstractions for international development financing through:

1. Import Certificates (IC): 
   - Exporters receive tradable certificates based on export volume
   - Certificates can be traded on secondary markets, creating a price discovery mechanism
   - Certificates can fund development projects in exporting countries, especially in undervalued sectors

2. Dynamic Tariff Adjustment:
   - Progressive tariff structure linked to development goals
   - Tariff revenues can be earmarked for development projects in both countries
   - Targets specific industrial sectors for growth with temporary protections

Example flow for infrastructure financing:
- Country A exports $10M of technology to Country B, receives $10M in ICs
- Country B charges 5% import tariff, generating $500K in revenue
- $250K of tariff revenue funds clean energy development in Country B
- $250K funds technology training programs in both countries
- Country A can trade ICs on secondary market at dynamic price, using proceeds to fund broadband infrastructure

This implementation allows for deal chains:
   Trade Deal 1: USA exports tech to Ghana, receives ICs
   Trade Deal 2: Ghana uses ICs to import construction equipment from Brazil
   Trade Deal 3: Brazil uses ICs to import agricultural products from USA
   
The system creates a closed loop where all countries receive economic benefits.
"""

import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class DealSide(Enum):
    """Represents the two sides in a trade transaction: government or civil/private sector."""
    GOV = "GOV"  # Government entities (federal agencies, regulatory bodies)
    CIV = "CIV"  # Civil entities (private businesses, individuals)


@dataclass
class TradeFlow:
    """
    Represents a single transaction flow in a micro-trade deal:
    - volume: monetary value or quantity of the trade
    - from_side: which side initiated (GOV or CIV)
    - to_side: which side is receiving (GOV or CIV)
    - sector: economic sector for this trade flow
    - timestamp: when the transaction occurred
    """
    volume: float
    from_side: DealSide
    to_side: DealSide
    sector: str = "general"
    timestamp: Optional[str] = None
    description: Optional[str] = None
    

@dataclass
class ComplianceCheck:
    """
    Stores the compliance state and relevant metrics for trade regulation.
    Informs dynamic tariff adjustments and Gov/Civ win-win calculations.
    """
    is_compliant: bool
    compliance_score: float  # 0-1 scale
    reason: str = ""
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ImportCertificate:
    """
    Represents a tradable import certificate based on Warren Buffett's proposal.
    Each certificate is issued to exporters and must be purchased by importers.
    
    Acts as a financial instrument to:
    1. Balance trade by requiring imports to be matched by exports
    2. Create funding for development through certificate trading
    3. Enable multi-country deal chains through certificate transfers
    """
    id: str
    owner: str  # entity holding the certificate
    value: float  # monetary amount of imports it allows
    issued_date: str
    expiry_date: str
    issuing_authority: str = "USTDA"
    status: str = "active"  # active, pending, consumed, expired
    history: List[Dict] = field(default_factory=list)
    
    # Development financing metadata
    earmark_percentage: float = 0.0  # % earmarked for development projects
    project_allocation: Dict[str, float] = field(default_factory=dict)  # Project allocations


@dataclass
class DevelopmentFund:
    """
    Represents a fund for development projects created from trade activities.
    Links trade flows directly to development outcomes.
    """
    fund_id: str
    country: str
    balance: float = 0.0
    created_date: str = None
    
    # Sources of funding
    tariff_revenue: float = 0.0
    certificate_revenue: float = 0.0
    efficiency_gains: float = 0.0
    
    # Allocation by sector
    allocations: Dict[str, float] = field(default_factory=dict)
    
    # Project linkages
    projects: List[Dict] = field(default_factory=list)


class TradeDealBase(abc.ABC):
    """
    Abstract base class defining the interface for a Moneyball-style trade deal system.
    Implements dynamic tariffs, import certificates, and Gov/Civ layers with
    specific support for financing international development and domestic programs.
    """

    def __init__(
        self,
        deal_id: str,
        country_a: str,
        country_b: str,
        base_tariff: float = 0.05,
        target_balance: float = 0.0,
    ):
        """
        Initialize a trade deal between two countries.
        
        Args:
            deal_id: Unique identifier for the trade deal
            country_a: First country in the deal (e.g., USA)
            country_b: Second country in the deal (e.g., China)
            base_tariff: Starting tariff rate
            target_balance: Desired trade balance corridor (0.0 for perfect balance)
        """
        self.deal_id = deal_id
        self.country_a = country_a
        self.country_b = country_b
        self.base_tariff = base_tariff
        self.target_balance = target_balance

        # Trade metrics
        self.current_balance = 0.0  # positive means A exports > imports, negative means A imports > exports
        self.tariff_rate = base_tariff
        self.total_volume = 0.0
        self.flow_history: List[TradeFlow] = []
        
        # Import certificate tracking
        self.import_certificates: Dict[str, List[ImportCertificate]] = {
            country_a: [],
            country_b: []
        }
        
        # Country-specific metrics
        self.metrics = {
            country_a: {"exports": 0.0, "imports": 0.0, "tariff_revenue": 0.0, "certificate_value": 0.0},
            country_b: {"exports": 0.0, "imports": 0.0, "tariff_revenue": 0.0, "certificate_value": 0.0}
        }
        
        # Sector metrics for Moneyball-style analysis
        self.sector_performance: Dict[str, Dict[str, float]] = {}
        
        # Development fund tracking
        self.development_funds: Dict[str, DevelopmentFund] = {
            country_a: DevelopmentFund(fund_id=f"DEV-{country_a}-{deal_id}", country=country_a),
            country_b: DevelopmentFund(fund_id=f"DEV-{country_b}-{deal_id}", country=country_b)
        }
        
        # Efficiency gain tracking for domestic program funding
        self.efficiency_gains: Dict[str, float] = {
            country_a: 0.0,
            country_b: 0.0
        }
        self.sector_efficiency_gains: Dict[str, float] = {}

    @abc.abstractmethod
    def record_trade_flow(self, flow: TradeFlow) -> Dict:
        """
        Records a trade flow transaction and updates metrics.
        
        Args:
            flow: TradeFlow object with transaction details
            
        Returns:
            Dict containing updated metrics and win-win calculation
        """
        pass

    @abc.abstractmethod
    def check_and_update_tariff(self) -> Tuple[float, str]:
        """
        Dynamically adjusts tariffs based on trade balance and compliance checks.
        
        Returns:
            Tuple of (new_tariff_rate, reason)
        """
        pass

    @abc.abstractmethod
    def issue_import_certificate(self, owner: str, value: float) -> ImportCertificate:
        """
        Issues a new import certificate to an exporter based on export volume.
        
        Args:
            owner: Entity receiving the certificate
            value: Monetary value of the certificate
            
        Returns:
            The created ImportCertificate object
        """
        pass

    @abc.abstractmethod
    def consume_import_certificate(self, owner: str, value: float) -> bool:
        """
        Consumes import certificates for imports.
        
        Args:
            owner: Entity using certificates
            value: Value of imports to be certified
            
        Returns:
            True if successful, False if insufficient certificates
        """
        pass

    @abc.abstractmethod
    def run_compliance_check(self, country: str = None) -> ComplianceCheck:
        """
        Evaluates compliance with trade agreement terms.
        
        Args:
            country: Optional country to check specifically
            
        Returns:
            ComplianceCheck object with evaluation results
        """
        pass
    
    @abc.abstractmethod
    def calculate_trade_war_score(self) -> Dict[str, float]:
        """
        Calculates a WAR-like (Wins Above Replacement) metric for the trade deal.
        This composite score helps evaluate deal effectiveness vs. baseline.
        
        Returns:
            Dict with scores by country and deal-wide metrics
        """
        pass
    
    @abc.abstractmethod
    def simulate_scenario(self, scenario: Dict) -> Dict:
        """
        Runs a what-if analysis for different scenarios (currency changes, 
        demand shocks, etc.) without changing actual deal state.
        
        Args:
            scenario: Parameters defining the scenario
            
        Returns:
            Dict with projected outcomes
        """
        pass
    
    @abc.abstractmethod
    def calculate_efficiency_gain(self, flow: TradeFlow) -> float:
        """
        Calculate efficiency gain from optimized trade flow that can fund domestic programs.
        
        Args:
            flow: The trade flow being processed
            
        Returns:
            Float value representing monetized efficiency gain
        """
        pass
    
    @abc.abstractmethod
    def allocate_domestic_funding(self, country: str) -> Dict[str, float]:
        """
        Allocates trade efficiency gains to domestic programs.
        
        Args:
            country: Country code for allocation
            
        Returns:
            Dict mapping program categories to funding amounts
        """
        pass
    
    @abc.abstractmethod
    def get_development_fund_status(self, country: str) -> Dict:
        """
        Gets the current status of a country's development fund.
        
        Args:
            country: Country code
            
        Returns:
            Dict with development fund details and allocations
        """
        pass