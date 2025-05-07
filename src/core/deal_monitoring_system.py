"""
Real-Time Deal Monitoring System for Moneyball Deal Model

This module implements a comprehensive monitoring system for real-time
evaluation of deals across the HMS ecosystem. It tracks deal performance,
compares against projections, and provides early warning for deals at risk.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Tuple, Optional, Union
from dataclasses import dataclass
import datetime
import json
import io
import base64
import math
from collections import defaultdict
import time
import threading

# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class DealMetric:
    """A tracked metric for a deal."""
    id: str
    name: str
    dimension: str  # economic, social, environmental, etc.
    component: str  # Which deal component this belongs to
    entity_id: str  # Which entity this metric is for
    units: str  # Units of measurement (dollars, people, etc.)
    frequency: str  # daily, weekly, monthly, quarterly
    target_values: Dict[str, float]  # Target values by time period
    actual_values: Dict[str, float]  # Actual values by time period
    created_at: datetime.datetime
    updated_at: datetime.datetime
    is_critical: bool  # Whether this is a critical metric to track

@dataclass
class MonitoringAlert:
    """An alert triggered by monitoring system."""
    id: str
    deal_id: str
    metric_id: str
    alert_type: str  # negative_variance, critical_threshold, trend
    severity: str  # info, warning, critical
    timestamp: datetime.datetime
    description: str
    value: float
    threshold: float
    recommended_actions: List[str]
    status: str  # new, acknowledged, resolved
    acknowledged_by: str = None
    resolved_at: datetime.datetime = None
    resolution_notes: str = None

@dataclass
class DealStatus:
    """Current status of a deal."""
    deal_id: str
    overall_health: float  # 0-1 score
    component_health: Dict[str, float]  # Health by component
    entity_health: Dict[str, float]  # Health by entity
    alerts: List[MonitoringAlert]
    current_stage: str
    is_on_track: bool
    variance_summary: Dict[str, Any]
    last_updated: datetime.datetime

@dataclass
class HistoricalPerformance:
    """Historical performance data for comparative analysis."""
    metric_id: str
    values: Dict[str, float]  # Values by time period
    mean: float
    std_dev: float
    min_value: float
    max_value: float
    trend_slope: float
    seasonal_factors: Dict[str, float]  # Seasonal adjustment factors

@dataclass
class PredictiveModel:
    """Predictive model for forecasting metric values."""
    metric_id: str
    model_type: str  # arima, ets, prophet, linear, etc.
    parameters: Dict[str, Any]
    last_training_date: datetime.datetime
    forecast_horizon: int  # Number of periods to forecast
    forecast_values: Dict[str, float]  # Forecasted values by time period
    forecast_intervals: Dict[str, Tuple[float, float]]  # Prediction intervals
    accuracy_metrics: Dict[str, float]  # MAPE, RMSE, etc.

# =============================================================================
# Monitoring System Core
# =============================================================================

class DealMonitoringSystem:
    """
    Real-time monitoring system for deal evaluation.
    
    This class implements the core functionality for tracking deal metrics,
    generating alerts, and providing performance dashboards.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the monitoring system.
        
        Args:
            config: Configuration parameters
        """
        self.config = config or {}
        self.metrics = {}  # Dictionary of metrics by metric_id
        self.alerts = {}  # Dictionary of alerts by alert_id
        self.deal_status = {}  # Dictionary of deal status by deal_id
        self.historical_performance = {}  # Historical performance by metric_id
        self.predictive_models = {}  # Predictive models by metric_id
        
        # Alert thresholds
        self.alert_thresholds = self.config.get('alert_thresholds', {
            'critical_negative_variance': -0.15,  # 15% below target
            'warning_negative_variance': -0.05,  # 5% below target
            'critical_positive_variance': 0.25,  # 25% above target (can indicate data issues)
            'warning_positive_variance': 0.15,  # 15% above target
            'trend_detection_periods': 3,  # Number of periods for trend detection
            'trend_threshold': -0.1  # 10% downward trend
        })
        
        # Initialize monitoring threads
        self.monitoring_active = False
        self.monitoring_thread = None
    
    def register_metric(self, metric: DealMetric) -> str:
        """
        Register a new metric to be tracked.
        
        Args:
            metric: DealMetric object
            
        Returns:
            Metric ID
        """
        # Update timestamps
        current_time = datetime.datetime.now()
        metric.created_at = current_time
        metric.updated_at = current_time
        
        # Store metric
        self.metrics[metric.id] = metric
        
        # Initialize historical performance
        if metric.id not in self.historical_performance:
            self.historical_performance[metric.id] = HistoricalPerformance(
                metric_id=metric.id,
                values={},
                mean=0.0,
                std_dev=0.0,
                min_value=float('inf'),
                max_value=float('-inf'),
                trend_slope=0.0,
                seasonal_factors={}
            )
        
        return metric.id
    
    def update_metric(self, metric_id: str, time_period: str, actual_value: float) -> None:
        """
        Update a metric with an actual value for a time period.
        
        Args:
            metric_id: Metric ID
            time_period: Time period (e.g., "2023-Q1", "2023-01", etc.)
            actual_value: Actual value for the period
        """
        if metric_id not in self.metrics:
            raise ValueError(f"Metric {metric_id} not found")
        
        # Update metric
        metric = self.metrics[metric_id]
        metric.actual_values[time_period] = actual_value
        metric.updated_at = datetime.datetime.now()
        
        # Update historical performance
        hist_perf = self.historical_performance[metric_id]
        hist_perf.values[time_period] = actual_value
        
        # Recalculate statistics
        if hist_perf.values:
            values = list(hist_perf.values.values())
            hist_perf.mean = np.mean(values)
            hist_perf.std_dev = np.std(values)
            hist_perf.min_value = min(values)
            hist_perf.max_value = max(values)
        
        # Check for alerts
        self._check_for_alerts(metric_id, time_period)
        
        # Update deal status
        if metric.deal_id in self.deal_status:
            self._update_deal_status(metric.deal_id)
    
    def _check_for_alerts(self, metric_id: str, time_period: str) -> None:
        """
        Check if a metric update should trigger alerts.
        
        Args:
            metric_id: Metric ID
            time_period: Time period
        """
        metric = self.metrics[metric_id]
        
        # Skip if no target for this period
        if time_period not in metric.target_values:
            return
        
        target_value = metric.target_values[time_period]
        actual_value = metric.actual_values[time_period]
        
        # Calculate variance
        if target_value != 0:
            variance_pct = (actual_value - target_value) / abs(target_value)
        else:
            variance_pct = 0 if actual_value == 0 else float('inf')
        
        # Check for negative variance
        if variance_pct < self.alert_thresholds['critical_negative_variance'] and metric.is_critical:
            self._create_alert(
                deal_id=metric.deal_id,
                metric_id=metric_id,
                alert_type='negative_variance',
                severity='critical',
                description=f"Critical negative variance for {metric.name}",
                value=actual_value,
                threshold=target_value,
                recommended_actions=[
                    f"Review {metric.component} component",
                    f"Meet with stakeholder {metric.entity_id}",
                    "Adjust projections or implement corrective actions"
                ]
            )
        elif variance_pct < self.alert_thresholds['warning_negative_variance']:
            self._create_alert(
                deal_id=metric.deal_id,
                metric_id=metric_id,
                alert_type='negative_variance',
                severity='warning',
                description=f"Negative variance for {metric.name}",
                value=actual_value,
                threshold=target_value,
                recommended_actions=[
                    f"Monitor {metric.component} component",
                    "Prepare contingency plans"
                ]
            )
        
        # Check for unusually high positive variance (may indicate data issues)
        if variance_pct > self.alert_thresholds['critical_positive_variance']:
            self._create_alert(
                deal_id=metric.deal_id,
                metric_id=metric_id,
                alert_type='positive_variance',
                severity='warning',
                description=f"Unusually high positive variance for {metric.name}",
                value=actual_value,
                threshold=target_value,
                recommended_actions=[
                    "Verify data accuracy",
                    "Update projections if confirmed accurate"
                ]
            )
        
        # Check for trends
        self._check_for_trends(metric_id)
    
    def _check_for_trends(self, metric_id: str) -> None:
        """
        Check for concerning trends in a metric.
        
        Args:
            metric_id: Metric ID
        """
        metric = self.metrics[metric_id]
        hist_perf = self.historical_performance[metric_id]
        
        # Need at least N periods for trend detection
        n_periods = self.alert_thresholds['trend_detection_periods']
        if len(metric.actual_values) < n_periods:
            return
        
        # Get the most recent N periods
        periods = sorted(metric.actual_values.keys())[-n_periods:]
        values = [metric.actual_values[p] for p in periods]
        
        # Calculate simple trend (slope)
        x = np.arange(n_periods)
        if np.std(values) > 0:  # Avoid division by zero
            slope, _ = np.polyfit(x, values, 1)
            hist_perf.trend_slope = slope
            
            # Normalize slope as percentage of mean value
            if hist_perf.mean != 0:
                normalized_slope = slope / abs(hist_perf.mean)
                
                # Check for negative trend
                if normalized_slope < self.alert_thresholds['trend_threshold'] and metric.is_critical:
                    self._create_alert(
                        deal_id=metric.deal_id,
                        metric_id=metric_id,
                        alert_type='negative_trend',
                        severity='warning',
                        description=f"Negative trend detected for {metric.name}",
                        value=normalized_slope,
                        threshold=self.alert_thresholds['trend_threshold'],
                        recommended_actions=[
                            f"Investigate {metric.component} component",
                            "Review external factors",
                            "Update risk assessment"
                        ]
                    )
    
    def _create_alert(
        self,
        deal_id: str,
        metric_id: str,
        alert_type: str,
        severity: str,
        description: str,
        value: float,
        threshold: float,
        recommended_actions: List[str]
    ) -> str:
        """
        Create a new alert.
        
        Args:
            deal_id: Deal ID
            metric_id: Metric ID
            alert_type: Type of alert
            severity: Alert severity
            description: Alert description
            value: Current value
            threshold: Threshold value
            recommended_actions: List of recommended actions
            
        Returns:
            Alert ID
        """
        # Generate alert ID
        alert_id = f"ALT-{int(time.time())}-{hash(f'{deal_id}-{metric_id}-{alert_type}') % 10000:04d}"
        
        # Create alert
        alert = MonitoringAlert(
            id=alert_id,
            deal_id=deal_id,
            metric_id=metric_id,
            alert_type=alert_type,
            severity=severity,
            timestamp=datetime.datetime.now(),
            description=description,
            value=value,
            threshold=threshold,
            recommended_actions=recommended_actions,
            status='new'
        )
        
        # Store alert
        self.alerts[alert_id] = alert
        
        # Add to deal status
        if deal_id in self.deal_status:
            self.deal_status[deal_id].alerts.append(alert)
        
        return alert_id
    
    def _update_deal_status(self, deal_id: str) -> None:
        """
        Update the status of a deal based on its metrics.
        
        Args:
            deal_id: Deal ID
        """
        # Get deal metrics
        deal_metrics = {m_id: m for m_id, m in self.metrics.items() if m.deal_id == deal_id}
        
        if not deal_metrics:
            return
        
        # Get current time period for each frequency
        current_periods = self._get_current_periods()
        
        # Calculate component health
        component_health = {}
        for metric_id, metric in deal_metrics.items():
            # Skip if no data for current period
            period = current_periods.get(metric.frequency)
            if not period:
                continue
            
            if period not in metric.target_values or period not in metric.actual_values:
                continue
            
            # Calculate health score for this metric
            target = metric.target_values[period]
            actual = metric.actual_values[period]
            
            if target != 0:
                variance_pct = (actual - target) / abs(target)
            else:
                variance_pct = 0 if actual == 0 else float('inf')
            
            # Convert variance to health score (0-1)
            # 0 = very unhealthy, 1 = very healthy
            if variance_pct >= 0:
                # Cap positive variance at 25%
                health_score = min(1.0, 0.75 + variance_pct / 4)
            else:
                # Negative variance is worse
                health_score = max(0.0, 0.75 + variance_pct)
            
            # Apply critical flag weight
            if metric.is_critical:
                health_score = health_score ** 2  # Square to amplify low scores
            
            # Add to component health
            if metric.component not in component_health:
                component_health[metric.component] = []
            
            component_health[metric.component].append(health_score)
        
        # Calculate average health for each component
        component_health = {
            c: np.mean(scores) for c, scores in component_health.items()
        }
        
        # Calculate entity health
        entity_health = {}
        for metric_id, metric in deal_metrics.items():
            # Skip if no data for current period
            period = current_periods.get(metric.frequency)
            if not period:
                continue
            
            if period not in metric.target_values or period not in metric.actual_values:
                continue
            
            # Calculate health score for this metric
            target = metric.target_values[period]
            actual = metric.actual_values[period]
            
            if target != 0:
                variance_pct = (actual - target) / abs(target)
            else:
                variance_pct = 0 if actual == 0 else float('inf')
            
            # Convert variance to health score (0-1)
            if variance_pct >= 0:
                health_score = min(1.0, 0.75 + variance_pct / 4)
            else:
                health_score = max(0.0, 0.75 + variance_pct)
            
            # Apply critical flag weight
            if metric.is_critical:
                health_score = health_score ** 2
            
            # Add to entity health
            if metric.entity_id not in entity_health:
                entity_health[metric.entity_id] = []
            
            entity_health[metric.entity_id].append(health_score)
        
        # Calculate average health for each entity
        entity_health = {
            e: np.mean(scores) for e, scores in entity_health.items()
        }
        
        # Calculate overall health
        # Weight critical components more heavily
        critical_components = self.config.get('critical_components', [])
        critical_entities = self.config.get('critical_entities', [])
        
        # Start with average of all components
        if component_health:
            overall_health = np.mean(list(component_health.values()))
        else:
            overall_health = 0.5  # Default if no data
        
        # Adjust for critical components
        for component in critical_components:
            if component in component_health:
                # Adjust overall health down if critical component is unhealthy
                critical_weight = self.config.get('critical_component_weight', 2.0)
                health_diff = component_health[component] - overall_health
                overall_health += health_diff * (critical_weight - 1)
        
        # Adjust for critical entities
        for entity_id in critical_entities:
            if entity_id in entity_health:
                # Adjust overall health down if critical entity is unhealthy
                critical_weight = self.config.get('critical_entity_weight', 2.0)
                health_diff = entity_health[entity_id] - overall_health
                overall_health += health_diff * (critical_weight - 1)
        
        # Calculate variance summary
        variance_summary = self._calculate_variance_summary(deal_id, deal_metrics, current_periods)
        
        # Determine if deal is on track
        open_critical_alerts = sum(1 for a in self.alerts.values() 
                                if a.deal_id == deal_id and 
                                   a.severity == 'critical' and 
                                   a.status != 'resolved')
        
        is_on_track = (overall_health >= 0.7) and (open_critical_alerts == 0)
        
        # Determine current stage
        # This would be based on deal-specific logic
        current_stage = "unknown"
        
        # Create or update deal status
        if deal_id in self.deal_status:
            status = self.deal_status[deal_id]
            status.overall_health = overall_health
            status.component_health = component_health
            status.entity_health = entity_health
            status.is_on_track = is_on_track
            status.variance_summary = variance_summary
            status.current_stage = current_stage
            status.last_updated = datetime.datetime.now()
        else:
            # Get active alerts for this deal
            deal_alerts = [a for a in self.alerts.values() if a.deal_id == deal_id and a.status != 'resolved']
            
            # Create new status
            status = DealStatus(
                deal_id=deal_id,
                overall_health=overall_health,
                component_health=component_health,
                entity_health=entity_health,
                alerts=deal_alerts,
                current_stage=current_stage,
                is_on_track=is_on_track,
                variance_summary=variance_summary,
                last_updated=datetime.datetime.now()
            )
            
            self.deal_status[deal_id] = status
    
    def _get_current_periods(self) -> Dict[str, str]:
        """
        Get current time periods for different frequencies.
        
        Returns:
            Dictionary of current periods by frequency
        """
        now = datetime.datetime.now()
        
        return {
            'daily': now.strftime('%Y-%m-%d'),
            'weekly': f"{now.year}-W{now.isocalendar()[1]:02d}",
            'monthly': now.strftime('%Y-%m'),
            'quarterly': f"{now.year}-Q{(now.month - 1) // 3 + 1}",
            'yearly': str(now.year)
        }
    
    def _calculate_variance_summary(
        self,
        deal_id: str,
        deal_metrics: Dict[str, DealMetric],
        current_periods: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Calculate variance summary for a deal.
        
        Args:
            deal_id: Deal ID
            deal_metrics: Dictionary of deal metrics
            current_periods: Dictionary of current periods by frequency
            
        Returns:
            Variance summary
        """
        # Initialize summary
        summary = {
            'total_metrics': len(deal_metrics),
            'metrics_with_data': 0,
            'metrics_above_target': 0,
            'metrics_on_target': 0,
            'metrics_below_target': 0,
            'avg_positive_variance': 0.0,
            'avg_negative_variance': 0.0,
            'largest_positive_variance': {
                'metric_id': None,
                'variance_pct': 0.0
            },
            'largest_negative_variance': {
                'metric_id': None,
                'variance_pct': 0.0
            }
        }
        
        # Collect variances
        positive_variances = []
        negative_variances = []
        
        for metric_id, metric in deal_metrics.items():
            # Skip if no data for current period
            period = current_periods.get(metric.frequency)
            if not period:
                continue
            
            if period not in metric.target_values or period not in metric.actual_values:
                continue
            
            # Count metrics with data
            summary['metrics_with_data'] += 1
            
            # Calculate variance
            target = metric.target_values[period]
            actual = metric.actual_values[period]
            
            if target != 0:
                variance_pct = (actual - target) / abs(target)
            else:
                variance_pct = 0 if actual == 0 else float('inf')
            
            # Categorize variance
            if abs(variance_pct) < 0.05:  # Within 5% of target
                summary['metrics_on_target'] += 1
            elif variance_pct > 0:
                summary['metrics_above_target'] += 1
                positive_variances.append(variance_pct)
                
                # Check if largest positive variance
                if variance_pct > summary['largest_positive_variance']['variance_pct']:
                    summary['largest_positive_variance'] = {
                        'metric_id': metric_id,
                        'metric_name': metric.name,
                        'variance_pct': variance_pct
                    }
            else:
                summary['metrics_below_target'] += 1
                negative_variances.append(variance_pct)
                
                # Check if largest negative variance
                if variance_pct < summary['largest_negative_variance']['variance_pct']:
                    summary['largest_negative_variance'] = {
                        'metric_id': metric_id,
                        'metric_name': metric.name,
                        'variance_pct': variance_pct
                    }
        
        # Calculate averages
        if positive_variances:
            summary['avg_positive_variance'] = np.mean(positive_variances)
        if negative_variances:
            summary['avg_negative_variance'] = np.mean(negative_variances)
        
        return summary
    
    def get_deal_status(self, deal_id: str) -> Optional[DealStatus]:
        """
        Get the current status of a deal.
        
        Args:
            deal_id: Deal ID
            
        Returns:
            DealStatus object or None if deal not found
        """
        if deal_id not in self.deal_status:
            # Try to compute it
            deal_metrics = {m_id: m for m_id, m in self.metrics.items() if m.deal_id == deal_id}
            if deal_metrics:
                self._update_deal_status(deal_id)
        
        return self.deal_status.get(deal_id)
    
    def get_alerts(
        self,
        deal_id: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[MonitoringAlert]:
        """
        Get alerts filtered by criteria.
        
        Args:
            deal_id: Filter by deal ID
            severity: Filter by severity
            status: Filter by status
            
        Returns:
            List of filtered alerts
        """
        filtered_alerts = []
        
        for alert in self.alerts.values():
            # Apply filters
            if deal_id and alert.deal_id != deal_id:
                continue
            if severity and alert.severity != severity:
                continue
            if status and alert.status != status:
                continue
            
            # Add to filtered list
            filtered_alerts.append(alert)
        
        # Sort by timestamp (newest first)
        filtered_alerts.sort(key=lambda a: a.timestamp, reverse=True)
        
        return filtered_alerts
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> None:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: Alert ID
            acknowledged_by: Name of acknowledger
        """
        if alert_id not in self.alerts:
            raise ValueError(f"Alert {alert_id} not found")
        
        alert = self.alerts[alert_id]
        alert.status = 'acknowledged'
        alert.acknowledged_by = acknowledged_by
    
    def resolve_alert(self, alert_id: str, resolution_notes: str) -> None:
        """
        Resolve an alert.
        
        Args:
            alert_id: Alert ID
            resolution_notes: Notes on resolution
        """
        if alert_id not in self.alerts:
            raise ValueError(f"Alert {alert_id} not found")
        
        alert = self.alerts[alert_id]
        alert.status = 'resolved'
        alert.resolved_at = datetime.datetime.now()
        alert.resolution_notes = resolution_notes
    
    def start_monitoring(self, update_interval: int = 60) -> None:
        """
        Start the monitoring thread.
        
        Args:
            update_interval: Interval between updates in seconds
        """
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        def monitoring_loop():
            while self.monitoring_active:
                # Update all deal statuses
                for deal_id in set(m.deal_id for m in self.metrics.values()):
                    try:
                        self._update_deal_status(deal_id)
                    except Exception as e:
                        print(f"Error updating status for deal {deal_id}: {e}")
                
                # Update predictive models
                try:
                    self._update_predictive_models()
                except Exception as e:
                    print(f"Error updating predictive models: {e}")
                
                # Sleep until next update
                time.sleep(update_interval)
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring thread."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
    
    def _update_predictive_models(self) -> None:
        """Update predictive models for all metrics."""
        for metric_id, metric in self.metrics.items():
            # Skip if not enough data
            if len(metric.actual_values) < 5:  # Need at least 5 data points
                continue
            
            # Skip if model was updated recently
            if metric_id in self.predictive_models:
                model = self.predictive_models[metric_id]
                days_since_update = (datetime.datetime.now() - model.last_training_date).days
                
                # Only update weekly
                if days_since_update < 7:
                    continue
            
            # Use simple linear regression for forecasting
            try:
                # Sort periods and values
                periods = sorted(metric.actual_values.keys())
                values = [metric.actual_values[p] for p in periods]
                
                # Convert periods to numeric values
                x = np.arange(len(periods))
                
                # Fit linear model
                slope, intercept = np.polyfit(x, values, 1)
                
                # Generate forecast
                forecast_horizon = 5  # Forecast 5 periods ahead
                forecast_x = np.arange(len(periods), len(periods) + forecast_horizon)
                forecast_values = slope * forecast_x + intercept
                
                # Calculate prediction intervals
                # Using standard error of regression for simplicity
                y_pred = slope * x + intercept
                rmse = np.sqrt(np.mean((np.array(values) - y_pred) ** 2))
                
                # Create forecast dictionaries
                next_periods = self._generate_next_periods(periods[-1], metric.frequency, forecast_horizon)
                forecast_values_dict = {p: v for p, v in zip(next_periods, forecast_values)}
                
                # Create prediction intervals (mean ± 2*rmse for ~95% confidence)
                forecast_intervals = {
                    p: (v - 2 * rmse, v + 2 * rmse) 
                    for p, v in zip(next_periods, forecast_values)
                }
                
                # Calculate accuracy metrics
                mape = np.mean(np.abs((np.array(values) - y_pred) / np.array(values))) * 100
                
                # Create or update model
                model = PredictiveModel(
                    metric_id=metric_id,
                    model_type='linear',
                    parameters={
                        'slope': float(slope),
                        'intercept': float(intercept)
                    },
                    last_training_date=datetime.datetime.now(),
                    forecast_horizon=forecast_horizon,
                    forecast_values=forecast_values_dict,
                    forecast_intervals=forecast_intervals,
                    accuracy_metrics={
                        'rmse': float(rmse),
                        'mape': float(mape)
                    }
                )
                
                self.predictive_models[metric_id] = model
            
            except Exception as e:
                print(f"Error updating predictive model for metric {metric_id}: {e}")
    
    def _generate_next_periods(self, last_period: str, frequency: str, n: int) -> List[str]:
        """
        Generate the next n periods after a given period.
        
        Args:
            last_period: Last period (e.g., "2023-Q1", "2023-01", etc.)
            frequency: Frequency (daily, weekly, monthly, quarterly, yearly)
            n: Number of periods to generate
            
        Returns:
            List of next periods
        """
        next_periods = []
        
        if frequency == 'daily':
            # Format: YYYY-MM-DD
            last_date = datetime.datetime.strptime(last_period, '%Y-%m-%d')
            for i in range(1, n + 1):
                next_date = last_date + datetime.timedelta(days=i)
                next_periods.append(next_date.strftime('%Y-%m-%d'))
        
        elif frequency == 'weekly':
            # Format: YYYY-Www
            year, week = last_period.split('-W')
            year = int(year)
            week = int(week)
            
            for i in range(1, n + 1):
                next_week = week + i
                next_year = year
                
                # Handle year overflow
                while next_week > 52:
                    next_week -= 52
                    next_year += 1
                
                next_periods.append(f"{next_year}-W{next_week:02d}")
        
        elif frequency == 'monthly':
            # Format: YYYY-MM
            year, month = last_period.split('-')
            year = int(year)
            month = int(month)
            
            for i in range(1, n + 1):
                next_month = month + i
                next_year = year
                
                # Handle year overflow
                while next_month > 12:
                    next_month -= 12
                    next_year += 1
                
                next_periods.append(f"{next_year}-{next_month:02d}")
        
        elif frequency == 'quarterly':
            # Format: YYYY-Qn
            year, quarter = last_period.split('-Q')
            year = int(year)
            quarter = int(quarter)
            
            for i in range(1, n + 1):
                next_quarter = quarter + i
                next_year = year
                
                # Handle year overflow
                while next_quarter > 4:
                    next_quarter -= 4
                    next_year += 1
                
                next_periods.append(f"{next_year}-Q{next_quarter}")
        
        elif frequency == 'yearly':
            # Format: YYYY
            year = int(last_period)
            
            for i in range(1, n + 1):
                next_periods.append(str(year + i))
        
        return next_periods
    
    def get_metric_forecast(self, metric_id: str) -> Optional[Dict[str, Any]]:
        """
        Get forecast for a metric.
        
        Args:
            metric_id: Metric ID
            
        Returns:
            Dictionary with forecast data or None if not available
        """
        if metric_id not in self.predictive_models:
            return None
        
        model = self.predictive_models[metric_id]
        metric = self.metrics.get(metric_id)
        
        if not metric:
            return None
        
        # Prepare forecast data
        forecast = {
            'metric_name': metric.name,
            'forecast_type': model.model_type,
            'last_training_date': model.last_training_date.isoformat(),
            'accuracy': model.accuracy_metrics,
            'periods': [],
            'values': [],
            'lower_bounds': [],
            'upper_bounds': []
        }
        
        # Add forecast values
        for period, value in sorted(model.forecast_values.items()):
            forecast['periods'].append(period)
            forecast['values'].append(value)
            
            lower, upper = model.forecast_intervals.get(period, (value, value))
            forecast['lower_bounds'].append(lower)
            forecast['upper_bounds'].append(upper)
        
        return forecast
    
    def generate_dashboard(self, deal_id: str) -> Dict[str, Any]:
        """
        Generate a dashboard for a deal.
        
        Args:
            deal_id: Deal ID
            
        Returns:
            Dictionary with dashboard data
        """
        status = self.get_deal_status(deal_id)
        if not status:
            return {"error": f"Deal {deal_id} not found"}
        
        # Get deal metrics
        deal_metrics = {m_id: m for m_id, m in self.metrics.items() if m.deal_id == deal_id}
        
        # Get current periods
        current_periods = self._get_current_periods()
        
        # Prepare dashboard data
        dashboard = {
            'deal_id': deal_id,
            'overall_health': status.overall_health,
            'is_on_track': status.is_on_track,
            'current_stage': status.current_stage,
            'last_updated': status.last_updated.isoformat(),
            'component_health': status.component_health,
            'entity_health': status.entity_health,
            'variance_summary': status.variance_summary,
            'alerts': [
                {
                    'id': a.id,
                    'type': a.alert_type,
                    'severity': a.severity,
                    'description': a.description,
                    'timestamp': a.timestamp.isoformat(),
                    'status': a.status
                }
                for a in self.get_alerts(deal_id=deal_id, status='new')
            ],
            'metrics': [],
            'forecasts': []
        }
        
        # Add metrics data
        for metric_id, metric in deal_metrics.items():
            # Create time series data
            time_series = []
            for period, actual in sorted(metric.actual_values.items()):
                target = metric.target_values.get(period)
                time_series.append({
                    'period': period,
                    'actual': actual,
                    'target': target
                })
            
            # Add to metrics list
            dashboard['metrics'].append({
                'id': metric_id,
                'name': metric.name,
                'dimension': metric.dimension,
                'component': metric.component,
                'entity_id': metric.entity_id,
                'is_critical': metric.is_critical,
                'time_series': time_series
            })
        
        # Add forecasts
        for metric_id in deal_metrics:
            forecast = self.get_metric_forecast(metric_id)
            if forecast:
                dashboard['forecasts'].append(forecast)
        
        return dashboard
    
    def generate_dashboard_plot(
        self,
        deal_id: str,
        metric_ids: Optional[List[str]] = None,
        include_forecast: bool = True,
        plot_type: str = 'time_series'
    ) -> str:
        """
        Generate a plot for a dashboard.
        
        Args:
            deal_id: Deal ID
            metric_ids: List of metric IDs to include (None for all)
            include_forecast: Whether to include forecast
            plot_type: Type of plot (time_series, health_gauge, variance)
            
        Returns:
            Base64-encoded PNG image
        """
        # Get deal metrics
        deal_metrics = {m_id: m for m_id, m in self.metrics.items() if m.deal_id == deal_id}
        
        if not deal_metrics:
            return ""
        
        # Filter metrics if specified
        if metric_ids:
            deal_metrics = {m_id: m for m_id, m in deal_metrics.items() if m_id in metric_ids}
        
        if plot_type == 'time_series':
            return self._generate_time_series_plot(deal_metrics, include_forecast)
        elif plot_type == 'health_gauge':
            return self._generate_health_gauge_plot(deal_id)
        elif plot_type == 'variance':
            return self._generate_variance_plot(deal_metrics)
        else:
            return ""
    
    def _generate_time_series_plot(
        self,
        metrics: Dict[str, DealMetric],
        include_forecast: bool
    ) -> str:
        """
        Generate a time series plot for metrics.
        
        Args:
            metrics: Dictionary of metrics
            include_forecast: Whether to include forecast
            
        Returns:
            Base64-encoded PNG image
        """
        plt.figure(figsize=(10, 6))
        
        for metric_id, metric in metrics.items():
            # Skip if no data
            if not metric.actual_values:
                continue
            
            # Sort periods and values
            periods = sorted(metric.actual_values.keys())
            actuals = [metric.actual_values[p] for p in periods]
            targets = [metric.target_values.get(p, None) for p in periods]
            
            # Plot actual values
            plt.plot(periods, actuals, marker='o', label=f"{metric.name} (Actual)")
            
            # Plot target values
            valid_targets = [(p, t) for p, t in zip(periods, targets) if t is not None]
            if valid_targets:
                target_periods, target_values = zip(*valid_targets)
                plt.plot(target_periods, target_values, linestyle='--', marker='x', label=f"{metric.name} (Target)")
            
            # Add forecast if requested
            if include_forecast and metric_id in self.predictive_models:
                model = self.predictive_models[metric_id]
                forecast_periods = list(model.forecast_values.keys())
                forecast_values = [model.forecast_values[p] for p in forecast_periods]
                
                if forecast_periods:
                    # Plot forecast
                    plt.plot(forecast_periods, forecast_values, linestyle=':', marker='v', label=f"{metric.name} (Forecast)")
                    
                    # Plot confidence intervals
                    lower_bounds = [model.forecast_intervals[p][0] for p in forecast_periods]
                    upper_bounds = [model.forecast_intervals[p][1] for p in forecast_periods]
                    
                    plt.fill_between(forecast_periods, lower_bounds, upper_bounds, alpha=0.2)
        
        plt.xlabel('Time Period')
        plt.ylabel('Value')
        plt.title('Metric Time Series')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    def _generate_health_gauge_plot(self, deal_id: str) -> str:
        """
        Generate a health gauge plot for a deal.
        
        Args:
            deal_id: Deal ID
            
        Returns:
            Base64-encoded PNG image
        """
        status = self.get_deal_status(deal_id)
        if not status:
            return ""
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 4), subplot_kw={'projection': 'polar'})
        
        # Define gauge range (0 to 180 degrees)
        gauge_range = np.linspace(0, np.pi, 100)
        
        # Define color ranges
        red = gauge_range[gauge_range <= np.pi * 0.4]  # 0-40%
        yellow = gauge_range[(gauge_range > np.pi * 0.4) & (gauge_range <= np.pi * 0.7)]  # 40-70%
        green = gauge_range[gauge_range > np.pi * 0.7]  # 70-100%
        
        # Plot colored arcs
        ax.plot(red, [1] * len(red), 'r-', linewidth=20, alpha=0.6)
        ax.plot(yellow, [1] * len(yellow), 'y-', linewidth=20, alpha=0.6)
        ax.plot(green, [1] * len(green), 'g-', linewidth=20, alpha=0.6)
        
        # Convert health to angle
        health_angle = status.overall_health * np.pi
        
        # Plot needle
        ax.plot([0, health_angle], [0, 0.8], 'k-', linewidth=2)
        ax.plot([health_angle], [0.8], 'ko', markersize=8)
        
        # Configure gauge appearance
        ax.set_ylim(0, 1.5)
        ax.set_frame_on(False)
        ax.axes.get_yaxis().set_visible(False)
        ax.set_xticks(np.linspace(0, np.pi, 5))
        ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
        
        # Add deal name and health
        plt.title(f"Deal Health: {status.overall_health * 100:.1f}%")
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    def _generate_variance_plot(self, metrics: Dict[str, DealMetric]) -> str:
        """
        Generate a variance plot for metrics.
        
        Args:
            metrics: Dictionary of metrics
            
        Returns:
            Base64-encoded PNG image
        """
        # Get current periods
        current_periods = self._get_current_periods()
        
        # Calculate variances
        variances = []
        labels = []
        
        for metric_id, metric in metrics.items():
            # Skip if no data for current period
            period = current_periods.get(metric.frequency)
            if not period:
                continue
            
            if period not in metric.target_values or period not in metric.actual_values:
                continue
            
            # Calculate variance
            target = metric.target_values[period]
            actual = metric.actual_values[period]
            
            if target != 0:
                variance_pct = (actual - target) / abs(target) * 100
            else:
                variance_pct = 0 if actual == 0 else float('inf')
            
            # Add to list
            variances.append(variance_pct)
            labels.append(metric.name)
        
        if not variances:
            return ""
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Define color function
        def get_color(variance):
            if variance >= 0:
                return 'g' if variance <= 10 else 'y'
            else:
                return 'y' if variance >= -10 else 'r'
        
        # Plot horizontal bars
        y_pos = np.arange(len(labels))
        colors = [get_color(v) for v in variances]
        
        plt.barh(y_pos, variances, color=colors)
        plt.yticks(y_pos, labels)
        plt.xlabel('Variance (%)')
        plt.title('Metric Variances from Target')
        
        # Add reference line at 0
        plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        # Add reference lines for thresholds
        plt.axvline(x=-10, color='r', linestyle='--', alpha=0.3)
        plt.axvline(x=10, color='g', linestyle='--', alpha=0.3)
        
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    def create_metric(
        self,
        deal_id: str,
        name: str,
        dimension: str,
        component: str,
        entity_id: str,
        units: str,
        frequency: str,
        target_values: Dict[str, float],
        is_critical: bool = False
    ) -> str:
        """
        Create a new metric.
        
        Args:
            deal_id: Deal ID
            name: Metric name
            dimension: Value dimension
            component: Deal component
            entity_id: Entity ID
            units: Units of measurement
            frequency: Measurement frequency
            target_values: Target values by time period
            is_critical: Whether this is a critical metric
            
        Returns:
            Metric ID
        """
        # Generate metric ID
        metric_id = f"MET-{int(time.time())}-{hash(f'{deal_id}-{name}') % 10000:04d}"
        
        # Create metric
        metric = DealMetric(
            id=metric_id,
            name=name,
            dimension=dimension,
            component=component,
            entity_id=entity_id,
            units=units,
            frequency=frequency,
            target_values=target_values,
            actual_values={},
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            is_critical=is_critical
        )
        
        # Register metric
        self.register_metric(metric)
        
        return metric_id
    
    def export_data(self) -> Dict[str, Any]:
        """
        Export all monitoring data.
        
        Returns:
            Dictionary with all monitoring data
        """
        return {
            'metrics': {m_id: self._metric_to_dict(m) for m_id, m in self.metrics.items()},
            'alerts': {a_id: self._alert_to_dict(a) for a_id, a in self.alerts.items()},
            'deal_status': {d_id: self._status_to_dict(s) for d_id, s in self.deal_status.items()},
            'predictive_models': {p_id: self._model_to_dict(m) for p_id, m in self.predictive_models.items()}
        }
    
    def _metric_to_dict(self, metric: DealMetric) -> Dict[str, Any]:
        """Convert metric to dictionary."""
        return {
            'id': metric.id,
            'name': metric.name,
            'dimension': metric.dimension,
            'component': metric.component,
            'entity_id': metric.entity_id,
            'units': metric.units,
            'frequency': metric.frequency,
            'target_values': metric.target_values,
            'actual_values': metric.actual_values,
            'created_at': metric.created_at.isoformat(),
            'updated_at': metric.updated_at.isoformat(),
            'is_critical': metric.is_critical
        }
    
    def _alert_to_dict(self, alert: MonitoringAlert) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            'id': alert.id,
            'deal_id': alert.deal_id,
            'metric_id': alert.metric_id,
            'alert_type': alert.alert_type,
            'severity': alert.severity,
            'timestamp': alert.timestamp.isoformat(),
            'description': alert.description,
            'value': alert.value,
            'threshold': alert.threshold,
            'recommended_actions': alert.recommended_actions,
            'status': alert.status,
            'acknowledged_by': alert.acknowledged_by,
            'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
            'resolution_notes': alert.resolution_notes
        }
    
    def _status_to_dict(self, status: DealStatus) -> Dict[str, Any]:
        """Convert deal status to dictionary."""
        return {
            'deal_id': status.deal_id,
            'overall_health': status.overall_health,
            'component_health': status.component_health,
            'entity_health': status.entity_health,
            'alerts': [a.id for a in status.alerts],
            'current_stage': status.current_stage,
            'is_on_track': status.is_on_track,
            'variance_summary': status.variance_summary,
            'last_updated': status.last_updated.isoformat()
        }
    
    def _model_to_dict(self, model: PredictiveModel) -> Dict[str, Any]:
        """Convert predictive model to dictionary."""
        return {
            'metric_id': model.metric_id,
            'model_type': model.model_type,
            'parameters': model.parameters,
            'last_training_date': model.last_training_date.isoformat(),
            'forecast_horizon': model.forecast_horizon,
            'forecast_values': model.forecast_values,
            'forecast_intervals': {k: list(v) for k, v in model.forecast_intervals.items()},
            'accuracy_metrics': model.accuracy_metrics
        }
    
    def import_data(self, data: Dict[str, Any]) -> None:
        """
        Import monitoring data.
        
        Args:
            data: Dictionary with monitoring data
        """
        # Import metrics
        for metric_data in data.get('metrics', {}).values():
            metric = DealMetric(
                id=metric_data['id'],
                name=metric_data['name'],
                dimension=metric_data['dimension'],
                component=metric_data['component'],
                entity_id=metric_data['entity_id'],
                units=metric_data['units'],
                frequency=metric_data['frequency'],
                target_values=metric_data['target_values'],
                actual_values=metric_data['actual_values'],
                created_at=datetime.datetime.fromisoformat(metric_data['created_at']),
                updated_at=datetime.datetime.fromisoformat(metric_data['updated_at']),
                is_critical=metric_data['is_critical']
            )
            self.metrics[metric.id] = metric
        
        # Import alerts
        for alert_data in data.get('alerts', {}).values():
            alert = MonitoringAlert(
                id=alert_data['id'],
                deal_id=alert_data['deal_id'],
                metric_id=alert_data['metric_id'],
                alert_type=alert_data['alert_type'],
                severity=alert_data['severity'],
                timestamp=datetime.datetime.fromisoformat(alert_data['timestamp']),
                description=alert_data['description'],
                value=alert_data['value'],
                threshold=alert_data['threshold'],
                recommended_actions=alert_data['recommended_actions'],
                status=alert_data['status'],
                acknowledged_by=alert_data['acknowledged_by'],
                resolved_at=datetime.datetime.fromisoformat(alert_data['resolved_at']) if alert_data['resolved_at'] else None,
                resolution_notes=alert_data['resolution_notes']
            )
            self.alerts[alert.id] = alert
        
        # Import deal status
        for status_data in data.get('deal_status', {}).values():
            # Get alerts for this deal
            deal_alerts = [a for a in self.alerts.values() if a.deal_id == status_data['deal_id']]
            
            status = DealStatus(
                deal_id=status_data['deal_id'],
                overall_health=status_data['overall_health'],
                component_health=status_data['component_health'],
                entity_health=status_data['entity_health'],
                alerts=deal_alerts,
                current_stage=status_data['current_stage'],
                is_on_track=status_data['is_on_track'],
                variance_summary=status_data['variance_summary'],
                last_updated=datetime.datetime.fromisoformat(status_data['last_updated'])
            )
            self.deal_status[status.deal_id] = status
        
        # Import predictive models
        for model_data in data.get('predictive_models', {}).values():
            model = PredictiveModel(
                metric_id=model_data['metric_id'],
                model_type=model_data['model_type'],
                parameters=model_data['parameters'],
                last_training_date=datetime.datetime.fromisoformat(model_data['last_training_date']),
                forecast_horizon=model_data['forecast_horizon'],
                forecast_values=model_data['forecast_values'],
                forecast_intervals={k: tuple(v) for k, v in model_data['forecast_intervals'].items()},
                accuracy_metrics=model_data['accuracy_metrics']
            )
            self.predictive_models[model.metric_id] = model
        
        # Initialize historical performance
        for metric_id, metric in self.metrics.items():
            self.historical_performance[metric_id] = HistoricalPerformance(
                metric_id=metric_id,
                values=metric.actual_values.copy(),
                mean=np.mean(list(metric.actual_values.values())) if metric.actual_values else 0.0,
                std_dev=np.std(list(metric.actual_values.values())) if metric.actual_values else 0.0,
                min_value=min(metric.actual_values.values()) if metric.actual_values else float('inf'),
                max_value=max(metric.actual_values.values()) if metric.actual_values else float('-inf'),
                trend_slope=0.0,
                seasonal_factors={}
            )

# =============================================================================
# Command-line interface
# =============================================================================

def main():
    """Example usage of the monitoring system."""
    # Create monitoring system
    monitoring_system = DealMonitoringSystem()
    
    # Create a test deal
    deal_id = "DEAL-001"
    
    # Create metrics
    metric1_id = monitoring_system.create_metric(
        deal_id=deal_id,
        name="Economic Value",
        dimension="economic",
        component="financing",
        entity_id="GOV-001",
        units="USD",
        frequency="monthly",
        target_values={
            "2023-01": 100000,
            "2023-02": 120000,
            "2023-03": 150000,
            "2023-04": 180000,
            "2023-05": 200000
        },
        is_critical=True
    )
    
    metric2_id = monitoring_system.create_metric(
        deal_id=deal_id,
        name="Social Impact",
        dimension="social",
        component="delivery",
        entity_id="NGO-001",
        units="people",
        frequency="monthly",
        target_values={
            "2023-01": 500,
            "2023-02": 600,
            "2023-03": 750,
            "2023-04": 900,
            "2023-05": 1000
        },
        is_critical=False
    )
    
    # Update metrics with actual values
    monitoring_system.update_metric(metric1_id, "2023-01", 95000)
    monitoring_system.update_metric(metric1_id, "2023-02", 115000)
    monitoring_system.update_metric(metric1_id, "2023-03", 130000)  # Below target
    
    monitoring_system.update_metric(metric2_id, "2023-01", 520)
    monitoring_system.update_metric(metric2_id, "2023-02", 610)
    monitoring_system.update_metric(metric2_id, "2023-03", 780)  # Above target
    
    # Generate dashboard
    dashboard = monitoring_system.generate_dashboard(deal_id)
    
    # Print some results
    print(f"Deal Status: {'ON TRACK' if dashboard['is_on_track'] else 'OFF TRACK'}")
    print(f"Overall Health: {dashboard['overall_health'] * 100:.1f}%")
    print(f"Component Health:")
    for component, health in dashboard['component_health'].items():
        print(f"  {component}: {health * 100:.1f}%")
    
    print(f"Entity Health:")
    for entity_id, health in dashboard['entity_health'].items():
        print(f"  {entity_id}: {health * 100:.1f}%")
    
    print(f"Alerts:")
    for alert in dashboard['alerts']:
        print(f"  [{alert['severity']}] {alert['description']}")

if __name__ == "__main__":
    main()