"""
Bird Flu Unified Dashboard Application

This application integrates data from CDC, EPA, and FEMA to provide
a comprehensive view of bird flu monitoring and response across agencies.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
import requests
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)

# Configuration
FEDERATION_API_URL = os.environ.get('FEDERATION_API_URL', 'http://localhost:8000/api/v1/federation')

def get_federated_data(query_type, parameters=None, agencies=None):
    """
    Execute a federated query across agencies.
    
    Args:
        query_type: Type of query to execute
        parameters: Query parameters
        agencies: List of agencies to query (None = all)
        
    Returns:
        Dictionary with results from each agency
    """
    if parameters is None:
        parameters = {}
        
    query = {
        "type": query_type,
        "parameters": parameters,
        "agencies": agencies
    }
    
    try:
        response = requests.post(f"{FEDERATION_API_URL}/query", json=query)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error executing federated query: {str(e)}")
        return {"error": str(e)}

def get_joint_analysis(analysis_type, parameters=None, agencies=None):
    """
    Execute a joint analysis across agencies.
    
    Args:
        analysis_type: Type of analysis to execute
        parameters: Analysis parameters
        agencies: List of agencies to include
        
    Returns:
        Analysis results
    """
    if parameters is None:
        parameters = {}
        
    analysis_request = {
        "analysis_type": analysis_type,
        "parameters": parameters,
        "requesting_agency": "dashboard",
        "target_agencies": agencies
    }
    
    try:
        response = requests.post(f"{FEDERATION_API_URL}/analysis", json=analysis_request)
        response.raise_for_status()
        
        # Get analysis ID from response
        analysis_id = response.json().get("analysis_id")
        if not analysis_id:
            return {"error": "No analysis ID returned"}
            
        # Poll for analysis completion (simple approach for demo)
        for _ in range(10):  # Try up to 10 times
            status_response = requests.get(f"{FEDERATION_API_URL}/analysis/{analysis_id}")
            status_response.raise_for_status()
            result = status_response.json()
            
            if result.get("status") == "completed":
                return result
                
        return {"error": "Analysis timed out", "analysis_id": analysis_id}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error executing joint analysis: {str(e)}")
        return {"error": str(e)}

def create_chart_from_data(chart_type, data, title=None, **kwargs):
    """
    Create a base64-encoded chart image from data.
    
    Args:
        chart_type: Type of chart to create (time_series, bar, pie, etc.)
        data: Data for the chart
        title: Chart title
        **kwargs: Additional parameters for the chart
        
    Returns:
        Base64-encoded PNG image
    """
    # Set style
    sns.set_style('whitegrid')
    
    # Create figure
    figsize = kwargs.get('figsize', (10, 6))
    fig, ax = plt.subplots(figsize=figsize)
    
    # Different chart types
    if chart_type == 'time_series':
        x = data.get('dates', [])
        y = data.get('values', [])
        labels = data.get('labels', None)
        
        if labels:
            # Multiple series
            for i, label in enumerate(labels):
                ax.plot(x, y[i], label=label)
            ax.legend()
        else:
            # Single series
            ax.plot(x, y)
            
        ax.set_xlabel('Date')
        ax.set_ylabel(kwargs.get('ylabel', 'Value'))
        plt.xticks(rotation=45)
        
    elif chart_type == 'bar':
        x = data.get('categories', [])
        y = data.get('values', [])
        color = kwargs.get('color', 'steelblue')
        
        ax.bar(x, y, color=color)
        ax.set_xlabel(kwargs.get('xlabel', 'Category'))
        ax.set_ylabel(kwargs.get('ylabel', 'Value'))
        plt.xticks(rotation=45)
        
    elif chart_type == 'pie':
        labels = data.get('labels', [])
        values = data.get('values', [])
        
        ax.pie(values, labels=labels, autopct='%1.1f%%')
        ax.axis('equal')  # Equal aspect ratio ensures circular pie
        
    elif chart_type == 'heatmap':
        matrix = data.get('matrix', [])
        x_labels = data.get('x_labels', [])
        y_labels = data.get('y_labels', [])
        
        sns.heatmap(matrix, annot=True, fmt=".2f", cmap="YlGnBu", 
                   xticklabels=x_labels, yticklabels=y_labels, ax=ax)
        
    elif chart_type == 'scatter':
        x = data.get('x', [])
        y = data.get('y', [])
        color = kwargs.get('color', 'steelblue')
        
        ax.scatter(x, y, color=color, alpha=0.7)
        ax.set_xlabel(kwargs.get('xlabel', 'X'))
        ax.set_ylabel(kwargs.get('ylabel', 'Y'))
    
    # Set title
    if title:
        ax.set_title(title)
        
    # Make layout tight
    fig.tight_layout()
    
    # Convert to base64 image
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    
    return img_base64

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')

@app.route('/api/summary')
def get_summary():
    """Get summary of bird flu data across all agencies."""
    try:
        # Get case summary from CDC
        cdc_data = get_federated_data("disease_surveillance", {
            "disease_type": "avian_influenza",
            "start_date": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            "end_date": datetime.now().strftime('%Y-%m-%d')
        }, ["cdc"])
        
        # Get environmental quality data from EPA
        epa_data = get_federated_data("env_quality_monitoring", {
            "factor_type": "air_quality",
            "start_date": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            "end_date": datetime.now().strftime('%Y-%m-%d')
        }, ["epa"])
        
        # Get resource deployment data from FEMA
        fema_data = get_federated_data("resource_deployment", {
            "emergency_type": "disease_outbreak",
            "start_date": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            "end_date": datetime.now().strftime('%Y-%m-%d')
        }, ["fema"])
        
        # Process and combine data
        summary = {
            "timestamp": datetime.now().isoformat(),
            "health": process_cdc_summary(cdc_data),
            "environmental": process_epa_summary(epa_data),
            "emergency": process_fema_summary(fema_data)
        }
        
        return jsonify(summary)
    except Exception as e:
        logger.exception("Error generating summary")
        return jsonify({"error": str(e)})

def process_cdc_summary(cdc_data):
    """Process CDC data for summary display."""
    # Extract CDC agency data
    cdc_agency_data = cdc_data.get("cdc", {})
    
    # Check for errors
    if "error" in cdc_agency_data:
        return {"error": cdc_agency_data["error"]}
    
    # Extract surveillance data
    data = cdc_agency_data.get("data", [])
    
    # Process data for summary
    total_cases = 0
    human_cases = 0
    bird_cases = 0
    by_subtype = {}
    
    for case in data:
        total_cases += 1
        
        # Count by host type
        host_type = case.get("host_type", "unknown")
        if host_type == "human":
            human_cases += 1
        elif host_type == "bird":
            bird_cases += 1
            
        # Count by subtype
        subtype = case.get("virus_subtype", "unknown")
        if subtype not in by_subtype:
            by_subtype[subtype] = 0
        by_subtype[subtype] += 1
    
    return {
        "total_cases": total_cases,
        "human_cases": human_cases,
        "bird_cases": bird_cases,
        "by_subtype": by_subtype
    }

def process_epa_summary(epa_data):
    """Process EPA data for summary display."""
    # Extract EPA agency data
    epa_agency_data = epa_data.get("epa", {})
    
    # Check for errors
    if "error" in epa_agency_data:
        return {"error": epa_agency_data["error"]}
    
    # Extract monitoring data
    data = epa_agency_data.get("data", [])
    
    # Process data for summary
    monitoring_sites = len(set(item.get("site_id") for item in data))
    air_quality_ratings = {}
    
    for item in data:
        rating = item.get("quality_rating", "unknown")
        if rating not in air_quality_ratings:
            air_quality_ratings[rating] = 0
        air_quality_ratings[rating] += 1
    
    return {
        "monitoring_sites": monitoring_sites,
        "air_quality_ratings": air_quality_ratings
    }

def process_fema_summary(fema_data):
    """Process FEMA data for summary display."""
    # Extract FEMA agency data
    fema_agency_data = fema_data.get("fema", {})
    
    # Check for errors
    if "error" in fema_agency_data:
        return {"error": fema_agency_data["error"]}
    
    # Extract resource data
    data = fema_agency_data.get("data", [])
    
    # Process data for summary
    active_deployments = 0
    resources_deployed = 0
    regions_covered = set()
    
    for item in data:
        if item.get("status") == "active":
            active_deployments += 1
            resources_deployed += item.get("quantity", 0)
            regions_covered.add(item.get("region"))
    
    return {
        "active_deployments": active_deployments,
        "resources_deployed": resources_deployed,
        "regions_covered": len(regions_covered)
    }

@app.route('/api/cdc/cases')
def get_cdc_cases():
    """Get CDC case data for visualization."""
    try:
        # Get parameters
        days = int(request.args.get('days', 30))
        region = request.args.get('region')
        
        # Build query parameters
        params = {
            "disease_type": "avian_influenza",
            "start_date": (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            "end_date": datetime.now().strftime('%Y-%m-%d')
        }
        
        if region:
            params["region"] = region
            
        # Execute query
        cdc_data = get_federated_data("disease_surveillance", params, ["cdc"])
        
        # Extract and format data
        if "cdc" in cdc_data:
            cases = cdc_data["cdc"].get("data", [])
            return jsonify({"cases": cases})
        else:
            return jsonify({"error": "No CDC data available"})
    except Exception as e:
        logger.exception("Error retrieving CDC case data")
        return jsonify({"error": str(e)})

@app.route('/api/epa/air_quality')
def get_epa_air_quality():
    """Get EPA air quality data for visualization."""
    try:
        # Get parameters
        days = int(request.args.get('days', 30))
        region = request.args.get('region')
        
        # Build query parameters
        params = {
            "factor_type": "air_quality",
            "start_date": (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            "end_date": datetime.now().strftime('%Y-%m-%d')
        }
        
        if region:
            params["region"] = region
            
        # Execute query
        epa_data = get_federated_data("env_quality_monitoring", params, ["epa"])
        
        # Extract and format data
        if "epa" in epa_data:
            measurements = epa_data["epa"].get("data", [])
            return jsonify({"measurements": measurements})
        else:
            return jsonify({"error": "No EPA data available"})
    except Exception as e:
        logger.exception("Error retrieving EPA air quality data")
        return jsonify({"error": str(e)})

@app.route('/api/fema/resources')
def get_fema_resources():
    """Get FEMA resource deployment data for visualization."""
    try:
        # Get parameters
        days = int(request.args.get('days', 30))
        region = request.args.get('region')
        
        # Build query parameters
        params = {
            "emergency_type": "disease_outbreak",
            "start_date": (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            "end_date": datetime.now().strftime('%Y-%m-%d')
        }
        
        if region:
            params["region"] = region
            
        # Execute query
        fema_data = get_federated_data("resource_deployment", params, ["fema"])
        
        # Extract and format data
        if "fema" in fema_data:
            deployments = fema_data["fema"].get("data", [])
            return jsonify({"deployments": deployments})
        else:
            return jsonify({"error": "No FEMA data available"})
    except Exception as e:
        logger.exception("Error retrieving FEMA resource data")
        return jsonify({"error": str(e)})

@app.route('/api/correlation')
def get_correlation_analysis():
    """Get correlation analysis between health cases and environmental factors."""
    try:
        # Get parameters
        days = int(request.args.get('days', 30))
        region = request.args.get('region')
        
        # Build analysis parameters
        params = {
            "analysis_type": "environmental_health_correlation",
            "parameters": {
                "env_factor": "air_quality",
                "health_outcome": "avian_influenza",
                "start_date": (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                "end_date": datetime.now().strftime('%Y-%m-%d'),
                "confidence_level": 0.95
            }
        }
        
        if region:
            params["parameters"]["region"] = region
            
        # Execute joint analysis
        analysis_results = get_joint_analysis(
            "environmental_health_correlation",
            params["parameters"],
            ["cdc", "epa"]
        )
        
        return jsonify(analysis_results)
    except Exception as e:
        logger.exception("Error retrieving correlation analysis")
        return jsonify({"error": str(e)})

@app.route('/api/case_map')
def get_case_map():
    """Generate a map visualization of bird flu cases."""
    try:
        # Get case data from CDC
        cdc_data = get_federated_data("disease_surveillance", {
            "disease_type": "avian_influenza",
            "start_date": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            "end_date": datetime.now().strftime('%Y-%m-%d')
        }, ["cdc"])
        
        # For demo purposes, we'll return a mock chart
        # In a real implementation, this would use a mapping library
        chart_data = {
            "dates": [(datetime.now() - timedelta(days=d)).strftime('%Y-%m-%d') for d in range(30, 0, -1)],
            "values": [list(range(5, 35)) for _ in range(3)],  # Sample data
            "labels": ["H5N1", "H7N9", "H9N2"]
        }
        
        img_base64 = create_chart_from_data('time_series', chart_data, 
                                         title="Bird Flu Cases - Last 30 Days", 
                                         figsize=(10, 6))
        
        return jsonify({
            "image": img_base64,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception("Error generating case map")
        return jsonify({"error": str(e)})

@app.route('/api/subtype_distribution')
def get_subtype_distribution():
    """Generate a chart showing distribution of virus subtypes."""
    try:
        # Get case data from CDC
        cdc_data = get_federated_data("disease_surveillance", {
            "disease_type": "avian_influenza",
            "start_date": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            "end_date": datetime.now().strftime('%Y-%m-%d')
        }, ["cdc"])
        
        # For demo purposes, create sample data
        # In a real implementation, this would process actual CDC data
        chart_data = {
            "labels": ["H5N1", "H7N9", "H9N2"],
            "values": [158, 67, 32]  # Sample data
        }
        
        img_base64 = create_chart_from_data('pie', chart_data, 
                                         title="Bird Flu Virus Subtype Distribution",
                                         figsize=(8, 8))
        
        return jsonify({
            "image": img_base64,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception("Error generating subtype distribution")
        return jsonify({"error": str(e)})

@app.route('/api/air_quality_trends')
def get_air_quality_trends():
    """Generate a chart showing air quality trends."""
    try:
        # Get air quality data from EPA
        epa_data = get_federated_data("env_quality_monitoring", {
            "factor_type": "air_quality",
            "start_date": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            "end_date": datetime.now().strftime('%Y-%m-%d')
        }, ["epa"])
        
        # For demo purposes, create sample data
        chart_data = {
            "dates": [(datetime.now() - timedelta(days=d)).strftime('%Y-%m-%d') for d in range(30, 0, -1)],
            "values": [[75 + i % 10 for i in range(30)]],  # Sample data with slight variation
            "labels": ["Air Quality Index"]
        }
        
        img_base64 = create_chart_from_data('time_series', chart_data, 
                                         title="Air Quality Index - Last 30 Days",
                                         ylabel="AQI Value",
                                         figsize=(10, 6))
        
        return jsonify({
            "image": img_base64,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception("Error generating air quality trends")
        return jsonify({"error": str(e)})

@app.route('/api/resource_allocation')
def get_resource_allocation():
    """Generate a chart showing emergency resource allocation."""
    try:
        # Get resource data from FEMA
        fema_data = get_federated_data("resource_deployment", {
            "emergency_type": "disease_outbreak",
            "start_date": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            "end_date": datetime.now().strftime('%Y-%m-%d')
        }, ["fema"])
        
        # For demo purposes, create sample data
        chart_data = {
            "categories": ["Medical Supplies", "Personnel", "Equipment", "Facilities", "Transportation"],
            "values": [45, 32, 18, 7, 5]  # Sample data
        }
        
        img_base64 = create_chart_from_data('bar', chart_data, 
                                         title="Emergency Resource Allocation",
                                         xlabel="Resource Type",
                                         ylabel="Percentage of Total",
                                         figsize=(10, 6))
        
        return jsonify({
            "image": img_base64,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception("Error generating resource allocation")
        return jsonify({"error": str(e)})

@app.route('/api/correlation_chart')
def get_correlation_chart():
    """Generate a correlation chart between cases and environmental factors."""
    try:
        # This would normally use the joint analysis data
        # For demo purposes, create sample data
        chart_data = {
            "matrix": [
                [1.0, 0.72, 0.68, 0.35],
                [0.72, 1.0, 0.54, 0.28],
                [0.68, 0.54, 1.0, 0.42],
                [0.35, 0.28, 0.42, 1.0]
            ],
            "x_labels": ["Cases", "PM2.5", "Temp", "Humidity"],
            "y_labels": ["Cases", "PM2.5", "Temp", "Humidity"]
        }
        
        img_base64 = create_chart_from_data('heatmap', chart_data, 
                                         title="Correlation Between Cases and Environmental Factors",
                                         figsize=(8, 8))
        
        return jsonify({
            "image": img_base64,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception("Error generating correlation chart")
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)