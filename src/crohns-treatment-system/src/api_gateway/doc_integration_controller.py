"""
Documentation Integration Controller

Exposes REST API endpoints for HMS-DOC and HMS-MFE integration.
"""

import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
import logging

from src.coordination.doc_integration import create_doc_integration_service
from src.coordination.doc_integration.integration_coordinator import coordinator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
doc_integration_bp = Blueprint('doc_integration', __name__, url_prefix='/api/doc-integration')

# Initialize service
doc_integration_service = create_doc_integration_service()

@doc_integration_bp.route('/export-abstractions', methods=['POST'])
def export_abstractions():
    """
    Export abstractions and relationships to HMS-DOC
    
    Request body:
    {
        "abstractions": [
            {"id": "...", "name": "...", "description": "...", ...},
            ...
        ],
        "relationships": [
            {"source": 0, "target": 1, "type": "..."},
            ...
        ],
        "project_name": "Crohns-Treatment-Abstractions" (optional)
    }
    """
    try:
        data = request.json
        
        if not data or 'abstractions' not in data or 'relationships' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: abstractions, relationships'
            }), 400
        
        project_name = data.get('project_name', 'Crohns-Treatment-Abstractions')
        
        output_path = doc_integration_service.export_abstractions_to_doc(
            abstractions=data['abstractions'],
            relationships=data['relationships'],
            project_name=project_name
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Abstractions exported successfully',
            'output_path': output_path,
            'project_name': project_name,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error exporting abstractions: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to export abstractions: {str(e)}'
        }), 500

@doc_integration_bp.route('/publish-trial', methods=['POST'])
def publish_trial():
    """
    Publish clinical trial data to HMS-MFE
    
    Request body:
    {
        "trial_data": {
            "id": "...",
            "title": "...",
            "description": "...",
            ...
        },
        "abstractions": [
            {"id": "...", "name": "...", "description": "...", ...},
            ...
        ],
        "writer_component_path": "..." (optional)
    }
    """
    try:
        data = request.json
        
        if not data or 'trial_data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: trial_data'
            }), 400
        
        abstractions = data.get('abstractions', [])
        writer_component_path = data.get('writer_component_path')
        
        publication_info = doc_integration_service.publish_clinical_trial(
            trial_data=data['trial_data'],
            abstractions=abstractions,
            writer_component_path=writer_component_path
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Clinical trial published successfully',
            'publication_info': publication_info
        })
        
    except Exception as e:
        logger.error(f"Error publishing clinical trial: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to publish clinical trial: {str(e)}'
        }), 500

@doc_integration_bp.route('/generate-documentation', methods=['POST'])
def generate_documentation():
    """
    Generate comprehensive documentation combining clinical trials and abstractions
    
    Request body:
    {
        "clinical_trials": [
            {"id": "...", "title": "...", ...},
            ...
        ],
        "abstractions": [
            {"id": "...", "name": "...", ...},
            ...
        ],
        "relationships": [
            {"source": 0, "target": 1, "type": "..."},
            ...
        ],
        "project_name": "..." (optional)
    }
    """
    try:
        data = request.json
        
        if not data or 'clinical_trials' not in data or 'abstractions' not in data or 'relationships' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: clinical_trials, abstractions, relationships'
            }), 400
        
        project_name = data.get('project_name', 'Crohns-Treatment-Documentation')
        
        doc_info = doc_integration_service.generate_integrated_documentation(
            clinical_trials=data['clinical_trials'],
            abstractions=data['abstractions'],
            relationships=data['relationships'],
            project_name=project_name
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Documentation generated successfully',
            'documentation_info': doc_info
        })
        
    except Exception as e:
        logger.error(f"Error generating documentation: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate documentation: {str(e)}'
        }), 500

@doc_integration_bp.route('/status', methods=['GET'])
def get_integration_status():
    """
    Get the current status of the documentation integration system
    """
    try:
        status = coordinator.get_system_status()
        return jsonify({
            'status': 'success',
            'data': status
        })
    except Exception as e:
        logger.error(f"Error getting integration status: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get integration status: {e}'
        }), 500

@doc_integration_bp.route('/publications', methods=['GET'])
def get_publications():
    """
    Get a list of publications

    Query parameters:
    - type: Type of publications to retrieve (hms_doc, hms_mfe, integrated)
    - limit: Maximum number of publications to return (default: 100)
    """
    try:
        publication_type = request.args.get('type')
        limit = int(request.args.get('limit', 100))

        publications = coordinator.get_publications(publication_type, limit)

        return jsonify({
            'status': 'success',
            'data': publications
        })
    except Exception as e:
        logger.error(f"Error getting publications: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get publications: {e}'
        }), 500

@doc_integration_bp.route('/publications/<publication_id>', methods=['GET'])
def get_publication(publication_id):
    """
    Get a publication by ID
    """
    try:
        publication = coordinator.get_publication_by_id(publication_id)

        if not publication:
            return jsonify({
                'status': 'error',
                'message': f'Publication not found: {publication_id}'
            }), 404

        return jsonify({
            'status': 'success',
            'data': publication
        })
    except Exception as e:
        logger.error(f"Error getting publication: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get publication: {e}'
        }), 500

@doc_integration_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Get a list of documentation tasks

    Query parameters:
    - limit: Maximum number of tasks to return (default: 100)
    """
    try:
        limit = int(request.args.get('limit', 100))

        tasks = coordinator.get_all_tasks(limit)

        return jsonify({
            'status': 'success',
            'data': tasks
        })
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get tasks: {e}'
        }), 500

@doc_integration_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """
    Get a task by ID
    """
    try:
        task = coordinator.get_task_status(task_id)

        if not task:
            return jsonify({
                'status': 'error',
                'message': f'Task not found: {task_id}'
            }), 404

        return jsonify({
            'status': 'success',
            'data': task
        })
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get task: {e}'
        }), 500

@doc_integration_bp.route('/schedule/export-abstractions', methods=['POST'])
def schedule_export_abstractions():
    """
    Schedule a task to export abstractions to HMS-DOC
    """
    try:
        data = request.json

        if not data or 'abstractions' not in data or 'relationships' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: abstractions, relationships'
            }), 400

        task_params = {
            'abstractions': data['abstractions'],
            'relationships': data['relationships']
        }

        if 'project_name' in data:
            task_params['project_name'] = data['project_name']

        task_id = coordinator.schedule_documentation_task('publish_doc', task_params)

        return jsonify({
            'status': 'success',
            'message': 'Export task scheduled successfully',
            'task_id': task_id
        })
    except Exception as e:
        logger.error(f"Error scheduling export task: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to schedule export task: {e}'
        }), 500

@doc_integration_bp.route('/schedule/publish-trial', methods=['POST'])
def schedule_publish_trial():
    """
    Schedule a task to publish a clinical trial to HMS-MFE
    """
    try:
        data = request.json

        if not data or 'trial_data' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: trial_data'
            }), 400

        task_params = {
            'trial_data': data['trial_data'],
            'abstractions': data.get('abstractions', [])
        }

        if 'writer_component_path' in data:
            task_params['writer_component_path'] = data['writer_component_path']

        task_id = coordinator.schedule_documentation_task('publish_mfe', task_params)

        return jsonify({
            'status': 'success',
            'message': 'Publish task scheduled successfully',
            'task_id': task_id
        })
    except Exception as e:
        logger.error(f"Error scheduling publish task: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to schedule publish task: {e}'
        }), 500

@doc_integration_bp.route('/schedule/integrated-documentation', methods=['POST'])
def schedule_integrated_documentation():
    """
    Schedule a task to generate integrated documentation
    """
    try:
        data = request.json

        if not data or 'clinical_trials' not in data or 'abstractions' not in data or 'relationships' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: clinical_trials, abstractions, relationships'
            }), 400

        task_params = {
            'clinical_trials': data['clinical_trials'],
            'abstractions': data['abstractions'],
            'relationships': data['relationships']
        }

        if 'project_name' in data:
            task_params['project_name'] = data['project_name']

        task_id = coordinator.schedule_documentation_task('generate_integrated', task_params)

        return jsonify({
            'status': 'success',
            'message': 'Integrated documentation task scheduled successfully',
            'task_id': task_id
        })
    except Exception as e:
        logger.error(f"Error scheduling integrated documentation task: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to schedule integrated documentation task: {e}'
        }), 500

def register_routes(app):
    """Register the blueprint routes with the Flask app"""
    app.register_blueprint(doc_integration_bp)
    logger.info("Registered doc_integration routes")