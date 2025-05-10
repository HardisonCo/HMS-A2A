#!/usr/bin/env python3
"""
Test suite for the Moneyball Deal Model implementation.

This module provides comprehensive tests to validate all components
of the Moneyball Deal Model according to the formal specifications.
"""

import unittest
import sys
import os
import json
import numpy as np
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import model components
try:
    from moneyball_deal_model import (
        Intent, Solution, Stakeholder, FinancingStructure, ExecutionPlan, Deal,
        create_moneyball_deal, analyze_deal_value, match_solutions, map_stakeholders,
        optimize_financing
    )
    from win_win_calculation_framework import (
        EntityProfile, ValueComponent, EntityValue,
        calculate_entity_value, translate_value_dimension, ensure_win_win_outcome,
        verify_deal_integrity, calculate_value_distribution
    )
    from deal_monitoring_system import (
        DealMetric, MonitoringAlert, DealStatus, HistoricalPerformance,
        PredictiveModel, DealMonitoringSystem
    )
    from o3_deal_roadmap_optimization import (
        EntityNode, ValueEdge, DealHyperedge, DealRoadmap,
        DealHypergraph, O3Optimizer
    )
    IMPORT_SUCCESS = True
except ImportError as e:
    print(f"Warning: Could not import model components: {e}")
    IMPORT_SUCCESS = False

class TestMoneyballModelCore(unittest.TestCase):
    """Test cases for the core Moneyball Deal Model components."""
    
    def setUp(self):
        """Setup test fixtures."""
        if not IMPORT_SUCCESS:
            self.skipTest("Required modules could not be imported")
        
        # Create a sample intent
        self.intent = Intent(
            id="intent1",
            description="Increase access to capital for small businesses",
            intent_vector=np.array([0.8, 0.6, 0.4, 0.2]),
            value_dimensions=["economic", "social", "innovation", "reputation"],
            constraints={"budget": 5000000, "timeline": 24},
            context={"domain": "small_business", "region": "northeast"}
        )
        
        # Create sample solutions
        self.solutions = [
            Solution(
                id="solution1",
                description="Revolving loan fund",
                solution_vector=np.array([0.9, 0.5, 0.3, 0.1]),
                potential_value=500000.0,
                intent_id="intent1",
                implementation_difficulty=0.4,
                time_horizon=18
            ),
            Solution(
                id="solution2",
                description="Technical assistance program",
                solution_vector=np.array([0.7, 0.7, 0.5, 0.3]),
                potential_value=300000.0,
                intent_id="intent1",
                implementation_difficulty=0.3,
                time_horizon=12
            )
        ]
        
        # Create sample stakeholders
        self.stakeholders = [
            Stakeholder(
                id="sba",
                name="Small Business Administration",
                type="government",
                capabilities={"funding": 0.9, "policy": 0.8, "expertise": 0.7},
                value_preferences={"economic": 0.4, "social": 0.3, "innovation": 0.2, "reputation": 0.1},
                risk_tolerance=0.5,
                participation_costs={"financial": 2000000, "time": 500},
                expected_returns={"economic": 3000000, "social": 1000000}
            ),
            Stakeholder(
                id="bank",
                name="Local Bank Consortium",
                type="corporate",
                capabilities={"funding": 0.8, "expertise": 0.7, "distribution": 0.9},
                value_preferences={"economic": 0.7, "social": 0.1, "innovation": 0.1, "reputation": 0.1},
                risk_tolerance=0.3,
                participation_costs={"financial": 1500000, "time": 300},
                expected_returns={"economic": 2000000, "reputation": 500000}
            ),
            Stakeholder(
                id="chamber",
                name="Chamber of Commerce",
                type="ngo",
                capabilities={"expertise": 0.6, "network": 0.8, "advocacy": 0.7},
                value_preferences={"economic": 0.3, "social": 0.4, "innovation": 0.2, "reputation": 0.1},
                risk_tolerance=0.6,
                participation_costs={"financial": 100000, "time": 400},
                expected_returns={"economic": 0, "social": 800000, "reputation": 300000}
            )
        ]
        
        # Create a sample financing structure
        self.financing = FinancingStructure(
            cost_allocation={
                "sba": 2000000,
                "bank": 1500000,
                "chamber": 100000
            },
            returns_allocation={
                "sba": {"economic": 1000000, "social": 1500000},
                "bank": {"economic": 2500000, "reputation": 500000},
                "chamber": {"social": 800000, "reputation": 300000}
            },
            timeline={
                "sba": {0: 1000000, 6: 1000000},
                "bank": {0: 750000, 6: 750000},
                "chamber": {0: 100000}
            },
            conditions={
                "performance_triggers": {"loan_volume": 10000000},
                "exit_conditions": {"program_completion": 36}
            },
            risk_sharing={
                "sba": 0.5,
                "bank": 0.4,
                "chamber": 0.1
            }
        )
        
        # Create a sample execution plan
        self.execution = ExecutionPlan(
            responsibility_matrix={
                "sba": {"program_oversight": 0.8, "policy_guidance": 0.9},
                "bank": {"loan_underwriting": 0.9, "customer_service": 0.7},
                "chamber": {"business_outreach": 0.8, "workshop_delivery": 0.7}
            },
            timeline={
                0: ["program_setup", "staff_training"],
                3: ["initial_outreach", "application_process"],
                6: ["funding_distribution", "technical_assistance"]
            },
            milestones={
                "launch": {"date": 3, "criteria": "All staff trained"},
                "phase1_complete": {"date": 12, "criteria": "50% of funds distributed"},
                "program_review": {"date": 18, "criteria": "Performance metrics evaluation"}
            },
            expertise_allocation={
                "program_oversight": {"sba": 0.8, "bank": 0.2},
                "loan_underwriting": {"bank": 0.9, "sba": 0.1},
                "business_outreach": {"chamber": 0.8, "sba": 0.2}
            }
        )
        
        # Create a sample deal
        self.deal = Deal(
            id="deal1",
            name="Small Business Capital Access Program",
            intent=self.intent,
            solutions=self.solutions,
            stakeholders=self.stakeholders,
            financing=self.financing,
            execution_plan=self.execution,
            creation_date="2025-01-01",
            status="proposed",
            total_value=6600000,
            win_win_status=True,
            confidence_score=0.85
        )
    
    def test_intent_creation(self):
        """Test Intent creation and properties."""
        self.assertEqual(self.intent.id, "intent1")
        self.assertEqual(self.intent.description, "Increase access to capital for small businesses")
        self.assertEqual(self.intent.dimension_count, 4)
        self.assertEqual(len(self.intent.intent_vector), 4)
    
    def test_solution_matching(self):
        """Test solution matching functionality."""
        matched_solutions = match_solutions(self.intent, self.solutions)
        self.assertIsNotNone(matched_solutions)
        self.assertTrue(len(matched_solutions) > 0)
        self.assertIn(self.solutions[0], matched_solutions)
    
    def test_stakeholder_mapping(self):
        """Test stakeholder mapping functionality."""
        mapped_stakeholders = map_stakeholders(self.intent, self.solutions, self.stakeholders)
        self.assertIsNotNone(mapped_stakeholders)
        self.assertTrue(len(mapped_stakeholders) > 0)
        self.assertIn(self.stakeholders[0], mapped_stakeholders)
    
    def test_financing_optimization(self):
        """Test financing optimization functionality."""
        optimized_financing = optimize_financing(self.intent, self.solutions, self.stakeholders)
        self.assertIsNotNone(optimized_financing)
        self.assertIsInstance(optimized_financing, FinancingStructure)
        # Verify total cost equals total allocation
        total_cost = sum(optimized_financing.cost_allocation.values())
        self.assertGreater(total_cost, 0)
    
    def test_deal_creation(self):
        """Test complete deal creation functionality."""
        deal = create_moneyball_deal(
            intent_description="Increase access to capital for small businesses",
            solutions=["Revolving loan fund", "Technical assistance program"],
            stakeholders=["SBA", "Local banks", "Chamber of Commerce"],
            financing={"public": 2000000, "private": 1500000, "grants": 100000},
            expertise=["Lending", "Business advising", "Program management"]
        )
        self.assertIsNotNone(deal)
        self.assertIsInstance(deal, Deal)
        self.assertTrue(hasattr(deal, 'intent'))
        self.assertTrue(hasattr(deal, 'solutions'))
        self.assertTrue(hasattr(deal, 'stakeholders'))
        self.assertTrue(hasattr(deal, 'financing'))
        self.assertTrue(hasattr(deal, 'execution_plan'))
    
    def test_deal_value_analysis(self):
        """Test deal value analysis functionality."""
        analysis = analyze_deal_value(self.deal)
        self.assertIsNotNone(analysis)
        self.assertIn('total_value', analysis)
        self.assertIn('is_win_win', analysis)
        self.assertIn('entity_values', analysis)
        self.assertIn('risk_adjusted_value', analysis)
        self.assertEqual(analysis['is_win_win'], True)
        
        # Entity values should be available for all stakeholders
        for stakeholder in self.stakeholders:
            self.assertIn(stakeholder.id, analysis['entity_values'])
            self.assertGreater(analysis['entity_values'][stakeholder.id], 0)

class TestWinWinCalculation(unittest.TestCase):
    """Test cases for the Win-Win Calculation Framework."""
    
    def setUp(self):
        """Setup test fixtures."""
        if not IMPORT_SUCCESS:
            self.skipTest("Required modules could not be imported")
        
        # Create sample entity profiles
        self.entity_profiles = {
            "gov": EntityProfile(
                id="gov1",
                name="Department of Commerce",
                type="government",
                dimensions={"economic": 0.3, "social": 0.3, "mission": 0.3, "reputation": 0.1},
                time_preference=0.05,
                risk_preference=0.4,
                resource_constraints={"budget": 1000000, "staff": 50},
                performance_metrics={"effectiveness": [0.8, 0.75, 0.82]}
            ),
            "corp": EntityProfile(
                id="corp1",
                name="TechCorp",
                type="corporate",
                dimensions={"economic": 0.7, "social": 0.1, "innovation": 0.1, "reputation": 0.1},
                time_preference=0.08,
                risk_preference=0.3,
                resource_constraints={"budget": 2000000, "staff": 100},
                performance_metrics={"roi": [0.12, 0.15, 0.14]}
            ),
            "ngo": EntityProfile(
                id="ngo1",
                name="Community Foundation",
                type="ngo",
                dimensions={"economic": 0.2, "social": 0.5, "mission": 0.2, "reputation": 0.1},
                time_preference=0.03,
                risk_preference=0.5,
                resource_constraints={"budget": 500000, "staff": 20},
                performance_metrics={"impact": [0.7, 0.75, 0.8]}
            ),
            "civ": EntityProfile(
                id="civ1",
                name="Local Business Association",
                type="civilian",
                dimensions={"economic": 0.4, "social": 0.3, "service": 0.2, "reputation": 0.1},
                time_preference=0.06,
                risk_preference=0.4,
                resource_constraints={"budget": 100000, "staff": 5},
                performance_metrics={"satisfaction": [0.8, 0.85, 0.9]}
            )
        }
        
        # Create sample value components
        self.value_components = {
            "econ1": ValueComponent(
                dimension="economic",
                amount=1000000.0,
                timeline=[(0, 200000), (6, 300000), (12, 500000)],
                probability=0.9,
                verification_method="financial_audit",
                is_quantifiable=True,
                network_effects={"social": 0.2, "reputation": 0.1}
            ),
            "social1": ValueComponent(
                dimension="social",
                amount=800000.0,
                timeline=[(3, 300000), (9, 500000)],
                probability=0.8,
                verification_method="impact_assessment",
                is_quantifiable=True,
                network_effects={"economic": 0.1, "reputation": 0.2}
            )
        }
    
    def test_government_value_translation(self):
        """Test government-specific value translation."""
        components = {
            "econ1": self.value_components["econ1"],
            "social1": self.value_components["social1"]
        }
        total_value, comp_values = calculate_entity_value(
            value_components=components,
            entity_profile=self.entity_profiles["gov"]
        )
        self.assertGreater(total_value, 0)
        self.assertIn("econ1", comp_values)
        self.assertIn("social1", comp_values)
    
    def test_corporate_value_translation(self):
        """Test corporate-specific value translation."""
        components = {
            "econ1": self.value_components["econ1"],
            "social1": self.value_components["social1"]
        }
        total_value, comp_values = calculate_entity_value(
            value_components=components,
            entity_profile=self.entity_profiles["corp"]
        )
        self.assertGreater(total_value, 0)
        self.assertIn("econ1", comp_values)
        self.assertIn("social1", comp_values)
    
    def test_dimension_translation(self):
        """Test value dimension translation."""
        source_dim = "economic"
        source_amount = 1000000.0
        target_dims = ["social", "mission", "reputation"]
        
        for entity_type in ["government", "corporate", "ngo", "civilian"]:
            translated_values = translate_value_dimension(
                source_dimension=source_dim,
                source_amount=source_amount,
                target_dimensions=target_dims,
                entity_type=entity_type
            )
            self.assertIsNotNone(translated_values)
            for dim in target_dims:
                self.assertIn(dim, translated_values)
                # Translation should be some fraction of original value
                self.assertLess(translated_values[dim], source_amount)
    
    def test_win_win_outcome(self):
        """Test win-win outcome validation."""
        # Create a win-win deal
        entity_values = {
            "gov1": 500000,
            "corp1": 1500000,
            "ngo1": 300000,
            "civ1": 100000
        }
        
        is_win_win = ensure_win_win_outcome(entity_values)
        self.assertTrue(is_win_win)
        
        # Create a not win-win deal
        non_win_entity_values = {
            "gov1": 500000,
            "corp1": 1500000,
            "ngo1": -50000,  # Negative value
            "civ1": 100000
        }
        
        is_win_win = ensure_win_win_outcome(non_win_entity_values)
        self.assertFalse(is_win_win)
    
    def test_deal_integrity(self):
        """Test deal integrity verification."""
        valid_deal = {
            "intent": "valid intent",
            "solutions": ["solution1", "solution2"],
            "stakeholders": ["gov1", "corp1", "ngo1"],
            "financing": {
                "total_cost": 1000000,
                "cost_allocation": {"gov1": 500000, "corp1": 500000}
            },
            "execution_plan": {"timeline": {0: ["task1"], 6: ["task2"]}}
        }
        
        is_valid, issues = verify_deal_integrity(valid_deal)
        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)
        
        # Create an invalid deal
        invalid_deal = {
            "intent": "valid intent",
            "solutions": [],  # No solutions
            "stakeholders": ["gov1", "corp1", "ngo1"],
            "financing": {
                "total_cost": 1000000,
                "cost_allocation": {"gov1": 400000, "corp1": 500000}  # Doesn't add up
            },
            "execution_plan": {"timeline": {0: ["task1"], 6: ["task2"]}}
        }
        
        is_valid, issues = verify_deal_integrity(invalid_deal)
        self.assertFalse(is_valid)
        self.assertTrue(len(issues) > 0)
    
    def test_value_distribution(self):
        """Test value distribution calculation."""
        stakeholder_values = {
            "gov1": 500000,
            "corp1": 1500000,
            "ngo1": 300000,
            "civ1": 100000
        }
        
        distribution = calculate_value_distribution(stakeholder_values)
        self.assertIsNotNone(distribution)
        self.assertIn("total_value", distribution)
        self.assertIn("percentages", distribution)
        self.assertIn("gini_coefficient", distribution)
        
        # Total value should match sum of individual values
        self.assertEqual(distribution["total_value"], sum(stakeholder_values.values()))
        
        # Percentages should add up to 100%
        self.assertAlmostEqual(sum(distribution["percentages"].values()), 1.0, places=5)
        
        # Gini coefficient should be between 0 and 1
        self.assertGreaterEqual(distribution["gini_coefficient"], 0.0)
        self.assertLessEqual(distribution["gini_coefficient"], 1.0)

class TestDealMonitoring(unittest.TestCase):
    """Test cases for the Deal Monitoring System."""
    
    def setUp(self):
        """Setup test fixtures."""
        if not IMPORT_SUCCESS:
            self.skipTest("Required modules could not be imported")
        
        # Create sample metrics
        self.metrics = [
            DealMetric(
                id="metric1",
                name="Capital Deployed",
                dimension="economic",
                component="financing",
                entity_id="sba",
                units="dollars",
                frequency="monthly",
                target_values={"m3": 1000000, "m6": 2000000, "m12": 5000000},
                actual_values={"m3": 950000, "m6": 2100000},
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
                is_critical=True
            ),
            DealMetric(
                id="metric2",
                name="Businesses Served",
                dimension="social",
                component="execution",
                entity_id="chamber",
                units="count",
                frequency="quarterly",
                target_values={"q1": 50, "q2": 100, "q3": 150, "q4": 200},
                actual_values={"q1": 45, "q2": 95},
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
                is_critical=False
            )
        ]
        
        # Create a sample deal status
        self.deal_status = DealStatus(
            deal_id="deal1",
            overall_health=0.85,
            component_health={
                "intent": 0.9,
                "solutions": 0.85,
                "stakeholders": 0.9,
                "financing": 0.8,
                "execution": 0.8
            },
            entity_health={
                "sba": 0.85,
                "bank": 0.9,
                "chamber": 0.8
            },
            alerts=[],
            current_stage="implementation",
            is_on_track=True,
            variance_summary={
                "average_variance": -0.03,
                "critical_variances": []
            },
            last_updated=datetime.datetime.now()
        )
        
        # Create a monitoring system
        self.monitoring_system = DealMonitoringSystem()
    
    def test_add_metric(self):
        """Test adding metrics to the monitoring system."""
        for metric in self.metrics:
            self.monitoring_system.add_metric(metric)
        
        # Check that metrics were added
        deal_metrics = self.monitoring_system.get_metrics("deal1")
        self.assertGreaterEqual(len(deal_metrics), 0)
    
    def test_update_metric(self):
        """Test updating metrics in the monitoring system."""
        # Add a metric
        self.monitoring_system.add_metric(self.metrics[0])
        
        # Update the metric
        updated_metric = self.metrics[0]
        updated_metric.actual_values["m9"] = 3500000
        self.monitoring_system.update_metric(updated_metric)
        
        # Check that the metric was updated
        deal_metrics = self.monitoring_system.get_metrics("deal1")
        for metric in deal_metrics:
            if metric.id == updated_metric.id:
                self.assertIn("m9", metric.actual_values)
                self.assertEqual(metric.actual_values["m9"], 3500000)
    
    def test_generate_alerts(self):
        """Test alert generation in the monitoring system."""
        # Add metrics
        for metric in self.metrics:
            self.monitoring_system.add_metric(metric)
        
        # Update with significant variance to trigger alert
        updated_metric = self.metrics[0]
        updated_metric.actual_values["m12"] = 3000000  # 40% below target
        self.monitoring_system.update_metric(updated_metric)
        
        # Generate alerts
        self.monitoring_system.generate_alerts("deal1")
        
        # Check that an alert was generated
        alerts = self.monitoring_system.get_alerts("deal1")
        self.assertTrue(len(alerts) > 0)
    
    def test_update_deal_status(self):
        """Test updating deal status in the monitoring system."""
        # Add metrics
        for metric in self.metrics:
            self.monitoring_system.add_metric(metric)
        
        # Set initial status
        self.monitoring_system.update_deal_status("deal1", self.deal_status)
        
        # Check that status was set
        status = self.monitoring_system.get_deal_status("deal1")
        self.assertIsNotNone(status)
        self.assertEqual(status.deal_id, "deal1")
        self.assertEqual(status.overall_health, 0.85)
    
    def test_create_dashboard(self):
        """Test dashboard creation in the monitoring system."""
        # Add metrics and status
        for metric in self.metrics:
            self.monitoring_system.add_metric(metric)
        self.monitoring_system.update_deal_status("deal1", self.deal_status)
        
        # Create dashboard
        dashboard = self.monitoring_system.create_dashboard("deal1")
        
        # Check dashboard contents
        self.assertIsNotNone(dashboard)
        self.assertIn("deal_id", dashboard)
        self.assertIn("timestamp", dashboard)
        self.assertIn("overall_health", dashboard)
        self.assertIn("metrics", dashboard)
        self.assertIn("alerts", dashboard)

class TestO3Optimization(unittest.TestCase):
    """Test cases for the O3 Optimization Process."""
    
    def setUp(self):
        """Setup test fixtures."""
        if not IMPORT_SUCCESS:
            self.skipTest("Required modules could not be imported")
        
        # Create a hypergraph
        self.graph = DealHypergraph()
        
        # Add entities
        self.entities = [
            EntityNode(
                id="govt1",
                name="Department of Commerce",
                entity_type="government",
                capacity={"budget": 100.0, "staff": 50.0},
                preferences={"economic": 0.4, "social": 0.3, "mission": 0.2, "reputation": 0.1}
            ),
            EntityNode(
                id="govt2",
                name="Small Business Administration",
                entity_type="government",
                capacity={"budget": 80.0, "staff": 30.0},
                preferences={"economic": 0.3, "social": 0.4, "mission": 0.2, "reputation": 0.1}
            ),
            EntityNode(
                id="corp1",
                name="TechCorp Inc.",
                entity_type="corporate",
                capacity={"budget": 200.0, "staff": 100.0},
                preferences={"economic": 0.7, "innovation": 0.2, "reputation": 0.1}
            ),
            EntityNode(
                id="ngo1",
                name="Community Development Fund",
                entity_type="ngo",
                capacity={"budget": 50.0, "staff": 20.0},
                preferences={"social": 0.6, "mission": 0.3, "economic": 0.1}
            )
        ]
        
        for entity in self.entities:
            self.graph.add_entity(entity)
        
        # Create a deal
        self.deal = DealHyperedge(
            id="deal1",
            name="Small Business Innovation Partnership",
            entities=["govt1", "govt2", "corp1"],
            intent="Accelerate technological innovation in small businesses"
        )
        
        # Add value edges to the deal
        value_edges = [
            ValueEdge(
                source_id="govt1",
                target_id="corp1",
                value={"economic": 30.0, "innovation": 20.0},
                deal_id="deal1"
            ),
            ValueEdge(
                source_id="govt2",
                target_id="corp1",
                value={"economic": 25.0, "social": 10.0},
                deal_id="deal1"
            ),
            ValueEdge(
                source_id="corp1",
                target_id="govt1",
                value={"economic": 15.0, "reputation": 10.0},
                deal_id="deal1"
            ),
            ValueEdge(
                source_id="corp1",
                target_id="govt2",
                value={"economic": 20.0, "mission": 15.0},
                deal_id="deal1"
            )
        ]
        
        for edge in value_edges:
            self.deal.add_value_edge(edge)
        
        # Add the deal to the graph
        self.graph.add_deal(self.deal)
        
        # Create an optimizer
        self.optimizer = O3Optimizer(self.graph)
    
    def test_entity_operations(self):
        """Test entity operations in the hypergraph."""
        entity = self.entities[0]
        
        # Test entity retrieval
        retrieved_entity = self.graph.entities[entity.id]
        self.assertEqual(retrieved_entity.id, entity.id)
        self.assertEqual(retrieved_entity.name, entity.name)
        
        # Test entity deal participation
        self.assertIn("deal1", retrieved_entity.deals)
        
        # Test subjective value calculation
        value_object = {"economic": 100.0, "social": 50.0}
        subjective_value = entity.get_subjective_value(value_object)
        self.assertGreater(subjective_value, 0.0)
        
        # Expected value: 100.0 * 0.4 (economic preference) + 50.0 * 0.3 (social preference) = 55.0
        expected_value = 100.0 * 0.4 + 50.0 * 0.3
        self.assertAlmostEqual(subjective_value, expected_value, places=5)
    
    def test_deal_operations(self):
        """Test deal operations in the hypergraph."""
        deal = self.deal
        
        # Test deal retrieval
        retrieved_deal = self.graph.deals[deal.id]
        self.assertEqual(retrieved_deal.id, deal.id)
        self.assertEqual(retrieved_deal.name, deal.name)
        
        # Test entity set
        for entity_id in ["govt1", "govt2", "corp1"]:
            self.assertIn(entity_id, retrieved_deal.entities)
        
        # Test value edges
        self.assertEqual(len(retrieved_deal.value_edges), 4)
        
        # Test total value calculation
        total_value = retrieved_deal.get_total_value()
        self.assertGreater(total_value, 0.0)
        
        # Expected value: sum of all edge values = 30 + 20 + 25 + 10 + 15 + 10 + 20 + 15 = 145
        expected_value = 30.0 + 20.0 + 25.0 + 10.0 + 15.0 + 10.0 + 20.0 + 15.0
        self.assertAlmostEqual(total_value, expected_value, places=5)
    
    def test_entity_value_calculation(self):
        """Test entity value calculation in a deal."""
        deal = self.deal
        
        # Calculate value for each entity
        for entity_id in deal.entities:
            entity_value = deal.get_entity_value(entity_id)
            self.assertIsNotNone(entity_value)
            # Each entity should have values for at least one dimension
            self.assertTrue(len(entity_value) > 0)
    
    def test_win_win_status(self):
        """Test win-win status determination for a deal."""
        deal = self.deal
        
        # Get entity preferences
        entity_preferences = {
            entity_id: self.graph.entities[entity_id].preferences
            for entity_id in deal.entities
            if entity_id in self.graph.entities
        }
        
        # Check if the deal is win-win
        is_win_win, entity_values = deal.is_win_win(entity_preferences)
        
        # Each entity should have a subjective value
        for entity_id in deal.entities:
            self.assertIn(entity_id, entity_values)
    
    def test_deal_optimization(self):
        """Test deal optimization in the O3 process."""
        result = self.optimizer.optimize_deal_values("deal1")
        
        self.assertIsNotNone(result)
        self.assertIn("deal_id", result)
        self.assertIn("status", result)
        self.assertIn("entity_values", result)
        
        # The deal should either be already win-win or optimized to be win-win
        self.assertIn(result["status"], ["already_win_win", "optimized"])
    
    def test_roadmap_optimization(self):
        """Test roadmap optimization in the O3 process."""
        # Create a test deal first to ensure we have enough deals for a roadmap
        test_deal = DealHyperedge(
            id="deal2",
            name="Community Development Initiative",
            entities=["govt2", "ngo1"],
            intent="Boost economic development in underserved communities"
        )
        
        value_edges = [
            ValueEdge(
                source_id="govt2",
                target_id="ngo1",
                value={"economic": 20.0, "social": 30.0},
                deal_id="deal2"
            ),
            ValueEdge(
                source_id="ngo1",
                target_id="govt2",
                value={"mission": 25.0, "reputation": 15.0},
                deal_id="deal2"
            )
        ]
        
        for edge in value_edges:
            test_deal.add_value_edge(edge)
        
        self.graph.add_deal(test_deal)
        
        # Optimize roadmap
        roadmap = self.optimizer.optimize_roadmap(
            entity_ids=["govt1", "govt2", "corp1", "ngo1"],
            max_deals=3,
            objective="total_value"
        )
        
        self.assertIsNotNone(roadmap)
        self.assertIn(roadmap.id, self.graph.roadmaps)
        
        # Roadmap should include at least one deal
        self.assertTrue(len(roadmap.deals) > 0)
        
        # Roadmap should have dependencies and timeline
        self.assertIsNotNone(roadmap.dependencies)
        self.assertIsNotNone(roadmap.timeline)
    
    def test_monte_carlo_simulation(self):
        """Test Monte Carlo simulation of a roadmap."""
        # Create a roadmap for simulation
        roadmap = DealRoadmap(
            id="roadmap1",
            name="Test Roadmap",
            deals=["deal1"],
            dependencies={},
            timeline={"deal1": {"start": 0, "duration": 90, "end": 90}},
            objectives={"primary_objective": "total_value"}
        )
        
        self.graph.add_roadmap(roadmap)
        
        # Run simulation
        simulation = self.optimizer.monte_carlo_roadmap_simulation(
            roadmap_id="roadmap1",
            num_simulations=10  # Small number for testing
        )
        
        self.assertIsNotNone(simulation)
        self.assertIn("roadmap_id", simulation)
        self.assertIn("num_simulations", simulation)
        self.assertIn("simulations", simulation)
        self.assertIn("summary", simulation)
        
        # Check summary statistics
        summary = simulation["summary"]
        self.assertIn("success_rate", summary)
        self.assertIn("expected_value", summary)
        self.assertIn("value_at_risk", summary)
        self.assertIn("expected_duration", summary)

class TestIntegration(unittest.TestCase):
    """Integration tests for the Moneyball Deal Model."""
    
    def setUp(self):
        """Setup test fixtures."""
        if not IMPORT_SUCCESS:
            self.skipTest("Required modules could not be imported")
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a sample agency file
        self.agency_file = os.path.join(self.temp_dir, "test_agency.md")
        with open(self.agency_file, "w") as f:
            f.write("""# Test Agency Use Case

Test Agency focuses on economic development.

## Problem Statement

Test Agency faces several challenges:

- Data fragmentation
- Limited resources
- Complex stakeholder landscape

## Stakeholders

The key stakeholders include:

- Government entities
- Private sector partners
- Non-profit organizations
- Community representatives

## Existing Solutions

Current approaches have limitations...

""")
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    @patch('update_agency_docs.get_agency_details')
    def test_documentation_update(self, mock_get_agency_details):
        """Test agency documentation update process."""
        # Skip if update_agency_docs module is not available
        if 'update_agency_docs' not in sys.modules:
            self.skipTest("update_agency_docs module not available")
        
        # Mock agency details
        mock_get_agency_details.return_value = {
            "agency_id": "TEST",
            "agency_name": "Test Agency",
            "domain": "economic development",
            "stakeholders": ["Government entities", "Private sector partners", "Non-profit organizations"],
            "challenges": ["Data fragmentation", "Limited resources", "Complex stakeholder landscape"]
        }
        
        # Create a sample template
        template_file = os.path.join(self.temp_dir, "template.md")
        with open(template_file, "w") as f:
            f.write("""# Moneyball Deal Model: [AGENCY_NAME] Implementation

[AGENCY_NAME] faces challenges including:
- Siloed information and decision-making processes
- Misaligned incentives between stakeholders
- Difficulty quantifying value across different dimensions

## Deal Structure
The deal model enables [AGENCY_NAME] to optimize value in [domain].
""")
        
        # Run the customization
        from update_agency_docs import customize_template
        custom_content = customize_template(template_file, mock_get_agency_details.return_value)
        
        # Check that content was customized
        self.assertIn("Test Agency", custom_content)
        self.assertIn("economic development", custom_content)
        
        # Check that challenges were customized
        self.assertIn("Data fragmentation", custom_content)
        self.assertIn("Limited resources", custom_content)
        self.assertIn("Complex stakeholder landscape", custom_content)
    
    def test_end_to_end_process(self):
        """Test end-to-end deal process."""
        # 1. Create a deal
        deal = create_moneyball_deal(
            intent_description="Increase economic development",
            solutions=["Funding program", "Technical assistance"],
            stakeholders=["Government", "Businesses", "Non-profits"],
            financing={"public": 1000000, "private": 2000000, "grants": 500000},
            expertise=["Program management", "Technical support", "Evaluation"]
        )
        
        # 2. Check if it's win-win
        analysis = analyze_deal_value(deal)
        is_win_win = analysis['is_win_win']
        
        if not is_win_win:
            # 3. Create a hypergraph and optimize the deal
            graph = DealHypergraph()
            
            # Add entities
            for stakeholder in deal.stakeholders:
                entity = EntityNode(
                    id=stakeholder.id,
                    name=stakeholder.name,
                    entity_type=stakeholder.type,
                    preferences=stakeholder.value_preferences
                )
                graph.add_entity(entity)
            
            # Create a deal hyperedge
            hyperedge = DealHyperedge(
                id=deal.id,
                name=deal.name,
                entities=[s.id for s in deal.stakeholders],
                intent=deal.intent.description
            )
            
            # Add deal to graph
            graph.add_deal(hyperedge)
            
            # Optimize
            optimizer = O3Optimizer(graph)
            optimization_result = optimizer.optimize_deal_values(deal.id)
            
            # Check if optimization succeeded
            self.assertIn(optimization_result["status"], ["already_win_win", "optimized"])
        
        # 4. Create a monitoring system for the deal
        monitoring_system = DealMonitoringSystem()
        
        # Add sample metrics
        metric = DealMetric(
            id="metric1",
            name="Funds Deployed",
            dimension="economic",
            component="financing",
            entity_id=deal.stakeholders[0].id,
            units="dollars",
            frequency="monthly",
            target_values={"m3": 1000000, "m6": 2000000},
            actual_values={"m3": 950000},
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            is_critical=True
        )
        
        monitoring_system.add_metric(metric)
        
        # 5. Create a dashboard
        dashboard = monitoring_system.create_dashboard(deal.id)
        
        # Verify dashboard
        self.assertIsNotNone(dashboard)
        self.assertIn("metrics", dashboard)
        self.assertTrue(len(dashboard["metrics"]) > 0)

if __name__ == '__main__':
    unittest.main()