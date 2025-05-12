"""
Integrated Documentation Service

This module provides integration between the Crohn's Treatment System, HMS-DOC, and HMS-MFE components.
It allows exporting abstractions, clinical trial data, and relationships to the HMS-DOC documentation 
system and the HMS-MFE interface.
"""

import os
import json
import yaml
import subprocess
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
import uuid
import shutil
import tempfile
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocIntegrationService:
    """
    Integration service for HMS-DOC and HMS-MFE components.
    
    This service provides methods to:
    1. Export abstractions and relationships to HMS-DOC for documentation generation
    2. Export clinical trial data to HMS-MFE for visualization and editing
    3. Publish documentation directly from the Crohn's Treatment System
    """
    
    def __init__(self, 
                 doc_root_path: str = '/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-DOC',
                 mfe_root_path: str = '/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE',
                 output_dir: str = '/Users/arionhardison/Desktop/Codify/output'):
        """
        Initialize the DocIntegrationService.
        
        Args:
            doc_root_path: Path to the HMS-DOC component
            mfe_root_path: Path to the HMS-MFE component
            output_dir: Directory to store generated documentation
        """
        self.doc_root_path = doc_root_path
        self.mfe_root_path = mfe_root_path
        self.output_dir = output_dir
        self._validate_paths()
        
    def _validate_paths(self):
        """Validate that the required directories exist"""
        if not os.path.exists(self.doc_root_path):
            raise ValueError(f"HMS-DOC directory not found at: {self.doc_root_path}")
        if not os.path.exists(self.mfe_root_path):
            raise ValueError(f"HMS-MFE directory not found at: {self.mfe_root_path}")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def export_abstractions_to_doc(self, 
                                  abstractions: List[Dict[str, Any]], 
                                  relationships: List[Dict[str, Any]],
                                  project_name: str = "Crohns-Treatment-Abstractions") -> str:
        """
        Export abstractions and relationships to HMS-DOC format.
        
        Args:
            abstractions: List of abstraction objects with name, description, etc.
            relationships: List of relationship objects between abstractions
            project_name: Name of the project for documentation
            
        Returns:
            Path to the generated documentation
        """
        # Create a temp directory to store files for HMS-DOC processing
        temp_dir = tempfile.mkdtemp(prefix="hms_doc_export_")
        
        try:
            # Transform abstractions and relationships to HMS-DOC format
            doc_abstractions = self._transform_abstractions(abstractions)
            doc_relationships = self._transform_relationships(relationships)
            
            # Write abstractions and relationships to temporary files
            abstractions_file = os.path.join(temp_dir, "abstractions.yaml")
            relationships_file = os.path.join(temp_dir, "relationships.yaml")
            
            with open(abstractions_file, 'w') as f:
                yaml.dump(doc_abstractions, f)
                
            with open(relationships_file, 'w') as f:
                yaml.dump({
                    "summary": "Analysis of patterns and abstractions in Crohn's Disease clinical trial data",
                    "details": doc_relationships
                }, f)
            
            # Run HMS-DOC generation using the temporary files
            output_path = os.path.join(self.output_dir, project_name)
            os.makedirs(output_path, exist_ok=True)
            
            cmd = [
                "python", 
                os.path.join(self.doc_root_path, "utils", "standalone_generator.py"),
                "--abstractions", abstractions_file,
                "--relationships", relationships_file,
                "--project-name", project_name,
                "--output", output_path
            ]
            
            logger.info(f"Running HMS-DOC generator with command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"HMS-DOC generation complete: {result.stdout}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting abstractions to HMS-DOC: {str(e)}")
            raise
        finally:
            # Clean up temporary files
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _transform_abstractions(self, abstractions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform abstractions from Crohn's system format to HMS-DOC format
        
        Args:
            abstractions: List of abstraction objects
            
        Returns:
            Transformed abstractions in HMS-DOC format
        """
        doc_abstractions = []
        
        for i, abstr in enumerate(abstractions):
            # Create file indices based on abstraction ID or name
            # In a real implementation, this would map to actual files
            files = [i]  # Dummy file index for demonstration
            
            doc_abstractions.append({
                "name": abstr["name"],
                "description": abstr["description"],
                "files": files
            })
            
        return doc_abstractions
    
    def _transform_relationships(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform relationships from Crohn's system format to HMS-DOC format
        
        Args:
            relationships: List of relationship objects
            
        Returns:
            Transformed relationships in HMS-DOC format
        """
        doc_relationships = []
        
        for rel in relationships:
            doc_relationships.append({
                "from": rel.get("source", 0),  # Index of source abstraction
                "to": rel.get("target", 0),    # Index of target abstraction
                "label": rel.get("type", "Related to")
            })
            
        return doc_relationships
    
    def publish_clinical_trial(self, 
                              trial_data: Dict[str, Any], 
                              abstractions: List[Dict[str, Any]],
                              writer_component_path: str = None) -> Dict[str, Any]:
        """
        Publish clinical trial data to HMS-MFE using the writer component
        
        Args:
            trial_data: Clinical trial data to publish
            abstractions: Related abstractions
            writer_component_path: Path to the writer component (defaults to the standard location)
            
        Returns:
            Publication information including URLs and status
        """
        if writer_component_path is None:
            writer_component_path = os.path.join(
                self.mfe_root_path, 
                "src/pages/sidebar/dashboards/writer.vue"
            )
        
        if not os.path.exists(writer_component_path):
            raise ValueError(f"Writer component not found at: {writer_component_path}")
        
        try:
            # Create publication metadata
            publication_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            publication_data = {
                "id": publication_id,
                "title": trial_data.get("title", "Untitled Clinical Trial"),
                "trial_id": trial_data.get("id", ""),
                "content": self._generate_markdown_content(trial_data, abstractions),
                "metadata": {
                    "trial_phase": trial_data.get("phase", ""),
                    "trial_status": trial_data.get("status", ""),
                    "abstractions": [a.get("id", "") for a in abstractions],
                    "generated_at": timestamp,
                    "source": "crohns-treatment-system"
                }
            }
            
            # Store publication data in MFE-compatible format
            mfe_data_dir = os.path.join(self.mfe_root_path, "json-server/data")
            os.makedirs(mfe_data_dir, exist_ok=True)
            
            output_file = os.path.join(mfe_data_dir, f"publication_{publication_id}.json")
            with open(output_file, 'w') as f:
                json.dump(publication_data, f, indent=2)
            
            logger.info(f"Published clinical trial to HMS-MFE: {output_file}")
            
            # Return publication information
            return {
                "publication_id": publication_id,
                "file_path": output_file,
                "writer_component": writer_component_path,
                "status": "published",
                "timestamp": timestamp,
                "metadata": publication_data["metadata"]
            }
            
        except Exception as e:
            logger.error(f"Error publishing clinical trial to HMS-MFE: {str(e)}")
            raise
    
    def _generate_markdown_content(self, 
                                  trial_data: Dict[str, Any], 
                                  abstractions: List[Dict[str, Any]]) -> str:
        """
        Generate markdown content for clinical trial publication
        
        Args:
            trial_data: Clinical trial data
            abstractions: Related abstractions
            
        Returns:
            Markdown content for the publication
        """
        # Basic template for clinical trial publication
        markdown = f"""# {trial_data.get('title', 'Clinical Trial Analysis')}

## Overview

{trial_data.get('description', 'No description provided.')}

## Trial Details

- **Phase:** {trial_data.get('phase', 'Unknown')}
- **Status:** {trial_data.get('status', 'Unknown')}
- **Start Date:** {trial_data.get('start_date', 'Not specified')}
- **End Date:** {trial_data.get('end_date', 'Ongoing')}

## Key Abstractions

The following patterns and abstractions were identified in this trial:

"""
        
        # Add abstraction details
        for abstraction in abstractions:
            markdown += f"### {abstraction.get('name', 'Unnamed Abstraction')}\n\n"
            markdown += f"{abstraction.get('description', 'No description available.')}\n\n"
            markdown += f"Confidence: {abstraction.get('confidence', 0.0):.2f}\n\n"
        
        # Add biomarkers if available
        if "biomarkers" in trial_data and trial_data["biomarkers"]:
            markdown += "## Biomarkers\n\n"
            for biomarker in trial_data["biomarkers"]:
                markdown += f"- {biomarker}\n"
            markdown += "\n"
        
        # Add treatment information if available
        if "treatments" in trial_data and trial_data["treatments"]:
            markdown += "## Treatments\n\n"
            for treatment in trial_data["treatments"]:
                markdown += f"- {treatment}\n"
            markdown += "\n"
        
        # Add outcomes if available
        if "outcomes" in trial_data and trial_data["outcomes"]:
            markdown += "## Outcomes\n\n"
            for outcome in trial_data["outcomes"]:
                markdown += f"- {outcome}\n"
            markdown += "\n"
        
        # Add footer
        markdown += """
---

*This document was automatically generated by the Crohn's Treatment System based on clinical trial data analysis and abstraction pattern identification.*
"""
        
        return markdown
    
    def generate_integrated_documentation(self,
                                         clinical_trials: List[Dict[str, Any]],
                                         abstractions: List[Dict[str, Any]],
                                         relationships: List[Dict[str, Any]],
                                         project_name: str = "Crohns-Treatment-Documentation") -> Dict[str, Any]:
        """
        Generate comprehensive documentation combining clinical trials and abstractions
        
        Args:
            clinical_trials: List of clinical trial data
            abstractions: List of abstraction objects
            relationships: List of relationship objects
            project_name: Name for the documentation project
            
        Returns:
            Information about the generated documentation
        """
        try:
            # First export abstractions to HMS-DOC
            doc_path = self.export_abstractions_to_doc(
                abstractions=abstractions,
                relationships=relationships,
                project_name=project_name
            )
            
            # Then publish each clinical trial to HMS-MFE
            published_trials = []
            for trial in clinical_trials:
                # Find relevant abstractions for this trial
                trial_abstractions = []
                if "abstraction_ids" in trial:
                    trial_abstractions = [a for a in abstractions if a.get("id", "") in trial.get("abstraction_ids", [])]
                
                # Publish the trial
                publication_info = self.publish_clinical_trial(
                    trial_data=trial,
                    abstractions=trial_abstractions
                )
                
                published_trials.append(publication_info)
            
            # Return the combined documentation information
            return {
                "documentation_path": doc_path,
                "published_trials": published_trials,
                "project_name": project_name,
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error generating integrated documentation: {str(e)}")
            raise

    def create_simulation_files(self) -> None:
        """
        Create simulation files for HMS-DOC and HMS-MFE integration
        This is for demonstration purposes where actual HMS-DOC or HMS-MFE might not be fully functional
        """
        # Create a standalone generator script for HMS-DOC if it doesn't exist
        standalone_generator_dir = os.path.join(self.doc_root_path, "utils")
        os.makedirs(standalone_generator_dir, exist_ok=True)
        
        standalone_generator_path = os.path.join(standalone_generator_dir, "standalone_generator.py")
        
        if not os.path.exists(standalone_generator_path):
            with open(standalone_generator_path, 'w') as f:
                f.write("""#!/usr/bin/env python
import argparse
import os
import yaml
import json

def generate_documentation(abstractions_file, relationships_file, project_name, output_dir):
    # Read abstractions and relationships
    with open(abstractions_file, 'r') as f:
        abstractions = yaml.safe_load(f)
    
    with open(relationships_file, 'r') as f:
        relationships = yaml.safe_load(f)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate index.md
    index_content = f"# {project_name}\\n\\n"
    index_content += f"{relationships.get('summary', 'No summary available.')}\\n\\n"
    index_content += "## Abstractions\\n\\n"
    
    for i, abstr in enumerate(abstractions):
        index_content += f"{i+1}. [{abstr['name']}](chapter_{i+1}.md)\\n"
    
    with open(os.path.join(output_dir, "index.md"), 'w') as f:
        f.write(index_content)
    
    # Generate chapter files
    for i, abstr in enumerate(abstractions):
        chapter_content = f"# Chapter {i+1}: {abstr['name']}\\n\\n"
        chapter_content += f"{abstr['description']}\\n\\n"
        
        # Add related abstractions based on relationships
        related_abstractions = []
        for rel in relationships.get('details', []):
            if rel['from'] == i:
                related_abstractions.append({
                    'target': rel['to'],
                    'label': rel['label'],
                    'name': abstractions[rel['to']]['name'] if rel['to'] < len(abstractions) else 'Unknown'
                })
        
        if related_abstractions:
            chapter_content += "## Related Abstractions\\n\\n"
            for rel in related_abstractions:
                chapter_content += f"- [{rel['name']}](chapter_{rel['target']+1}.md) - {rel['label']}\\n"
        
        with open(os.path.join(output_dir, f"chapter_{i+1}.md"), 'w') as f:
            f.write(chapter_content)
    
    # Generate metadata
    metadata = {
        'project_name': project_name,
        'abstractions_count': len(abstractions),
        'relationships_count': len(relationships.get('details', [])),
        'generated_at': '2024-05-09T12:00:00Z',
        'version': '1.0.0'
    }
    
    with open(os.path.join(output_dir, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return output_dir

def main():
    parser = argparse.ArgumentParser(description="Generate documentation from abstractions and relationships")
    parser.add_argument("--abstractions", required=True, help="Path to abstractions YAML file")
    parser.add_argument("--relationships", required=True, help="Path to relationships YAML file")
    parser.add_argument("--project-name", required=True, help="Project name")
    parser.add_argument("--output", required=True, help="Output directory")
    
    args = parser.parse_args()
    
    output_path = generate_documentation(
        args.abstractions,
        args.relationships,
        args.project_name,
        args.output
    )
    
    print(f"Documentation generated successfully at: {output_path}")

if __name__ == "__main__":
    main()
""")
            
            # Make the script executable
            os.chmod(standalone_generator_path, 0o755)
        
        # Create JSON server data directory for HMS-MFE if it doesn't exist
        mfe_data_dir = os.path.join(self.mfe_root_path, "json-server/data")
        os.makedirs(mfe_data_dir, exist_ok=True)
        
        logger.info("Simulation files created successfully")


def create_doc_integration_service() -> DocIntegrationService:
    """
    Factory function to create and configure a DocIntegrationService instance
    
    Returns:
        Configured DocIntegrationService instance
    """
    # Create base directories if they don't exist
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_dir = os.path.join(base_dir, "output", "documentation")
    
    # Create the service with default paths
    service = DocIntegrationService(
        doc_root_path='/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-DOC',
        mfe_root_path='/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE',
        output_dir=output_dir
    )
    
    # Create simulation files if needed
    service.create_simulation_files()
    
    return service