"""
Controller for avian influenza visualization services.

This module provides API endpoints for generating maps, charts,
and other visualizations for avian influenza data.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import base64

from ..models.base import GeoRegion
from ..models.case import Case
from ..models.surveillance import SurveillanceSite, SurveillanceEvent
from ..services.visualization import MapGenerator, DashboardGenerator

# Define API models
class MapRequest(BaseModel):
    """Parameters for generating a map visualization."""
    map_type: str = Field(..., description="Type of map to generate")
    start_date: Optional[str] = Field(None, description="Start date for filtering (ISO format)")
    end_date: Optional[str] = Field(None, description="End date for filtering (ISO format)")
    region_level: str = Field("county", description="Level of regional boundaries to display")
    title: Optional[str] = Field(None, description="Optional title for the map")
    width: int = Field(1200, description="Width of the map in pixels")
    height: int = Field(900, description="Height of the map in pixels")
    show_legend: bool = Field(True, description="Whether to show the legend")
    include_cases: bool = Field(True, description="Whether to include case data")
    include_surveillance: bool = Field(False, description="Whether to include surveillance sites")
    
    class Config:
        schema_extra = {
            "example": {
                "map_type": "case_map",
                "start_date": "2023-04-01T00:00:00",
                "end_date": "2023-05-01T00:00:00",
                "region_level": "county",
                "title": "Avian Influenza Cases - April 2023",
                "width": 1200,
                "height": 900,
                "show_legend": True,
                "include_cases": True,
                "include_surveillance": False
            }
        }

class ChartRequest(BaseModel):
    """Parameters for generating a chart visualization."""
    chart_type: str = Field(..., description="Type of chart to generate")
    days: int = Field(30, description="Number of days to include")
    title: Optional[str] = Field(None, description="Optional title for the chart")
    width: int = Field(800, description="Width of the chart in pixels")
    height: int = Field(500, description="Height of the chart in pixels")
    show_legend: bool = Field(True, description="Whether to show the legend")
    include_subtypes: bool = Field(True, description="Whether to break down by virus subtype")
    by_site_type: bool = Field(True, description="Whether to break down by site type")
    top_n: int = Field(10, description="Number of top items to display")
    chart_style: str = Field("pie", description="Style of chart (pie, bar, etc.)")
    
    class Config:
        schema_extra = {
            "example": {
                "chart_type": "case_trend",
                "days": 30,
                "title": "Avian Influenza Cases - Last 30 Days",
                "width": 800,
                "height": 500,
                "show_legend": True,
                "include_subtypes": True
            }
        }

class DashboardRequest(BaseModel):
    """Parameters for generating dashboard data."""
    days: int = Field(30, description="Number of days to include in summary")
    include_charts: bool = Field(True, description="Whether to include chart visualizations")
    include_maps: bool = Field(True, description="Whether to include map visualizations")
    
    class Config:
        schema_extra = {
            "example": {
                "days": 30,
                "include_charts": True,
                "include_maps": True
            }
        }

class RiskMapRequest(BaseModel):
    """Parameters for generating a risk map."""
    forecast_date: Optional[str] = Field(None, description="Date of the forecast (ISO format)")
    days_ahead: int = Field(7, description="Number of days ahead in the forecast")
    title: Optional[str] = Field(None, description="Optional title for the map")
    width: int = Field(1200, description="Width of the map in pixels")
    height: int = Field(900, description="Height of the map in pixels")
    show_legend: bool = Field(True, description="Whether to show the legend")
    
    class Config:
        schema_extra = {
            "example": {
                "forecast_date": "2023-05-01",
                "days_ahead": 7,
                "title": "Avian Influenza Risk Forecast - Next 7 Days",
                "width": 1200,
                "height": 900,
                "show_legend": True
            }
        }

class TransmissionMapRequest(BaseModel):
    """Parameters for generating a transmission network map."""
    start_date: Optional[str] = Field(None, description="Start date for filtering (ISO format)")
    end_date: Optional[str] = Field(None, description="End date for filtering (ISO format)")
    title: Optional[str] = Field(None, description="Optional title for the map")
    width: int = Field(1200, description="Width of the map in pixels")
    height: int = Field(900, description="Height of the map in pixels")
    show_legend: bool = Field(True, description="Whether to show the legend")
    
    class Config:
        schema_extra = {
            "example": {
                "start_date": "2023-04-01T00:00:00",
                "end_date": "2023-05-01T00:00:00",
                "title": "Avian Influenza Transmission Network - April 2023",
                "width": 1200,
                "height": 900,
                "show_legend": True
            }
        }

# Create router
router = APIRouter(
    prefix="/api/v1/visualizations",
    tags=["visualizations"],
    responses={404: {"description": "Not found"}},
)

# Service dependencies
def get_map_generator():
    """Dependency to get map generator service instance."""
    # In production, this would load boundary files from configuration
    boundary_file = None
    state_file = None
    county_file = None
    
    return MapGenerator(
        boundary_file=boundary_file,
        state_file=state_file,
        county_file=county_file
    )

def get_dashboard_generator():
    """Dependency to get dashboard generator service instance."""
    return DashboardGenerator()

# Data access dependencies
def get_case_repository():
    """Dependency to get case repository."""
    # This would be implemented based on your data access layer
    return None

def get_region_repository():
    """Dependency to get region repository."""
    # This would be implemented based on your data access layer
    return None

def get_surveillance_repository():
    """Dependency to get surveillance repository."""
    # This would be implemented based on your data access layer
    return None

def get_forecast_repository():
    """Dependency to get forecast repository."""
    # This would be implemented based on your data access layer
    return None

# API endpoints
@router.post("/maps", response_model=Dict[str, Any])
async def generate_map(
    request: MapRequest,
    map_generator: MapGenerator = Depends(get_map_generator),
    case_repo = Depends(get_case_repository),
    region_repo = Depends(get_region_repository),
    surveillance_repo = Depends(get_surveillance_repository)
):
    """
    Generate a map visualization of avian influenza data.
    """
    # Get cases
    cases = []
    if request.include_cases:
        # Get cases filtered by date range
        start_date = request.start_date or (datetime.now() - timedelta(days=30)).isoformat()
        end_date = request.end_date or datetime.now().isoformat()
        cases = case_repo.get_cases_by_date_range(start_date, end_date)
    
    # Get regions
    regions = region_repo.get_all_regions()
    
    # Get surveillance sites if needed
    surveillance_sites = []
    if request.include_surveillance:
        surveillance_sites = surveillance_repo.get_all_surveillance_sites()
    
    # Generate the appropriate map
    result = {}
    
    if request.map_type == "case_map":
        result = map_generator.create_case_map(
            cases=cases,
            regions=regions,
            start_date=request.start_date,
            end_date=request.end_date,
            title=request.title,
            show_legend=request.show_legend,
            width=request.width,
            height=request.height,
            region_level=request.region_level
        )
    elif request.map_type == "surveillance_map":
        # Get sampling allocation if available
        sampling_allocation = surveillance_repo.get_current_sampling_allocation()
        
        result = map_generator.create_surveillance_map(
            surveillance_sites=surveillance_sites,
            cases=cases if request.include_cases else None,
            regions=regions,
            sampling_allocation=sampling_allocation,
            title=request.title,
            width=request.width,
            height=request.height,
            show_legend=request.show_legend
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported map type: {request.map_type}")
    
    return result

@router.post("/maps/risk", response_model=Dict[str, Any])
async def generate_risk_map(
    request: RiskMapRequest,
    map_generator: MapGenerator = Depends(get_map_generator),
    region_repo = Depends(get_region_repository),
    forecast_repo = Depends(get_forecast_repository)
):
    """
    Generate a risk map visualization based on predictive model outputs.
    """
    # Get regions
    regions = region_repo.get_all_regions()
    
    # Get forecast data
    forecast_date = request.forecast_date or datetime.now().date().isoformat()
    risk_data = forecast_repo.get_risk_forecast(
        forecast_date=forecast_date,
        days_ahead=request.days_ahead
    )
    
    # Get region mapping if needed
    region_mapping = forecast_repo.get_region_mapping()
    
    # Generate risk map
    result = map_generator.create_risk_map(
        risk_data=risk_data,
        regions=regions,
        region_mapping=region_mapping,
        title=request.title,
        prediction_date=forecast_date,
        days_ahead=request.days_ahead,
        width=request.width,
        height=request.height,
        show_legend=request.show_legend
    )
    
    return result

@router.post("/maps/transmission", response_model=Dict[str, Any])
async def generate_transmission_map(
    request: TransmissionMapRequest,
    map_generator: MapGenerator = Depends(get_map_generator),
    case_repo = Depends(get_case_repository),
    region_repo = Depends(get_region_repository),
    forecast_repo = Depends(get_forecast_repository)
):
    """
    Generate a transmission network map visualization.
    """
    # Get cases
    start_date = request.start_date or (datetime.now() - timedelta(days=30)).isoformat()
    end_date = request.end_date or datetime.now().isoformat()
    cases = case_repo.get_cases_by_date_range(start_date, end_date)
    
    # Get regions
    regions = region_repo.get_all_regions()
    
    # Get transmission paths
    # This would typically come from a model or analysis
    transmission_paths = forecast_repo.get_transmission_paths(
        start_date=start_date,
        end_date=end_date
    )
    
    # Generate transmission map
    result = map_generator.create_transmission_network_map(
        cases=cases,
        transmission_paths=transmission_paths,
        regions=regions,
        title=request.title,
        width=request.width,
        height=request.height,
        show_legend=request.show_legend
    )
    
    return result

@router.post("/charts", response_model=Dict[str, Any])
async def generate_chart(
    request: ChartRequest,
    dashboard_generator: DashboardGenerator = Depends(get_dashboard_generator),
    case_repo = Depends(get_case_repository),
    region_repo = Depends(get_region_repository),
    surveillance_repo = Depends(get_surveillance_repository)
):
    """
    Generate a chart visualization of avian influenza data.
    """
    # Get data needed for the chart
    result = {}
    
    if request.chart_type == "case_trend":
        # Get cases for the specified period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days)
        cases = case_repo.get_cases_by_date_range(
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        result = dashboard_generator.create_case_trend_chart(
            cases=cases,
            days=request.days,
            title=request.title,
            include_subtypes=request.include_subtypes,
            width=request.width,
            height=request.height,
            show_legend=request.show_legend
        )
    
    elif request.chart_type == "geographic_distribution":
        # Get cases and regions
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days)
        cases = case_repo.get_cases_by_date_range(
            start_date.isoformat(),
            end_date.isoformat()
        )
        regions = region_repo.get_all_regions()
        
        result = dashboard_generator.create_geographic_distribution_chart(
            cases=cases,
            regions=regions,
            days=request.days,
            title=request.title,
            top_n=request.top_n,
            width=request.width,
            height=request.height
        )
    
    elif request.chart_type == "subtype_distribution":
        # Get cases
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days)
        cases = case_repo.get_cases_by_date_range(
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        result = dashboard_generator.create_subtype_distribution_chart(
            cases=cases,
            days=request.days,
            title=request.title,
            chart_type=request.chart_style,
            width=request.width,
            height=request.height
        )
    
    elif request.chart_type == "surveillance_effectiveness":
        # Get surveillance events
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days)
        events = surveillance_repo.get_events_by_date_range(
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        result = dashboard_generator.create_surveillance_effectiveness_chart(
            surveillance_events=events,
            days=request.days,
            title=request.title,
            by_site_type=request.by_site_type,
            width=request.width,
            height=request.height
        )
    
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported chart type: {request.chart_type}")
    
    return result

@router.post("/dashboard", response_model=Dict[str, Any])
async def generate_dashboard(
    request: DashboardRequest,
    dashboard_generator: DashboardGenerator = Depends(get_dashboard_generator),
    map_generator: MapGenerator = Depends(get_map_generator),
    case_repo = Depends(get_case_repository),
    region_repo = Depends(get_region_repository),
    surveillance_repo = Depends(get_surveillance_repository)
):
    """
    Generate a complete dashboard with summary statistics and visualizations.
    """
    # Get data for the specified period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=request.days)
    
    cases = case_repo.get_cases_by_date_range(
        start_date.isoformat(),
        end_date.isoformat()
    )
    
    events = surveillance_repo.get_events_by_date_range(
        start_date.isoformat(),
        end_date.isoformat()
    )
    
    # Generate summary statistics
    summary = dashboard_generator.generate_summary_statistics(
        cases=cases,
        surveillance_events=events,
        days=request.days
    )
    
    # Initialize dashboard result
    dashboard = {
        "summary": summary,
        "charts": {},
        "maps": {}
    }
    
    # Add charts if requested
    if request.include_charts:
        # Add case trend chart
        case_trend_chart = dashboard_generator.create_case_trend_chart(
            cases=cases,
            days=request.days,
            title=f"Avian Influenza Cases - Last {request.days} Days",
            include_subtypes=True,
            width=800,
            height=400,
            show_legend=True
        )
        dashboard["charts"]["case_trend"] = case_trend_chart
        
        # Add subtype distribution chart
        subtype_chart = dashboard_generator.create_subtype_distribution_chart(
            cases=cases,
            days=request.days,
            title=f"Virus Subtype Distribution - Last {request.days} Days",
            chart_type="pie",
            width=600,
            height=400
        )
        dashboard["charts"]["subtype_distribution"] = subtype_chart
        
        # Add surveillance effectiveness chart if we have events
        if events:
            surveillance_chart = dashboard_generator.create_surveillance_effectiveness_chart(
                surveillance_events=events,
                days=request.days,
                title=f"Surveillance Effectiveness - Last {request.days} Days",
                by_site_type=True,
                width=800,
                height=400
            )
            dashboard["charts"]["surveillance_effectiveness"] = surveillance_chart
        
        # Add geographic distribution chart
        regions = region_repo.get_all_regions()
        geo_chart = dashboard_generator.create_geographic_distribution_chart(
            cases=cases,
            regions=regions,
            days=request.days,
            title=f"Top Regions by Case Count - Last {request.days} Days",
            top_n=10,
            width=800,
            height=400
        )
        dashboard["charts"]["geographic_distribution"] = geo_chart
    
    # Add maps if requested
    if request.include_maps:
        # Add case map
        regions = region_repo.get_all_regions()
        case_map = map_generator.create_case_map(
            cases=cases,
            regions=regions,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            title=f"Avian Influenza Cases - Last {request.days} Days",
            show_legend=True,
            width=1000,
            height=600,
            region_level="county"
        )
        dashboard["maps"]["case_map"] = case_map
    
    return dashboard

@router.get("/image/{image_id}")
async def get_visualization_image(
    image_id: str = Path(..., description="Image identifier")
):
    """
    Get a visualization image directly by ID.
    """
    # This endpoint would retrieve a previously generated visualization
    # by its ID, allowing direct embedding in web pages or other applications
    
    # For now, we'll return a 501 Not Implemented
    raise HTTPException(status_code=501, detail="Not implemented")
    
    # In a real implementation, you would:
    # 1. Retrieve the image data from storage using the image_id
    # 2. Return it with the appropriate content type
    # 
    # For example:
    # image_data = visualization_storage.get_image(image_id)
    # if not image_data:
    #     raise HTTPException(status_code=404, detail="Image not found")
    # 
    # return Response(
    #     content=base64.b64decode(image_data),
    #     media_type="image/png"
    # )