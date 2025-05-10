"""
trade_agent.py - Simplified version for HMS-A2A integration.

Implementation of a dynamic trade agent system for Moneyball-style trade analysis.
Provides concrete implementation of trade deal logic, import certificates, 
and dynamic tariff adjustments.
"""

import uuid
import random
import datetime
from typing import Dict, List, Tuple, Optional, Any
import math

from trade_base import (
    TradeDealBase,
    TradeFlow,
    DealSide,
    ComplianceCheck,
    ImportCertificate,
    DevelopmentFund
)


class DynamicTradeAgent(TradeDealBase):
    """
    A concrete implementation of a data-driven trade deal agent that uses:
    - Dynamic tariffs adjusted for trade balance
    - Import certificates (Warren Buffett model)
    - Gov/Civ 'win-win' framework to ensure balanced benefits
    - Moneyball-style metrics to identify undervalued opportunities
    - International development financing mechanisms
    - Domestic program funding through efficiency gains
    """

    def __init__(
        self,
        deal_id: str,
        country_a: str,
        country_b: str,
        base_tariff: float = 0.05,
        target_balance: float = 0.0,
        max_tariff: float = 0.30,
        min_tariff: float = 0.0,
        compliance_threshold: float = 0.75,
        certificate_expiry_days: int = 180,
        development_earmark: float = 0.25,  # 25% of tariff revenue earmarked for development
        domestic_earmark: float = 0.30,     # 30% of efficiency gains for domestic programs
    ):
        """
        Initialize the dynamic trade agent with trade parameters.
        
        Args:
            deal_id: Unique identifier for the deal
            country_a: First country (usually issuing country)
            country_b: Second country (partner country)
            base_tariff: Initial tariff rate
            target_balance: Target trade balance (0.0 for perfect balance)
            max_tariff: Upper limit for tariff adjustments
            min_tariff: Lower limit for tariff adjustments
            compliance_threshold: Minimum score to avoid compliance penalties
            certificate_expiry_days: Days until import certificates expire
            development_earmark: Percentage of tariff revenue earmarked for development
            domestic_earmark: Percentage of efficiency gains for domestic programs
        """
        super().__init__(deal_id, country_a, country_b, base_tariff, target_balance)
        
        self.max_tariff = max_tariff
        self.min_tariff = min_tariff
        self.compliance_threshold = compliance_threshold
        self.certificate_expiry_days = certificate_expiry_days
        self.development_earmark = development_earmark
        self.domestic_earmark = domestic_earmark
        
        # Additional Moneyball metrics
        self.undervalued_sectors: Dict[str, float] = {}
        self.sector_growth_rates: Dict[str, float] = {}
        self.trade_war_baseline = 0.0
        
        # Win-win tracking
        self.win_win_balance = {
            country_a: {"gov": 0.0, "civ": 0.0},
            country_b: {"gov": 0.0, "civ": 0.0}
        }
        
        # Configuration for smart contracts
        self.smart_contract_rules = {
            "tariff_adjustment_frequency": "daily",
            "certificate_issuance_ratio": 1.0,  # 1:1 export:import ratio
            "win_win_correction_threshold": 0.2  # When imbalance exceeds 20%
        }
        
        # Development project tracking
        self.development_projects: Dict[str, Dict] = {}
        
        # Domestic program tracking
        self.domestic_programs: Dict[str, Dict[str, Dict]] = {
            country_a: {
                "education": {"budget": 100000, "trade_funding": 0.0},
                "healthcare": {"budget": 150000, "trade_funding": 0.0},
                "infrastructure": {"budget": 200000, "trade_funding": 0.0},
                "research": {"budget": 80000, "trade_funding": 0.0}
            },
            country_b: {
                "education": {"budget": 90000, "trade_funding": 0.0},
                "healthcare": {"budget": 130000, "trade_funding": 0.0},
                "infrastructure": {"budget": 180000, "trade_funding": 0.0},
                "research": {"budget": 70000, "trade_funding": 0.0}
            }
        }
        
        # Deal chains for Nth degree trading
        self.connected_deals: List[Dict] = []

    def record_trade_flow(self, flow: TradeFlow) -> Dict:
        """
        Records a trade flow and updates all relevant metrics.
        Implements Gov/Civ win-win logic to balance benefits.
        
        Args:
            flow: TradeFlow object with transaction details
            
        Returns:
            Dict with updated metrics and win-win adjustments
        """
        # Set timestamp if not provided
        if not flow.timestamp:
            flow.timestamp = datetime.datetime.now().isoformat()
        
        # Calculate applicable tariff for this flow
        tariff_cost = flow.volume * self.tariff_rate
        
        # Determine exporter/importer based on flow direction
        if flow.from_side == DealSide.GOV and flow.to_side == DealSide.CIV:
            # Gov to Civ flow
            exporter = self.country_a
            importer = self.country_b
            
            # Update win-win metrics
            self.win_win_balance[self.country_a]["gov"] += flow.volume * 0.1  # Gov benefit from export
            self.win_win_balance[self.country_b]["civ"] += flow.volume * 0.08  # Civ benefit from import
            
        elif flow.from_side == DealSide.CIV and flow.to_side == DealSide.GOV:
            # Civ to Gov flow
            exporter = self.country_b
            importer = self.country_a
            
            # Update win-win metrics
            self.win_win_balance[self.country_b]["civ"] += flow.volume * 0.1  # Civ benefit from export
            self.win_win_balance[self.country_a]["gov"] += flow.volume * 0.08  # Gov benefit from import
            
        elif flow.from_side == DealSide.GOV and flow.to_side == DealSide.GOV:
            # Gov to Gov flow (government procurement, etc.)
            exporter = self.country_a
            importer = self.country_b
            
            # Update win-win metrics
            self.win_win_balance[self.country_a]["gov"] += flow.volume * 0.1
            self.win_win_balance[self.country_b]["gov"] += flow.volume * 0.09
            
        else:  # CIV to CIV
            # Private sector trade between countries
            exporter = self.country_b
            importer = self.country_a
            
            # Update win-win metrics
            self.win_win_balance[self.country_b]["civ"] += flow.volume * 0.1
            self.win_win_balance[self.country_a]["civ"] += flow.volume * 0.09

        # Update country metrics
        self.metrics[exporter]["exports"] += flow.volume
        self.metrics[importer]["imports"] += flow.volume
        self.metrics[importer]["tariff_revenue"] += tariff_cost
        
        # Update trade balance
        if exporter == self.country_a:
            self.current_balance += flow.volume  # Positive: country_a exports more
        else:
            self.current_balance -= flow.volume  # Negative: country_a imports more
        
        # Update total volume
        self.total_volume += flow.volume
        
        # Update sector performance 
        if flow.sector not in self.sector_performance:
            self.sector_performance[flow.sector] = {
                "volume": 0.0,
                "count": 0,
                "growth_rate": 0.0,
                "value_index": 0.0
            }
        
        self.sector_performance[flow.sector]["volume"] += flow.volume
        self.sector_performance[flow.sector]["count"] += 1
        
        # Calculate Moneyball value metrics - is this sector undervalued?
        if flow.sector not in self.undervalued_sectors:
            # Simplified calculation - in real system would use historical data and ML
            growth_potential = random.uniform(0.8, 1.5)  # Random for demo
            market_share = self.sector_performance[flow.sector]["volume"] / max(self.total_volume, 1)
            value_index = growth_potential / max(market_share, 0.01)
            
            self.undervalued_sectors[flow.sector] = value_index
            self.sector_performance[flow.sector]["value_index"] = value_index
            
        # Calculate efficiency gain for domestic program funding
        efficiency_gain = self.calculate_efficiency_gain(flow)
        
        # Allocate tariff revenue to development fund
        development_allocation = tariff_cost * self.development_earmark
        self.development_funds[importer].tariff_revenue += development_allocation
        self.development_funds[importer].balance += development_allocation
        
        # Allocate efficiency gains to domestic programs
        domestic_allocation = efficiency_gain * self.domestic_earmark
        domestic_funding = self.allocate_domestic_funding(importer, domestic_allocation)
        
        # Store flow history
        self.flow_history.append(flow)
        
        # Trigger tariff update
        new_tariff, reason = self.check_and_update_tariff()
        
        # Check if win-win is balanced, apply corrections if needed
        win_win_adjustments = self._check_win_win_balance()
        
        # Return comprehensive update
        return {
            "flow_recorded": True,
            "exporter": exporter,
            "importer": importer,
            "tariff_applied": self.tariff_rate,
            "tariff_revenue": tariff_cost,
            "new_balance": self.current_balance,
            "new_tariff_rate": new_tariff,
            "tariff_adjustment_reason": reason,
            "win_win_metrics": self.win_win_balance,
            "win_win_adjustments": win_win_adjustments,
            "sector_performance": self.sector_performance.get(flow.sector),
            "development_allocation": development_allocation,
            "efficiency_gain": efficiency_gain,
            "domestic_funding": domestic_funding
        }

    def check_and_update_tariff(self) -> Tuple[float, str]:
        """
        Dynamically adjusts tariff rates based on current trade balance,
        compliance checks, sector performance, and win-win metrics.
        
        Returns:
            Tuple of (new_tariff_rate, reason_for_change)
        """
        # Start with current rate
        old_rate = self.tariff_rate
        
        # Calculate balance divergence from target
        balance_gap = self.current_balance - self.target_balance
        
        # Run compliance check
        compliance = self.run_compliance_check()
        compliance_factor = 1.0
        
        # Apply compliance penalty if below threshold
        if not compliance.is_compliant or compliance.compliance_score < self.compliance_threshold:
            compliance_factor = 1.2  # 20% penalty for non-compliance
            reason = f"Non-compliance penalty: score {compliance.compliance_score:.2f} < threshold {self.compliance_threshold}"
        else:
            reason = "Standard adjustment based on trade balance"
        
        # Apply balance-based adjustments
        if balance_gap > 0:
            # Country A exporting more than target - lower tariff to encourage imports
            adjustment = min(0.01, abs(balance_gap) / 1000)  # Scale by gap size, max 1% change
            self.tariff_rate -= adjustment
        else:
            # Country A importing more than target - raise tariff to reduce imports
            adjustment = min(0.01, abs(balance_gap) / 1000)  # Scale by gap size, max 1% change
            self.tariff_rate += adjustment
        
        # Apply compliance factor
        self.tariff_rate *= compliance_factor
        
        # Apply win-win correction if needed
        win_win_balance = self._check_win_win_balance()
        if win_win_balance["needs_correction"]:
            self.tariff_rate *= win_win_balance["tariff_multiplier"]
            reason += f"; Win-win correction: {win_win_balance['description']}"
        
        # Bound within min and max limits
        self.tariff_rate = max(self.min_tariff, min(self.tariff_rate, self.max_tariff))
        
        # If no significant change, keep reason simple
        if abs(self.tariff_rate - old_rate) < 0.001:
            reason = "No significant change needed"
            
        return self.tariff_rate, reason

    def issue_import_certificate(self, owner: str, value: float, development_earmark: float = 0.0) -> ImportCertificate:
        """
        Issues an import certificate to an exporter, with optional development earmark.
        Implements Warren Buffett's proposal for trade balance with development financing extension.
        
        Args:
            owner: Entity receiving the certificate (must be country in deal)
            value: Monetary value of exports to be certified
            development_earmark: Percentage of certificate value earmarked for development projects
            
        Returns:
            Created ImportCertificate object
        """
        # Validate owner is part of the deal
        if owner not in [self.country_a, self.country_b]:
            raise ValueError(f"Certificate owner must be deal participant: {self.country_a} or {self.country_b}")
        
        # Calculate expiration date
        today = datetime.datetime.now()
        expiry = today + datetime.timedelta(days=self.certificate_expiry_days)
        
        # Create certificate with unique ID
        cert_id = f"IC-{uuid.uuid4().hex[:8]}-{owner}-{int(value):08d}"
        
        # Calculate development earmark amount
        earmark_amount = value * (development_earmark / 100.0) if development_earmark > 0 else 0.0
        
        cert = ImportCertificate(
            id=cert_id,
            owner=owner,
            value=value,
            issued_date=today.isoformat(),
            expiry_date=expiry.isoformat(),
            issuing_authority="USTDA",
            status="active",
            history=[{
                "timestamp": today.isoformat(),
                "action": "issued",
                "value": value
            }],
            earmark_percentage=development_earmark,
            project_allocation={}
        )
        
        # Store in appropriate country's certificate list
        self.import_certificates[owner].append(cert)
        
        # Update metrics
        self.metrics[owner]["certificate_value"] += value
        
        # If there's an earmark, allocate to development fund
        if earmark_amount > 0:
            self.development_funds[owner].certificate_revenue += earmark_amount
            self.development_funds[owner].balance += earmark_amount
            
        return cert

    def consume_import_certificate(self, owner: str, value: float) -> bool:
        """
        Consumes (uses) import certificates for imports.
        
        Args:
            owner: Entity using certificates for imports
            value: Value of imports to be covered by certificates
            
        Returns:
            True if successful (enough certificates available), False otherwise
        """
        # Validate owner
        if owner not in self.import_certificates:
            return False
        
        # Calculate total available certificate value (excluding expired)
        now = datetime.datetime.now().isoformat()
        active_certificates = [
            cert for cert in self.import_certificates[owner]
            if cert.status == "active" and cert.expiry_date > now
        ]
        
        total_available = sum(cert.value for cert in active_certificates)
        
        # Check if enough certificate value
        if total_available < value:
            return False
        
        # Consume certificates starting with oldest
        remaining = value
        active_certificates.sort(key=lambda c: c.issued_date)  # Sort by age
        
        for cert in active_certificates:
            if cert.value <= remaining:
                # Use entire certificate
                remaining -= cert.value
                cert.status = "consumed"
                cert.history.append({
                    "timestamp": now,
                    "action": "consumed",
                    "value": cert.value
                })
                cert.value = 0
            else:
                # Use part of certificate
                cert.history.append({
                    "timestamp": now,
                    "action": "partially_consumed",
                    "value": remaining
                })
                cert.value -= remaining
                remaining = 0
            
            if remaining <= 0:
                break
        
        # Clean up consumed certificates
        self.import_certificates[owner] = [
            cert for cert in self.import_certificates[owner]
            if cert.value > 0 and cert.status != "consumed"
        ]
        
        # Update metrics
        self.metrics[owner]["certificate_value"] -= value
        
        return True

    def run_compliance_check(self, country: str = None) -> ComplianceCheck:
        """
        Evaluates compliance with trade deal terms and regulations.
        In a real system, this would check labor standards, environmental
        compliance, data sharing, etc.
        
        Args:
            country: Optional specific country to check, or both if None
            
        Returns:
            ComplianceCheck object with evaluation results
        """
        # This is a placeholder implementation
        # In a real system, would use actual compliance data
        
        # Basic metrics to check (randomly generated for demo)
        metrics = {
            "labor_standards": random.uniform(0.6, 1.0),
            "environmental_compliance": random.uniform(0.7, 1.0),
            "ip_protection": random.uniform(0.5, 0.95),
            "data_governance": random.uniform(0.6, 0.9),
            "financial_transparency": random.uniform(0.7, 0.95)
        }
        
        # If country specified, add country-specific metrics
        if country == self.country_a:
            metrics["country_specific"] = random.uniform(0.7, 0.95)
        elif country == self.country_b:
            metrics["country_specific"] = random.uniform(0.6, 0.9)
        
        # Calculate overall score (weighted average)
        weights = {
            "labor_standards": 0.2,
            "environmental_compliance": 0.2,
            "ip_protection": 0.25,
            "data_governance": 0.15,
            "financial_transparency": 0.2,
            "country_specific": 0.3  # Higher weight if present
        }
        
        # Calculate weighted score for available metrics
        total_weight = sum(weights[m] for m in metrics.keys() if m in weights)
        overall_score = sum(metrics[m] * weights[m] for m in metrics.keys() if m in weights) / total_weight
        
        # Determine compliance status
        is_compliant = overall_score >= self.compliance_threshold
        reason = f"Overall compliance score: {overall_score:.2f}"
        
        if not is_compliant:
            # Identify biggest issues
            problem_areas = [m for m in metrics if metrics[m] < 0.7]
            if problem_areas:
                reason += f" | Issues in: {', '.join(problem_areas)}"
        
        return ComplianceCheck(
            is_compliant=is_compliant,
            compliance_score=overall_score,
            reason=reason,
            metrics=metrics
        )
    
    def calculate_trade_war_score(self) -> Dict[str, float]:
        """
        Calculates a baseball WAR-like (Wins Above Replacement) metric
        for this trade deal, evaluating its performance vs. baseline.
        
        Returns:
            Dict with detailed metrics and WAR score
        """
        # Simplified calculation instead of full implementation
        
        # Balance ratio (how close to target balance)
        balance_ratio = 1.0 - min(abs(self.current_balance) / max(self.total_volume, 1), 1.0)
        
        # Volume ratio (growth in trade volume)
        baseline_annual_volume = 1000000  # Placeholder value
        volume_ratio = min(self.total_volume / baseline_annual_volume, 3.0)
        
        # Sector diversity (unique sectors / baseline)
        sector_diversity = len(self.sector_performance) / 10  # Normalize to baseline of 10
        
        # Compliance and governance
        compliance = self.run_compliance_check()
        compliance_score = compliance.compliance_score
        
        # Win-win balance
        win_win_balance = self._calculate_win_win_score()
        
        # Development financing factor
        dev_funding_a = self.development_funds[self.country_a].balance
        dev_funding_b = self.development_funds[self.country_b].balance
        dev_funding_ratio = min((dev_funding_a + dev_funding_b) / max(self.total_volume * 0.05, 1), 2.0)
        
        # Domestic program funding factor
        dom_funding_a = sum(p["trade_funding"] for p in self.domestic_programs[self.country_a].values())
        dom_funding_b = sum(p["trade_funding"] for p in self.domestic_programs[self.country_b].values())
        dom_funding_ratio = min((dom_funding_a + dom_funding_b) / max(self.total_volume * 0.05, 1), 2.0)
        
        # Composite WAR-like score (baseline is 0.0, higher is better)
        components = {
            "balance": balance_ratio,
            "volume": volume_ratio,
            "diversity": sector_diversity,
            "compliance": compliance_score,
            "win_win": win_win_balance,
            "development": dev_funding_ratio,
            "domestic": dom_funding_ratio
        }
        
        weights = {
            "balance": 0.20,
            "volume": 0.25,
            "diversity": 0.10, 
            "compliance": 0.10,
            "win_win": 0.10,
            "development": 0.15,
            "domestic": 0.10
        }
        
        # Calculate actual score relative to replacement baseline (0.0)
        war_score = sum(components[c] * weights[c] for c in components) * 10.0 - 5.0
        
        # Country-specific sub-scores
        country_a_score = (balance_ratio + volume_ratio + compliance_score + dev_funding_ratio) / 4 * 10 - 5
        country_b_score = (balance_ratio + volume_ratio + compliance_score + dev_funding_ratio) / 4 * 10 - 5
        
        # Return detailed score
        return {
            "trade_war_score": round(war_score, 2),
            f"{self.country_a}_score": round(country_a_score, 2),
            f"{self.country_b}_score": round(country_b_score, 2),
            "components": components,
            "details": {
                "baseline": 0.0,
                "calculation": "Composite weighted average of key metrics",
                "interpretation": "Points above/below replacement deal (0.0 is average)"
            }
        }
    
    def simulate_scenario(self, scenario: Dict) -> Dict:
        """
        Runs a what-if analysis on the current deal state, simulating
        changes in external factors like currency values, demand, etc.
        
        Args:
            scenario: Dict with scenario parameters
            
        Returns:
            Dict with projected outcomes
        """
        # Copy current state metrics
        current_metrics = {
            "balance": self.current_balance,
            "tariff": self.tariff_rate,
            "total_volume": self.total_volume,
            "trade_war_score": self.calculate_trade_war_score()["trade_war_score"]
        }
        
        # Apply scenario adjustments (temporary for simulation)
        temp_balance = self.current_balance
        temp_tariff = self.tariff_rate
        temp_volume = self.total_volume
        
        # Apply currency shift if specified (affects balance)
        if "currency_shift" in scenario:
            shift = scenario["currency_shift"]
            # Positive shift: country_a currency strengthens
            temp_balance = temp_balance * (1 + shift)
        
        # Apply demand shock if specified (affects volume)
        if "demand_shock" in scenario:
            shock = scenario["demand_shock"]
            temp_volume = temp_volume * (1 + shock)
            
        # Apply tariff override if specified
        if "tariff_override" in scenario:
            temp_tariff = scenario["tariff_override"]
        
        # Simplified WAR score recalculation
        balance_ratio = 1.0 - min(abs(temp_balance) / max(temp_volume, 1), 1.0)
        volume_ratio = min(temp_volume / 1000000, 3.0)
        projected_score = (balance_ratio * 0.4 + volume_ratio * 0.6) * 10 - 5
        
        # Return projected changes
        return {
            "scenario": scenario,
            "current": current_metrics,
            "projected": {
                "balance": temp_balance,
                "tariff": temp_tariff,
                "total_volume": temp_volume,
                "trade_war_score": round(projected_score, 2)
            },
            "change": {
                "balance": temp_balance - current_metrics["balance"],
                "tariff": temp_tariff - current_metrics["tariff"],
                "volume": temp_volume - current_metrics["total_volume"],
                "trade_war_score": round(projected_score - current_metrics["trade_war_score"], 2)
            }
        }
    
    def identify_undervalued_opportunities(self) -> List[Dict]:
        """
        Applies Moneyball principles to identify undervalued trade opportunities.
        Ranks sectors based on growth potential vs current valuation.
        
        Returns:
            List of sectors with opportunities and metrics
        """
        opportunities = []
        
        for sector, metrics in self.sector_performance.items():
            # Calculate opportunity score
            opportunity_score = metrics.get("value_index", 1.0)
            
            # Adjust for current trade balance (favor exports from importing country)
            if self.current_balance > 0:
                # Country A exports more - favor country B exports
                if sector not in self.undervalued_sectors:
                    self.undervalued_sectors[sector] = opportunity_score * 1.2
            else:
                # Country B exports more - favor country A exports
                if sector not in self.undervalued_sectors:
                    self.undervalued_sectors[sector] = opportunity_score * 1.1
            
            # Calculate development potential
            development_potential = random.uniform(0.8, 2.0)  # Random for demo
            
            # Add to opportunities if score is high enough
            if opportunity_score > 1.2:
                opportunities.append({
                    "sector": sector,
                    "opportunity_score": round(opportunity_score, 2),
                    "current_volume": metrics["volume"],
                    "growth_potential": round(random.uniform(1.2, 2.5), 2),  # Mock data
                    "development_potential": round(development_potential, 2),
                    "recommended_earmark": round(min(development_potential * 0.1, 0.35), 2),
                    "recommendation": "Increase focus" if opportunity_score > 1.5 else "Monitor growth"
                })
        
        # Sort by opportunity score (highest first)
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        return opportunities
    
    def calculate_efficiency_gain(self, flow: TradeFlow) -> float:
        """
        Calculate the efficiency gain from optimized trade flow.
        This represents the economic value created by the deal beyond
        the direct transaction, which can fund domestic programs.
        
        Args:
            flow: The trade flow to analyze
            
        Returns:
            Monetary value of efficiency gain
        """
        # In a real implementation, this would use sophisticated economic modeling
        # For demo purposes, using simplified calculation
        
        # Base efficiency factor (2-5% of transaction volume)
        base_efficiency = flow.volume * random.uniform(0.02, 0.05)
        
        # Adjust based on undervalued sectors
        sector_multiplier = 1.0
        if flow.sector in self.undervalued_sectors:
            sector_multiplier = min(self.undervalued_sectors[flow.sector] / 2.0, 3.0)
            
        # Adjust based on trade balance (more efficient if balancing trade)
        balance_multiplier = 1.0
        if (self.current_balance > 0 and flow.from_side == DealSide.CIV) or \
           (self.current_balance < 0 and flow.from_side == DealSide.GOV):
            # This flow helps balance trade
            balance_multiplier = 1.5
            
        # Compliance bonus
        compliance = self.run_compliance_check()
        compliance_multiplier = compliance.compliance_score
        
        # Calculate final efficiency gain
        efficiency_gain = base_efficiency * sector_multiplier * balance_multiplier * compliance_multiplier
        
        # Store in sector efficiency tracking
        if flow.sector not in self.sector_efficiency_gains:
            self.sector_efficiency_gains[flow.sector] = 0.0
        self.sector_efficiency_gains[flow.sector] += efficiency_gain
        
        # Store by country
        if flow.from_side == DealSide.GOV:
            self.efficiency_gains[self.country_a] += efficiency_gain
        else:
            self.efficiency_gains[self.country_b] += efficiency_gain
            
        return efficiency_gain
    
    def allocate_domestic_funding(self, country: str, amount: float = None) -> Dict[str, float]:
        """
        Allocates trade efficiency gains to domestic programs.
        Uses Moneyball-style statistics to optimize allocation.
        
        Args:
            country: Country code for allocation
            amount: Optional specific amount to allocate (uses available efficiency gains if None)
            
        Returns:
            Dict mapping program categories to allocated amounts
        """
        if country not in self.domestic_programs:
            return {}
            
        # Determine amount to allocate
        if amount is None:
            # Use all available unallocated efficiency gains
            amount = self.efficiency_gains[country]
            self.efficiency_gains[country] = 0.0  # Reset after allocation
            
        if amount <= 0:
            return {}
            
        # Get programs for this country
        programs = self.domestic_programs[country]
        
        # Calculate allocation weights based on:
        # 1. Current budget size (bigger programs need more funding)
        # 2. Current funding ratio (underfunded programs get priority)
        weights = {}
        total_weight = 0.0
        
        for name, program in programs.items():
            budget_factor = program["budget"] / 100000  # Normalize
            current_funding_ratio = program["trade_funding"] / max(program["budget"], 1)
            funding_need_factor = 1.0 - min(current_funding_ratio, 0.5) * 2  # Higher for underfunded
            optimization_factor = random.uniform(0.7, 1.3)  # Random for demo
            
            weight = budget_factor * funding_need_factor * optimization_factor
            weights[name] = weight
            total_weight += weight
            
        # Allocate based on weights
        allocations = {}
        for name, weight in weights.items():
            allocation = amount * (weight / total_weight)
            programs[name]["trade_funding"] += allocation
            allocations[name] = allocation
            
        return allocations
    
    def get_development_fund_status(self, country: str) -> Dict:
        """
        Gets the current status of a country's development fund.
        
        Args:
            country: Country code
            
        Returns:
            Dict with development fund details and allocations
        """
        if country not in self.development_funds:
            return {"error": "Country not found"}
            
        fund = self.development_funds[country]
        
        # Calculate allocation percentages
        total_allocated = sum(fund.allocations.values())
        allocation_percentages = {}
        
        if total_allocated > 0:
            for sector, amount in fund.allocations.items():
                allocation_percentages[sector] = round((amount / total_allocated) * 100, 1)
                
        # Format projects
        formatted_projects = []
        for project in fund.projects:
            formatted_projects.append({
                "name": project.get("name", "Unnamed Project"),
                "funding": project.get("funding", 0.0),
                "status": project.get("status", "proposed"),
                "sector": project.get("sector", "general")
            })
            
        return {
            "fund_id": fund.fund_id,
            "country": country,
            "total_balance": fund.balance,
            "sources": {
                "tariff_revenue": fund.tariff_revenue,
                "certificate_revenue": fund.certificate_revenue,
                "efficiency_gains": fund.efficiency_gains
            },
            "allocations": allocation_percentages,
            "projects": formatted_projects,
            "available_for_new_projects": fund.balance - total_allocated
        }
    
    def _calculate_win_win_score(self) -> float:
        """
        Calculates a score reflecting how balanced the Gov/Civ benefits are.
        Perfect balance gives 1.0, imbalance lowers the score.
        
        Returns:
            Float score from 0.0 to 1.0
        """
        # Get values for each quadrant
        a_gov = max(self.win_win_balance[self.country_a]["gov"], 0.1)
        a_civ = max(self.win_win_balance[self.country_a]["civ"], 0.1)
        b_gov = max(self.win_win_balance[self.country_b]["gov"], 0.1)
        b_civ = max(self.win_win_balance[self.country_b]["civ"], 0.1)
        
        # Calculate ratios (values close to 1.0 are balanced)
        a_ratio = min(a_gov, a_civ) / max(a_gov, a_civ)
        b_ratio = min(b_gov, b_civ) / max(b_gov, b_civ)
        
        # Cross-country ratios
        gov_ratio = min(a_gov, b_gov) / max(a_gov, b_gov)
        civ_ratio = min(a_civ, b_civ) / max(a_civ, b_civ)
        
        # Composite score (geometric mean)
        return (a_ratio * b_ratio * gov_ratio * civ_ratio) ** 0.25

    def _check_win_win_balance(self) -> Dict:
        """
        Checks if Gov/Civ benefits are balanced and suggests corrections.
        
        Returns:
            Dict with balance assessment and correction factors
        """
        # Calculate balance score
        balance_score = self._calculate_win_win_score()
        threshold = self.smart_contract_rules["win_win_correction_threshold"]
        
        # Default response (no correction needed)
        response = {
            "needs_correction": False,
            "balance_score": balance_score,
            "tariff_multiplier": 1.0,
            "description": "Benefits are adequately balanced"
        }
        
        # Check if correction needed
        if balance_score < (1.0 - threshold):
            # Identify which quadrant is most imbalanced
            a_gov = self.win_win_balance[self.country_a]["gov"]
            a_civ = self.win_win_balance[self.country_a]["civ"]
            b_gov = self.win_win_balance[self.country_b]["gov"]
            b_civ = self.win_win_balance[self.country_b]["civ"]
            
            # Find the max and min quadrants
            quadrants = {"a_gov": a_gov, "a_civ": a_civ, "b_gov": b_gov, "b_civ": b_civ}
            max_quad = max(quadrants, key=quadrants.get)
            min_quad = min(quadrants, key=quadrants.get)
            
            # Calculate correction factor
            correction = 1.0 - balance_score
            
            # Apply tariff adjustment to rebalance
            tariff_multiplier = 1.0
            description = "Complex benefit imbalance detected"
            
            # Simplified logic for this version
            if max_quad == "a_gov" and (min_quad == "b_civ" or min_quad == "a_civ"):
                # Country A gov benefits too much - reduce tariff
                tariff_multiplier = 1.0 - (correction * 0.2)
                description = f"{self.country_a} government benefits exceed civilian benefits"
            elif max_quad == "b_gov" and (min_quad == "a_civ" or min_quad == "b_civ"):
                # Country B gov benefits too much - increase tariff
                tariff_multiplier = 1.0 + (correction * 0.2)
                description = f"{self.country_b} government benefits exceed civilian benefits"
            
            response.update({
                "needs_correction": True,
                "tariff_multiplier": tariff_multiplier,
                "description": description,
                "imbalance_details": {
                    "max_quadrant": max_quad,
                    "min_quadrant": min_quad,
                    "correction_factor": correction
                }
            })
            
        return response