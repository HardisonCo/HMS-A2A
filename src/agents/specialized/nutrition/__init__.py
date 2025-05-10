"""
Nutrition Standards-Compliant Agent

This module provides a standards-compliant agent for dietitians and nutritionists.
"""

from specialized_agents import StandardsCompliantAgent, ValidationResult
from typing import Any, Dict, List, Optional


class NutritionAgent(StandardsCompliantAgent):
    """A standards-compliant agent for dietetic and nutrition domains.
    
    Implements nutrition-specific functionality and compliance with
    nutrition and dietetic standards like Nutrition Care Process, Dietary Reference Intakes,
    and Medical Nutrition Therapy standards.
    """
    
    def __init__(self, job_role: str, port: int = None):
        """Create a new nutrition domain agent.
        
        Args:
            job_role: The specific nutrition job role (e.g., "Dietitian", "Nutritionist")
            port: Optional port number for the agent server
        """
        supported_standards = [
            "NUTRITION_CARE_PROCESS",
            "DIETARY_REFERENCE_INTAKES",
            "CLINICAL_NUTRITION_GUIDELINES",
            "MEDICAL_NUTRITION_THERAPY"
        ]
        super().__init__(job_role, "Nutrition and Dietetics", supported_standards, port)
        
        # Register nutrition domain tools
        from specialized_agents.nutrition.tools import register_nutrition_tools
        tools = register_nutrition_tools()
        for tool in tools:
            self.addTool(tool)
    
    def getDomainPromptInstructions(self) -> str:
        """Provides domain-specific prompt instructions for nutrition professionals."""
        return """
As a nutrition professional, you must:
- Provide evidence-based nutritional advice and recommendations
- Respect scope of practice boundaries and avoid medical diagnoses unless qualified
- Individualize nutrition recommendations based on client profiles
- Utilize the Nutrition Care Process framework when applicable (Assessment, Diagnosis, Intervention, Monitoring/Evaluation)
- Reference current Dietary Reference Intakes (DRIs) for nutrient recommendations
- Respect cultural, ethical, and religious considerations related to food
- Use standardized nutrition terminology with clear definitions
- Consider food accessibility, affordability, and sustainability when appropriate
- Recognize and respond to potential red flags for disordered eating or nutritional deficiencies
- Include appropriate disclaimers when providing general versus personalized nutrition advice
"""
    
    def validateDomainCompliance(self, task: Any) -> ValidationResult:
        """Validates compliance with nutrition-specific standards.
        
        Args:
            task: The task to validate
            
        Returns:
            ValidationResult with validation status and issues
        """
        issues: List[str] = []
        
        # Extract the content to validate
        content = self._extract_content_from_task(task)
        
        # Check for nutritional misinformation or harmful advice
        harmful_advice_patterns = [
            r"\b(detox|cleanse)\s+(diet|plan)\b",  # Detox/cleanse diets
            r"\beliminate\s+(all|entire)\s+(food group|carbs|fats)\b",  # Eliminating entire food groups
            r"\blose\s+(\d+)\s+pounds\s+in\s+(\d+)\s+days\b",  # Rapid weight loss claims
            r"\bcure\s+(disease|cancer|diabetes)\b",  # Disease cure claims
        ]
        
        # Validate against harmful nutrition advice patterns
        import re
        for pattern in harmful_advice_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append("Potentially harmful or unscientific nutrition advice detected")
                break
        
        # Check for appropriate nutrient recommendation references
        nutrient_recommendations = r"(\d+)\s*(grams|mg|mcg|IU)\s*(of|per day)\s*(protein|vitamin|mineral|calcium|iron)"
        nutrient_matches = re.findall(nutrient_recommendations, content, re.IGNORECASE)
        
        if len(nutrient_matches) > 0 and "DRI" not in content and "Dietary Reference Intake" not in content:
            issues.append("Nutrient recommendations should reference appropriate DRIs or evidence-based guidelines")
        
        # Ensure nutrition diagnostic statements follow PES format when appropriate
        if "nutrition diagnosis" in content.lower() and "related to" not in content and "as evidenced by" not in content:
            issues.append("Nutrition diagnosis statements should follow PES format: Problem, Etiology, Signs/Symptoms")
        
        # Ensure MNT interventions have appropriate components
        if "nutrition intervention" in content.lower() or "MNT" in content:
            has_measurable_goals = bool(re.search(r"goal:.+?(reduce|increase|improve|maintain|achieve)", content, re.IGNORECASE))
            has_timeframe = bool(re.search(r"within\s+(\d+)\s+(days|weeks|months)", content, re.IGNORECASE))
            
            if not has_measurable_goals or not has_timeframe:
                issues.append("Medical Nutrition Therapy interventions should include measurable goals and timeframes")
        
        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues
        )