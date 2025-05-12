"""
Integration service for publishing clinical trial data based on abstraction analysis.

This service connects the abstraction analysis system with the HMS-MFE
writer.vue component to publish clinical trial data.
"""
import os
import json
import logging
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional

from flask import Blueprint, request, jsonify, send_file

from src.analysis.abstraction_analysis import TrialAbstractionAnalysis
from src.visualization.abstraction_visualizer import AbstractionVisualizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create blueprint
publisher_api = Blueprint('publisher_api', __name__)

# Create output directories
os.makedirs('output/publications', exist_ok=True)

@publisher_api.route('/analysis-data', methods=['GET'])
def get_analysis_data():
    """
    Get abstraction analysis data for the publication interface.
    
    Returns:
        JSON response with analysis data
    """
    try:
        # Get analysis ID from query parameter
        analysis_id = request.args.get('analysis_id')
        
        if not analysis_id:
            # Return error if no analysis ID provided
            return jsonify({"error": "No analysis ID provided"}), 400
            
        # Load analysis results
        analysis_file = f"output/analysis/abstraction_analysis_{analysis_id}.json"
        if not os.path.exists(analysis_file):
            # Return sample data if analysis file not found
            return jsonify({
                "status": "sample_data",
                "abstractions": get_sample_abstractions(),
                "relationships": get_sample_relationships(),
                "biomarker_patterns": get_sample_biomarker_patterns(),
                "summary": get_sample_summary()
            }), 200
            
        # Load actual analysis results
        with open(analysis_file, 'r') as f:
            analysis_results = json.load(f)
            
        # Extract data for the publication interface
        return jsonify({
            "status": "real_data",
            "abstractions": analysis_results.get("abstractions", []),
            "relationships": analysis_results.get("relationships", {}).get("details", []),
            "biomarker_patterns": analysis_results.get("biomarker_patterns", []),
            "summary": analysis_results.get("relationships", {}).get("summary", "")
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting analysis data: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@publisher_api.route('/clinical-trials', methods=['GET'])
def get_clinical_trials():
    """
    Get clinical trial data for the publication interface.
    
    Returns:
        JSON response with clinical trial data
    """
    try:
        # Get data file path
        data_file = request.args.get('data_file', 'tests/data/sample_trial_data.json')
        
        if not os.path.exists(data_file):
            # Return sample data if data file not found
            return jsonify({
                "status": "sample_data",
                "clinical_trials": get_sample_clinical_trials()
            }), 200
            
        # Load actual clinical trial data
        with open(data_file, 'r') as f:
            data = json.load(f)
            
        clinical_trials = data.get('clinical_trials', [])
        
        # Extract relevant information for each trial
        simplified_trials = []
        for trial in clinical_trials:
            simplified_trials.append({
                "trial_id": trial.get("trial_id", ""),
                "title": trial.get("title", ""),
                "phase": trial.get("phase", 0),
                "arms_count": len(trial.get("arms", [])),
                "total_patients": trial.get("outcomes", {}).get("total_patients", 0),
                "response_rate": trial.get("outcomes", {}).get("response_rate", 0)
            })
            
        return jsonify({
            "status": "real_data",
            "clinical_trials": simplified_trials
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting clinical trial data: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@publisher_api.route('/publications', methods=['GET'])
def get_publications():
    """
    Get existing publications.
    
    Returns:
        JSON response with publications
    """
    try:
        # Load publications from the output directory
        publications_dir = 'output/publications'
        
        if not os.path.exists(publications_dir):
            # Return sample data if directory not found
            return jsonify({
                "status": "sample_data",
                "publications": get_sample_publications()
            }), 200
            
        # Get list of publication files
        publication_files = [f for f in os.listdir(publications_dir) if f.endswith('.json')]
        
        # Load each publication
        publications = []
        for file_name in publication_files:
            with open(os.path.join(publications_dir, file_name), 'r') as f:
                publication = json.load(f)
                publications.append(publication)
                
        # Sort by published date (newest first)
        publications.sort(key=lambda x: x.get('publishedDate', ''), reverse=True)
                
        return jsonify({
            "status": "real_data",
            "publications": publications
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting publications: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@publisher_api.route('/publications', methods=['POST'])
def create_publication():
    """
    Create a new publication.
    
    Expected request body:
    {
        "title": "Publication Title",
        "summary": "Publication Summary",
        "content": "Markdown content",
        "author": {
            "name": "Author Name",
            "role": "Author Role",
            "avatar": "Avatar URL"
        },
        "trialId": "TRIAL-ID",
        "relatedAbstractions": [0, 1, 2],
        "analysisId": "ANALYSIS-ID"
    }
    
    Returns:
        JSON response with the created publication
    """
    try:
        # Parse request body
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "No request data provided"}), 400
            
        # Extract publication data
        title = request_data.get('title')
        summary = request_data.get('summary')
        content = request_data.get('content')
        author = request_data.get('author')
        trial_id = request_data.get('trialId')
        related_abstractions = request_data.get('relatedAbstractions', [])
        analysis_id = request_data.get('analysisId')
        
        # Validate required fields
        if not title or not summary or not content or not author or not trial_id:
            return jsonify({"error": "Missing required fields"}), 400
            
        # Create publication object
        publication_id = f"pub_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        publication = {
            "id": publication_id,
            "title": title,
            "summary": summary,
            "content": content,
            "author": author,
            "trialId": trial_id,
            "relatedAbstractions": related_abstractions,
            "analysisId": analysis_id,
            "publishedDate": datetime.now().isoformat(),
            "image": request_data.get('image', 'https://media.cssninja.io/content/photos/38.jpg')
        }
        
        # Save publication to file
        output_path = f"output/publications/{publication_id}.json"
        with open(output_path, 'w') as f:
            json.dump(publication, f, indent=2)
            
        # If analysis ID is provided, copy visualizations
        if analysis_id:
            viz_dir = f"output/visualizations/{analysis_id}"
            pub_viz_dir = f"output/publications/{publication_id}/visualizations"
            
            if os.path.exists(viz_dir):
                os.makedirs(pub_viz_dir, exist_ok=True)
                
                # Copy visualization files
                for file_name in os.listdir(viz_dir):
                    if file_name.endswith('.png') or file_name.endswith('.html'):
                        shutil.copy(
                            os.path.join(viz_dir, file_name),
                            os.path.join(pub_viz_dir, file_name)
                        )
                
                # Update publication with visualization paths
                publication["visualizations"] = {
                    "path": f"publications/{publication_id}/visualizations",
                    "files": [f for f in os.listdir(pub_viz_dir)]
                }
                
                # Update the saved publication
                with open(output_path, 'w') as f:
                    json.dump(publication, f, indent=2)
        
        return jsonify({
            "status": "success",
            "publication": publication
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating publication: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@publisher_api.route('/publications/<publication_id>', methods=['PUT'])
def update_publication(publication_id):
    """
    Update an existing publication.
    
    Args:
        publication_id: ID of the publication to update
        
    Returns:
        JSON response with the updated publication
    """
    try:
        # Parse request body
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "No request data provided"}), 400
            
        # Check if publication exists
        publication_path = f"output/publications/{publication_id}.json"
        if not os.path.exists(publication_path):
            return jsonify({"error": f"Publication {publication_id} not found"}), 404
            
        # Load existing publication
        with open(publication_path, 'r') as f:
            publication = json.load(f)
            
        # Update fields
        publication["title"] = request_data.get('title', publication["title"])
        publication["summary"] = request_data.get('summary', publication["summary"])
        publication["content"] = request_data.get('content', publication["content"])
        publication["author"] = request_data.get('author', publication["author"])
        publication["trialId"] = request_data.get('trialId', publication["trialId"])
        publication["relatedAbstractions"] = request_data.get('relatedAbstractions', publication["relatedAbstractions"])
        publication["image"] = request_data.get('image', publication["image"])
        publication["updatedDate"] = datetime.now().isoformat()
        
        # Save updated publication
        with open(publication_path, 'w') as f:
            json.dump(publication, f, indent=2)
            
        return jsonify({
            "status": "success",
            "publication": publication
        }), 200
    
    except Exception as e:
        logger.error(f"Error updating publication: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@publisher_api.route('/publications/<publication_id>', methods=['DELETE'])
def delete_publication(publication_id):
    """
    Delete a publication.
    
    Args:
        publication_id: ID of the publication to delete
        
    Returns:
        JSON response indicating success
    """
    try:
        # Check if publication exists
        publication_path = f"output/publications/{publication_id}.json"
        if not os.path.exists(publication_path):
            return jsonify({"error": f"Publication {publication_id} not found"}), 404
            
        # Delete publication file
        os.remove(publication_path)
        
        # Delete publication visualizations directory if it exists
        viz_dir = f"output/publications/{publication_id}/visualizations"
        if os.path.exists(viz_dir):
            shutil.rmtree(f"output/publications/{publication_id}")
            
        return jsonify({
            "status": "success",
            "message": f"Publication {publication_id} deleted successfully"
        }), 200
    
    except Exception as e:
        logger.error(f"Error deleting publication: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@publisher_api.route('/generate-publication', methods=['POST'])
def generate_publication():
    """
    Generate a publication from abstraction analysis.
    
    Expected request body:
    {
        "analysisId": "ANALYSIS-ID",
        "trialId": "TRIAL-ID",
        "author": {
            "name": "Author Name",
            "role": "Author Role",
            "avatar": "Avatar URL"
        }
    }
    
    Returns:
        JSON response with the generated publication
    """
    try:
        # Parse request body
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "No request data provided"}), 400
            
        # Extract required data
        analysis_id = request_data.get('analysisId')
        trial_id = request_data.get('trialId')
        author = request_data.get('author')
        
        # Validate required fields
        if not analysis_id or not trial_id or not author:
            return jsonify({"error": "Missing required fields"}), 400
            
        # Load analysis results
        analysis_file = f"output/analysis/abstraction_analysis_{analysis_id}.json"
        if not os.path.exists(analysis_file):
            return jsonify({"error": f"Analysis {analysis_id} not found"}), 404
            
        with open(analysis_file, 'r') as f:
            analysis_results = json.load(f)
            
        # Load trial data
        data_file = request_data.get('dataFile', 'tests/data/sample_trial_data.json')
        if not os.path.exists(data_file):
            return jsonify({"error": f"Data file {data_file} not found"}), 404
            
        with open(data_file, 'r') as f:
            data = json.load(f)
            
        clinical_trials = data.get('clinical_trials', [])
        trial = next((t for t in clinical_trials if t.get('trial_id') == trial_id), None)
        
        if not trial:
            return jsonify({"error": f"Trial {trial_id} not found"}), 404
            
        # Generate publication content
        publication_id = f"pub_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Extract key information
        abstractions = analysis_results.get("abstractions", [])
        relationships = analysis_results.get("relationships", {}).get("details", [])
        summary = analysis_results.get("relationships", {}).get("summary", "")
        
        # Find relevant abstractions for this trial
        relevant_abstractions = []
        for i, abstraction in enumerate(abstractions):
            if "biomarker" in abstraction.get("name", "").lower() or "treatment" in abstraction.get("name", "").lower():
                relevant_abstractions.append(i)
        
        # Generate title based on trial and abstractions
        if relevant_abstractions and len(relevant_abstractions) > 0:
            main_abstraction = abstractions[relevant_abstractions[0]]
            title = f"{main_abstraction.get('name')} in {trial.get('title')}"
        else:
            title = f"Analysis of {trial.get('title')}"
        
        # Generate summary based on trial outcomes and abstractions
        if summary:
            publication_summary = summary.split(".")[0] + "."
        else:
            publication_summary = f"Analysis of patterns and relationships in {trial.get('title')} based on abstraction analysis."
        
        # Generate content with markdown
        content = f"""## Introduction

This publication presents the results of abstraction analysis applied to {trial.get('title')}.

## Methods

{trial.get('title')} included {trial.get('outcomes', {}).get('total_patients', 'N/A')} patients across {len(trial.get('arms', []))} treatment arms. 
The overall response rate was {trial.get('outcomes', {}).get('response_rate', 'N/A')}%.

## Key Abstractions

"""
        
        # Add abstractions to content
        for i in relevant_abstractions:
            abstraction = abstractions[i]
            content += f"### {abstraction.get('name')}\n\n{abstraction.get('description')}\n\n"
        
        # Add relationships to content
        content += "## Key Relationships\n\n"
        
        relevant_relationships = []
        for rel in relationships:
            if rel.get("from") in relevant_abstractions or rel.get("to") in relevant_abstractions:
                relevant_relationships.append(rel)
                
        for rel in relevant_relationships:
            from_abstraction = abstractions[rel.get("from")].get("name")
            to_abstraction = abstractions[rel.get("to")].get("name")
            label = rel.get("label")
            
            content += f"- {from_abstraction} {label} {to_abstraction}\n"
            
        # Add conclusion
        content += "\n## Conclusion\n\n"
        content += "The abstraction analysis has revealed important patterns and relationships that can inform future clinical trials for Crohn's disease treatment."
        
        # Create publication object
        publication = {
            "id": publication_id,
            "title": title,
            "summary": publication_summary,
            "content": content,
            "author": author,
            "trialId": trial_id,
            "relatedAbstractions": relevant_abstractions,
            "analysisId": analysis_id,
            "publishedDate": datetime.now().isoformat(),
            "image": "https://media.cssninja.io/content/photos/38.jpg"
        }
        
        # Save publication to file
        output_path = f"output/publications/{publication_id}.json"
        with open(output_path, 'w') as f:
            json.dump(publication, f, indent=2)
            
        # Copy visualizations
        viz_dir = f"output/visualizations/{analysis_id}"
        pub_viz_dir = f"output/publications/{publication_id}/visualizations"
        
        if os.path.exists(viz_dir):
            os.makedirs(pub_viz_dir, exist_ok=True)
            
            # Copy visualization files
            for file_name in os.listdir(viz_dir):
                if file_name.endswith('.png') or file_name.endswith('.html'):
                    shutil.copy(
                        os.path.join(viz_dir, file_name),
                        os.path.join(pub_viz_dir, file_name)
                    )
            
            # Update publication with visualization paths
            publication["visualizations"] = {
                "path": f"publications/{publication_id}/visualizations",
                "files": [f for f in os.listdir(pub_viz_dir)]
            }
            
            # Update the saved publication
            with open(output_path, 'w') as f:
                json.dump(publication, f, indent=2)
        
        return jsonify({
            "status": "success",
            "publication": publication
        }), 201
    
    except Exception as e:
        logger.error(f"Error generating publication: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


def get_sample_abstractions():
    """Return sample abstractions for testing."""
    return [
        {
            "name": "Biomarker Response Patterns",
            "description": "Patterns of response to treatment based on specific biomarkers like NOD2 and IL23R variants.",
            "files": [0, 1, 2]
        },
        {
            "name": "Treatment Efficacy Correlations",
            "description": "Correlations between specific treatments and their efficacy for different patient subgroups.",
            "files": [1, 3, 4]
        },
        {
            "name": "Adaptive Trial Design",
            "description": "Methodologies for adapting trial protocols based on interim analysis results.",
            "files": [2, 5]
        },
        {
            "name": "Genetic Markers for Crohn's",
            "description": "Key genetic markers associated with Crohn's disease subtypes and treatment responses.",
            "files": [0, 6]
        },
        {
            "name": "Patient Stratification",
            "description": "Methods for stratifying patients in clinical trials based on biomarker profiles.",
            "files": [1, 3, 7]
        }
    ]


def get_sample_relationships():
    """Return sample relationships for testing."""
    return [
        { "from": 0, "to": 1, "label": "Influences efficacy" },
        { "from": 0, "to": 2, "label": "Guides adaptation" },
        { "from": 3, "to": 0, "label": "Defines patterns" },
        { "from": 3, "to": 4, "label": "Determines stratification" },
        { "from": 4, "to": 2, "label": "Improves design" },
        { "from": 1, "to": 2, "label": "Informs adjustments" }
    ]


def get_sample_biomarker_patterns():
    """Return sample biomarker patterns for testing."""
    return [
        {
            "cluster_id": 0,
            "cluster_name": "NOD2 Variant Cluster",
            "response_by_arm": {
                "ARM-001": {
                    "patients": 15,
                    "response_rate": 0.65,
                    "significance": "high"
                },
                "ARM-002": {
                    "patients": 18,
                    "response_rate": 0.72,
                    "significance": "high"
                },
                "ARM-003": {
                    "patients": 12,
                    "response_rate": 0.25,
                    "significance": "low"
                }
            }
        },
        {
            "cluster_id": 1,
            "cluster_name": "IL23R Variant Cluster",
            "response_by_arm": {
                "ARM-001": {
                    "patients": 12,
                    "response_rate": 0.45,
                    "significance": "medium"
                },
                "ARM-002": {
                    "patients": 10,
                    "response_rate": 0.80,
                    "significance": "high"
                },
                "ARM-003": {
                    "patients": 8,
                    "response_rate": 0.12,
                    "significance": "low"
                }
            }
        }
    ]


def get_sample_summary():
    """Return sample summary for testing."""
    return "The Crohn's Disease Treatment System is a comprehensive platform that integrates genetic analysis, treatment optimization, and adaptive clinical trials to deliver personalized treatment plans for Crohn's disease patients. The system analyzes patient biomarkers and clinical data to identify optimal treatments, runs adaptive clinical trials that evolve based on interim results, and provides detailed visualizations of outcomes for clinical decision support."


def get_sample_clinical_trials():
    """Return sample clinical trials for testing."""
    return [
        {
            "trial_id": "CROHNS-001",
            "title": "Adaptive Trial of JAK Inhibitors in Crohn's Disease",
            "phase": 2,
            "arms_count": 3,
            "total_patients": 120,
            "response_rate": 45
        },
        {
            "trial_id": "CROHNS-002",
            "title": "IL-23 Inhibitors for Moderate-to-Severe Crohn's Disease",
            "phase": 3,
            "arms_count": 3,
            "total_patients": 180,
            "response_rate": 50
        },
        {
            "trial_id": "CROHNS-003",
            "title": "Advanced Adaptive Trial for Crohn's Disease",
            "phase": 2,
            "arms_count": 3,
            "total_patients": 0,
            "response_rate": 0
        }
    ]


def get_sample_publications():
    """Return sample publications for testing."""
    return [
        {
            "id": "pub_20230415123456",
            "title": "NOD2 Variants Predict Response to JAK Inhibitors",
            "summary": "Analysis of biomarker response patterns in JAK inhibitor trials for Crohn's disease patients.",
            "content": "## Introduction\n\nThis publication analyzes the relationship between NOD2 genetic variants and response to JAK inhibitors in patients with moderate-to-severe Crohn's disease.\n\n## Methods\n\nWe conducted an adaptive clinical trial with 120 patients, stratified by NOD2 variant status. Patients received either Upadacitinib (15mg or 30mg) or placebo.\n\n## Results\n\nPatients with NOD2 variants showed a significantly higher response rate to Upadacitinib compared to patients without the variant (68% vs. 42%, p<0.001).\n\n## Conclusions\n\nNOD2 variant status may be a useful biomarker for predicting response to JAK inhibitors in Crohn's disease patients.",
            "image": "https://media.cssninja.io/content/photos/38.jpg",
            "author": {
                "name": "Dr. Alice Thompson",
                "role": "Clinical Researcher",
                "avatar": "https://media.cssninja.io/content/avatars/7.jpg"
            },
            "publishedDate": "2023-04-15T12:34:56",
            "relatedAbstractions": [0, 1, 3],
            "trialId": "CROHNS-001"
        },
        {
            "id": "pub_20230322123456",
            "title": "Adaptive Trial Design Improves Patient Outcomes",
            "summary": "How response-adaptive randomization improved outcomes in the IL-23 inhibitor trial.",
            "content": "## Background\n\nTraditional randomized clinical trials often maintain fixed randomization ratios throughout the study. This publication examines the benefits of adaptive randomization in our IL-23 inhibitor trial.\n\n## Methods\n\nWe implemented response-adaptive randomization after the first interim analysis, adjusting allocation probabilities based on observed outcomes.\n\n## Results\n\nAdaptive randomization resulted in:\n- 15% more patients receiving effective treatment\n- Reduced time to identify effective treatment arms\n- Earlier termination of ineffective arms\n\n## Conclusions\n\nAdaptive trial designs can significantly improve patient outcomes while maintaining statistical rigor.",
            "image": "https://media.cssninja.io/content/photos/37.jpg",
            "author": {
                "name": "Dr. James Wilson",
                "role": "Biostatistician",
                "avatar": "https://media.cssninja.io/content/avatars/32.jpg"
            },
            "publishedDate": "2023-03-22T12:34:56",
            "relatedAbstractions": [2, 4],
            "trialId": "CROHNS-002"
        }
    ]


def register_routes(app):
    """
    Register the API routes with the Flask app.
    
    Args:
        app: Flask application
    """
    app.register_blueprint(publisher_api, url_prefix='/api/v1/publisher')