"""
Controller for avian influenza notification services.

This module provides API endpoints for managing and triggering
notifications related to avian influenza outbreaks and predictions.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field
from datetime import datetime

from ..services.notification import NotificationService

# Define API models
class NotificationRecipients(BaseModel):
    """Recipients for notifications."""
    email: Optional[List[str]] = Field(None, description="Email recipients")
    sms: Optional[List[str]] = Field(None, description="SMS recipients")
    webhook_endpoints: Optional[List[str]] = Field(None, description="Webhook endpoints")

class NotificationConfig(BaseModel):
    """Configuration for notification service."""
    channels: Dict[str, Any] = Field(..., description="Channel configurations")
    recipients: NotificationRecipients = Field(..., description="Default recipients")
    
    class Config:
        schema_extra = {
            "example": {
                "channels": {
                    "email": {
                        "enabled": True,
                        "smtp_server": "smtp.example.com",
                        "smtp_port": 587,
                        "from_address": "alerts@aphis.usda.gov",
                        "use_tls": True
                    },
                    "sms": {
                        "enabled": True,
                        "provider": "twilio",
                        "from_number": "+18001234567"
                    },
                    "webhook": {
                        "enabled": True,
                        "endpoints": ["https://example.com/webhook"]
                    }
                },
                "recipients": {
                    "email": ["team@aphis.usda.gov"],
                    "sms": ["+18005551234"],
                    "webhook_endpoints": ["https://example.com/receive-alert"]
                }
            }
        }

class Region(BaseModel):
    """Region information for notifications."""
    id: str = Field(..., description="Region identifier")
    name: Optional[str] = Field(None, description="Region name")
    risk_score: Optional[float] = Field(None, description="Risk score (0-1)")
    predicted_cases: Optional[float] = Field(None, description="Predicted case count")

class OutbreakAlert(BaseModel):
    """Parameters for outbreak alerts."""
    regions: List[Region] = Field(..., description="Affected regions")
    detection_time: str = Field(..., description="Detection time (ISO format)")
    severity_level: str = Field("moderate", description="Severity level (low, moderate, high, severe)")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    
    class Config:
        schema_extra = {
            "example": {
                "regions": [
                    {"id": "region-001", "name": "King County, WA"},
                    {"id": "region-002", "name": "Pierce County, WA"}
                ],
                "detection_time": "2023-05-01T14:30:00Z",
                "severity_level": "high",
                "details": {
                    "virus_strain": "H5N1",
                    "farm_type": "Commercial Poultry",
                    "affected_birds": 25000
                }
            }
        }

class RiskPredictionAlert(BaseModel):
    """Parameters for risk prediction alerts."""
    high_risk_regions: List[Region] = Field(..., description="High risk regions")
    forecast_date: str = Field(..., description="Forecast date (ISO format)")
    days_ahead: int = Field(7, description="Days ahead in forecast")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    
    class Config:
        schema_extra = {
            "example": {
                "high_risk_regions": [
                    {
                        "id": "region-003", 
                        "name": "Skagit County, WA",
                        "risk_score": 0.85,
                        "predicted_cases": 3.2
                    },
                    {
                        "id": "region-004",
                        "name": "Whatcom County, WA",
                        "risk_score": 0.78,
                        "predicted_cases": 2.7
                    }
                ],
                "forecast_date": "2023-05-01",
                "days_ahead": 14,
                "details": {
                    "model_used": "ensemble",
                    "confidence_level": "high"
                }
            }
        }

class SystemNotification(BaseModel):
    """Parameters for system notifications."""
    subject: str = Field(..., description="Notification subject")
    message: str = Field(..., description="Notification message")
    level: str = Field("info", description="Notification level (info, warning, error)")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    
    class Config:
        schema_extra = {
            "example": {
                "subject": "Model Training Complete",
                "message": "Predictive models have been successfully trained with the latest data",
                "level": "info",
                "details": {
                    "models_trained": ["distance_based", "gaussian_process"],
                    "training_data_size": 1250,
                    "accuracy": 0.87
                }
            }
        }

class NotificationResult(BaseModel):
    """Result of a notification operation."""
    success: bool = Field(..., description="Overall success status")
    timestamp: str = Field(..., description="Timestamp of the notification")
    channel_results: Dict[str, bool] = Field(..., description="Success status by channel")
    notification_id: str = Field(..., description="Unique notification identifier")


# Create router
router = APIRouter(
    prefix="/api/v1/notifications",
    tags=["notifications"],
    responses={404: {"description": "Not found"}},
)

# Service dependency
def get_notification_service():
    """Dependency to get notification service instance."""
    config_path = "config/notification_config.json"
    return NotificationService(config_path)


# API endpoints
@router.post("/config", response_model=Dict[str, Any])
async def update_notification_config(
    config: NotificationConfig,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Update notification service configuration.
    """
    # This would update the configuration file in practice
    # For this implementation, we'll just return the config
    return {
        "status": "success",
        "message": "Configuration updated",
        "config": config.dict()
    }


@router.post("/outbreak-alert", response_model=NotificationResult)
async def send_outbreak_alert(
    alert: OutbreakAlert,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Send an alert about a detected outbreak.
    """
    # Convert regions to dictionaries
    regions = [region.dict() for region in alert.regions]
    
    # Send the alert
    results = notification_service.send_outbreak_alert(
        regions=regions,
        detection_time=alert.detection_time,
        severity_level=alert.severity_level,
        details=alert.details
    )
    
    # Determine overall success
    success = any(results.values())
    timestamp = datetime.now().isoformat()
    notification_id = f"notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return NotificationResult(
        success=success,
        timestamp=timestamp,
        channel_results=results,
        notification_id=notification_id
    )


@router.post("/risk-prediction-alert", response_model=NotificationResult)
async def send_risk_prediction_alert(
    alert: RiskPredictionAlert,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Send an alert about high-risk predictions for future outbreaks.
    """
    # Convert regions to dictionaries
    regions = [region.dict() for region in alert.high_risk_regions]
    
    # Send the alert
    results = notification_service.send_risk_prediction_alert(
        high_risk_regions=regions,
        forecast_date=alert.forecast_date,
        days_ahead=alert.days_ahead,
        details=alert.details
    )
    
    # Determine overall success
    success = any(results.values())
    timestamp = datetime.now().isoformat()
    notification_id = f"notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return NotificationResult(
        success=success,
        timestamp=timestamp,
        channel_results=results,
        notification_id=notification_id
    )


@router.post("/system-notification", response_model=NotificationResult)
async def send_system_notification(
    notification: SystemNotification,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Send a system notification (e.g., model training completed, data updated).
    """
    # Send the notification
    results = notification_service.send_system_notification(
        subject=notification.subject,
        message=notification.message,
        level=notification.level,
        details=notification.details
    )
    
    # Determine overall success
    success = any(results.values())
    timestamp = datetime.now().isoformat()
    notification_id = f"notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return NotificationResult(
        success=success,
        timestamp=timestamp,
        channel_results=results,
        notification_id=notification_id
    )


@router.get("/channels", response_model=Dict[str, Any])
async def get_notification_channels(
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Get available notification channels and their status.
    """
    channels = {}
    for channel_name, channel in notification_service.channels.items():
        channels[channel_name] = {
            "enabled": channel.enabled,
            "type": channel.__class__.__name__
        }
    
    return {
        "available_channels": channels
    }