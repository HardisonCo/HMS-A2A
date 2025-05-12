"""
Surveillance models for the APHIS Bird Flu Tracking System.
Defines data models for surveillance sites and sampling plans.
"""
from typing import Dict, Any, Optional, List, Union
from datetime import date, datetime
from enum import Enum

from .base import BaseModel, GeoLocation, GeoRegion


class SiteType(str, Enum):
    """Types of surveillance sites"""
    COMMERCIAL_POULTRY = "commercial_poultry"
    BACKYARD_POULTRY = "backyard_poultry"
    LIVE_BIRD_MARKET = "live_bird_market"
    WILD_BIRD_HABITAT = "wild_bird_habitat"
    WATERFOWL_REST_AREA = "waterfowl_rest_area"
    POULTRY_EXHIBITION = "poultry_exhibition"
    RENDERING_PLANT = "rendering_plant"
    FEED_MILL = "feed_mill"
    PROCESSING_PLANT = "processing_plant"
    HATCHERY = "hatchery"
    OTHER = "other"


class SiteStatus(str, Enum):
    """Status of a surveillance site"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    QUARANTINED = "quarantined"
    INFECTED = "infected"
    CLEANED = "cleaned_disinfected"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    """Risk levels for sites or regions"""
    NEGLIGIBLE = "negligible"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    UNKNOWN = "unknown"


class SurveillanceSite(BaseModel):
    """A site where surveillance is being conducted"""
    
    def __init__(
        self,
        name: str,
        location: Union[GeoLocation, Dict[str, Any]],
        site_type: Union[SiteType, str],
        jurisdiction: str,
        population: Optional[int] = None,
        status: Union[SiteStatus, str] = SiteStatus.ACTIVE,
        risk_level: Union[RiskLevel, str] = RiskLevel.UNKNOWN,
        risk_factors: Optional[Dict[str, Any]] = None,
        sampling_history: Optional[List[Dict[str, Any]]] = None,
        contact_info: Optional[Dict[str, str]] = None,
        notes: Optional[str] = None,
        **kwargs
    ):
        """Initialize a surveillance site"""
        # Convert location dict to GeoLocation if needed
        if isinstance(location, dict):
            location = GeoLocation.from_dict(location)
        
        # Convert string enums to Enum values if needed
        if isinstance(site_type, str):
            site_type = SiteType(site_type)
        
        if isinstance(status, str):
            status = SiteStatus(status)
        
        if isinstance(risk_level, str):
            risk_level = RiskLevel(risk_level)
        
        super().__init__(
            name=name,
            location=location,
            site_type=site_type,
            jurisdiction=jurisdiction,
            population=population,
            status=status,
            risk_level=risk_level,
            risk_factors=risk_factors or {},
            sampling_history=sampling_history or [],
            contact_info=contact_info or {},
            notes=notes,
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert complex objects to dictionaries
        if isinstance(result.get('location'), GeoLocation):
            result['location'] = result['location'].to_dict()
        
        # Convert enum values to strings
        for field in ['site_type', 'status', 'risk_level']:
            if field in result and isinstance(result[field], Enum):
                result[field] = result[field].value
        
        return result
    
    def add_sampling_event(self, 
                          date: Union[date, str], 
                          samples_collected: int, 
                          collector: str, 
                          results: Optional[Dict[str, Any]] = None) -> None:
        """Add a sampling event to the site's history"""
        # Convert date string to date if needed
        if isinstance(date, str):
            date = date.fromisoformat(date)
        
        sampling_event = {
            'date': date.isoformat(),
            'samples_collected': samples_collected,
            'collector': collector,
            'results': results or {}
        }
        
        self.sampling_history.append(sampling_event)
        self.updated_at = datetime.now().isoformat()
    
    def update_risk_level(self, new_level: Union[RiskLevel, str], reason: Optional[str] = None) -> None:
        """Update the site's risk level"""
        if isinstance(new_level, str):
            new_level = RiskLevel(new_level)
        
        old_level = self.risk_level
        self.risk_level = new_level
        
        # Add to risk factors if reason provided
        if reason:
            risk_update = {
                'date': datetime.now().isoformat(),
                'old_level': old_level.value if isinstance(old_level, Enum) else old_level,
                'new_level': new_level.value,
                'reason': reason
            }
            
            if 'risk_history' not in self.risk_factors:
                self.risk_factors['risk_history'] = []
            
            self.risk_factors['risk_history'].append(risk_update)
        
        self.updated_at = datetime.now().isoformat()
    
    def update_status(self, new_status: Union[SiteStatus, str], reason: Optional[str] = None) -> None:
        """Update the site's status"""
        if isinstance(new_status, str):
            new_status = SiteStatus(new_status)
        
        old_status = self.status
        self.status = new_status
        
        # Record status change if reason provided
        if reason:
            status_update = {
                'date': datetime.now().isoformat(),
                'old_status': old_status.value if isinstance(old_status, Enum) else old_status,
                'new_status': new_status.value,
                'reason': reason
            }
            
            if 'status_history' not in self.__dict__:
                self.status_history = []
            
            self.status_history.append(status_update)
        
        self.updated_at = datetime.now().isoformat()


class AllocationStrategy(str, Enum):
    """Strategies for allocating sampling resources"""
    EQUAL = "equal_allocation"
    RISK_BASED = "risk_based"
    RESPONSE_ADAPTIVE = "response_adaptive"
    OPTIMIZED = "optimized"
    MANUAL = "manual"


class AdaptiveSamplingPlan(BaseModel):
    """A plan for adapting sampling based on real-time data"""
    
    def __init__(
        self,
        name: str,
        region: Union[GeoRegion, Dict[str, Any]],
        start_date: Union[date, str],
        end_date: Union[date, str],
        allocation_strategy: Union[AllocationStrategy, str] = AllocationStrategy.RISK_BASED,
        sample_sites: Optional[List[str]] = None,  # List of site IDs
        current_stage: int = 0,
        max_stages: int = 3,
        total_resources: Optional[Dict[str, int]] = None,
        stage_results: Optional[List[Dict[str, Any]]] = None,
        adaptation_rules: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None,
        **kwargs
    ):
        """Initialize an adaptive sampling plan"""
        # Convert region dict to GeoRegion if needed
        if isinstance(region, dict):
            region = GeoRegion.from_dict(region)
        
        # Convert date strings to date if needed
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)
        
        # Convert string enum to Enum value if needed
        if isinstance(allocation_strategy, str):
            allocation_strategy = AllocationStrategy(allocation_strategy)
        
        super().__init__(
            name=name,
            region=region,
            start_date=start_date,
            end_date=end_date,
            allocation_strategy=allocation_strategy,
            sample_sites=sample_sites or [],
            current_stage=current_stage,
            max_stages=max_stages,
            total_resources=total_resources or {'tests': 0, 'personnel_hours': 0},
            stage_results=stage_results or [],
            adaptation_rules=adaptation_rules or {},
            notes=notes,
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert complex objects to dictionaries
        if isinstance(result.get('region'), GeoRegion):
            result['region'] = result['region'].to_dict()
        
        # Convert date objects to strings
        for field in ['start_date', 'end_date']:
            if field in result and isinstance(result[field], date):
                result[field] = result[field].isoformat()
        
        # Convert enum values to strings
        if 'allocation_strategy' in result and isinstance(result['allocation_strategy'], Enum):
            result['allocation_strategy'] = result['allocation_strategy'].value
        
        return result
    
    def add_site(self, site_id: str) -> None:
        """Add a site to the sampling plan"""
        if site_id not in self.sample_sites:
            self.sample_sites.append(site_id)
            self.updated_at = datetime.now().isoformat()
    
    def remove_site(self, site_id: str) -> None:
        """Remove a site from the sampling plan"""
        if site_id in self.sample_sites:
            self.sample_sites.remove(site_id)
            self.updated_at = datetime.now().isoformat()
    
    def advance_stage(self, stage_summary: Dict[str, Any]) -> bool:
        """
        Advance to the next stage of the sampling plan
        Returns True if successfully advanced, False if already at max stage
        """
        if self.current_stage >= self.max_stages - 1:
            return False
        
        self.stage_results.append({
            'stage': self.current_stage,
            'date': datetime.now().isoformat(),
            'summary': stage_summary
        })
        
        self.current_stage += 1
        self.updated_at = datetime.now().isoformat()
        return True
    
    def get_current_allocations(self) -> Dict[str, float]:
        """
        Get the current resource allocation for each site
        Returns a dictionary mapping site IDs to allocation proportions
        """
        # This is a placeholder implementation
        # In a real system, this would use the allocation_strategy to calculate
        # the appropriate allocation based on the adaptation_rules and stage_results
        
        total_sites = len(self.sample_sites)
        if total_sites == 0:
            return {}
        
        if self.allocation_strategy == AllocationStrategy.EQUAL:
            return {site_id: 1.0 / total_sites for site_id in self.sample_sites}
        
        # For other strategies, this would be more complex
        # For now, return equal allocation as a placeholder
        return {site_id: 1.0 / total_sites for site_id in self.sample_sites}


class SurveillanceEvent(BaseModel):
    """A surveillance sampling event at a particular site"""
    
    def __init__(
        self,
        site_id: str,
        plan_id: Optional[str],
        event_date: Union[date, str],
        collector: str,
        samples_collected: int,
        sample_types: List[str],
        target_species: List[str],
        weather_conditions: Optional[Dict[str, Any]] = None,
        samples: Optional[List[str]] = None,  # List of sample IDs
        notes: Optional[str] = None,
        **kwargs
    ):
        """Initialize a surveillance event"""
        # Convert date string to date if needed
        if isinstance(event_date, str):
            event_date = date.fromisoformat(event_date)
        
        super().__init__(
            site_id=site_id,
            plan_id=plan_id,
            event_date=event_date,
            collector=collector,
            samples_collected=samples_collected,
            sample_types=sample_types,
            target_species=target_species,
            weather_conditions=weather_conditions or {},
            samples=samples or [],
            notes=notes,
            **kwargs
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = super().to_dict()
        
        # Convert date to string
        if isinstance(result.get('event_date'), date):
            result['event_date'] = result['event_date'].isoformat()
        
        return result
    
    def add_sample(self, sample_id: str) -> None:
        """Add a sample to the surveillance event"""
        if sample_id not in self.samples:
            self.samples.append(sample_id)
            self.updated_at = datetime.now().isoformat()
    
    def update_count(self, new_count: int) -> None:
        """Update the samples collected count"""
        self.samples_collected = new_count
        self.updated_at = datetime.now().isoformat()