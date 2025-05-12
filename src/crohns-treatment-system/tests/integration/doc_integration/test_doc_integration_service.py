"""
Tests for the DocIntegrationService module
"""

import os
import json
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from src.coordination.doc_integration.doc_integration_service import DocIntegrationService

class DocIntegrationServiceTestCase(unittest.TestCase):
    """Test case for the DocIntegrationService class"""

    def setUp(self):
        """Set up test environment for each test"""
        # Create temporary directories for HMS-DOC and HMS-MFE
        self.temp_doc_dir = tempfile.mkdtemp(prefix="test_hms_doc_")
        self.temp_mfe_dir = tempfile.mkdtemp(prefix="test_hms_mfe_")
        self.temp_output_dir = tempfile.mkdtemp(prefix="test_output_")
        
        # Create Utils directory in HMS-DOC
        utils_dir = os.path.join(self.temp_doc_dir, "utils")
        os.makedirs(utils_dir, exist_ok=True)
        
        # Create standalone_generator.py in HMS-DOC/utils
        standalone_generator_path = os.path.join(utils_dir, "standalone_generator.py")
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
        # Make it executable
        os.chmod(standalone_generator_path, 0o755)
        
        # Create json-server/data directory in HMS-MFE
        json_server_dir = os.path.join(self.temp_mfe_dir, "json-server", "data")
        os.makedirs(json_server_dir, exist_ok=True)
        
        # Create writer.vue component in HMS-MFE
        pages_dir = os.path.join(self.temp_mfe_dir, "src", "pages", "sidebar", "dashboards")
        os.makedirs(pages_dir, exist_ok=True)
        with open(os.path.join(pages_dir, "writer.vue"), 'w') as f:
            f.write("""<template>
  <div class="writer">
    <h1>HMS-MFE Writer Component</h1>
    <div class="editor">
      <textarea v-model="content" placeholder="Enter content here..."></textarea>
    </div>
    <div class="controls">
      <button @click="save">Save</button>
      <button @click="publish">Publish</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Writer',
  data() {
    return {
      content: '',
      metadata: {}
    }
  },
  methods: {
    save() {
      // Save content logic
    },
    publish() {
      // Publish content logic
    }
  }
}
</script>
""")
        
        # Create test data file path
        self.test_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                         "data", "doc_integration_test_data.json")
        
        # Load test data
        with open(self.test_data_path, 'r') as f:
            self.test_data = json.load(f)
            
        # Initialize DocIntegrationService
        self.service = DocIntegrationService(
            doc_root_path=self.temp_doc_dir,
            mfe_root_path=self.temp_mfe_dir,
            output_dir=self.temp_output_dir
        )

    def tearDown(self):
        """Clean up after each test"""
        shutil.rmtree(self.temp_doc_dir)
        shutil.rmtree(self.temp_mfe_dir)
        shutil.rmtree(self.temp_output_dir)

    def test_init(self):
        """Test initialization of DocIntegrationService"""
        self.assertEqual(self.service.doc_root_path, self.temp_doc_dir)
        self.assertEqual(self.service.mfe_root_path, self.temp_mfe_dir)
        self.assertEqual(self.service.output_dir, self.temp_output_dir)

    def test_transform_abstractions(self):
        """Test transformation of abstractions from Crohn's format to HMS-DOC format"""
        abstractions = self.test_data["abstractions"]
        transformed = self.service._transform_abstractions(abstractions)
        
        self.assertEqual(len(transformed), len(abstractions))
        
        for i, abstr in enumerate(transformed):
            self.assertIn("name", abstr)
            self.assertIn("description", abstr)
            self.assertIn("files", abstr)
            self.assertEqual(abstr["name"], abstractions[i]["name"])
            self.assertEqual(abstr["description"], abstractions[i]["description"])

    def test_transform_relationships(self):
        """Test transformation of relationships from Crohn's format to HMS-DOC format"""
        relationships = self.test_data["relationships"]
        transformed = self.service._transform_relationships(relationships)
        
        self.assertEqual(len(transformed), len(relationships))
        
        for i, rel in enumerate(transformed):
            self.assertIn("from", rel)
            self.assertIn("to", rel)
            self.assertIn("label", rel)
            self.assertEqual(rel["from"], relationships[i]["source"])
            self.assertEqual(rel["to"], relationships[i]["target"])
            self.assertEqual(rel["label"], relationships[i]["type"])

    @patch("subprocess.run")
    def test_export_abstractions_to_doc(self, mock_run):
        """Test exporting abstractions to HMS-DOC"""
        # Mock the subprocess.run call to avoid actually running the script
        mock_run.return_value = MagicMock(stdout="Documentation generated successfully", stderr="")
        
        abstractions = self.test_data["abstractions"]
        relationships = self.test_data["relationships"]
        project_name = "Test-Project"
        
        output_path = self.service.export_abstractions_to_doc(
            abstractions=abstractions,
            relationships=relationships,
            project_name=project_name
        )
        
        # Verify that output_path was created
        self.assertTrue(os.path.exists(output_path))
        self.assertEqual(os.path.basename(output_path), project_name)
        
        # Verify subprocess.run was called
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(kwargs["check"], True)
        self.assertEqual(kwargs["capture_output"], True)
        self.assertEqual(kwargs["text"], True)

    def test_generate_markdown_content(self):
        """Test generation of markdown content for clinical trial publication"""
        trial_data = self.test_data["clinical_trial"]
        abstractions = [a for a in self.test_data["abstractions"] if a["id"] in trial_data["abstraction_ids"]]
        
        markdown = self.service._generate_markdown_content(trial_data, abstractions)
        
        # Check basic elements in the markdown
        self.assertIn(f"# {trial_data['title']}", markdown)
        self.assertIn("## Overview", markdown)
        self.assertIn("## Trial Details", markdown)
        self.assertIn("## Key Abstractions", markdown)
        
        # Check for abstraction details
        for abstraction in abstractions:
            self.assertIn(f"### {abstraction['name']}", markdown)
            self.assertIn(abstraction['description'], markdown)
        
        # Check for trial details
        self.assertIn(f"**Phase:** {trial_data['phase']}", markdown)
        self.assertIn(f"**Status:** {trial_data['status']}", markdown)
        self.assertIn(f"**Start Date:** {trial_data['start_date']}", markdown)
        self.assertIn(f"**End Date:** {trial_data['end_date']}", markdown)
        
        # Check for additional sections
        self.assertIn("## Biomarkers", markdown)
        self.assertIn("## Treatments", markdown)
        self.assertIn("## Outcomes", markdown)
        
        # Check for footer
        self.assertIn("*This document was automatically generated", markdown)

    def test_publish_clinical_trial(self):
        """Test publishing clinical trial data to HMS-MFE"""
        trial_data = self.test_data["clinical_trial"]
        abstractions = [a for a in self.test_data["abstractions"] if a["id"] in trial_data["abstraction_ids"]]
        
        result = self.service.publish_clinical_trial(
            trial_data=trial_data,
            abstractions=abstractions
        )
        
        # Check result structure
        self.assertIn("publication_id", result)
        self.assertIn("file_path", result)
        self.assertIn("writer_component", result)
        self.assertIn("status", result)
        self.assertIn("timestamp", result)
        self.assertIn("metadata", result)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(result["file_path"]))
        
        # Check file content
        with open(result["file_path"], 'r') as f:
            content = json.load(f)
            
        self.assertEqual(content["title"], trial_data["title"])
        self.assertEqual(content["trial_id"], trial_data["id"])
        self.assertIn("content", content)
        self.assertIn("metadata", content)
        
        # Check metadata
        self.assertEqual(content["metadata"]["trial_phase"], trial_data["phase"])
        self.assertEqual(content["metadata"]["trial_status"], trial_data["status"])
        self.assertEqual(content["metadata"]["abstractions"], trial_data["abstraction_ids"])
        self.assertEqual(content["metadata"]["source"], "crohns-treatment-system")

    def test_generate_integrated_documentation(self):
        """Test generating integrated documentation"""
        clinical_trials = [self.test_data["clinical_trial"]]
        abstractions = self.test_data["abstractions"]
        relationships = self.test_data["relationships"]
        project_name = "Integrated-Test-Project"
        
        # Mock the subprocess.run call to avoid actually running the script
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="Documentation generated successfully", stderr="")
            
            result = self.service.generate_integrated_documentation(
                clinical_trials=clinical_trials,
                abstractions=abstractions,
                relationships=relationships,
                project_name=project_name
            )
            
            # Check result structure
            self.assertIn("documentation_path", result)
            self.assertIn("published_trials", result)
            self.assertIn("project_name", result)
            self.assertIn("timestamp", result)
            self.assertIn("status", result)
            
            # Check documentation path
            self.assertTrue(os.path.exists(result["documentation_path"]))
            self.assertEqual(os.path.basename(result["documentation_path"]), project_name)
            
            # Check published trials
            self.assertEqual(len(result["published_trials"]), len(clinical_trials))
            for pub_info in result["published_trials"]:
                self.assertIn("publication_id", pub_info)
                self.assertIn("file_path", pub_info)
                self.assertTrue(os.path.exists(pub_info["file_path"]))

    def test_create_simulation_files(self):
        """Test creating simulation files"""
        # Remove existing simulation files
        standalone_generator_path = os.path.join(self.temp_doc_dir, "utils", "standalone_generator.py")
        if os.path.exists(standalone_generator_path):
            os.remove(standalone_generator_path)
            
        json_server_dir = os.path.join(self.temp_mfe_dir, "json-server", "data")
        if os.path.exists(json_server_dir):
            shutil.rmtree(json_server_dir)
            
        # Call create_simulation_files
        self.service.create_simulation_files()
        
        # Verify files were created
        self.assertTrue(os.path.exists(standalone_generator_path))
        self.assertTrue(os.path.exists(json_server_dir))

    def test_invalid_paths(self):
        """Test error handling for invalid paths"""
        with self.assertRaises(ValueError):
            DocIntegrationService(
                doc_root_path="/nonexistent/path",
                mfe_root_path=self.temp_mfe_dir,
                output_dir=self.temp_output_dir
            )
            
        with self.assertRaises(ValueError):
            DocIntegrationService(
                doc_root_path=self.temp_doc_dir,
                mfe_root_path="/nonexistent/path",
                output_dir=self.temp_output_dir
            )

if __name__ == '__main__':
    unittest.main()