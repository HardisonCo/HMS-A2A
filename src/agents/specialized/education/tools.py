"""
MCP Tools for Education Domain.

This module provides MCP-compliant tools for educational services, curriculum
development, and assessment design.
"""
from typing import Dict, List, Any, Optional
import json
import re
from datetime import datetime, date

from ..tools_base import StandardsCompliantTool
from ..standards_validation import StandardsValidator
from ..mcp_registry import register_tool


class EducationTools:
    """Collection of MCP-compliant tools for education domain."""

    @register_tool(
        name="design_learning_objectives",
        description="Design measurable learning objectives using educational taxonomy",
        domains=["education", "curriculum_development"],
        standard="education_standards"
    )
    def design_learning_objectives(
        subject_area: str,
        grade_level: str,
        topic: str,
        cognitive_levels: List[str],
        standards_alignment: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Design measurable learning objectives using educational taxonomy.

        Args:
            subject_area: Subject area (e.g., "mathematics", "language_arts")
            grade_level: Grade level or education stage
            topic: Specific topic within the subject area
            cognitive_levels: Bloom's taxonomy levels to target
            standards_alignment: Optional standards to align with

        Returns:
            Dictionary with designed learning objectives
        """
        validator = StandardsValidator()
        
        # Validate subject area
        valid_subjects = [
            "mathematics", "language_arts", "science", "social_studies", 
            "arts", "physical_education", "technology", "foreign_language",
            "stem", "history", "geography", "music", "computer_science"
        ]
        
        if subject_area.lower() not in [s.lower() for s in valid_subjects]:
            validator.add_violation(
                standard="education_standards",
                rule="subject_area",
                message=f"Subject area '{subject_area}' is not recognized",
                severity="medium"
            )
        
        # Validate grade level
        valid_grade_levels = [
            "kindergarten", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
            "elementary", "middle_school", "high_school", "higher_education",
            "undergraduate", "graduate", "adult_education", "professional_development"
        ]
        
        if grade_level.lower() not in [g.lower() for g in valid_grade_levels]:
            validator.add_violation(
                standard="education_standards",
                rule="grade_level",
                message=f"Grade level '{grade_level}' is not recognized",
                severity="medium"
            )
        
        # Validate cognitive levels (Bloom's Taxonomy)
        valid_cognitive_levels = [
            "remember", "understand", "apply", "analyze", "evaluate", "create",
            "knowledge", "comprehension", "application", "analysis", "synthesis", "evaluation"
        ]
        
        for level in cognitive_levels:
            if level.lower() not in [l.lower() for l in valid_cognitive_levels]:
                validator.add_violation(
                    standard="education_standards",
                    rule="cognitive_level",
                    message=f"Cognitive level '{level}' is not recognized in Bloom's Taxonomy",
                    severity="medium"
                )
        
        # Define action verbs for each cognitive level
        action_verbs = {
            "remember": ["define", "describe", "identify", "label", "list", "match", "name", "recall", "recognize", "select", "state"],
            "understand": ["classify", "compare", "contrast", "demonstrate", "explain", "illustrate", "interpret", "paraphrase", "predict", "summarize", "translate"],
            "apply": ["apply", "calculate", "complete", "construct", "demonstrate", "execute", "implement", "modify", "solve", "use"],
            "analyze": ["analyze", "categorize", "classify", "compare", "contrast", "differentiate", "distinguish", "examine", "experiment", "question", "test"],
            "evaluate": ["appraise", "argue", "assess", "critique", "defend", "evaluate", "judge", "justify", "prioritize", "rate", "select", "support"],
            "create": ["assemble", "construct", "create", "design", "develop", "formulate", "generate", "invent", "organize", "plan", "produce", "propose"]
        }
        
        # Map old taxonomy terms to new ones
        taxonomy_mapping = {
            "knowledge": "remember",
            "comprehension": "understand",
            "application": "apply",
            "analysis": "analyze",
            "synthesis": "create",
            "evaluation": "evaluate"
        }
        
        # Map cognitive levels to action verbs
        mapped_levels = []
        for level in cognitive_levels:
            mapped_level = level.lower()
            if mapped_level in taxonomy_mapping:
                mapped_level = taxonomy_mapping[mapped_level]
            
            if mapped_level in action_verbs:
                mapped_levels.append(mapped_level)
        
        # Skip further processing if there are validation issues
        if any(v["severity"] == "high" for v in validator.get_violations()):
            return {
                "valid": False,
                "violations": validator.get_violations(),
                "recommendations": ["Correct validation issues before designing objectives"]
            }
        
        # Generate learning objectives
        learning_objectives = []
        
        # Subject-specific considerations
        condition_templates = {
            "mathematics": [
                f"Given a {topic} problem",
                f"Using {topic} formulas",
                f"When presented with a {topic} scenario",
                f"After completing a unit on {topic}"
            ],
            "language_arts": [
                f"After reading a text about {topic}",
                f"Given a writing prompt related to {topic}",
                f"During a discussion about {topic}",
                f"After analyzing a {topic} passage"
            ],
            "science": [
                f"After conducting a {topic} experiment",
                f"Using scientific methods to investigate {topic}",
                f"Given data about {topic}",
                f"When observing {topic} phenomena"
            ],
            "social_studies": [
                f"After studying {topic}",
                f"When analyzing primary sources about {topic}",
                f"Given a map/timeline of {topic}",
                f"When comparing perspectives on {topic}"
            ]
        }
        
        # Default conditions if subject not found
        condition_templates_default = [
            f"After instruction on {topic}",
            f"Given resources about {topic}",
            f"When presented with {topic} content",
            f"During a {topic} activity"
        ]
        
        # Get appropriate conditions for the subject
        conditions = condition_templates.get(subject_area.lower(), condition_templates_default)
        
        # For each cognitive level, generate objectives
        for level in mapped_levels:
            level_verbs = action_verbs[level]
            
            # Generate 2-3 objectives per cognitive level
            for i in range(min(3, len(level_verbs))):
                verb = level_verbs[i]
                condition = conditions[i % len(conditions)]
                
                # Create objective components
                objective_components = {
                    "condition": condition,
                    "audience": f"students will",
                    "behavior": f"{verb} {topic}",
                    "degree": ""
                }
                
                # Add degree component based on cognitive level
                if level in ["remember", "understand"]:
                    objective_components["degree"] = "with at least 80% accuracy"
                elif level in ["apply", "analyze"]:
                    objective_components["degree"] = "correctly in multiple contexts"
                elif level in ["evaluate", "create"]:
                    objective_components["degree"] = "that meets established criteria"
                
                # Construct full objective
                full_objective = f"{objective_components['condition']}, {objective_components['audience']} {objective_components['behavior']} {objective_components['degree']}".strip()
                
                # Add to list
                learning_objectives.append({
                    "objective": full_objective,
                    "cognitive_level": level,
                    "components": objective_components
                })
        
        # Add standards alignment if provided
        if standards_alignment:
            for i, objective in enumerate(learning_objectives):
                if i < len(standards_alignment):
                    objective["aligned_standard"] = standards_alignment[i]
        
        # Return result
        result = {
            "subject_area": subject_area,
            "grade_level": grade_level,
            "topic": topic,
            "cognitive_levels": cognitive_levels,
            "learning_objectives": learning_objectives
        }
        
        # Add guidelines for implementation
        result["implementation_guidelines"] = [
            "Share objectives with students at the beginning of the lesson",
            "Refer back to objectives during instruction to maintain focus",
            "Use objectives to guide assessment design",
            "Ensure all activities align with at least one objective"
        ]
        
        # Add violations if any
        violations = validator.get_violations()
        if violations:
            result["design_limitations"] = violations
        
        return result

    @register_tool(
        name="analyze_assessment_alignment",
        description="Analyze alignment between assessment items and learning objectives",
        domains=["education", "assessment"],
        standard="education_standards"
    )
    def analyze_assessment_alignment(
        learning_objectives: List[Dict[str, Any]],
        assessment_items: List[Dict[str, Any]],
        assessment_type: str
    ) -> Dict[str, Any]:
        """
        Analyze alignment between assessment items and learning objectives.

        Args:
            learning_objectives: List of learning objectives
            assessment_items: List of assessment items to analyze
            assessment_type: Type of assessment (e.g., "formative", "summative")

        Returns:
            Dictionary with alignment analysis results
        """
        validator = StandardsValidator()
        
        # Validate assessment type
        valid_assessment_types = [
            "formative", "summative", "diagnostic", "performance",
            "project", "portfolio", "quiz", "test", "exam"
        ]
        
        if assessment_type.lower() not in [t.lower() for t in valid_assessment_types]:
            validator.add_violation(
                standard="education_standards",
                rule="assessment_type",
                message=f"Assessment type '{assessment_type}' is not recognized",
                severity="medium"
            )
        
        # Validate learning objectives
        for i, objective in enumerate(learning_objectives):
            if "objective" not in objective:
                validator.add_violation(
                    standard="education_standards",
                    rule="objective_format",
                    message=f"Learning objective {i+1} missing 'objective' field",
                    severity="high"
                )
            
            if "cognitive_level" not in objective:
                validator.add_violation(
                    standard="education_standards",
                    rule="objective_format",
                    message=f"Learning objective {i+1} missing 'cognitive_level' field",
                    severity="medium"
                )
        
        # Validate assessment items
        for i, item in enumerate(assessment_items):
            required_fields = ["item_text", "item_type", "expected_answer"]
            for field in required_fields:
                if field not in item:
                    validator.add_violation(
                        standard="education_standards",
                        rule="assessment_item_format",
                        message=f"Assessment item {i+1} missing required field: '{field}'",
                        severity="high"
                    )
        
        # Skip further analysis if there are critical issues
        if any(v["severity"] == "high" for v in validator.get_violations()):
            return {
                "valid": False,
                "violations": validator.get_violations(),
                "recommendations": ["Correct format issues before analyzing alignment"]
            }
        
        # Cognitive level mapping (for comparison)
        cognitive_levels_hierarchy = {
            "remember": 1,
            "understand": 2,
            "apply": 3,
            "analyze": 4,
            "evaluate": 5,
            "create": 6
        }
        
        # Item type to cognitive level mapping
        item_type_cognitive_mapping = {
            "multiple_choice": ["remember", "understand"],
            "true_false": ["remember"],
            "matching": ["remember", "understand"],
            "fill_in_blank": ["remember", "understand"],
            "short_answer": ["understand", "apply"],
            "essay": ["analyze", "evaluate", "create"],
            "performance_task": ["apply", "analyze", "evaluate", "create"],
            "project": ["apply", "analyze", "evaluate", "create"]
        }
        
        # Analysis variables
        alignment_results = []
        objectives_covered = set()
        objectives_not_covered = set()
        item_levels = {}
        
        # Analyze each assessment item
        for i, item in enumerate(assessment_items):
            item_text = item["item_text"]
            item_type = item.get("item_type", "").lower()
            targeted_objective_ids = item.get("targeted_objectives", [])
            
            # Determine cognitive level of the item
            item_cognitive_level = item.get("cognitive_level")
            
            if not item_cognitive_level:
                # Infer from item type
                if item_type in item_type_cognitive_mapping:
                    item_cognitive_level = item_type_cognitive_mapping[item_type][-1]  # Take highest level
                else:
                    item_cognitive_level = "unknown"
            
            item_levels[i] = item_cognitive_level
            
            # Check alignment with objectives
            matched_objectives = []
            
            # First check explicit targeting
            if targeted_objective_ids:
                for obj_id in targeted_objective_ids:
                    if 0 <= obj_id < len(learning_objectives):
                        objective = learning_objectives[obj_id]["objective"]
                        cognitive_level = learning_objectives[obj_id].get("cognitive_level", "unknown")
                        
                        # Check cognitive level alignment
                        level_alignment = "unknown"
                        if item_cognitive_level in cognitive_levels_hierarchy and cognitive_level in cognitive_levels_hierarchy:
                            item_level_value = cognitive_levels_hierarchy[item_cognitive_level]
                            obj_level_value = cognitive_levels_hierarchy[cognitive_level]
                            
                            if item_level_value == obj_level_value:
                                level_alignment = "exact"
                            elif item_level_value < obj_level_value:
                                level_alignment = "below"
                            else:
                                level_alignment = "above"
                        
                        matched_objectives.append({
                            "objective_id": obj_id,
                            "objective": objective,
                            "match_type": "explicit",
                            "cognitive_alignment": level_alignment
                        })
                        
                        objectives_covered.add(obj_id)
            
            # If no explicit targeting, try content matching
            if not matched_objectives:
                for j, obj in enumerate(learning_objectives):
                    objective_text = obj["objective"]
                    cognitive_level = obj.get("cognitive_level", "unknown")
                    
                    # Extract key terms from objective
                    if "components" in obj and "behavior" in obj["components"]:
                        key_terms = obj["components"]["behavior"].split()
                    else:
                        key_terms = objective_text.split()
                    
                    # Count matching terms
                    matches = sum(1 for term in key_terms if term.lower() in item_text.lower())
                    match_ratio = matches / len(key_terms) if key_terms else 0
                    
                    # If good match, consider it aligned
                    if match_ratio > 0.4:  # Arbitrary threshold
                        # Check cognitive level alignment
                        level_alignment = "unknown"
                        if item_cognitive_level in cognitive_levels_hierarchy and cognitive_level in cognitive_levels_hierarchy:
                            item_level_value = cognitive_levels_hierarchy[item_cognitive_level]
                            obj_level_value = cognitive_levels_hierarchy[cognitive_level]
                            
                            if item_level_value == obj_level_value:
                                level_alignment = "exact"
                            elif item_level_value < obj_level_value:
                                level_alignment = "below"
                            else:
                                level_alignment = "above"
                        
                        matched_objectives.append({
                            "objective_id": j,
                            "objective": objective_text,
                            "match_type": "content_similarity",
                            "match_strength": f"{int(match_ratio * 100)}%",
                            "cognitive_alignment": level_alignment
                        })
                        
                        objectives_covered.add(j)
            
            # Record alignment results for this item
            alignment_results.append({
                "item_id": i,
                "item_text": item_text[:100] + "..." if len(item_text) > 100 else item_text,
                "item_type": item_type,
                "cognitive_level": item_cognitive_level,
                "matching_objectives": matched_objectives,
                "alignment_strength": "strong" if matched_objectives else "weak"
            })
        
        # Identify objectives not covered by any assessment item
        for j in range(len(learning_objectives)):
            if j not in objectives_covered:
                objectives_not_covered.add(j)
        
        # Calculate overall alignment metrics
        objective_coverage_ratio = len(objectives_covered) / len(learning_objectives) if learning_objectives else 0
        objective_coverage_percentage = int(objective_coverage_ratio * 100)
        
        # Count items by cognitive level
        cognitive_level_counts = {}
        for level in cognitive_levels_hierarchy.keys():
            cognitive_level_counts[level] = sum(1 for item_level in item_levels.values() if item_level == level)
        
        # Determine if there's a cognitive level imbalance
        highest_level = max(cognitive_level_counts.items(), key=lambda x: x[1])[0] if cognitive_level_counts else None
        cognitive_imbalance = any(count > 0 and count < len(assessment_items) * 0.2 for count in cognitive_level_counts.values())
        
        # Generate recommendations based on analysis
        recommendations = []
        
        if objectives_not_covered:
            recommendations.append(f"Add assessment items for {len(objectives_not_covered)} uncovered learning objectives")
        
        if objective_coverage_percentage < 80:
            recommendations.append(f"Improve assessment coverage (currently at {objective_coverage_percentage}%)")
        
        if cognitive_imbalance:
            recommendations.append("Ensure better balance of cognitive levels in assessment items")
        
        if any(res["alignment_strength"] == "weak" for res in alignment_results):
            recommendations.append("Revise items with weak alignment to better target specific objectives")
        
        # Compile final results
        analysis_results = {
            "assessment_type": assessment_type,
            "number_of_objectives": len(learning_objectives),
            "number_of_assessment_items": len(assessment_items),
            "objective_coverage": {
                "covered": len(objectives_covered),
                "not_covered": len(objectives_not_covered),
                "coverage_percentage": objective_coverage_percentage
            },
            "cognitive_level_distribution": cognitive_level_counts,
            "item_alignment_details": alignment_results,
            "uncovered_objectives": [
                {
                    "objective_id": j,
                    "objective": learning_objectives[j]["objective"]
                } for j in objectives_not_covered
            ],
            "alignment_quality": "strong" if objective_coverage_percentage >= 80 else "needs improvement",
            "recommendations": recommendations
        }
        
        # Add violations if any
        violations = validator.get_violations()
        if violations:
            analysis_results["analysis_limitations"] = violations
        
        return analysis_results

    @register_tool(
        name="design_differentiated_activities",
        description="Design differentiated learning activities for diverse learners",
        domains=["education", "instructional_design"],
        standard="education_standards"
    )
    def design_differentiated_activities(
        learning_objective: Dict[str, Any],
        learner_profiles: List[Dict[str, Any]],
        content_area: str,
        time_constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Design differentiated learning activities for diverse learners.

        Args:
            learning_objective: The primary learning objective
            learner_profiles: Profiles of different learner groups to accommodate
            content_area: Subject or content area
            time_constraints: Optional constraints on activity duration

        Returns:
            Dictionary with differentiated learning activities
        """
        validator = StandardsValidator()
        
        # Validate learning objective
        if "objective" not in learning_objective:
            validator.add_violation(
                standard="education_standards",
                rule="objective_format",
                message="Learning objective missing 'objective' field",
                severity="high"
            )
        
        # Validate content area
        valid_content_areas = [
            "mathematics", "language_arts", "science", "social_studies", 
            "arts", "physical_education", "technology", "foreign_language"
        ]
        
        if content_area.lower() not in [c.lower() for c in valid_content_areas]:
            validator.add_violation(
                standard="education_standards",
                rule="content_area",
                message=f"Content area '{content_area}' is not recognized",
                severity="medium"
            )
        
        # Validate learner profiles
        for i, profile in enumerate(learner_profiles):
            required_fields = ["group_name", "learning_needs"]
            for field in required_fields:
                if field not in profile:
                    validator.add_violation(
                        standard="education_standards",
                        rule="learner_profile_format",
                        message=f"Learner profile {i+1} missing required field: '{field}'",
                        severity="high"
                    )
        
        # Skip further processing if there are critical issues
        if any(v["severity"] == "high" for v in validator.get_violations()):
            return {
                "valid": False,
                "violations": validator.get_violations(),
                "recommendations": ["Correct format issues before designing activities"]
            }
        
        # Extract key information
        objective_text = learning_objective.get("objective", "")
        cognitive_level = learning_objective.get("cognitive_level", "understand")
        
        # Differentiation approaches
        differentiation_approaches = {
            "content": "Adapting what is taught based on learner needs",
            "process": "Adapting how learners access content and develop understanding",
            "product": "Adapting how learners demonstrate their learning",
            "environment": "Adapting the learning environment to support diverse needs"
        }
        
        # Learning modalities
        learning_modalities = ["visual", "auditory", "kinesthetic", "reading/writing"]
        
        # Activity templates by cognitive level
        activity_templates = {
            "remember": [
                "Flashcard review of {topic} concepts",
                "Matching activity for {topic} terminology",
                "Create a vocabulary list for {topic}",
                "{topic} quiz game"
            ],
            "understand": [
                "Concept map of {topic} relationships",
                "Summarize main points of {topic}",
                "Compare and contrast {topic} elements",
                "Explain {topic} in your own words"
            ],
            "apply": [
                "Solve practice problems related to {topic}",
                "Create examples demonstrating {topic}",
                "Role-play scenario involving {topic}",
                "Apply {topic} to a real-world situation"
            ],
            "analyze": [
                "Categorize {topic} elements and explain rationale",
                "Diagram relationships within {topic}",
                "Identify patterns or themes in {topic}",
                "Analyze a case study involving {topic}"
            ],
            "evaluate": [
                "Critique an example of {topic}",
                "Debate different perspectives on {topic}",
                "Assess the effectiveness of {topic} approaches",
                "Rank solutions to {topic} problems"
            ],
            "create": [
                "Design a new approach to {topic}",
                "Create an original project demonstrating {topic}",
                "Develop a plan addressing {topic} challenge",
                "Compose a creative work incorporating {topic}"
            ]
        }
        
        # Extract topic from objective
        topic_match = re.search(r'(?:identify|describe|explain|analyze|evaluate|create)\s+([\w\s]+)', objective_text)
        topic = topic_match.group(1) if topic_match else "the topic"
        
        # Generate differentiated activities
        differentiated_activities = []
        
        for profile in learner_profiles:
            group_name = profile["group_name"]
            learning_needs = profile["learning_needs"]
            preferred_modalities = profile.get("preferred_modalities", [])
            support_level = profile.get("support_level", "medium")
            
            # Choose differentiation approaches based on needs
            approaches = []
            
            if "reading" in learning_needs.lower() or "language" in learning_needs.lower():
                approaches.append("content")
            
            if "attention" in learning_needs.lower() or "focus" in learning_needs.lower():
                approaches.append("environment")
            
            if "expression" in learning_needs.lower() or "output" in learning_needs.lower():
                approaches.append("product")
            
            if not approaches or "process" not in approaches:
                approaches.append("process")
            
            # Ensure uniqueness
            approaches = list(set(approaches))
            
            # Select activity templates based on cognitive level
            templates = activity_templates.get(cognitive_level, activity_templates["understand"])
            
            # Generate activity for this group
            activity = {
                "group": group_name,
                "learning_needs": learning_needs,
                "differentiation_approaches": approaches,
                "activities": []
            }
            
            # Add content differentiation if applicable
            if "content" in approaches:
                content_adaptation = {
                    "name": f"Content-Differentiated {templates[0].format(topic=topic)}",
                    "type": "content",
                    "description": templates[0].format(topic=topic),
                    "adaptations": []
                }
                
                # Add specific adaptations based on needs
                if "reading" in learning_needs.lower():
                    content_adaptation["adaptations"].append("Provide simplified texts with key vocabulary highlighted")
                    content_adaptation["adaptations"].append("Include visual supports alongside text")
                
                if "advanced" in learning_needs.lower():
                    content_adaptation["adaptations"].append("Incorporate more complex concepts and applications")
                    content_adaptation["adaptations"].append("Provide extension materials for deeper exploration")
                
                if support_level == "high":
                    content_adaptation["adaptations"].append("Break content into smaller, manageable chunks")
                    content_adaptation["adaptations"].append("Provide reference sheets with key information")
                
                activity["activities"].append(content_adaptation)
            
            # Add process differentiation if applicable
            if "process" in approaches:
                process_adaptation = {
                    "name": f"Process-Differentiated {templates[1].format(topic=topic)}",
                    "type": "process",
                    "description": templates[1].format(topic=topic),
                    "adaptations": []
                }
                
                # Add specific adaptations based on modalities
                if preferred_modalities:
                    for modality in preferred_modalities:
                        if modality == "visual":
                            process_adaptation["adaptations"].append("Incorporate diagrams, charts, and visual organizers")
                        elif modality == "auditory":
                            process_adaptation["adaptations"].append("Include discussion opportunities and audio resources")
                        elif modality == "kinesthetic":
                            process_adaptation["adaptations"].append("Integrate hands-on activities and movement")
                        elif modality == "reading/writing":
                            process_adaptation["adaptations"].append("Provide written guides and reflective writing tasks")
                
                if support_level == "high":
                    process_adaptation["adaptations"].append("Provide step-by-step instructions with checkpoints")
                    process_adaptation["adaptations"].append("Include teacher modeling and guided practice")
                elif support_level == "low":
                    process_adaptation["adaptations"].append("Offer open-ended exploration with minimal scaffolding")
                    process_adaptation["adaptations"].append("Provide self-directed learning options")
                
                activity["activities"].append(process_adaptation)
            
            # Add product differentiation if applicable
            if "product" in approaches:
                product_adaptation = {
                    "name": f"Product-Differentiated {templates[2].format(topic=topic)}",
                    "type": "product",
                    "description": templates[2].format(topic=topic),
                    "adaptations": []
                }
                
                # Add specific adaptations based on needs
                if "expression" in learning_needs.lower():
                    product_adaptation["adaptations"].append("Offer multiple formats for demonstrating learning")
                    product_adaptation["adaptations"].append("Provide options for written, visual, or oral presentations")
                
                if "advanced" in learning_needs.lower():
                    product_adaptation["adaptations"].append("Encourage more sophisticated analysis and evaluation")
                    product_adaptation["adaptations"].append("Set higher expectations for depth and complexity")
                
                if support_level == "high":
                    product_adaptation["adaptations"].append("Provide templates and structured formats")
                    product_adaptation["adaptations"].append("Break final product into manageable components")
                
                activity["activities"].append(product_adaptation)
            
            # Add environment differentiation if applicable
            if "environment" in approaches:
                environment_adaptation = {
                    "name": f"Environment-Differentiated {templates[3].format(topic=topic)}",
                    "type": "environment",
                    "description": templates[3].format(topic=topic),
                    "adaptations": []
                }
                
                # Add specific adaptations based on needs
                if "attention" in learning_needs.lower():
                    environment_adaptation["adaptations"].append("Minimize distractions in the learning space")
                    environment_adaptation["adaptations"].append("Provide opportunities for movement breaks")
                
                if "social" in learning_needs.lower():
                    environment_adaptation["adaptations"].append("Balance individual and collaborative activities")
                    environment_adaptation["adaptations"].append("Create structured group interactions with clear roles")
                
                if support_level == "high":
                    environment_adaptation["adaptations"].append("Establish consistent routines and expectations")
                    environment_adaptation["adaptations"].append("Provide frequent check-ins and feedback")
                
                activity["activities"].append(environment_adaptation)
            
            # Add to differentiated activities
            differentiated_activities.append(activity)
        
        # Consider time constraints if provided
        if time_constraints:
            available_minutes = time_constraints.get("available_minutes", 60)
            
            # Add timing recommendations
            for activity in differentiated_activities:
                # Estimate time needed for each activity type
                total_activities = len(activity["activities"])
                minutes_per_activity = available_minutes / total_activities if total_activities > 0 else available_minutes
                
                for sub_activity in activity["activities"]:
                    sub_activity["estimated_time"] = f"{int(minutes_per_activity)} minutes"
        
        # Compile final results
        result = {
            "objective": objective_text,
            "content_area": content_area,
            "cognitive_level": cognitive_level,
            "differentiated_activities": differentiated_activities,
            "implementation_notes": [
                "Monitor student engagement and adjust activities as needed",
                "Ensure all students have access to necessary materials and supports",
                "Consider flexible grouping strategies to maximize learning",
                "Provide choice within activities where appropriate",
                "Use formative assessment to gauge effectiveness of differentiation"
            ]
        }
        
        # Add time constraints if provided
        if time_constraints:
            result["time_constraints"] = time_constraints
        
        # Add violations if any
        violations = validator.get_violations()
        if violations:
            result["design_limitations"] = violations
        
        return result

    @register_tool(
        name="generate_rubric",
        description="Generate a standards-aligned assessment rubric",
        domains=["education", "assessment"],
        standard="education_standards"
    )
    def generate_rubric(
        assignment_type: str,
        learning_objectives: List[Dict[str, Any]],
        grade_level: str,
        performance_levels: int = 4
    ) -> Dict[str, Any]:
        """
        Generate a standards-aligned assessment rubric.

        Args:
            assignment_type: Type of assignment (e.g., "essay", "project", "presentation")
            learning_objectives: List of learning objectives being assessed
            grade_level: Grade level or education stage
            performance_levels: Number of performance levels (default: 4)

        Returns:
            Dictionary with the generated rubric
        """
        validator = StandardsValidator()
        
        # Validate assignment type
        valid_assignment_types = [
            "essay", "project", "presentation", "lab_report", "portfolio",
            "research_paper", "creative_writing", "debate", "performance",
            "multimedia", "experiment", "problem_set"
        ]
        
        if assignment_type.lower() not in [t.lower() for t in valid_assignment_types]:
            validator.add_violation(
                standard="education_standards",
                rule="assignment_type",
                message=f"Assignment type '{assignment_type}' is not recognized",
                severity="medium"
            )
        
        # Validate grade level
        valid_grade_levels = [
            "elementary", "middle_school", "high_school", "higher_education",
            "k-2", "3-5", "6-8", "9-12", "undergraduate", "graduate"
        ]
        
        if grade_level.lower() not in [g.lower() for g in valid_grade_levels] and not grade_level.isdigit():
            validator.add_violation(
                standard="education_standards",
                rule="grade_level",
                message=f"Grade level '{grade_level}' is not recognized",
                severity="medium"
            )
        
        # Validate performance levels
        if performance_levels < 2 or performance_levels > 6:
            validator.add_violation(
                standard="education_standards",
                rule="performance_levels",
                message=f"Performance levels ({performance_levels}) should be between 2 and 6",
                severity="medium"
            )
        
        # Validate learning objectives
        for i, objective in enumerate(learning_objectives):
            if "objective" not in objective:
                validator.add_violation(
                    standard="education_standards",
                    rule="objective_format",
                    message=f"Learning objective {i+1} missing 'objective' field",
                    severity="high"
                )
        
        # Skip further processing if there are critical issues
        if any(v["severity"] == "high" for v in validator.get_violations()):
            return {
                "valid": False,
                "violations": validator.get_violations(),
                "recommendations": ["Correct format issues before generating rubric"]
            }
        
        # Define performance level labels
        if performance_levels == 2:
            level_labels = ["Developing", "Proficient"]
        elif performance_levels == 3:
            level_labels = ["Developing", "Proficient", "Exemplary"]
        elif performance_levels == 4:
            level_labels = ["Beginning", "Developing", "Proficient", "Exemplary"]
        elif performance_levels == 5:
            level_labels = ["Beginning", "Developing", "Proficient", "Accomplished", "Exemplary"]
        else:  # 6 levels
            level_labels = ["Beginning", "Emerging", "Developing", "Proficient", "Accomplished", "Exemplary"]
        
        # Define default criteria by assignment type
        default_criteria = {
            "essay": ["Content/Ideas", "Organization", "Evidence/Support", "Language/Conventions"],
            "project": ["Content Knowledge", "Process/Methodology", "Product Quality", "Presentation"],
            "presentation": ["Content", "Organization", "Delivery", "Visual Aids", "Engagement"],
            "lab_report": ["Hypothesis", "Methodology", "Data Analysis", "Conclusions", "Scientific Accuracy"],
            "portfolio": ["Completeness", "Reflection", "Growth Over Time", "Quality of Artifacts"],
            "research_paper": ["Research Quality", "Thesis Development", "Evidence", "Analysis", "Citation Format"],
            "creative_writing": ["Originality", "Development", "Language Use", "Structure", "Impact"],
            "debate": ["Argument Construction", "Evidence Use", "Rebuttal", "Delivery", "Organization"],
            "performance": ["Technical Skill", "Artistic Interpretation", "Preparation", "Communication"],
            "multimedia": ["Content Quality", "Technical Execution", "Creativity", "Organization", "Impact"],
            "experiment": ["Experimental Design", "Data Collection", "Analysis", "Conclusions", "Documentation"],
            "problem_set": ["Problem Understanding", "Solution Strategy", "Execution", "Verification"]
        }
        
        # Get criteria for this assignment type
        criteria_list = default_criteria.get(assignment_type.lower(), ["Content", "Organization", "Presentation", "Accuracy"])
        
        # Extract objective-specific criteria
        for objective in learning_objectives:
            objective_text = objective.get("objective", "")
            
            # Extract key verbs and content
            verb_match = re.search(r'will\s+(\w+)', objective_text)
            verb = verb_match.group(1) if verb_match else ""
            
            # Map verb to potential criterion
            verb_criterion_map = {
                "analyze": "Analysis",
                "evaluate": "Evaluation",
                "create": "Creativity",
                "apply": "Application",
                "synthesize": "Synthesis",
                "design": "Design",
                "demonstrate": "Demonstration of Skills",
                "explain": "Explanation/Reasoning",
                "interpret": "Interpretation",
                "compare": "Comparison/Contrast",
                "research": "Research Quality"
            }
            
            if verb in verb_criterion_map and verb_criterion_map[verb] not in criteria_list:
                criteria_list.append(verb_criterion_map[verb])
        
        # Limit to a reasonable number of criteria
        if len(criteria_list) > 7:
            criteria_list = criteria_list[:7]
        
        # Generate performance descriptors for each criterion
        criteria = []
        
        for criterion in criteria_list:
            # Generate level descriptors based on criterion
            descriptors = self._generate_performance_descriptors(criterion, level_labels, assignment_type, grade_level)
            
            # Add to criteria list
            criteria.append({
                "criterion": criterion,
                "descriptors": descriptors
            })
        
        # Generate overall rubric
        rubric = {
            "title": f"{assignment_type.capitalize()} Rubric",
            "assignment_type": assignment_type,
            "grade_level": grade_level,
            "performance_levels": {
                "count": performance_levels,
                "labels": level_labels
            },
            "criteria": criteria,
            "learning_objectives": [obj.get("objective", "") for obj in learning_objectives],
            "scoring_guide": {
                "total_points": performance_levels * len(criteria),
                "grading_scale": self._generate_grading_scale(performance_levels * len(criteria))
            },
            "implementation_notes": [
                "Share rubric with students before they begin the assignment",
                "Use specific examples to clarify expectations for each criterion",
                "Consider involving students in rubric development or review",
                "Focus feedback on specific criteria rather than general comments",
                "Use rubric data to inform future instruction"
            ]
        }
        
        # Add violations if any
        violations = validator.get_violations()
        if violations:
            rubric["design_limitations"] = violations
        
        return rubric
    
    def _generate_performance_descriptors(self, criterion, level_labels, assignment_type, grade_level):
        """Helper method to generate performance descriptors for a criterion."""
        descriptors = {}
        
        # Customize descriptors based on criterion
        if criterion == "Content/Ideas" or criterion == "Content":
            for i, label in enumerate(level_labels):
                if i == 0:  # Lowest level
                    descriptors[label] = "Content is minimal, inaccurate, or irrelevant to the assignment"
                elif i == len(level_labels) - 1:  # Highest level
                    descriptors[label] = "Content is comprehensive, accurate, insightful, and exceeds expectations"
                elif i == 1 and len(level_labels) > 2:  # Second level
                    descriptors[label] = "Content is partially developed with some inaccuracies or irrelevance"
                elif i == len(level_labels) - 2:  # Second highest level
                    descriptors[label] = "Content is thorough, accurate, and relevant to the assignment"
                else:  # Middle levels
                    descriptors[label] = "Content is mostly accurate and relevant with adequate development"
        
        elif criterion == "Organization":
            for i, label in enumerate(level_labels):
                if i == 0:  # Lowest level
                    descriptors[label] = "Organization is unclear, illogical, or ineffective"
                elif i == len(level_labels) - 1:  # Highest level
                    descriptors[label] = "Organization is clear, logical, and enhances the effectiveness of the work"
                elif i == 1 and len(level_labels) > 2:  # Second level
                    descriptors[label] = "Organization shows some structure but may be inconsistent or confusing"
                elif i == len(level_labels) - 2:  # Second highest level
                    descriptors[label] = "Organization is clear and logical throughout most of the work"
                else:  # Middle levels
                    descriptors[label] = "Organization is generally clear with some minor logical inconsistencies"
        
        elif criterion == "Evidence/Support" or criterion == "Evidence":
            for i, label in enumerate(level_labels):
                if i == 0:  # Lowest level
                    descriptors[label] = "Little or no relevant evidence provided to support ideas"
                elif i == len(level_labels) - 1:  # Highest level
                    descriptors[label] = "Comprehensive, relevant evidence that strongly supports and enhances ideas"
                elif i == 1 and len(level_labels) > 2:  # Second level
                    descriptors[label] = "Some evidence provided but may be limited, irrelevant, or misinterpreted"
                elif i == len(level_labels) - 2:  # Second highest level
                    descriptors[label] = "Sufficient, relevant evidence that effectively supports ideas"
                else:  # Middle levels
                    descriptors[label] = "Adequate evidence provided that generally supports ideas"
        
        else:
            # Generic descriptors for other criteria
            for i, label in enumerate(level_labels):
                if i == 0:  # Lowest level
                    descriptors[label] = f"{criterion} shows minimal competence or significant errors"
                elif i == len(level_labels) - 1:  # Highest level
                    descriptors[label] = f"{criterion} demonstrates exceptional skill and comprehensive understanding"
                elif i == 1 and len(level_labels) > 2:  # Second level
                    descriptors[label] = f"{criterion} shows developing competence with notable errors or gaps"
                elif i == len(level_labels) - 2:  # Second highest level
                    descriptors[label] = f"{criterion} demonstrates proficient skill and solid understanding"
                else:  # Middle levels
                    descriptors[label] = f"{criterion} shows adequate competence with some minor errors"
        
        return descriptors
    
    def _generate_grading_scale(self, total_points):
        """Helper method to generate grading scale based on total points."""
        scale = {}
        
        # Calculate grade ranges
        a_threshold = total_points * 0.9
        b_threshold = total_points * 0.8
        c_threshold = total_points * 0.7
        d_threshold = total_points * 0.6
        
        # Create scale
        scale["A"] = f"{int(a_threshold)}-{total_points} points"
        scale["B"] = f"{int(b_threshold)}-{int(a_threshold)-1} points"
        scale["C"] = f"{int(c_threshold)}-{int(b_threshold)-1} points"
        scale["D"] = f"{int(d_threshold)}-{int(c_threshold)-1} points"
        scale["F"] = f"0-{int(d_threshold)-1} points"
        
        return scale


def register_education_tools() -> List[str]:
    """Register all education tools and return their names.
    
    Returns:
        List of registered tool names
    """
    # In a real implementation, this would register tools with a central registry
    tools = [
        EducationTools.design_learning_objectives,
        EducationTools.analyze_assessment_alignment,
        EducationTools.design_differentiated_activities,
        EducationTools.generate_rubric
    ]
    
    return [tool.__name__ for tool in tools]