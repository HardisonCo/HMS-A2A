"""
FEMA System Supervisor for Adaptive Surveillance and Response System

This module implements the system-supervisor pattern for the FEMA implementation
of the Adaptive Surveillance and Response System, coordinating all components
including health monitoring, component lifecycle management, and cross-component
orchestration for disaster risk monitoring, resource deployment optimization,
and recovery progress tracking.
"""

import logging
import time
from typing import Dict, List, Optional, Any
from enum import Enum
import asyncio
from datetime import datetime
import json
import os

# Import FEMA-specific service implementations
from agency_implementation.fema.services.disaster_risk_monitoring.monitoring_service import DisasterRiskMonitoringService
from agency_implementation.fema.services.resource_deployment_optimization.optimization_service import ResourceDeploymentOptimizationService
from agency_implementation.fema.services.recovery_progress_tracking.tracking_service import RecoveryProgressTrackingService

# Import necessary repositories and adapters
from agency_implementation.fema.services.disaster_risk_monitoring.repository import (
    HazardZoneRepository, HazardMeasurementRepository, DisasterEventRepository,
    DisasterAlertRepository, RiskAssessmentRepository, ForecastModelRepository,
    DisasterForecastRepository
)
from agency_implementation.fema.services.resource_deployment_optimization.repository import (
    ResourceRepository, ResourceDeploymentRepository,
    ResourceRequestRepository, ResourceAllocationPlanRepository
)
from agency_implementation.fema.services.recovery_progress_tracking.repository import (
    RecoveryProjectRepository, DamageAssessmentRepository,
    RecoveryMetricsRepository, RecoveryProgramRepository
)

from agency_implementation.fema.services.disaster_risk_monitoring.adapters import (
    WeatherMonitoringAdapter, SeismicMonitoringAdapter, 
    EmailNotificationAdapter, SMSNotificationAdapter
)
from agency_implementation.fema.services.resource_deployment_optimization.adapters import (
    FEMAInventoryAdapter, FEMADeploymentAdapter, OptimizationEngineAdapter
)
from agency_implementation.fema.services.recovery_progress_tracking.adapters import (
    FEMAAssessmentAdapter, FEMAProjectAdapter, FEMAReportingAdapter
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("fema_supervisor")

class ComponentStatus(str, Enum):
    """Status options for system components."""
    INITIALIZING = "initializing"
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    ERROR = "error"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class FEMASupervisor:
    """
    System supervisor for the FEMA implementation of the Adaptive Surveillance and Response System.
    
    This class coordinates all FEMA-specific components, manages their lifecycle,
    monitors health, and orchestrates cross-component operations focused on
    disaster risk monitoring, resource deployment optimization, and recovery
    progress tracking.
    
    Key responsibilities:
    1. Component health monitoring and status tracking
    2. System initialization and shutdown sequences
    3. Cross-component workflow orchestration
    4. Error handling and recovery strategies
    5. Resource optimization for emergency response
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the FEMA supervisor.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.component_status: Dict[str, ComponentStatus] = {}
        self.component_registry: Dict[str, Any] = {}
        self.data_store = {}  # Shared data store for repositories
        self.health_check_interval = self.config.get("health_check_interval", 60)  # seconds
        self.last_health_check: Dict[str, datetime] = {}
        self.is_running = False
        self.health_check_task = None
        
        # Initialize status for each component
        self._initialize_component_statuses()
        
        logger.info("FEMA Supervisor initialized")
    
    def _initialize_component_statuses(self):
        """Initialize status tracker for all FEMA components."""
        core_components = [
            "disaster_risk_monitoring",
            "resource_deployment_optimization",
            "recovery_progress_tracking",
            "impact_prediction",
            "resource_allocation",
            "notification_system",
            "visualization_services", 
            "emergency_coordination"
        ]
        
        for component in core_components:
            self.component_status[component] = ComponentStatus.INITIALIZING
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """
        Load supervisor configuration.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dictionary with configuration values
        """
        default_config = {
            "health_check_interval": 60,
            "auto_recovery": True,
            "component_timeouts": {
                "default": 30,
                "impact_prediction": 120,
                "resource_allocation": 90
            },
            "fema_specific": {
                "disaster_types": ["hurricane", "flood", "wildfire", "earthquake", "tornado", "winter_storm"],
                "resource_categories": ["shelter", "food", "water", "medical", "search_rescue", "transportation"],
                "emergency_levels": ["local", "state", "regional", "national"]
            },
            "thresholds": {
                "wind_speed": 74.0,  # Hurricane force winds (mph)
                "precipitation": 2.0,  # Heavy rainfall (inches in 24 hours)
                "river_level": 15.0,  # Flood stage (feet)
                "magnitude": 5.0,  # Moderate earthquake (Richter)
            },
            "apis": {
                "weather_api": {
                    "url": None,  # Set to None to use mock data
                    "key": None
                },
                "seismic_api": {
                    "url": None,  # Set to None to use mock data
                    "key": None
                },
                "inventory_api": {
                    "url": None,  # Set to None to use mock data
                    "key": None
                },
                "deployment_api": {
                    "url": None,  # Set to None to use mock data
                    "key": None
                },
                "assessment_api": {
                    "url": None,  # Set to None to use mock data
                    "key": None
                },
                "project_api": {
                    "url": None,  # Set to None to use mock data
                    "key": None
                },
                "reporting_api": {
                    "url": None,  # Set to None to use mock data
                    "key": None
                }
            }
        }
        
        if not config_path or not os.path.exists(config_path):
            logger.warning(f"Config path {config_path} not found, using default configuration")
            return default_config
        
        try:
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
                # Merge with defaults to ensure all expected keys exist
                return {**default_config, **config}
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return default_config
    
    async def start(self):
        """Start the supervisor and initialize all components."""
        if self.is_running:
            logger.warning("Supervisor is already running")
            return
        
        logger.info("Starting FEMA Supervisor")
        self.is_running = True
        
        # Initialize components in the correct order
        await self._initialize_components()
        
        # Start health monitoring
        self.health_check_task = asyncio.create_task(self._health_monitoring_loop())
        
        logger.info("FEMA Supervisor started successfully")
    
    async def stop(self):
        """Stop the supervisor and shut down all components."""
        if not self.is_running:
            logger.warning("Supervisor is not running")
            return
        
        logger.info("Stopping FEMA Supervisor")
        
        # Cancel health monitoring
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        # Shutdown components in reverse order
        await self._shutdown_components()
        
        self.is_running = False
        logger.info("FEMA Supervisor stopped successfully")
    
    async def _initialize_components(self):
        """Initialize all components in dependency order."""
        # Order matters here - initialize in dependency order
        components_order = [
            "disaster_risk_monitoring", 
            "emergency_coordination",
            "impact_prediction",
            "resource_allocation",
            "resource_deployment_optimization",
            "recovery_progress_tracking",
            "visualization_services",
            "notification_system"
        ]
        
        # Initialize repositories first
        self._initialize_repositories()
        
        # Initialize adapters
        self._initialize_adapters()
        
        # Initialize core service components
        for component in components_order:
            try:
                logger.info(f"Initializing {component}")
                
                if component == "disaster_risk_monitoring":
                    self._initialize_disaster_risk_monitoring()
                elif component == "resource_deployment_optimization":
                    self._initialize_resource_deployment_optimization()
                elif component == "recovery_progress_tracking":
                    self._initialize_recovery_progress_tracking()
                else:
                    # For components without specific implementations yet, just simulate initialization
                    await asyncio.sleep(0.5)
                    
                self.component_status[component] = ComponentStatus.OPERATIONAL
                self.last_health_check[component] = datetime.now()
                logger.info(f"{component} initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing {component}: {str(e)}")
                self.component_status[component] = ComponentStatus.ERROR
    
    def _initialize_repositories(self):
        """Initialize all repositories with shared data store."""
        # Disaster Risk Monitoring repositories
        self.component_registry["hazard_zone_repository"] = HazardZoneRepository(self.data_store)
        self.component_registry["hazard_measurement_repository"] = HazardMeasurementRepository(self.data_store)
        self.component_registry["disaster_event_repository"] = DisasterEventRepository(self.data_store)
        self.component_registry["disaster_alert_repository"] = DisasterAlertRepository(self.data_store)
        self.component_registry["risk_assessment_repository"] = RiskAssessmentRepository(self.data_store)
        self.component_registry["forecast_model_repository"] = ForecastModelRepository(self.data_store)
        self.component_registry["disaster_forecast_repository"] = DisasterForecastRepository(self.data_store)
        
        # Resource Deployment Optimization repositories
        self.component_registry["resource_repository"] = ResourceRepository(self.data_store)
        self.component_registry["resource_deployment_repository"] = ResourceDeploymentRepository(self.data_store)
        self.component_registry["resource_request_repository"] = ResourceRequestRepository(self.data_store)
        self.component_registry["resource_allocation_plan_repository"] = ResourceAllocationPlanRepository(self.data_store)
        
        # Recovery Progress Tracking repositories
        self.component_registry["recovery_project_repository"] = RecoveryProjectRepository(self.data_store)
        self.component_registry["damage_assessment_repository"] = DamageAssessmentRepository(self.data_store)
        self.component_registry["recovery_metrics_repository"] = RecoveryMetricsRepository(self.data_store)
        self.component_registry["recovery_program_repository"] = RecoveryProgramRepository(self.data_store)
        
        logger.info("All repositories initialized successfully")
    
    def _initialize_adapters(self):
        """Initialize all external system adapters."""
        # Get API configurations
        api_config = self.config.get("apis", {})
        
        # Disaster Risk Monitoring adapters
        self.component_registry["weather_monitoring_adapter"] = WeatherMonitoringAdapter(
            api_url=api_config.get("weather_api", {}).get("url"),
            api_key=api_config.get("weather_api", {}).get("key")
        )
        self.component_registry["seismic_monitoring_adapter"] = SeismicMonitoringAdapter(
            api_url=api_config.get("seismic_api", {}).get("url"),
            api_key=api_config.get("seismic_api", {}).get("key")
        )
        self.component_registry["email_notification_adapter"] = EmailNotificationAdapter()
        self.component_registry["sms_notification_adapter"] = SMSNotificationAdapter()
        
        # Resource Deployment Optimization adapters
        self.component_registry["inventory_adapter"] = FEMAInventoryAdapter(
            api_url=api_config.get("inventory_api", {}).get("url"),
            api_key=api_config.get("inventory_api", {}).get("key")
        )
        self.component_registry["deployment_adapter"] = FEMADeploymentAdapter(
            api_url=api_config.get("deployment_api", {}).get("url"),
            api_key=api_config.get("deployment_api", {}).get("key")
        )
        self.component_registry["optimization_adapter"] = OptimizationEngineAdapter()
        
        # Recovery Progress Tracking adapters
        self.component_registry["assessment_adapter"] = FEMAAssessmentAdapter(
            api_url=api_config.get("assessment_api", {}).get("url"),
            api_key=api_config.get("assessment_api", {}).get("key")
        )
        self.component_registry["project_adapter"] = FEMAProjectAdapter(
            api_url=api_config.get("project_api", {}).get("url"),
            api_key=api_config.get("project_api", {}).get("key")
        )
        self.component_registry["reporting_adapter"] = FEMAReportingAdapter(
            api_url=api_config.get("reporting_api", {}).get("url"),
            api_key=api_config.get("reporting_api", {}).get("key")
        )
        
        logger.info("All adapters initialized successfully")
    
    def _initialize_disaster_risk_monitoring(self):
        """Initialize the disaster risk monitoring service."""
        # Create notification adapters dictionary
        notification_adapters = {
            "email": self.component_registry["email_notification_adapter"],
            "sms": self.component_registry["sms_notification_adapter"]
        }
        
        # Create monitoring adapters dictionary
        monitoring_adapters = {
            "weather": self.component_registry["weather_monitoring_adapter"],
            "seismic": self.component_registry["seismic_monitoring_adapter"]
        }
        
        # Create service with repositories and adapters
        service = DisasterRiskMonitoringService(
            hazard_zone_repository=self.component_registry["hazard_zone_repository"],
            hazard_measurement_repository=self.component_registry["hazard_measurement_repository"],
            disaster_event_repository=self.component_registry["disaster_event_repository"],
            disaster_alert_repository=self.component_registry["disaster_alert_repository"],
            risk_assessment_repository=self.component_registry["risk_assessment_repository"],
            forecast_model_repository=self.component_registry["forecast_model_repository"],
            disaster_forecast_repository=self.component_registry["disaster_forecast_repository"],
            monitoring_adapters=monitoring_adapters,
            notification_adapters=notification_adapters,
            config={
                "thresholds": self.config.get("thresholds", {})
            }
        )
        
        # Register the service
        self.component_registry["disaster_risk_monitoring_service"] = service
        logger.info("Disaster Risk Monitoring Service initialized")
    
    def _initialize_resource_deployment_optimization(self):
        """Initialize the resource deployment optimization service."""
        # Create service with repositories and adapters
        service = ResourceDeploymentOptimizationService(
            resource_repository=self.component_registry["resource_repository"],
            deployment_repository=self.component_registry["resource_deployment_repository"],
            request_repository=self.component_registry["resource_request_repository"],
            allocation_plan_repository=self.component_registry["resource_allocation_plan_repository"],
            inventory_adapter=self.component_registry["inventory_adapter"],
            deployment_adapter=self.component_registry["deployment_adapter"],
            optimization_adapter=self.component_registry["optimization_adapter"],
            config={
                "optimization": {
                    "default_method": "multi_objective",
                    "weights": {
                        "priority": 0.4,
                        "requirements": 0.3,
                        "distance": 0.2,
                        "deploy_time": 0.1
                    }
                }
            }
        )
        
        # Register the service
        self.component_registry["resource_deployment_optimization_service"] = service
        logger.info("Resource Deployment Optimization Service initialized")
    
    def _initialize_recovery_progress_tracking(self):
        """Initialize the recovery progress tracking service."""
        # Create service with repositories and adapters
        service = RecoveryProgressTrackingService(
            project_repository=self.component_registry["recovery_project_repository"],
            assessment_repository=self.component_registry["damage_assessment_repository"],
            metrics_repository=self.component_registry["recovery_metrics_repository"],
            program_repository=self.component_registry["recovery_program_repository"],
            assessment_adapter=self.component_registry["assessment_adapter"],
            project_adapter=self.component_registry["project_adapter"],
            reporting_adapter=self.component_registry["reporting_adapter"]
        )
        
        # Register the service
        self.component_registry["recovery_progress_tracking_service"] = service
        logger.info("Recovery Progress Tracking Service initialized")
    
    async def _shutdown_components(self):
        """Shut down all components in reverse dependency order."""
        # Shutdown in reverse order of initialization
        components_order = [
            "notification_system",
            "visualization_services",
            "recovery_progress_tracking",
            "resource_deployment_optimization",
            "resource_allocation",
            "impact_prediction",
            "emergency_coordination",
            "disaster_risk_monitoring"
        ]
        
        for component in components_order:
            try:
                logger.info(f"Shutting down {component}")
                # Here would be actual shutdown code for each component
                # For now, just simulate shutdown with a delay
                await asyncio.sleep(0.5)
                self.component_status[component] = ComponentStatus.OFFLINE
                logger.info(f"{component} shut down successfully")
            except Exception as e:
                logger.error(f"Error shutting down {component}: {str(e)}")
    
    async def _health_monitoring_loop(self):
        """Run continuous health checks on all components."""
        while self.is_running:
            await self._check_all_components_health()
            await asyncio.sleep(self.health_check_interval)
    
    async def _check_all_components_health(self):
        """Check health of all components."""
        logger.debug("Running health check on all components")
        
        for component, status in self.component_status.items():
            if status != ComponentStatus.OFFLINE:
                try:
                    # Here would be actual health check code
                    # For demonstration, randomly set some components to degraded occasionally
                    if component == "impact_prediction" and time.time() % 120 < 5:
                        self.component_status[component] = ComponentStatus.DEGRADED
                        logger.warning(f"Component {component} is degraded")
                        
                        # Auto-recovery if enabled
                        if self.config.get("auto_recovery", True):
                            await self._attempt_recovery(component)
                    else:
                        self.component_status[component] = ComponentStatus.OPERATIONAL
                    
                    self.last_health_check[component] = datetime.now()
                except Exception as e:
                    logger.error(f"Health check failed for {component}: {str(e)}")
                    self.component_status[component] = ComponentStatus.ERROR
                    
                    # Auto-recovery if enabled
                    if self.config.get("auto_recovery", True):
                        await self._attempt_recovery(component)
    
    async def _attempt_recovery(self, component: str):
        """
        Attempt to recover a failed component.
        
        Args:
            component: Name of the component to recover
        """
        logger.info(f"Attempting to recover {component}")
        
        try:
            # Here would be recovery strategy specific to each component
            # For now, just simulate recovery with a delay
            await asyncio.sleep(1)
            self.component_status[component] = ComponentStatus.OPERATIONAL
            logger.info(f"Successfully recovered {component}")
        except Exception as e:
            logger.error(f"Recovery failed for {component}: {str(e)}")
            self.component_status[component] = ComponentStatus.ERROR
    
    def get_system_status(self) -> Dict:
        """
        Get the current status of all system components.
        
        Returns:
            Dictionary with system status information
        """
        return {
            "system": "FEMA Adaptive Surveillance and Response System",
            "status": self._calculate_overall_status(),
            "timestamp": datetime.now().isoformat(),
            "components": {
                component: status.value 
                for component, status in self.component_status.items()
            },
            "last_health_check": {
                component: timestamp.isoformat()
                for component, timestamp in self.last_health_check.items()
            }
        }
    
    def _calculate_overall_status(self) -> str:
        """
        Calculate overall system status based on component statuses.
        
        Returns:
            Overall system status
        """
        statuses = list(self.component_status.values())
        
        if any(status == ComponentStatus.ERROR for status in statuses):
            return "degraded - critical components in error state"
        elif any(status == ComponentStatus.DEGRADED for status in statuses):
            return "degraded - some components have issues"
        elif all(status == ComponentStatus.OPERATIONAL for status in statuses):
            return "fully operational"
        elif any(status == ComponentStatus.INITIALIZING for status in statuses):
            return "initializing - some components still starting"
        else:
            return "partially operational"
    
    async def orchestrate_workflow(self, workflow_type: str, params: Dict) -> Dict:
        """
        Orchestrate a cross-component workflow.
        
        Args:
            workflow_type: Type of workflow to orchestrate
            params: Parameters for the workflow
            
        Returns:
            Results of the workflow
        """
        logger.info(f"Orchestrating workflow: {workflow_type}")
        
        if workflow_type == "disaster_impact_prediction":
            return await self._orchestrate_disaster_impact_prediction(params)
        elif workflow_type == "resource_deployment_planning":
            return await self._orchestrate_resource_deployment_planning(params)
        elif workflow_type == "recovery_effectiveness_assessment":
            return await self._orchestrate_recovery_effectiveness_assessment(params)
        else:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
    
    async def _orchestrate_disaster_impact_prediction(self, params: Dict) -> Dict:
        """
        Orchestrate a disaster impact prediction workflow.
        
        This workflow coordinates across monitoring, forecasting, and alert generation
        to predict the impact of a disaster and generate appropriate alerts.
        
        Args:
            params: Parameters for the workflow including disaster type and location
            
        Returns:
            Dictionary with prediction results
        """
        # Get the disaster risk monitoring service
        monitoring_service = self.component_registry.get("disaster_risk_monitoring_service")
        if not monitoring_service:
            raise RuntimeError("Disaster risk monitoring service not initialized")
        
        try:
            # Generate the disaster forecast
            model_params = {
                "hazard_type": params.get("disaster_type", "hurricane"),
                "model_id": params.get("model_id"),
                "region": params.get("region")
            }
            
            # Create or retrieve a forecast model
            forecast_models = monitoring_service.find_models_by_hazard_type(model_params["hazard_type"])
            model_id = model_params["model_id"]
            
            if not model_id and forecast_models:
                model_id = forecast_models[0].id
            elif not model_id:
                # Create a new forecast model if none exists
                model_data = {
                    "model_name": f"{model_params['hazard_type'].capitalize()} Impact Model",
                    "hazard_type": model_params["hazard_type"],
                    "model_type": "ensemble"
                }
                model = monitoring_service.create_forecast_model(model_data)
                model_id = model.id
            
            # Generate disaster forecast
            forecast_data = {
                "model_id": model_id,
                "hazard_type": model_params["hazard_type"],
                "forecast_area": params.get("forecast_area", {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            # Simple polygon for demo
                            [[-85, 25], [-80, 25], [-80, 30], [-85, 30], [-85, 25]]
                        ]
                    }
                }),
                "prediction_values": {
                    "intensity": params.get("severity", "category 3"),
                    "wind_speed": 120,
                    "storm_surge": 10,
                    "rainfall": 15
                },
                "probability": 0.85,
                "severity_prediction": "major",
                "expected_impacts": {
                    "power_outage": "75% affected areas",
                    "flooding": "Significant coastal and inland",
                    "infrastructure": "Moderate to severe damage",
                    "displacement": "Estimated 100,000 people"
                }
            }
            
            forecast = monitoring_service.create_disaster_forecast(forecast_data)
            
            # Generate alerts based on forecast
            alerts = monitoring_service.generate_alerts_from_forecast(forecast.id)
            
            # Prepare the workflow result
            result = {
                "status": "completed",
                "disaster_type": params.get("disaster_type", "hurricane"),
                "severity": forecast_data["prediction_values"]["intensity"],
                "forecast_id": forecast.id,
                "alerts_generated": len(alerts),
                "probability": forecast_data["probability"] * 100,
                "impact_areas": [
                    {"region": "Coastal Region A", "impact": "severe", "population_affected": 320000},
                    {"region": "Inland Region B", "impact": "moderate", "population_affected": 150000}
                ],
                "expected_impacts": forecast_data["expected_impacts"],
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in disaster impact prediction workflow: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _orchestrate_resource_deployment_planning(self, params: Dict) -> Dict:
        """
        Orchestrate a resource deployment planning workflow.
        
        This workflow coordinates across resource allocation, optimization, and deployment
        to plan the deployment of resources in response to a disaster.
        
        Args:
            params: Parameters for the workflow including disaster event ID
            
        Returns:
            Dictionary with deployment planning results
        """
        # Get the resource deployment optimization service
        optimization_service = self.component_registry.get("resource_deployment_optimization_service")
        if not optimization_service:
            raise RuntimeError("Resource deployment optimization service not initialized")
        
        try:
            # Get disaster event ID from parameters
            event_id = params.get("event_id")
            if not event_id:
                raise ValueError("Event ID is required for resource deployment planning")
            
            # Generate an allocation plan
            plan_name = params.get("plan_name", f"Resource Plan for Event {event_id}")
            
            # Create the allocation plan
            allocation_plan = optimization_service.generate_allocation_plan(
                event_id=event_id,
                plan_name=plan_name,
                method=params.get("optimization_method")
            )
            
            # If auto-execute is requested, execute the plan
            execution_result = None
            if params.get("auto_execute", False):
                # Approve the plan
                approved_plan = optimization_service.approve_allocation_plan(
                    plan_id=allocation_plan.id,
                    approver=params.get("approver", "System")
                )
                
                # Activate the plan
                activated_plan = optimization_service.activate_allocation_plan(
                    plan_id=approved_plan.id
                )
                
                # Execute the plan
                execution_result = optimization_service.execute_allocation_plan(
                    plan_id=activated_plan.id
                )
            
            # Prepare the workflow result
            result = {
                "status": "completed",
                "disaster_type": params.get("disaster_type", "hurricane"),
                "plan_id": allocation_plan.id,
                "plan_name": allocation_plan.plan_name,
                "resource_count": len(getattr(allocation_plan, "resource_allocations", [])),
                "execution_status": "executed" if execution_result else "pending approval",
                "deployment_timeframe": params.get("deployment_timeframe", "72 hours"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add execution results if available
            if execution_result:
                result["execution_result"] = {
                    "successful_deployments": execution_result.get("successful", 0),
                    "failed_deployments": execution_result.get("failed", 0),
                    "success_rate": execution_result.get("success_rate", 0)
                }
            
            # Add mock data for UI display (would be generated from real data in production)
            result["resource_allocation"] = {
                "shelter": {
                    "locations": [
                        {"facility": "Regional Center A", "capacity": 1500},
                        {"facility": "School Complex B", "capacity": 800}
                    ],
                    "staffing": {"red_cross": 45, "fema": 20, "local": 30},
                    "supplies": {"cots": 2500, "blankets": 3000, "hygiene_kits": 2500}
                },
                "medical": {
                    "field_hospitals": 2,
                    "ambulances": 18,
                    "medical_personnel": 75
                },
                "search_rescue": {
                    "teams": 12,
                    "vehicles": 24,
                    "helicopters": 4
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in resource deployment planning workflow: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _orchestrate_recovery_effectiveness_assessment(self, params: Dict) -> Dict:
        """
        Orchestrate a recovery effectiveness assessment workflow.
        
        This workflow coordinates across recovery tracking, damage assessment, and metrics
        to assess the effectiveness of recovery efforts for a disaster.
        
        Args:
            params: Parameters for the workflow including disaster event ID
            
        Returns:
            Dictionary with assessment results
        """
        # Get the recovery progress tracking service
        tracking_service = self.component_registry.get("recovery_progress_tracking_service")
        if not tracking_service:
            raise RuntimeError("Recovery progress tracking service not initialized")
        
        try:
            # Get disaster event ID from parameters
            event_id = params.get("event_id")
            if not event_id:
                raise ValueError("Event ID is required for recovery effectiveness assessment")
            
            # Generate comprehensive metrics for the event
            metrics = tracking_service.generate_comprehensive_metrics(event_id)
            
            # Generate a summary report
            if tracking_service.reporting_adapter:
                report = tracking_service.generate_summary_report(event_id)
            else:
                report = None
            
            # Prepare the workflow result
            result = {
                "status": "completed",
                "disaster_id": event_id,
                "assessment_period": params.get("assessment_period", "30 days post-impact"),
                "metrics_id": metrics.id,
                "report_generated": report is not None,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add metrics data if available
            if hasattr(metrics, "metrics_values"):
                metrics_values = metrics.metrics_values
                
                # Add recovery progress metrics
                if "recovery_progress" in metrics_values:
                    recovery_progress = metrics_values["recovery_progress"]
                    result["recovery_progress"] = {
                        "total_projects": recovery_progress.get("total_projects", 0),
                        "completed_projects": recovery_progress.get("completed_projects", 0),
                        "completion_percentage": recovery_progress.get("average_completion", 0)
                    }
                
                # Add financial progress metrics
                if "financial_progress" in metrics_values:
                    financial_progress = metrics_values["financial_progress"]
                    result["financial_progress"] = {
                        "total_budget": financial_progress.get("total_budget", 0),
                        "total_disbursed": financial_progress.get("total_disbursed", 0),
                        "disbursement_rate": financial_progress.get("disbursement_rate", 0)
                    }
                
                # Add impact metrics
                if "impact" in metrics_values:
                    impact = metrics_values["impact"]
                    result["impact_assessment"] = {
                        "total_damage_estimate": impact.get("total_damage_estimate", 0),
                        "affected_population": impact.get("affected_population", 0)
                    }
                
                # Add summary metrics
                if "summary" in metrics_values:
                    summary = metrics_values["summary"]
                    result["recovery_index"] = summary.get("recovery_index", 0)
            
            # Add mock data for UI display (would be generated from real data in production)
            result["recovery_progress"] = {
                "power_restoration": {"percent_complete": 92, "ahead_of_schedule": True},
                "water_services": {"percent_complete": 88, "on_schedule": True},
                "debris_removal": {"percent_complete": 65, "behind_schedule": True},
                "temporary_housing": {"percent_complete": 78, "on_schedule": True}
            }
            
            result["resource_utilization"] = {
                "efficiency_rating": 0.82,
                "underutilized_resources": ["heavy equipment", "volunteer management"],
                "overstretched_resources": ["housing inspectors", "mental health services"]
            }
            
            result["community_impact"] = {
                "households_returned": "64%",
                "businesses_reopened": "58%",
                "school_operations": "85%"
            }
            
            result["recommendations"] = [
                "Reallocate debris removal resources from Region C to Region A",
                "Increase mental health service capacity by 40%",
                "Transition shelter operations to long-term housing assistance"
            ]
            
            return result
            
        except Exception as e:
            logger.error(f"Error in recovery effectiveness assessment workflow: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Example of how to use the supervisor
async def main():
    """Example of how to use the supervisor."""
    supervisor = FEMASupervisor()
    await supervisor.start()
    
    # Simulate running for a while
    await asyncio.sleep(5)
    
    # Get system status
    status = supervisor.get_system_status()
    print(f"System status: {json.dumps(status, indent=2)}")
    
    # Orchestrate a workflow
    result = await supervisor.orchestrate_workflow("disaster_impact_prediction", {
        "disaster_type": "hurricane",
        "region": "Southeast Atlantic Coast",
        "severity": "category 3",
        "timeframe": "72 hours"
    })
    print(f"Workflow result: {json.dumps(result, indent=2)}")
    
    # Shut down
    await supervisor.stop()


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())