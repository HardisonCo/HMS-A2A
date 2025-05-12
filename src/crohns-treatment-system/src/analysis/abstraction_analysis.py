"""
Abstraction analysis module for clinical trial data.

This module implements abstraction identification and relationship analysis for the
Crohn's Disease Treatment System, enabling advanced pattern recognition and insights.
"""
import json
import yaml
import logging
from datetime import datetime
from .node import Node

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def call_llm(prompt, use_cache=True):
    """
    Calls the LLM with the given prompt.
    
    Args:
        prompt: The prompt to send to the LLM
        use_cache: Whether to use cached responses
        
    Returns:
        The LLM response
    """
    try:
        # In a real implementation, this would call an actual LLM
        # For now, we'll just return a sample response for demonstration
        logger.info(f"Calling LLM with prompt of length {len(prompt)} (use_cache={use_cache})")
        
        # In real implementation, call the actual LLM service here
        # For testing purposes, we're returning sample responses to simulate LLM output
        if "Identify the top" in prompt and "core most important abstractions" in prompt:
            return sample_abstraction_response()
        elif "provide a high-level `summary`" in prompt and "list (`relationships`)" in prompt:
            return sample_relationship_response()
        else:
            return "No sample response available for this prompt type."
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        raise


def sample_abstraction_response():
    """Returns a sample abstraction identification response"""
    return """
Based on the codebase context, here are the top abstractions to help those new to the codebase:

```yaml
- name: |
    Biomarker Analysis System
  description: |
    Core system for analyzing genetic and non-genetic biomarkers in Crohn's disease patients. 
    It's like a detective that searches for clues in patient data to predict treatment response.
    The system examines genetic markers such as NOD2, IL23R variants and correlates them with 
    disease activity and treatment outcomes.
  file_indices:
    - 0 # src/coordination/genetic-engine/genetic_sequence_analyzer.rs
    - 4 # src/coordination/genetic-engine/ffi_sequence.rs
    - 11 # src/coordination/a2a-integration/genetic_sequence_ffi.py
- name: |
    Treatment Optimization Engine
  description: |
    Genetic algorithm-based system that optimizes treatment plans for individual patients.
    Think of it as a chess AI that explores millions of potential treatment combinations to
    find the optimal strategy for each patient. It weighs factors like efficacy, safety, 
    and patient-specific characteristics to suggest personalized treatments.
  file_indices:
    - 1 # src/coordination/genetic-engine/core.rs
    - 2 # src/coordination/genetic-engine/crohns_integration.rs
    - 3 # src/coordination/genetic-engine/ffi.rs
- name: |
    Adaptive Trial Framework
  description: |
    System for designing and managing clinical trials that adapt based on interim results.
    It's like a self-adjusting scientific experiment that evolves as data comes in.
    The framework supports response-adaptive randomization, arm dropping, and biomarker-based
    stratification to optimize the trial while it's still running.
  file_indices:
    - 6 # src/coordination/a2a-integration/clinical_trial_agent.py
    - 8 # src/coordination/a2a-integration/codex_rs_integration.py
- name: |
    EHR Integration System
  description: |
    Framework for securely connecting with Electronic Health Record systems using FHIR standards.
    Think of it as a universal translator that speaks the language of different healthcare 
    systems. It handles patient data synchronization, privacy protections, and ensures 
    bidirectional data flow while maintaining security and compliance.
  file_indices:
    - 14 # src/data-layer/ehr-integration/fhir_client.py
    - 16 # src/data-layer/ehr-integration/patient_model.py
    - 17 # src/data-layer/ehr-integration/patient_service.py
- name: |
    Visualization Engine
  description: |
    System for creating interactive visualizations of trial results and patient data.
    It's like a storyteller that transforms complex medical data into clear, insightful
    visuals. The engine generates dashboards showing treatment efficacy, biomarker correlations,
    and patient response patterns to help clinicians make evidence-based decisions.
  file_indices:
    - 22 # src/visualization/trial_results_visualizer.py
```
"""


def sample_relationship_response():
    """Returns a sample relationship analysis response"""
    return """
Based on the provided abstractions and code snippets, here's my analysis:

```yaml
summary: |
  The Crohn's Disease Treatment System is a **comprehensive platform** that integrates *genetic analysis*, *treatment optimization*, and *adaptive clinical trials* to deliver personalized treatment plans for Crohn's disease patients. The system analyzes patient **biomarkers** and clinical data to identify optimal treatments, runs *adaptive clinical trials* that evolve based on interim results, and provides detailed *visualizations* of outcomes for clinical decision support.
relationships:
  - from_abstraction: 0 # Biomarker Analysis System
    to_abstraction: 1 # Treatment Optimization Engine
    label: "Provides predictive markers"
  - from_abstraction: 1 # Treatment Optimization Engine
    to_abstraction: 2 # Adaptive Trial Framework
    label: "Guides treatment allocation"
  - from_abstraction: 3 # EHR Integration System
    to_abstraction: 0 # Biomarker Analysis System
    label: "Supplies patient data"
  - from_abstraction: 2 # Adaptive Trial Framework
    to_abstraction: 4 # Visualization Engine
    label: "Generates trial results"
  - from_abstraction: 4 # Visualization Engine
    to_abstraction: 1 # Treatment Optimization Engine
    label: "Informs efficacy metrics"
```
"""


class IdentifyAbstractions(Node):
    """
    Node that identifies key abstractions in clinical trial data.
    """
    def prep(self, shared):
        files_data = shared["files"]
        project_name = shared["project_name"]  # Get project name
        language = shared.get("language", "english")  # Get language
        use_cache = shared.get("use_cache", True)  # Get use_cache flag, default to True
        max_abstraction_num = shared.get("max_abstraction_num", 10)  # Get max_abstraction_num, default to 10

        # Helper to create context from files, respecting limits (basic example)
        def create_llm_context(files_data):
            context = ""
            file_info = []  # Store tuples of (index, path)
            for i, (path, content) in enumerate(files_data):
                entry = f"--- File Index {i}: {path} ---\n{content}\n\n"
                context += entry
                file_info.append((i, path))

            return context, file_info  # file_info is list of (index, path)

        context, file_info = create_llm_context(files_data)
        # Format file info for the prompt (comment is just a hint for LLM)
        file_listing_for_prompt = "\n".join(
            [f"- {idx} # {path}" for idx, path in file_info]
        )
        return (
            context,
            file_listing_for_prompt,
            len(files_data),
            project_name,
            language,
            use_cache,
            max_abstraction_num,
        )  # Return all parameters

    def exec(self, prep_res):
        (
            context,
            file_listing_for_prompt,
            file_count,
            project_name,
            language,
            use_cache,
            max_abstraction_num,
        ) = prep_res  # Unpack all parameters
        logger.info(f"Identifying abstractions using LLM...")

        # Add language instruction and hints only if not English
        language_instruction = ""
        name_lang_hint = ""
        desc_lang_hint = ""
        if language.lower() != "english":
            language_instruction = f"IMPORTANT: Generate the `name` and `description` for each abstraction in **{language.capitalize()}** language. Do NOT use English for these fields.\n\n"
            # Keep specific hints here as name/description are primary targets
            name_lang_hint = f" (value in {language.capitalize()})"
            desc_lang_hint = f" (value in {language.capitalize()})"

        prompt = f"""
For the project `{project_name}`:

Codebase Context:
{context}

{language_instruction}Analyze the codebase context.
Identify the top 5-{max_abstraction_num} core most important abstractions to help those new to the codebase.

For each abstraction, provide:
1. A concise `name`{name_lang_hint}.
2. A beginner-friendly `description` explaining what it is with a simple analogy, in around 100 words{desc_lang_hint}.
3. A list of relevant `file_indices` (integers) using the format `idx # path/comment`.

List of file indices and paths present in the context:
{file_listing_for_prompt}

Format the output as a YAML list of dictionaries:

```yaml
- name: |
    Query Processing{name_lang_hint}
  description: |
    Explains what the abstraction does.
    It's like a central dispatcher routing requests.{desc_lang_hint}
  file_indices:
    - 0 # path/to/file1.py
    - 3 # path/to/related.py
- name: |
    Query Optimization{name_lang_hint}
  description: |
    Another core concept, similar to a blueprint for objects.{desc_lang_hint}
  file_indices:
    - 5 # path/to/another.js
# ... up to {max_abstraction_num} abstractions
```"""
        response = call_llm(prompt, use_cache=(use_cache and self.cur_retry == 0))  # Use cache only if enabled and not retrying

        # --- Validation ---
        yaml_str = response.strip().split("```yaml")[1].split("```")[0].strip()
        abstractions = yaml.safe_load(yaml_str)

        if not isinstance(abstractions, list):
            raise ValueError("LLM Output is not a list")

        validated_abstractions = []
        for item in abstractions:
            if not isinstance(item, dict) or not all(
                k in item for k in ["name", "description", "file_indices"]
            ):
                raise ValueError(f"Missing keys in abstraction item: {item}")
            if not isinstance(item["name"], str):
                raise ValueError(f"Name is not a string in item: {item}")
            if not isinstance(item["description"], str):
                raise ValueError(f"Description is not a string in item: {item}")
            if not isinstance(item["file_indices"], list):
                raise ValueError(f"file_indices is not a list in item: {item}")

            # Validate indices
            validated_indices = []
            for idx_entry in item["file_indices"]:
                try:
                    if isinstance(idx_entry, int):
                        idx = idx_entry
                    elif isinstance(idx_entry, str) and "#" in idx_entry:
                        idx = int(idx_entry.split("#")[0].strip())
                    else:
                        idx = int(str(idx_entry).strip())

                    if not (0 <= idx < file_count):
                        raise ValueError(
                            f"Invalid file index {idx} found in item {item['name']}. Max index is {file_count - 1}."
                        )
                    validated_indices.append(idx)
                except (ValueError, TypeError):
                    raise ValueError(
                        f"Could not parse index from entry: {idx_entry} in item {item['name']}"
                    )

            item["files"] = sorted(list(set(validated_indices)))
            # Store only the required fields
            validated_abstractions.append(
                {
                    "name": item["name"],  # Potentially translated name
                    "description": item[
                        "description"
                    ],  # Potentially translated description
                    "files": item["files"],
                }
            )

        logger.info(f"Identified {len(validated_abstractions)} abstractions.")
        return validated_abstractions

    def post(self, shared, prep_res, exec_res):
        shared["abstractions"] = (
            exec_res  # List of {"name": str, "description": str, "files": [int]}
        )


def get_content_for_indices(files_data, indices):
    """
    Helper function to get content for specific file indices.
    
    Args:
        files_data: List of tuples (path, content)
        indices: List of file indices to include
        
    Returns:
        Dictionary mapping "index # path" to content
    """
    result = {}
    for idx in indices:
        if 0 <= idx < len(files_data):
            path, content = files_data[idx]
            result[f"{idx} # {path}"] = content
    return result


class AnalyzeRelationships(Node):
    """
    Node that analyzes relationships between identified abstractions.
    """
    def prep(self, shared):
        abstractions = shared[
            "abstractions"
        ]  # Now contains 'files' list of indices, name/description potentially translated
        files_data = shared["files"]
        project_name = shared["project_name"]  # Get project name
        language = shared.get("language", "english")  # Get language
        use_cache = shared.get("use_cache", True)  # Get use_cache flag, default to True

        # Get the actual number of abstractions directly
        num_abstractions = len(abstractions)

        # Create context with abstraction names, indices, descriptions, and relevant file snippets
        context = "Identified Abstractions:\\n"
        all_relevant_indices = set()
        abstraction_info_for_prompt = []
        for i, abstr in enumerate(abstractions):
            # Use 'files' which contains indices directly
            file_indices_str = ", ".join(map(str, abstr["files"]))
            # Abstraction name and description might be translated already
            info_line = f"- Index {i}: {abstr['name']} (Relevant file indices: [{file_indices_str}])\\n  Description: {abstr['description']}"
            context += info_line + "\\n"
            abstraction_info_for_prompt.append(
                f"{i} # {abstr['name']}"
            )  # Use potentially translated name here too
            all_relevant_indices.update(abstr["files"])

        context += "\\nRelevant File Snippets (Referenced by Index and Path):\\n"
        # Get content for relevant files using helper
        relevant_files_content_map = get_content_for_indices(
            files_data, sorted(list(all_relevant_indices))
        )
        # Format file content for context
        file_context_str = "\\n\\n".join(
            f"--- File: {idx_path} ---\\n{content}"
            for idx_path, content in relevant_files_content_map.items()
        )
        context += file_context_str

        return (
            context,
            "\n".join(abstraction_info_for_prompt),
            num_abstractions, # Pass the actual count
            project_name,
            language,
            use_cache,
        )  # Return use_cache

    def exec(self, prep_res):
        (
            context,
            abstraction_listing,
            num_abstractions, # Receive the actual count
            project_name,
            language,
            use_cache,
         ) = prep_res  # Unpack use_cache
        logger.info(f"Analyzing relationships using LLM...")

        # Add language instruction and hints only if not English
        language_instruction = ""
        lang_hint = ""
        list_lang_note = ""
        if language.lower() != "english":
            language_instruction = f"IMPORTANT: Generate the `summary` and relationship `label` fields in **{language.capitalize()}** language. Do NOT use English for these fields.\n\n"
            lang_hint = f" (in {language.capitalize()})"
            list_lang_note = f" (Names might be in {language.capitalize()})"  # Note for the input list

        prompt = f"""
Based on the following abstractions and relevant code snippets from the project `{project_name}`:

List of Abstraction Indices and Names{list_lang_note}:
{abstraction_listing}

Context (Abstractions, Descriptions, Code):
{context}

{language_instruction}Please provide:
1. A high-level `summary` of the project's main purpose and functionality in a few beginner-friendly sentences{lang_hint}. Use markdown formatting with **bold** and *italic* text to highlight important concepts.
2. A list (`relationships`) describing the key interactions between these abstractions. For each relationship, specify:
    - `from_abstraction`: Index of the source abstraction (e.g., `0 # AbstractionName1`)
    - `to_abstraction`: Index of the target abstraction (e.g., `1 # AbstractionName2`)
    - `label`: A brief label for the interaction **in just a few words**{lang_hint} (e.g., "Manages", "Inherits", "Uses").
    Ideally the relationship should be backed by one abstraction calling or passing parameters to another.
    Simplify the relationship and exclude those non-important ones.

IMPORTANT: Make sure EVERY abstraction is involved in at least ONE relationship (either as source or target). Each abstraction index must appear at least once across all relationships.

Format the output as YAML:

```yaml
summary: |
  A brief, simple explanation of the project{lang_hint}.
  Can span multiple lines with **bold** and *italic* for emphasis.
relationships:
  - from_abstraction: 0 # AbstractionName1
    to_abstraction: 1 # AbstractionName2
    label: "Manages"{lang_hint}
  - from_abstraction: 2 # AbstractionName3
    to_abstraction: 0 # AbstractionName1
    label: "Provides config"{lang_hint}
  # ... other relationships
```

Now, provide the YAML output:
"""
        response = call_llm(prompt, use_cache=(use_cache and self.cur_retry == 0)) # Use cache only if enabled and not retrying

        # --- Validation ---
        yaml_str = response.strip().split("```yaml")[1].split("```")[0].strip()
        relationships_data = yaml.safe_load(yaml_str)

        if not isinstance(relationships_data, dict) or not all(
            k in relationships_data for k in ["summary", "relationships"]
        ):
            raise ValueError(
                "LLM output is not a dict or missing keys ('summary', 'relationships')"
            )
        if not isinstance(relationships_data["summary"], str):
            raise ValueError("summary is not a string")
        if not isinstance(relationships_data["relationships"], list):
            raise ValueError("relationships is not a list")

        # Validate relationships structure
        validated_relationships = []
        for rel in relationships_data["relationships"]:
            # Check for 'label' key
            if not isinstance(rel, dict) or not all(
                k in rel for k in ["from_abstraction", "to_abstraction", "label"]
            ):
                raise ValueError(
                    f"Missing keys (expected from_abstraction, to_abstraction, label) in relationship item: {rel}"
                )
            # Validate 'label' is a string
            if not isinstance(rel["label"], str):
                raise ValueError(f"Relationship label is not a string: {rel}")

            # Validate indices
            try:
                from_idx = int(str(rel["from_abstraction"]).split("#")[0].strip())
                to_idx = int(str(rel["to_abstraction"]).split("#")[0].strip())
                if not (
                    0 <= from_idx < num_abstractions and 0 <= to_idx < num_abstractions
                ):
                    raise ValueError(
                        f"Invalid index in relationship: from={from_idx}, to={to_idx}. Max index is {num_abstractions-1}."
                    )
                validated_relationships.append(
                    {
                        "from": from_idx,
                        "to": to_idx,
                        "label": rel["label"],  # Potentially translated label
                    }
                )
            except (ValueError, TypeError):
                raise ValueError(f"Could not parse indices from relationship: {rel}")

        logger.info("Generated project summary and relationship details.")
        return {
            "summary": relationships_data["summary"],  # Potentially translated summary
            "details": validated_relationships,  # Store validated, index-based relationships with potentially translated labels
        }

    def post(self, shared, prep_res, exec_res):
        # Structure is now {"summary": str, "details": [{"from": int, "to": int, "label": str}]}
        # Summary and label might be translated
        shared["relationships"] = exec_res


class TrialAbstractionAnalysis:
    """
    Main class for abstraction and relationship analysis of clinical trial data.
    """
    def __init__(self, max_abstractions=10, language="english", use_cache=True):
        """
        Initialize the analysis system.
        
        Args:
            max_abstractions: Maximum number of abstractions to identify
            language: Language to use for generated text
            use_cache: Whether to use cached LLM responses
        """
        self.max_abstractions = max_abstractions
        self.language = language
        self.use_cache = use_cache
        self.abstraction_node = IdentifyAbstractions()
        self.relationship_node = AnalyzeRelationships()
        logger.info(f"Initialized TrialAbstractionAnalysis with max_abstractions={max_abstractions}, language={language}")
        
    def prepare_trial_data(self, clinical_trials, patient_data, biomarker_data):
        """
        Transforms clinical trial data into a format suitable for abstraction analysis.
        
        Args:
            clinical_trials: List of clinical trial data
            patient_data: Patient demographics and baseline characteristics
            biomarker_data: Biomarker measurements for patients
            
        Returns:
            Dictionary with prepared data for analysis
        """
        logger.info(f"Preparing trial data for analysis: {len(clinical_trials)} trials, {len(patient_data)} patients")
        
        # Transform clinical data into file-like structures for the analysis engine
        files_data = []
        
        # Transform trial protocols
        for i, trial in enumerate(clinical_trials):
            trial_content = self._format_trial_protocol(trial)
            files_data.append((f"trial_{i}_protocol.json", trial_content))
        
        # Transform patient cohorts
        patient_cohort_content = self._format_patient_cohort(patient_data)
        files_data.append(("patient_cohort.json", patient_cohort_content))
        
        # Transform biomarker data
        biomarker_content = self._format_biomarker_data(biomarker_data)
        files_data.append(("biomarker_data.json", biomarker_content))
        
        # Transform outcome data
        for i, trial in enumerate(clinical_trials):
            if 'outcomes' in trial:
                outcome_content = self._format_trial_outcomes(trial)
                files_data.append((f"trial_{i}_outcomes.json", outcome_content))
            
        # Prepare shared context for analysis nodes
        shared = {
            "files": files_data,
            "project_name": "Crohn's Disease Treatment Analysis",
            "language": self.language,
            "use_cache": self.use_cache,
            "max_abstraction_num": self.max_abstractions
        }
        
        return shared
    
    def _format_trial_protocol(self, trial):
        """Format trial protocol as structured text"""
        return (
            f"Trial ID: {trial['trial_id']}\n"
            f"Title: {trial['title']}\n"
            f"Phase: {trial['phase']}\n\n"
            f"Arms:\n{self._format_arms(trial['arms'])}\n\n"
            f"Adaptive Rules:\n{self._format_adaptive_rules(trial.get('adaptiveRules', []))}"
        )
    
    def _format_arms(self, arms):
        """Format trial arms as structured text"""
        result = ""
        for arm in arms:
            result += (
                f"  - Arm ID: {arm['armId']}\n"
                f"    Name: {arm['name']}\n"
                f"    Treatment: {arm['treatment']['medication']} {arm['treatment']['dosage']}{arm['treatment']['unit']} {arm['treatment']['frequency']}\n"
                f"    Biomarker Stratification: {self._format_biomarkers(arm.get('biomarkerStratification', []))}\n\n"
            )
        return result
    
    def _format_biomarkers(self, biomarkers):
        """Format biomarker stratification as text"""
        if not biomarkers:
            return "None"
        return ", ".join([f"{b['biomarker']}:{b['criteria']}" for b in biomarkers])
    
    def _format_adaptive_rules(self, rules):
        """Format adaptive rules as structured text"""
        if not rules:
            return "None"
            
        result = ""
        for rule in rules:
            result += (
                f"  - Trigger: {rule['triggerCondition']}\n"
                f"    Action: {rule['action']}\n"
                f"    Parameters: {self._format_parameters(rule.get('parameters', {}))}\n\n"
            )
        return result
    
    def _format_parameters(self, params):
        """Format parameters as text"""
        if not params:
            return "None"
        return ", ".join([f"{k}={v}" for k, v in params.items()])
    
    def _format_patient_cohort(self, patients):
        """Format patient cohort as structured text"""
        result = "Patient Cohort:\n\n"
        for patient in patients:
            result += (
                f"Patient ID: {patient['patient_id']}\n"
                f"Demographics: {patient['demographics']['age']} y/o {patient['demographics']['sex']}, {patient['demographics']['ethnicity']}\n"
                f"Crohn's Type: {patient['clinical_data']['crohns_type']}\n"
                f"Diagnosis Date: {patient['clinical_data']['diagnosis_date']}\n"
                f"Disease Activity: CDAI={patient['clinical_data']['disease_activity']['CDAI']}, "
                f"SES_CD={patient['clinical_data']['disease_activity']['SES_CD']}, "
                f"Calprotectin={patient['clinical_data']['disease_activity']['fecal_calprotectin']}\n"
                f"Genetic Markers: {self._format_genetic_markers(patient['biomarkers'].get('genetic_markers', []))}\n\n"
            )
        return result
    
    def _format_genetic_markers(self, markers):
        """Format genetic markers as text"""
        if not markers:
            return "None"
        return ", ".join([f"{m['gene']}:{m['variant']}({m['zygosity']})" for m in markers])
    
    def _format_biomarker_data(self, biomarker_data):
        """Format biomarker data as structured text"""
        result = "Biomarker Data:\n\n"
        for biomarker in biomarker_data:
            result += (
                f"Biomarker: {biomarker['name']}\n"
                f"Type: {biomarker['type']}\n"
                f"Description: {biomarker['description']}\n"
                f"Relevance: {biomarker['relevance']}\n"
                f"Normal Range: {biomarker['normal_range']}\n\n"
            )
        return result
    
    def _format_trial_outcomes(self, trial):
        """Format trial outcomes as structured text"""
        result = f"Trial Outcomes for {trial['trial_id']}:\n\n"
        
        if 'outcomes' not in trial:
            return result + "No outcome data available\n"
            
        result += f"Total Patients: {trial['outcomes']['total_patients']}\n"
        result += f"Response Rate: {trial['outcomes']['response_rate']}%\n\n"
        
        result += "Arm Outcomes:\n"
        for arm in trial['outcomes'].get('arms', []):
            result += (
                f"  - Arm: {arm['arm_id']}\n"
                f"    Patients: {arm['patients']}\n"
                f"    Response Rate: {arm['response_rate']}%\n"
                f"    Mean CDAI Reduction: {arm['mean_cdai_reduction']}\n"
                f"    Biomarker Correlations: {self._format_correlations(arm.get('biomarker_correlations', []))}\n\n"
            )
        return result
    
    def _format_correlations(self, correlations):
        """Format biomarker correlations as text"""
        if not correlations:
            return "None"
        return ", ".join([f"{c['biomarker']}:{c['correlation_coefficient']}" for c in correlations])
    
    def run_analysis(self, clinical_trials, patient_data, biomarker_data):
        """
        Run the full abstraction and relationship analysis pipeline.
        
        Args:
            clinical_trials: List of clinical trial data
            patient_data: Patient demographics and baseline characteristics
            biomarker_data: Biomarker measurements for patients
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Running full abstraction analysis pipeline")
        
        # Prepare data
        shared = self.prepare_trial_data(clinical_trials, patient_data, biomarker_data)
        
        # Run abstraction identification
        logger.info("Step 1: Identifying abstractions")
        prep_res_abstractions = self.abstraction_node.prep(shared)
        abstractions = self.abstraction_node.exec(prep_res_abstractions)
        self.abstraction_node.post(shared, prep_res_abstractions, abstractions)
        
        # Run relationship analysis
        logger.info("Step 2: Analyzing relationships")
        prep_res_relationships = self.relationship_node.prep(shared)
        relationships = self.relationship_node.exec(prep_res_relationships)
        self.relationship_node.post(shared, prep_res_relationships, relationships)
        
        # Combine results
        analysis_results = {
            "abstractions": shared["abstractions"],
            "relationships": shared["relationships"],
            "meta": {
                "num_trials": len(clinical_trials),
                "num_patients": len(patient_data),
                "num_biomarkers": len(biomarker_data),
                "analysis_timestamp": self._get_timestamp()
            }
        }
        
        logger.info(f"Analysis complete: found {len(shared['abstractions'])} abstractions and {len(shared['relationships']['details'])} relationships")
        return analysis_results
    
    def _get_timestamp(self):
        """Get current timestamp"""
        return datetime.now().isoformat()