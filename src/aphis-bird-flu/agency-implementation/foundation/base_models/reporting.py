"""
Reporting models for the APHIS Agency Implementation.
Defines data models for reports, metrics, and analytics data.
"""
from typing import Dict, Any, Optional, List, Union
from datetime import date, datetime
from enum import Enum

from .base import BaseModel


class ReportFrequency(str, Enum):
    """Frequency of scheduled reports"""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    CUSTOM = "custom"
    ONE_TIME = "one_time"


class ReportStatus(str, Enum):
    """Status of a report"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ReportType(str, Enum):
    """Types of reports"""
    STANDARD = "standard"
    ANALYTICS = "analytics"
    COMPLIANCE = "compliance"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    CUSTOM = "custom"


class Report(BaseModel):
    """A report generated from system data"""
    
    def __init__(
        self,
        title: str,
        description: str,
        report_type: Union[ReportType, str],
        parameters: Dict[str, Any],
        status: Union[ReportStatus, str] = ReportStatus.DRAFT,
        created_by: Optional[str] = None,
        agency_id: Optional[str] = None,
        program_id: Optional[str] = None,
        date_range: Optional[Dict[str, str]] = None,
        generated_at: Optional[Union[datetime, str]] = None,
        file_urls: Optional[Dict[str, str]] = None,
        scheduled: Optional[bool] = False,
        frequency: Optional[Union[ReportFrequency, str]] = None,
        next_run: Optional[Union[datetime, str]] = None,
        last_run: Optional[Union[datetime, str]] = None,
        result_summary: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize a report"""
        # Convert string enums to Enum values if needed
        if isinstance(report_type, str):
            report_type = ReportType(report_type)
            
        if isinstance(status, str):
            status = ReportStatus(status)
            
        if isinstance(frequency, str) and frequency:
            frequency = ReportFrequency(frequency)
        
        # Convert datetime strings to datetime if needed
        for date_field, date_value in [
            ('generated_at', generated_at),
            ('next_run', next_run),
            ('last_run', last_run)
        ]:
            if isinstance(date_value, str) and date_value:
                date_value = datetime.fromisoformat(date_value)
                locals()[date_field] = date_value
        
        super().__init__(
            title=title,
            description=description,
            report_type=report_type,
            parameters=parameters,
            status=status,
            created_by=created_by,
            agency_id=agency_id,
            program_id=program_id,
            date_range=date_range,
            generated_at=generated_at,
            file_urls=file_urls or {},
            scheduled=scheduled,
            frequency=frequency,
            next_run=next_run,
            last_run=last_run,
            result_summary=result_summary or {},
            metadata=metadata or {},
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert enum values to strings
        for field in ['report_type', 'status', 'frequency']:
            if field in result and isinstance(result[field], Enum):
                result[field] = result[field].value
        
        # Convert datetime objects to strings
        for field in ['generated_at', 'next_run', 'last_run']:
            if field in result and isinstance(result[field], datetime):
                result[field] = result[field].isoformat()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Report':
        """Create from dictionary representation"""
        return cls(**data)
    
    def update_status(self, new_status: Union[ReportStatus, str]) -> None:
        """Update the report status"""
        if isinstance(new_status, str):
            new_status = ReportStatus(new_status)
            
        self.status = new_status
        
        if new_status == ReportStatus.COMPLETED:
            self.generated_at = datetime.now()
            
        self.updated_at = datetime.now().isoformat()
    
    def add_file_url(self, format_type: str, url: str) -> None:
        """Add a file URL to the report"""
        if not hasattr(self, 'file_urls'):
            self.file_urls = {}
            
        self.file_urls[format_type] = url
        self.updated_at = datetime.now().isoformat()
    
    def set_schedule(self, frequency: Union[ReportFrequency, str], next_run: Union[datetime, str]) -> None:
        """Set the report schedule"""
        if isinstance(frequency, str):
            frequency = ReportFrequency(frequency)
            
        if isinstance(next_run, str):
            next_run = datetime.fromisoformat(next_run)
            
        self.scheduled = True
        self.frequency = frequency
        self.next_run = next_run
        self.status = ReportStatus.SCHEDULED
        self.updated_at = datetime.now().isoformat()


class Metric(BaseModel):
    """A metric to track and analyze system data"""
    
    def __init__(
        self,
        name: str,
        description: str,
        category: str,
        unit: str,
        calculation_method: str,
        data_source: str,
        agency_id: Optional[str] = None,
        program_id: Optional[str] = None,
        target_value: Optional[float] = None,
        warning_threshold: Optional[float] = None,
        critical_threshold: Optional[float] = None,
        is_higher_better: bool = True,
        display_format: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize a metric"""
        super().__init__(
            name=name,
            description=description,
            category=category,
            unit=unit,
            calculation_method=calculation_method,
            data_source=data_source,
            agency_id=agency_id,
            program_id=program_id,
            target_value=target_value,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            is_higher_better=is_higher_better,
            display_format=display_format,
            metadata=metadata or {},
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Metric':
        """Create from dictionary representation"""
        return cls(**data)


class MetricValue(BaseModel):
    """A recorded value for a metric at a specific time"""
    
    def __init__(
        self,
        metric_id: str,
        value: float,
        timestamp: Union[datetime, str],
        status: str = "normal",
        source_data: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None,
        **kwargs
    ):
        """Initialize a metric value"""
        # Convert timestamp string to datetime if needed
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        super().__init__(
            metric_id=metric_id,
            value=value,
            timestamp=timestamp,
            status=status,
            source_data=source_data or {},
            notes=notes,
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert datetime to string
        if 'timestamp' in result and isinstance(result['timestamp'], datetime):
            result['timestamp'] = result['timestamp'].isoformat()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetricValue':
        """Create from dictionary representation"""
        return cls(**data)


class Dashboard(BaseModel):
    """A dashboard displaying multiple metrics and reports"""
    
    def __init__(
        self,
        name: str,
        description: str,
        layout: List[Dict[str, Any]],
        owner_id: str,
        agency_id: Optional[str] = None,
        is_public: bool = False,
        shared_with: Optional[List[str]] = None,
        refresh_interval: Optional[int] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize a dashboard"""
        super().__init__(
            name=name,
            description=description,
            layout=layout,
            owner_id=owner_id,
            agency_id=agency_id,
            is_public=is_public,
            shared_with=shared_with or [],
            refresh_interval=refresh_interval,
            tags=tags or [],
            metadata=metadata or {},
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dashboard':
        """Create from dictionary representation"""
        return cls(**data)
    
    def add_widget(self, widget_type: str, title: str, data_source: Dict[str, Any], 
                 position: Dict[str, int], size: Dict[str, int], 
                 configuration: Optional[Dict[str, Any]] = None) -> None:
        """Add a widget to the dashboard layout"""
        if not hasattr(self, 'layout'):
            self.layout = []
            
        widget = {
            'id': f"widget_{len(self.layout) + 1}",
            'type': widget_type,
            'title': title,
            'data_source': data_source,
            'position': position,
            'size': size,
            'configuration': configuration or {}
        }
        
        self.layout.append(widget)
        self.updated_at = datetime.now().isoformat()
    
    def share_with(self, user_id: str) -> None:
        """Share the dashboard with a user"""
        if not hasattr(self, 'shared_with'):
            self.shared_with = []
            
        if user_id not in self.shared_with:
            self.shared_with.append(user_id)
            self.updated_at = datetime.now().isoformat()