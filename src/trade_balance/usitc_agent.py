"""
USITC Agent for the Trade Balance System.

This module implements the US International Trade Commission (USITC) agent
for the trade balance system, providing economic analysis, trade impact
assessment, and policy optimization.
"""

import datetime
import random
import uuid
from typing import Dict, List, Optional, Any, Union

from trade_balance.interfaces import (
    EconomicModel, ModelType, TradeImpactAssessment, 
    AssessmentStatus, AssessmentMetrics, IUSITCAgent
)


class USITCAgent(IUSITCAgent):
    """
    US International Trade Commission (USITC) agent implementation for
    economic analysis and trade policy evaluation.
    """
    
    def __init__(self):
        """Initialize the USITC agent."""
        self.name = "US International Trade Commission"
        self._agent_id = "USITC-001"
        self.description = "Government agency for economic analysis and trade policy evaluation."
        self._capabilities = [
            "economic_analysis", 
            "policy_evaluation", 
            "trade_impact_assessment",
            "sector_analysis"
        ]
        
        # Initialize components
        self.models: Dict[str, EconomicModel] = {}
        self.assessments: Dict[str, TradeImpactAssessment] = {}
        
        # Create default economic model
        self._create_default_model()
    
    @property
    def agent_id(self) -> str:
        """Get agent ID."""
        return self._agent_id
    
    @property
    def capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return self._capabilities.copy()
    
    def _create_default_model(self):
        """Create default economic model."""
        model_id = f"MOD-{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.now().isoformat()
        
        model = EconomicModel(
            model_id=model_id,
            title="General Equilibrium Trade Model",
            description="Comprehensive model for trade policy impact analysis",
            model_type=ModelType.GENERAL_EQUILIBRIUM,
            version="1.0",
            created_at=now,
            updated_at=now,
            parameters={
                "elasticity": -1.5,
                "time_horizon": 5,
                "confidence_level": 0.9
            }
        )
        
        self.models[model_id] = model
    
    def create_model(self, model_data: Dict[str, Any]) -> EconomicModel:
        """
        Create a new economic model.
        
        Args:
            model_data: Model data
            
        Returns:
            Created model
        """
        model_id = model_data.get("model_id", f"MOD-{uuid.uuid4().hex[:8]}")
        now = datetime.datetime.now().isoformat()
        
        # Convert string model type to enum if needed
        model_type = model_data.get("model_type")
        if isinstance(model_type, str):
            model_type = ModelType(model_type)
        
        # Create model
        model = EconomicModel(
            model_id=model_id,
            title=model_data.get("title", "Untitled Model"),
            description=model_data.get("description", ""),
            model_type=model_type,
            version=model_data.get("version", "1.0"),
            created_at=now,
            updated_at=now,
            parameters=model_data.get("parameters", {})
        )
        
        # Store model
        self.models[model_id] = model
        
        return model
    
    def update_model(self, model_id: str, updates: Dict[str, Any]) -> EconomicModel:
        """
        Update an existing model.
        
        Args:
            model_id: Model ID
            updates: Updates to apply
            
        Returns:
            Updated model
        """
        # Check if model exists
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        model = self.models[model_id]
        now = datetime.datetime.now().isoformat()
        
        # Update fields
        if "title" in updates:
            model.title = updates["title"]
        
        if "description" in updates:
            model.description = updates["description"]
        
        if "version" in updates:
            model.version = updates["version"]
        
        if "model_type" in updates:
            model_type = updates["model_type"]
            # Convert string model type to enum if needed
            if isinstance(model_type, str):
                model_type = ModelType(model_type)
            model.model_type = model_type
        
        if "parameters" in updates:
            model.parameters.update(updates["parameters"])
        
        # Update timestamp
        model.updated_at = now
        
        # Store updated model
        self.models[model_id] = model
        
        return model
    
    def get_model(self, model_id: str) -> Optional[EconomicModel]:
        """
        Get a model by ID.
        
        Args:
            model_id: Model ID
            
        Returns:
            Model if found, None otherwise
        """
        return self.models.get(model_id)
    
    def list_models(self, filters: Dict[str, Any] = None) -> List[EconomicModel]:
        """
        List models matching the specified filters.
        
        Args:
            filters: Filters to apply
            
        Returns:
            List of matching models
        """
        if not filters:
            return list(self.models.values())
        
        # Apply filters
        result = []
        for model in self.models.values():
            match = True
            
            for key, value in filters.items():
                if key == "model_type":
                    # Handle enum matching
                    if isinstance(value, str):
                        value = ModelType(value)
                    if model.model_type != value:
                        match = False
                        break
                elif hasattr(model, key):
                    if getattr(model, key) != value:
                        match = False
                        break
                elif key in model.parameters:
                    if model.parameters[key] != value:
                        match = False
                        break
            
            if match:
                result.append(model)
        
        return result
    
    def run_model(self, model_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run an economic model with given inputs.
        
        Args:
            model_id: Model ID
            inputs: Model inputs
            
        Returns:
            Model outputs
        """
        # Check if model exists
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        model = self.models[model_id]
        
        # Extract key inputs
        deal_id = inputs.get("deal_id", "unknown")
        deal_name = inputs.get("deal_name", "Unnamed Deal")
        value = inputs.get("value", 100.0)
        
        # Generate outputs based on model type
        if model.model_type == ModelType.GENERAL_EQUILIBRIUM:
            # Generate general equilibrium model outputs
            gdp_impact = value * random.uniform(0.03, 0.07)
            job_creation = int(value * random.uniform(0.1, 0.3))
            trade_balance_effect = value * random.uniform(0.05, 0.15)
            multiplier_effect = random.uniform(1.3, 2.2)
        elif model.model_type == ModelType.ECONOMETRIC:
            # Generate econometric model outputs
            gdp_impact = value * random.uniform(0.02, 0.05)
            job_creation = int(value * random.uniform(0.08, 0.25))
            trade_balance_effect = value * random.uniform(0.03, 0.12)
            multiplier_effect = random.uniform(1.2, 1.8)
        elif model.model_type == ModelType.INPUT_OUTPUT:
            # Generate input-output model outputs
            gdp_impact = value * random.uniform(0.04, 0.08)
            job_creation = int(value * random.uniform(0.15, 0.35))
            trade_balance_effect = value * random.uniform(0.04, 0.1)
            multiplier_effect = random.uniform(1.5, 2.5)
        elif model.model_type == ModelType.SECTOR_SPECIFIC:
            # Generate sector-specific model outputs
            # Use sector information if available
            sectors = inputs.get("sectors", [])
            if sectors and "technology" in sectors:
                # Technology sector has higher job creation but lower trade balance effect
                gdp_impact = value * random.uniform(0.05, 0.09)
                job_creation = int(value * random.uniform(0.2, 0.4))
                trade_balance_effect = value * random.uniform(0.02, 0.08)
                multiplier_effect = random.uniform(1.8, 2.8)
            elif sectors and "agriculture" in sectors:
                # Agriculture sector has lower job creation but higher trade balance effect
                gdp_impact = value * random.uniform(0.02, 0.06)
                job_creation = int(value * random.uniform(0.05, 0.15))
                trade_balance_effect = value * random.uniform(0.1, 0.2)
                multiplier_effect = random.uniform(1.2, 1.6)
            else:
                # Default sector-specific outputs
                gdp_impact = value * random.uniform(0.03, 0.1)
                job_creation = int(value * random.uniform(0.1, 0.3))
                trade_balance_effect = value * random.uniform(0.05, 0.15)
                multiplier_effect = random.uniform(1.4, 2.2)
        else:
            # Default model outputs
            gdp_impact = value * 0.05
            job_creation = int(value * 0.2)
            trade_balance_effect = value * 0.1
            multiplier_effect = 1.5
        
        # Generate risk metrics
        risk_score = random.uniform(0.2, 0.8)
        confidence_interval_lower = gdp_impact * (1 - risk_score * 0.5)
        confidence_interval_upper = gdp_impact * (1 + risk_score * 0.5)
        volatility_index = risk_score * 0.5
        
        # Create result
        result = {
            "model_id": model.model_id,
            "model_type": model.model_type.value,
            "deal_id": deal_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "economic_impact": {
                "gdp_impact": round(gdp_impact, 2),
                "job_creation": job_creation,
                "trade_balance_effect": round(trade_balance_effect, 2),
                "multiplier_effect": round(multiplier_effect, 2)
            },
            "risk_assessment": {
                "risk_score": round(risk_score, 2),
                "confidence_interval": [
                    round(confidence_interval_lower, 2),
                    round(confidence_interval_upper, 2)
                ],
                "volatility_index": round(volatility_index, 2)
            }
        }
        
        return result
    
    def create_assessment(self, assessment_data: Dict[str, Any]) -> TradeImpactAssessment:
        """
        Create a new trade impact assessment.
        
        Args:
            assessment_data: Assessment data
            
        Returns:
            Created assessment
        """
        assessment_id = assessment_data.get("assessment_id", f"ASSESS-{uuid.uuid4().hex[:8]}")
        now = datetime.datetime.now().isoformat()
        
        # Convert string status to enum if needed
        status = assessment_data.get("status", "pending")
        if isinstance(status, str):
            status = AssessmentStatus(status)
        
        # Create metrics
        if "metrics" in assessment_data:
            metrics_data = assessment_data["metrics"]
            metrics = AssessmentMetrics(
                gdp_impact=metrics_data.get("gdp_impact", 0.0),
                job_creation=metrics_data.get("job_creation", 0),
                trade_balance_effect=metrics_data.get("trade_balance_effect", 0.0),
                confidence_level=metrics_data.get("confidence_level", 0.0),
                custom_metrics=metrics_data.get("custom_metrics", {})
            )
        else:
            metrics = AssessmentMetrics(
                gdp_impact=0.0,
                job_creation=0,
                trade_balance_effect=0.0,
                confidence_level=0.0,
                custom_metrics={}
            )
        
        # Create assessment
        assessment = TradeImpactAssessment(
            assessment_id=assessment_id,
            deal_id=assessment_data.get("deal_id", ""),
            title=assessment_data.get("title", "Untitled Assessment"),
            model_id=assessment_data.get("model_id", ""),
            created_at=now,
            status=status,
            results=assessment_data.get("results", {}),
            metrics=metrics
        )
        
        # Store assessment
        self.assessments[assessment_id] = assessment
        
        return assessment
    
    def get_assessment(self, assessment_id: str) -> Optional[TradeImpactAssessment]:
        """
        Get an assessment by ID.
        
        Args:
            assessment_id: Assessment ID
            
        Returns:
            Assessment if found, None otherwise
        """
        return self.assessments.get(assessment_id)
    
    def list_assessments(self, filters: Dict[str, Any] = None) -> List[TradeImpactAssessment]:
        """
        List assessments matching the specified filters.
        
        Args:
            filters: Filters to apply
            
        Returns:
            List of matching assessments
        """
        if not filters:
            return list(self.assessments.values())
        
        # Apply filters
        result = []
        for assessment in self.assessments.values():
            match = True
            
            for key, value in filters.items():
                if key == "status":
                    # Handle enum matching
                    if isinstance(value, str):
                        value = AssessmentStatus(value)
                    if assessment.status != value:
                        match = False
                        break
                elif key == "deal_id":
                    if assessment.deal_id != value:
                        match = False
                        break
                elif key == "model_id":
                    if assessment.model_id != value:
                        match = False
                        break
                elif hasattr(assessment, key):
                    if getattr(assessment, key) != value:
                        match = False
                        break
            
            if match:
                result.append(assessment)
        
        return result
    
    def analyze_trade_program(self, program_id: str) -> Dict[str, Any]:
        """
        Analyze economic impacts of a trade program.
        
        Args:
            program_id: Program ID
            
        Returns:
            Dictionary with analysis results
        """
        # Create a new assessment ID
        assessment_id = f"ASSESS-{uuid.uuid4().hex[:8]}"
        
        # Use the first available model
        if not self.models:
            # Create a default model if none exists
            self._create_default_model()
        
        model_id = next(iter(self.models.keys()))
        model = self.models[model_id]
        
        # Create assessment
        assessment = TradeImpactAssessment(
            assessment_id=assessment_id,
            deal_id=program_id,
            title=f"Economic Impact Assessment of {program_id}",
            model_id=model_id,
            created_at=datetime.datetime.now().isoformat(),
            status=AssessmentStatus.PENDING,
            results={},
            metrics=AssessmentMetrics(
                gdp_impact=0.0,
                job_creation=0,
                trade_balance_effect=0.0,
                confidence_level=0.0
            )
        )
        
        # Store assessment
        self.assessments[assessment_id] = assessment
        
        # Create simulated inputs
        inputs = {
            "deal_id": program_id,
            "deal_name": f"Trade Program {program_id}",
            "value": random.uniform(500000, 2000000),
            "stakeholder_count": random.randint(3, 8),
            "timeline": random.randint(3, 10),
            "sectors": ["technology", "manufacturing", "agriculture"]
        }
        
        # Run the model
        results = self.run_model(model_id, inputs)
        
        # Update assessment
        assessment.results = results
        assessment.status = AssessmentStatus.COMPLETED
        assessment.metrics = AssessmentMetrics(
            gdp_impact=results["economic_impact"]["gdp_impact"],
            job_creation=results["economic_impact"]["job_creation"],
            trade_balance_effect=results["economic_impact"]["trade_balance_effect"],
            confidence_level=1.0 - results["risk_assessment"]["risk_score"]
        )
        
        # Store updated assessment
        self.assessments[assessment_id] = assessment
        
        # Generate policy recommendation
        gdp_impact = results["economic_impact"]["gdp_impact"]
        job_creation = results["economic_impact"]["job_creation"]
        trade_balance = results["economic_impact"]["trade_balance_effect"]
        
        if gdp_impact > 0 and job_creation > 0 and trade_balance > 0:
            recommendation = "Program shows positive economic impact across all metrics. Recommend implementation."
            confidence = "High"
        elif gdp_impact > 0 and job_creation > 0:
            recommendation = "Program shows positive economic impact but may affect trade balance. Consider implementation with balance monitoring."
            confidence = "Medium"
        elif gdp_impact > 0:
            recommendation = "Program shows positive GDP impact but mixed effects on jobs and trade balance. Consider targeted implementation."
            confidence = "Medium"
        else:
            recommendation = "Program shows mixed economic impacts. Further analysis recommended before implementation."
            confidence = "Low"
        
        return {
            "assessment_id": assessment_id,
            "deal_id": program_id,
            "model_id": model_id,
            "status": assessment.status.value,
            "economic_impact": results["economic_impact"],
            "risk_assessment": results["risk_assessment"],
            "policy_recommendation": recommendation,
            "confidence_level": confidence
        }
    
    def optimize_trade_policy(
        self,
        program_id: str,
        optimization_goal: str
    ) -> Dict[str, Any]:
        """
        Optimize trade policy parameters for a specific goal.
        
        Args:
            program_id: Program ID
            optimization_goal: Goal to optimize for (welfare, balance, growth, employment)
            
        Returns:
            Dictionary with optimized policy parameters
        """
        # Simulate different policy options
        tariff_options = [0.01, 0.03, 0.05, 0.07, 0.10, 0.15]
        
        best_score = -float('inf')
        best_policy = {}
        
        for tariff in tariff_options:
            # Simulate this policy
            score = self._score_policy(tariff, optimization_goal)
            
            if score > best_score:
                best_score = score
                best_policy = {
                    "tariff": tariff,
                    "development_earmark": random.uniform(0.2, 0.4),
                    "domestic_earmark": random.uniform(0.25, 0.45)
                }
        
        # Generate recommendation
        if optimization_goal == "welfare":
            recommendation = f"To maximize economic welfare, set tariffs to {best_policy['tariff'] * 100:.1f}% and allocate {best_policy['development_earmark'] * 100:.0f}% of tariff revenue to development."
        elif optimization_goal == "balance":
            recommendation = f"To optimize trade balance, set tariffs to {best_policy['tariff'] * 100:.1f}% and focus on sectoral adjustments in your most competitive industries."
        elif optimization_goal == "growth":
            recommendation = f"To maximize economic growth, set tariffs to {best_policy['tariff'] * 100:.1f}% and invest {best_policy['development_earmark'] * 100:.0f}% in infrastructure development."
        elif optimization_goal == "employment":
            recommendation = f"To maximize employment, set tariffs to {best_policy['tariff'] * 100:.1f}% and allocate {best_policy['domestic_earmark'] * 100:.0f}% to domestic industry support."
        else:
            recommendation = f"For balanced economic benefits, set tariffs to {best_policy['tariff'] * 100:.1f}% with {best_policy['development_earmark'] * 100:.0f}% development earmark."
        
        return {
            "program_id": program_id,
            "optimization_goal": optimization_goal,
            "optimized_policy": best_policy,
            "improvement_score": best_score,
            "recommendation": recommendation
        }
    
    def _score_policy(self, tariff: float, optimization_goal: str) -> float:
        """
        Score a policy option based on the optimization goal.
        
        Args:
            tariff: Tariff rate to evaluate
            optimization_goal: Goal to optimize for
            
        Returns:
            Numerical score (higher is better)
        """
        # Base metrics
        base_volume = 1000000
        elasticity = -1.5
        
        # Calculate volume effect
        tariff_change = tariff - 0.05  # 5% baseline
        volume_change = tariff_change * elasticity
        new_volume = base_volume * (1 + volume_change)
        
        # Calculate welfare effect
        consumer_surplus = (base_volume - new_volume) * (tariff - 0.05) * 0.5
        producer_surplus = new_volume * (tariff - 0.05) * 0.7
        govt_revenue = new_volume * tariff
        deadweight_loss = (base_volume - new_volume) * (tariff - 0.05) * 0.3
        net_welfare = consumer_surplus + producer_surplus - deadweight_loss
        
        # Calculate employment effect
        job_effect = volume_change * 0.6
        
        # Calculate trade balance effect
        # Higher tariffs tend to reduce imports more than exports
        import_effect = volume_change * 1.2
        export_effect = volume_change * 0.8
        balance_effect = import_effect - export_effect
        
        # Score based on optimization goal
        if optimization_goal == "welfare":
            score = net_welfare / 1000
        elif optimization_goal == "balance":
            score = 10000 - abs(balance_effect * base_volume)
        elif optimization_goal == "growth":
            score = new_volume - base_volume
        elif optimization_goal == "employment":
            score = 100 * job_effect
        else:
            # Balanced score
            score = (net_welfare / 1000 +
                   (10000 - abs(balance_effect * base_volume)) / 100 +
                   (new_volume - base_volume) / 1000 +
                   job_effect * 100)
        
        # Add random variation for demo purposes
        score *= random.uniform(0.9, 1.1)
        
        return score
    
    def calculate_war_score(
        self,
        economic_data: Dict[str, Any]
    ) -> float:
        """
        Calculate WAR (Wins Above Replacement) score for economic policy.
        
        Args:
            economic_data: Economic data dictionary
            
        Returns:
            WAR score (0-5 scale)
        """
        # WAR score components
        # 1. Balance component (0-1)
        balance_ratio = abs(economic_data.get("trade_balance", 0)) / max(economic_data.get("trade_volume", 1), 1)
        balance_score = 1.0 - min(balance_ratio, 1.0)
        
        # 2. Growth component (0-1)
        baseline_growth = economic_data.get("baseline_growth", 0.02)
        actual_growth = economic_data.get("actual_growth", 0.02)
        growth_score = min(max(actual_growth / baseline_growth, 0), 1)
        
        # 3. Job creation component (0-1)
        baseline_jobs = economic_data.get("baseline_jobs", 100)
        actual_jobs = economic_data.get("actual_jobs", 100)
        job_score = min(max(actual_jobs / baseline_jobs, 0), 1)
        
        # 4. Competitiveness component (0-1)
        competitiveness = economic_data.get("competitiveness", 0.5)
        
        # Weighted WAR score (0-5 scale)
        weights = {
            "balance": 0.3,
            "growth": 0.3,
            "jobs": 0.2,
            "competitiveness": 0.2
        }
        
        weighted_score = (
            weights["balance"] * balance_score +
            weights["growth"] * growth_score +
            weights["jobs"] * job_score +
            weights["competitiveness"] * competitiveness
        )
        
        # Scale to 0-5 range
        war_score = weighted_score * 5.0
        
        return war_score