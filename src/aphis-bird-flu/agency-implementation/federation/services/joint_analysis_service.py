"""
Joint Analysis Service

This module implements a service for running analyses that span multiple agencies,
combining data and insights across organizational boundaries.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from ..core.federation_hub import get_federation_hub

logger = logging.getLogger(__name__)

class AnalysisRequest(BaseModel):
    """Model for cross-agency analysis requests"""
    analysis_id: str
    analysis_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    requesting_agency: str
    target_agencies: Optional[List[str]] = None  # None = all agencies
    timestamp: datetime = Field(default_factory=datetime.now)
    priority: str = "medium"  # low, medium, high

class AnalysisResult(BaseModel):
    """Model for joint analysis results"""
    analysis_id: str
    status: str  # pending, in_progress, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    contributing_agencies: List[str] = Field(default_factory=list)
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None

class JointAnalysisService:
    """
    Service for running analyses across multiple agencies.
    
    This service provides capabilities for submitting analysis requests,
    tracking analysis status, and retrieving results that combine data
    and insights from multiple agencies.
    """
    
    def __init__(self):
        self.federation_hub = get_federation_hub()
        self._analysis_requests = {}  # Dictionary mapping analysis IDs to requests
        self._analysis_results = {}  # Dictionary mapping analysis IDs to results
        logger.info("Joint Analysis Service initialized")
    
    def submit_analysis(self, analysis_request: AnalysisRequest) -> AnalysisResult:
        """
        Submit a joint analysis request across multiple agencies
        
        Args:
            analysis_request: Analysis request details
            
        Returns:
            Initial analysis result status
        """
        logger.info(f"Submitting joint analysis {analysis_request.analysis_id} "
                   f"of type {analysis_request.analysis_type}")
        
        # Store the request
        self._analysis_requests[analysis_request.analysis_id] = analysis_request
        
        # Create initial result object
        result = AnalysisResult(
            analysis_id=analysis_request.analysis_id,
            status="pending",
            start_time=datetime.now()
        )
        
        # Store the result
        self._analysis_results[analysis_request.analysis_id] = result
        
        # Submit to federation hub (non-blocking)
        self._run_analysis_async(analysis_request)
        
        return result
    
    def _run_analysis_async(self, analysis_request: AnalysisRequest) -> None:
        """
        Run the analysis asynchronously
        
        This is a simplified implementation that runs synchronously. In a real
        implementation, this would be run in a background task or message queue.
        
        Args:
            analysis_request: Analysis request details
        """
        try:
            # Update status to in_progress
            result = self._analysis_results[analysis_request.analysis_id]
            result.status = "in_progress"
            
            # Convert to dictionary for federation hub
            request_dict = analysis_request.dict()
            
            # Call federation hub to run joint analysis
            joint_result = self.federation_hub.run_joint_analysis(
                request_dict, analysis_request.target_agencies
            )
            
            # Update result with success
            result.status = "completed"
            result.result = joint_result
            result.contributing_agencies = joint_result.get("agency_contributions", {}).keys()
            result.completion_time = datetime.now()
            
        except Exception as e:
            # Update result with failure
            logger.error(f"Error running joint analysis {analysis_request.analysis_id}: {str(e)}")
            
            if analysis_request.analysis_id in self._analysis_results:
                result = self._analysis_results[analysis_request.analysis_id]
                result.status = "failed"
                result.error = str(e)
                result.completion_time = datetime.now()
    
    def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get the status of a joint analysis
        
        Args:
            analysis_id: Analysis identifier
            
        Returns:
            Status of the analysis and results if available
        """
        if analysis_id not in self._analysis_results:
            return {"error": f"Analysis {analysis_id} not found"}
        
        result = self._analysis_results[analysis_id]
        return result.dict()
    
    def get_analysis_types(self) -> Dict[str, Dict[str, Any]]:
        """
        Get available analysis types and their capabilities
        
        Returns:
            Dictionary of analysis types with descriptions and parameters
        """
        # This would typically be populated dynamically based on registered analysis types
        return {
            "environmental_health_correlation": {
                "description": "Correlate environmental factors with health outcomes",
                "required_parameters": ["region", "env_factor", "health_outcome", "start_date", "end_date"],
                "optional_parameters": ["demographic_factors", "confidence_level"],
                "recommended_agencies": ["cdc", "epa"]
            },
            "disaster_impact_assessment": {
                "description": "Assess the impact of disasters across multiple dimensions",
                "required_parameters": ["region", "disaster_type", "date"],
                "optional_parameters": ["impact_types", "recovery_metrics"],
                "recommended_agencies": ["fema", "epa", "cdc"]
            },
            "disease_spread": {
                "description": "Analyze disease spread patterns and contributing factors",
                "required_parameters": ["region", "disease_type", "start_date", "end_date"],
                "optional_parameters": ["environmental_factors", "mobility_data"],
                "recommended_agencies": ["cdc", "epa"]
            },
            "resource_needs_forecast": {
                "description": "Forecast future resource needs based on current data",
                "required_parameters": ["region", "resource_types", "time_horizon"],
                "optional_parameters": ["scenario", "confidence_level"],
                "recommended_agencies": ["fema", "cdc", "epa"]
            }
        }
    
    def create_analysis_request(self,
                              analysis_type: str,
                              parameters: Dict[str, Any],
                              requesting_agency: str,
                              target_agencies: Optional[List[str]] = None,
                              priority: str = "medium") -> AnalysisRequest:
        """
        Create a new analysis request with automatic ID generation
        
        Args:
            analysis_type: Type of analysis to perform
            parameters: Analysis parameters
            requesting_agency: Agency requesting the analysis
            target_agencies: Optional list of target agencies (None = all)
            priority: Priority level
            
        Returns:
            Created AnalysisRequest object
        """
        # Generate a unique analysis ID
        analysis_id = f"{requesting_agency}-{analysis_type}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create the analysis request
        analysis_request = AnalysisRequest(
            analysis_id=analysis_id,
            analysis_type=analysis_type,
            parameters=parameters,
            requesting_agency=requesting_agency,
            target_agencies=target_agencies,
            timestamp=datetime.now(),
            priority=priority
        )
        
        return analysis_request