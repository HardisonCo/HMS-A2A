"""
API controller for abstraction analysis endpoints.

This module provides REST API endpoints for the abstraction analysis functionality.
"""
import json
import logging
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file

from src.analysis.abstraction_analysis import TrialAbstractionAnalysis
from src.visualization.abstraction_visualizer import AbstractionVisualizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create blueprint
abstraction_api = Blueprint('abstraction_api', __name__)

# Create output directories
os.makedirs('output/analysis', exist_ok=True)
os.makedirs('output/visualizations', exist_ok=True)

@abstraction_api.route('/analyze', methods=['POST'])
def analyze_abstractions():
    """
    Analyze clinical trial data to identify abstractions and relationships.
    
    Expected request body:
    {
        "clinical_trials": [...],   # List of clinical trial data
        "patient_data": [...],      # List of patient data
        "biomarker_data": [...],    # List of biomarker data
        "options": {                # Optional analysis options
            "max_abstractions": 10,
            "language": "english",
            "use_cache": true
        }
    }
    
    Returns:
        JSON response with abstraction analysis results
    """
    try:
        # Parse request body
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "No request data provided"}), 400
            
        # Extract data
        clinical_trials = request_data.get('clinical_trials', [])
        patient_data = request_data.get('patient_data', [])
        biomarker_data = request_data.get('biomarker_data', [])
        
        # Extract options
        options = request_data.get('options', {})
        max_abstractions = options.get('max_abstractions', 10)
        language = options.get('language', 'english')
        use_cache = options.get('use_cache', True)
        
        # Validate required data
        if not clinical_trials:
            return jsonify({"error": "No clinical trial data provided"}), 400
        if not patient_data:
            return jsonify({"error": "No patient data provided"}), 400
        
        # Initialize analyzer
        analyzer = TrialAbstractionAnalysis(
            max_abstractions=max_abstractions,
            language=language,
            use_cache=use_cache
        )
        
        # Run analysis
        logger.info(f"Starting abstraction analysis with {len(clinical_trials)} trials, {len(patient_data)} patients")
        analysis_results = analyzer.run_analysis(clinical_trials, patient_data, biomarker_data)
        
        # Generate unique ID for this analysis
        analysis_id = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Save analysis results
        output_path = f"output/analysis/abstraction_analysis_{analysis_id}.json"
        with open(output_path, 'w') as f:
            json.dump(analysis_results, f, indent=2)
        
        # Return results
        return jsonify({
            "analysis_id": analysis_id,
            "results": analysis_results,
            "output_path": output_path
        }), 200
    
    except Exception as e:
        logger.error(f"Error in abstraction analysis: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@abstraction_api.route('/visualize/<analysis_id>', methods=['GET'])
def visualize_abstractions(analysis_id):
    """
    Generate visualizations for abstraction analysis results.
    
    Args:
        analysis_id: ID of the analysis to visualize
        
    Returns:
        JSON response with visualization paths
    """
    try:
        # Validate analysis ID
        if not analysis_id:
            return jsonify({"error": "No analysis ID provided"}), 400
            
        # Load analysis results
        input_path = f"output/analysis/abstraction_analysis_{analysis_id}.json"
        if not os.path.exists(input_path):
            return jsonify({"error": f"No analysis found with ID {analysis_id}"}), 404
            
        with open(input_path, 'r') as f:
            analysis_results = json.load(f)
        
        # Initialize visualizer
        visualizer = AbstractionVisualizer(output_dir=f"output/visualizations/{analysis_id}")
        
        # Generate visualizations
        visualization_paths = visualizer.visualize_abstractions(analysis_results)
        
        # Generate HTML report
        html_report_path = f"output/visualizations/{analysis_id}/report.html"
        visualizer.generate_html_report(analysis_results, html_report_path)
        
        # Add HTML report to visualization paths
        visualization_paths["html_report"] = html_report_path
        
        # Return results
        return jsonify({
            "analysis_id": analysis_id,
            "visualization_paths": visualization_paths
        }), 200
    
    except Exception as e:
        logger.error(f"Error in abstraction visualization: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@abstraction_api.route('/report/<analysis_id>', methods=['GET'])
def get_html_report(analysis_id):
    """
    Get the HTML report for an abstraction analysis.
    
    Args:
        analysis_id: ID of the analysis
        
    Returns:
        HTML report file
    """
    try:
        # Validate analysis ID
        if not analysis_id:
            return jsonify({"error": "No analysis ID provided"}), 400
            
        # Check if report exists
        html_report_path = f"output/visualizations/{analysis_id}/report.html"
        if not os.path.exists(html_report_path):
            return jsonify({"error": f"No report found for analysis ID {analysis_id}"}), 404
            
        # Return HTML report
        return send_file(html_report_path, mimetype='text/html')
    
    except Exception as e:
        logger.error(f"Error serving HTML report: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@abstraction_api.route('/optimize-treatment', methods=['POST'])
def optimize_treatment():
    """
    Optimize treatment using abstraction-guided genetic algorithm.
    
    Expected request body:
    {
        "patient_data": {...},      # Patient data
        "analysis_id": "...",       # Optional analysis ID to use existing results
        "abstraction_guided": true  # Whether to use abstraction guidance
    }
    
    Returns:
        JSON response with optimized treatment plan
    """
    try:
        # Import here to avoid circular imports
        from src.coordination.genetic_engine_ffi import GeneticEngine
        from src.coordination.genetic-engine.enhanced_genetic_engine import EnhancedGeneticEngine
        
        # Parse request body
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "No request data provided"}), 400
            
        # Extract data
        patient_data = request_data.get('patient_data')
        analysis_id = request_data.get('analysis_id')
        abstraction_guided = request_data.get('abstraction_guided', True)
        
        # Validate required data
        if not patient_data:
            return jsonify({"error": "No patient data provided"}), 400
        
        # Load analysis results if provided
        analysis_results = None
        if analysis_id:
            input_path = f"output/analysis/abstraction_analysis_{analysis_id}.json"
            if os.path.exists(input_path):
                with open(input_path, 'r') as f:
                    analysis_results = json.load(f)
        
        # Initialize enhanced genetic engine
        genetic_engine = EnhancedGeneticEngine(abstraction_analysis_results=analysis_results)
        
        # Optimize treatment
        treatment_plan = genetic_engine.optimize_treatment(patient_data, abstraction_guided=abstraction_guided)
        
        # Return results
        return jsonify({
            "patient_id": patient_data.get("patient_id", "unknown"),
            "treatment_plan": treatment_plan,
            "abstraction_guided": abstraction_guided
        }), 200
    
    except Exception as e:
        logger.error(f"Error in treatment optimization: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@abstraction_api.route('/design-trial', methods=['POST'])
def design_adaptive_trial():
    """
    Design an adaptive trial using abstraction insights.
    
    Expected request body:
    {
        "protocol_template": {...},  # Trial protocol template
        "patient_population": [...],  # Target patient population
        "analysis_id": "...",        # Optional analysis ID to use existing results
        "abstraction_guided": true   # Whether to use abstraction guidance
    }
    
    Returns:
        JSON response with complete trial protocol
    """
    try:
        # Import here to avoid circular imports
        from src.coordination.a2a_integration.enhanced_adaptive_trial import EnhancedAdaptiveTrialFramework
        
        # Parse request body
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "No request data provided"}), 400
            
        # Extract data
        protocol_template = request_data.get('protocol_template')
        patient_population = request_data.get('patient_population', [])
        analysis_id = request_data.get('analysis_id')
        abstraction_guided = request_data.get('abstraction_guided', True)
        
        # Validate required data
        if not protocol_template:
            return jsonify({"error": "No protocol template provided"}), 400
        
        # Load analysis results if provided
        analysis_results = None
        if analysis_id:
            input_path = f"output/analysis/abstraction_analysis_{analysis_id}.json"
            if os.path.exists(input_path):
                with open(input_path, 'r') as f:
                    analysis_results = json.load(f)
        
        # Initialize enhanced adaptive trial framework
        adaptive_trial_framework = EnhancedAdaptiveTrialFramework(abstraction_analysis_results=analysis_results)
        
        # Design trial
        trial_protocol = adaptive_trial_framework.design_trial(
            protocol_template, 
            patient_population, 
            abstraction_guided=abstraction_guided
        )
        
        # Return results
        return jsonify({
            "trial_id": trial_protocol.get("trial_id", "unknown"),
            "protocol": trial_protocol,
            "abstraction_guided": abstraction_guided
        }), 200
    
    except Exception as e:
        logger.error(f"Error in trial design: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


def register_routes(app):
    """
    Register the API routes with the Flask app.
    
    Args:
        app: Flask application
    """
    app.register_blueprint(abstraction_api, url_prefix='/api/v1/abstractions')