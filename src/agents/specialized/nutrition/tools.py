"""
Nutrition Tools

This module provides MCP-compliant tools for dietitians and nutritionists.
"""

from typing import Dict, Any, List, Optional, Type, Union
from pydantic import BaseModel, Field
from enum import Enum
import json
import re
import math
from datetime import datetime


class StandardsCompliantMCPTool:
    """Base class for standards-compliant MCP tools."""
    
    def __init__(
        self,
        name: str,
        description: str,
        schema_model: Type[BaseModel],
        supported_standards: List[str],
        domain: str,
        tool_metadata: Dict[str, Any] = None
    ):
        """Initialize a standards-compliant MCP tool.
        
        Args:
            name: Tool name
            description: Tool description
            schema_model: Pydantic model defining the input schema
            supported_standards: List of standards supported by this tool
            domain: Industry domain (e.g., "Nutrition and Dietetics")
            tool_metadata: Additional metadata for the tool
        """
        self.name = name
        self.description = description
        self.schema_model = schema_model
        self.supported_standards = supported_standards
        self.domain = domain
        self.tool_metadata = tool_metadata or {}
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for registration with MCP.
        
        Returns:
            Dictionary containing the tool definition
        """
        schema = self.schema_model.model_json_schema()
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": schema,
            "metadata": {
                "domain": self.domain,
                "supportedStandards": self.supported_standards,
                **self.tool_metadata
            }
        }
    
    async def __call__(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with the given arguments.
        
        Args:
            **kwargs: Tool arguments
            
        Returns:
            Tool execution result
        """
        # Validate input against schema
        validated_args = self.schema_model(**kwargs)
        
        # Execute the tool
        result = await self.execute(validated_args.model_dump())
        
        # Format the result
        formatted_result = self.formatResult(result)
        
        # Check if human review is required
        requires_review = self.requiresHumanReview(validated_args.model_dump(), result)
        
        # Add metadata to the result
        for part in formatted_result:
            if "metadata" not in part:
                part["metadata"] = {}
            part["metadata"]["requiresHumanReview"] = requires_review
        
        return formatted_result
    
    async def execute(self, args: Dict[str, Any]) -> Any:
        """Execute the tool with the given arguments.
        
        This method should be overridden by subclasses.
        
        Args:
            args: Validated tool arguments
            
        Returns:
            Tool execution result
        """
        raise NotImplementedError("Tool execution not implemented")
    
    def formatResult(self, result: Any) -> List[Dict[str, Any]]:
        """Format the result for return to the agent.
        
        Args:
            result: Tool execution result
            
        Returns:
            List of formatted result parts
        """
        return [
            {
                "type": "text",
                "text": json.dumps(result, indent=2)
            }
        ]
    
    def requiresHumanReview(self, args: Dict[str, Any], result: Any) -> bool:
        """Determine if the result requires human review.
        
        Args:
            args: Tool arguments
            result: Tool execution result
            
        Returns:
            Boolean indicating if human review is required
        """
        return False


# Schema definitions for Nutritional Assessment Tool

class Gender(str, Enum):
    """Patient gender options."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class ActivityLevel(str, Enum):
    """Physical activity level options."""
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"


class GoalType(str, Enum):
    """Nutritional goal types."""
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    WEIGHT_MAINTENANCE = "weight_maintenance"
    ATHLETIC_PERFORMANCE = "athletic_performance"
    MEDICAL_MANAGEMENT = "medical_management"


class PatientProfile(BaseModel):
    """Basic patient information."""
    age: int = Field(description="Patient age in years")
    gender: Gender = Field(description="Patient gender")
    height: float = Field(description="Height in centimeters")
    weight: float = Field(description="Weight in kilograms")
    activityLevel: ActivityLevel = Field(description="Physical activity level")
    goalType: GoalType = Field(description="Nutritional goal type")


class Supplement(BaseModel):
    """Nutritional supplement information."""
    name: str
    dosage: str
    frequency: str


class MedicalFactors(BaseModel):
    """Medical factors affecting nutritional needs."""
    existingConditions: Optional[List[str]] = Field(None, description="List of existing medical conditions (e.g., diabetes, hypertension)")
    medications: Optional[List[str]] = Field(None, description="Current medications that may affect nutrition")
    allergies: Optional[List[str]] = Field(None, description="Food allergies or intolerances")
    laboratoryValues: Optional[Dict[str, Union[str, float]]] = Field(None, description="Recent laboratory test results relevant to nutrition")


class DietaryRestriction(str, Enum):
    """Dietary restriction options."""
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    KOSHER = "kosher"
    HALAL = "halal"
    LOW_SODIUM = "low_sodium"
    LOW_FAT = "low_fat"
    LOW_CARB = "low_carb"
    DIABETIC = "diabetic"
    RENAL = "renal"
    FODMAP = "fodmap"


class DietaryFactors(BaseModel):
    """Dietary factors and preferences."""
    currentDiet: Optional[str] = Field(None, description="Description of current dietary pattern")
    dietaryRestrictions: Optional[List[DietaryRestriction]] = Field(None, description="Dietary restrictions or special diets")
    foodPreferences: Optional[List[str]] = Field(None, description="Food preferences or cultural considerations")
    supplementUse: Optional[List[Supplement]] = Field(None, description="Current nutritional supplements")


class AssessmentType(str, Enum):
    """Nutritional assessment type options."""
    INITIAL = "initial"
    FOLLOW_UP = "follow_up"
    COMPREHENSIVE = "comprehensive"
    FOCUSED = "focused"
    SPORTS_NUTRITION = "sports_nutrition"


class NutritionalAssessment(BaseModel):
    """Schema for nutritional assessment."""
    patientProfile: PatientProfile = Field(description="Basic patient profile information")
    medicalFactors: Optional[MedicalFactors] = Field(None, description="Medical factors affecting nutritional needs")
    dietaryFactors: Optional[DietaryFactors] = Field(None, description="Dietary factors and preferences")
    assessmentType: AssessmentType = Field(description="Type of nutritional assessment to perform")
    includeRecommendations: bool = Field(True, description="Whether to include dietary recommendations")


class Anthropometrics(BaseModel):
    """Anthropometric measurements."""
    bmi: float
    bmiCategory: str
    idealBodyWeight: float
    bodyFatEstimate: Optional[float] = None


class EnergyRequirements(BaseModel):
    """Energy requirements calculation."""
    basalMetabolicRate: int  # kcal/day
    totalEnergyExpenditure: int  # kcal/day
    targetIntake: int  # kcal/day for goal


class ProteinNeeds(BaseModel):
    """Protein nutritional needs."""
    grams: int
    caloriePercentage: int
    gramsPerKg: float


class CarbohydrateNeeds(BaseModel):
    """Carbohydrate nutritional needs."""
    grams: int
    caloriePercentage: int


class FatNeeds(BaseModel):
    """Fat nutritional needs."""
    grams: int
    caloriePercentage: int


class FiberNeeds(BaseModel):
    """Fiber nutritional needs."""
    grams: int


class MacronutrientNeeds(BaseModel):
    """Macronutrient nutritional needs."""
    protein: ProteinNeeds
    carbohydrates: CarbohydrateNeeds
    fats: FatNeeds
    fiber: FiberNeeds


class MicronutrientStatus(str, Enum):
    """Micronutrient status options."""
    ADEQUATE = "adequate"
    POTENTIAL_CONCERN = "potential_concern"
    DEFICIENT = "deficient"
    EXCESSIVE = "excessive"


class MicronutrientConsideration(BaseModel):
    """Micronutrient status and recommendations."""
    nutrient: str
    status: MicronutrientStatus
    recommendation: str


class HydrationNeeds(BaseModel):
    """Hydration requirements."""
    totalFluidRequirement: int  # ml/day
    activityAdjustment: int  # additional ml based on activity


class NutritionalDiagnosis(BaseModel):
    """Nutritional diagnosis using PES format."""
    problem: str
    etiology: str
    signs: List[str]


class NutritionalRecommendations(BaseModel):
    """Nutritional recommendations."""
    caloricTarget: int
    macronutrientDistribution: str
    mealFrequency: str
    specificFoodRecommendations: List[str]
    supplementRecommendations: List[str]
    followUpTimeframe: str
    educationalFocus: List[str]


class NutritionalAssessmentResult(BaseModel):
    """Complete nutritional assessment result."""
    anthropometrics: Anthropometrics
    energyRequirements: EnergyRequirements
    macronutrientNeeds: MacronutrientNeeds
    micronutrientConsiderations: List[MicronutrientConsideration]
    hydrationNeeds: HydrationNeeds
    nutritionalDiagnosis: List[NutritionalDiagnosis]
    recommendations: Optional[NutritionalRecommendations] = None


# Schema definitions for Meal Plan Generator Tool

class NutritionalGoals(BaseModel):
    """Nutritional targets for the meal plan."""
    caloricTarget: float = Field(description="Daily caloric target in kcal")
    proteinGrams: float = Field(description="Daily protein target in grams")
    carbGrams: float = Field(description="Daily carbohydrate target in grams")
    fatGrams: float = Field(description="Daily fat target in grams")
    fiberGrams: Optional[float] = Field(None, description="Daily fiber target in grams")


class CalorieDistribution(BaseModel):
    """Percentage of calories allocated to each meal."""
    breakfast: Optional[float] = Field(None, description="Percentage for breakfast")
    lunch: Optional[float] = Field(None, description="Percentage for lunch")
    dinner: Optional[float] = Field(None, description="Percentage for dinner")
    snacks: Optional[float] = Field(None, description="Percentage for snacks")


class DietaryPatternRestriction(str, Enum):
    """Dietary restriction options for meal planning."""
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    EGG_FREE = "egg_free"
    NUT_FREE = "nut_free"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    KOSHER = "kosher"
    HALAL = "halal"
    LOW_FODMAP = "low_fodmap"
    LOW_SODIUM = "low_sodium"
    LOW_CARB = "low_carb"
    KETO = "keto"
    PALEO = "paleo"


class DietaryPatterns(BaseModel):
    """Dietary patterns and preferences for meal planning."""
    mealFrequency: int = Field(description="Number of eating occasions per day")
    preferredCuisines: Optional[List[str]] = Field(None, description="Preferred cuisine styles")
    excludedIngredients: Optional[List[str]] = Field(None, description="Ingredients to exclude")
    dietaryRestrictions: Optional[List[DietaryPatternRestriction]] = Field(None, description="Dietary restrictions or special diets")
    calorieDistribution: Optional[CalorieDistribution] = Field(None, description="Percentage of calories allocated to each meal")


class NutrientRestriction(BaseModel):
    """Specific nutrient restriction."""
    limit: float
    units: str


class MedicalConsiderations(BaseModel):
    """Medical considerations affecting meal planning."""
    conditions: Optional[List[str]] = Field(None, description="Medical conditions affecting meal planning")
    nutrientRestrictions: Optional[Dict[str, NutrientRestriction]] = Field(None, description="Specific nutrient restrictions (e.g., sodium, potassium)")
    medicationInteractions: Optional[List[str]] = Field(None, description="Medications that interact with food")


class ComplexityLevel(str, Enum):
    """Recipe complexity level options."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class BudgetLevel(str, Enum):
    """Budget level options for food choices."""
    ECONOMY = "economy"
    MODERATE = "moderate"
    PREMIUM = "premium"


class Season(str, Enum):
    """Seasonal focus options for meal planning."""
    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    ANY = "any"


class PlanningParameters(BaseModel):
    """Meal planning parameters."""
    durationDays: int = Field(7, description="Number of days to generate meal plan for")
    complexity: ComplexityLevel = Field(ComplexityLevel.MODERATE, description="Recipe complexity level")
    budgetLevel: Optional[BudgetLevel] = Field(None, description="Budget level for food choices")
    seasonality: Season = Field(Season.ANY, description="Seasonal focus of the meal plan")
    includeShopping: bool = Field(True, description="Include shopping list")


class MealPlanGenerator(BaseModel):
    """Schema for meal plan generation."""
    nutritionalGoals: NutritionalGoals = Field(description="Nutritional targets for the meal plan")
    dietaryPatterns: DietaryPatterns = Field(description="Dietary patterns and preferences")
    medicalConsiderations: Optional[MedicalConsiderations] = Field(None, description="Medical considerations affecting meal planning")
    planningParameters: PlanningParameters = Field(description="Meal planning parameters")


class MacronutrientBreakdown(BaseModel):
    """Macronutrient breakdown in grams and percentage."""
    protein: Dict[str, float]
    carbohydrates: Dict[str, float]
    fat: Dict[str, float]
    fiber: Optional[Dict[str, float]] = None


class NutritionalAdherence(BaseModel):
    """Adherence to nutritional targets."""
    calories: float
    protein: float
    carbohydrates: float
    fat: float
    fiber: Optional[float] = None


class NutritionalSummary(BaseModel):
    """Summary of nutritional information for meal plan."""
    averageDailyCalories: float
    macronutrientBreakdown: MacronutrientBreakdown
    adherenceToTarget: NutritionalAdherence


class NutritionInfo(BaseModel):
    """Nutritional information for a meal or day."""
    calories: float
    protein: float
    carbohydrates: float
    fat: float
    fiber: Optional[float] = None


class Ingredient(BaseModel):
    """Recipe ingredient information."""
    name: str
    amount: float
    unit: str
    notes: Optional[str] = None


class Recipe(BaseModel):
    """Recipe information."""
    name: str
    portions: float
    ingredients: List[Ingredient]
    nutritionPerServing: NutritionInfo
    preparationMethod: str
    preparationTime: int  # minutes
    dietaryNotes: List[str]


class Meal(BaseModel):
    """Meal information including recipes."""
    mealType: str  # breakfast, lunch, dinner, snack1, snack2, etc.
    recipes: List[Recipe]


class DailyPlan(BaseModel):
    """Daily meal plan information."""
    day: int
    totalNutrition: NutritionInfo
    meals: List[Meal]


class ShoppingListItem(BaseModel):
    """Shopping list item information."""
    ingredient: str
    amount: float
    unit: str


class ShoppingList(BaseModel):
    """Shopping list with categorized items and tips."""
    categorized: Dict[str, List[ShoppingListItem]]
    mealPrepTips: List[str]
    storageSuggestions: List[str]


class MealPlanResult(BaseModel):
    """Complete meal plan generation result."""
    nutritionalSummary: NutritionalSummary
    mealPlan: List[DailyPlan]
    shoppingList: Optional[ShoppingList] = None
    adherenceStrategies: List[str]
    customizations: List[str]


# Schema for Dietary Analysis Tool (simplified for brevity)
class DietaryAnalysis(BaseModel):
    """Schema for dietary analysis inputs."""
    # Would include fields for dietary analysis
    pass


class DietaryAnalysisResult(BaseModel):
    """Result structure for dietary analysis."""
    # Would include fields for dietary analysis results
    pass


# Implement Nutritional Assessment Tool
class NutritionalAssessmentTool(StandardsCompliantMCPTool):
    """MCP-compliant tool for nutritional assessment."""
    
    def __init__(self):
        """Initialize the nutritional assessment tool."""
        super().__init__(
            name="nutritional_assessment",
            description="Conducts comprehensive nutritional assessment including anthropometrics, energy requirements, macro/micronutrient needs, and personalized dietary recommendations.",
            schema_model=NutritionalAssessment,
            supported_standards=[
                "NUTRITION_CARE_PROCESS",
                "DIETARY_REFERENCE_INTAKES",
                "CLINICAL_NUTRITION_GUIDELINES",
                "MEDICAL_NUTRITION_THERAPY"
            ],
            domain="Nutrition and Dietetics",
            tool_metadata={
                "title": "Nutritional Assessment Tool",
                "readOnlyHint": True,
                "destructiveHint": False,
                "idempotentHint": True,
                "openWorldHint": False,
            }
        )
    
    async def execute(self, args: Dict[str, Any]) -> NutritionalAssessmentResult:
        """Execute the nutritional assessment.
        
        Args:
            args: Tool arguments
            
        Returns:
            Nutritional assessment result
        """
        patient = args["patientProfile"]
        medical_factors = args.get("medicalFactors", {"existingConditions": [], "medications": [], "allergies": []})
        dietary_factors = args.get("dietaryFactors", {"dietaryRestrictions": []})
        
        # Calculate BMI
        height_in_meters = patient["height"] / 100
        bmi = patient["weight"] / (height_in_meters * height_in_meters)
        
        # Determine BMI category
        if bmi < 18.5:
            bmi_category = "Underweight"
        elif bmi < 25:
            bmi_category = "Normal weight"
        elif bmi < 30:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obese"
        
        # Calculate ideal body weight (Hamwi formula)
        if patient["gender"] == "male":
            ideal_body_weight = 48 + (2.7 * ((patient["height"] / 100 * 39.37) - 60))
        else:
            ideal_body_weight = 45.5 + (2.2 * ((patient["height"] / 100 * 39.37) - 60))
        
        # Calculate Basal Metabolic Rate (using Mifflin-St Jeor equation)
        if patient["gender"] == "male":
            bmr = 10 * patient["weight"] + 6.25 * patient["height"] - 5 * patient["age"] + 5
        else:
            bmr = 10 * patient["weight"] + 6.25 * patient["height"] - 5 * patient["age"] - 161
        
        # Activity factor
        activity_factor = 1.2  # sedentary
        if patient["activityLevel"] == "lightly_active":
            activity_factor = 1.375
        elif patient["activityLevel"] == "moderately_active":
            activity_factor = 1.55
        elif patient["activityLevel"] == "very_active":
            activity_factor = 1.725
        elif patient["activityLevel"] == "extremely_active":
            activity_factor = 1.9
        
        # Calculate Total Energy Expenditure
        tee = bmr * activity_factor
        
        # Adjust for goal
        target_intake = tee
        if patient["goalType"] == "weight_loss":
            target_intake = tee - 500
        elif patient["goalType"] == "weight_gain":
            target_intake = tee + 500
        elif patient["goalType"] == "athletic_performance":
            target_intake = tee * 1.1
        
        # Medical adjustments
        if medical_factors.get("existingConditions"):
            if "diabetes" in medical_factors["existingConditions"]:
                # Adjust for diabetes
                target_intake = min(target_intake, 1800)  # simplified example
            
            if "kidney disease" in medical_factors["existingConditions"]:
                # Adjust for kidney disease
                target_intake = min(target_intake, 2000)  # simplified example
        
        # Calculate macronutrient needs
        protein_grams_per_kg = 0.8  # RDA
        if patient["goalType"] == "athletic_performance":
            protein_grams_per_kg = 1.6
        elif patient["goalType"] == "weight_loss":
            protein_grams_per_kg = 1.2
        
        # Adjust protein needs based on medical conditions
        if medical_factors.get("existingConditions"):
            if "kidney disease" in medical_factors["existingConditions"]:
                protein_grams_per_kg = 0.6  # Renal diet restriction
        
        protein_grams = patient["weight"] * protein_grams_per_kg
        protein_calories = protein_grams * 4
        protein_percentage = (protein_calories / target_intake) * 100
        
        # Carbohydrates (adjusted for conditions)
        carb_percentage = 50
        if dietary_factors.get("dietaryRestrictions") and "low_carb" in dietary_factors["dietaryRestrictions"]:
            carb_percentage = 25
        if medical_factors.get("existingConditions") and "diabetes" in medical_factors["existingConditions"]:
            carb_percentage = 40
        
        carb_calories = target_intake * (carb_percentage / 100)
        carb_grams = carb_calories / 4
        
        # Fats
        fat_percentage = 100 - carb_percentage - protein_percentage
        fat_calories = target_intake * (fat_percentage / 100)
        fat_grams = fat_calories / 9
        
        # Fiber recommendation (IOM guidelines)
        if patient["gender"] == "male":
            fiber_grams = 38
        else:
            fiber_grams = 25
        
        if patient["age"] > 50:
            if patient["gender"] == "male":
                fiber_grams = 30
            else:
                fiber_grams = 21
        
        # Hydration needs
        base_fluid_requirement = patient["weight"] * 35  # mL/day
        activity_adjustment = 0
        if patient["activityLevel"] == "moderately_active":
            activity_adjustment = 500
        elif patient["activityLevel"] == "very_active":
            activity_adjustment = 1000
        elif patient["activityLevel"] == "extremely_active":
            activity_adjustment = 1500
        
        # Generate micronutrient considerations based on patient profile
        micronutrient_considerations = []
        
        # Age-related considerations
        if patient["age"] > 50:
            micronutrient_considerations.append({
                "nutrient": "Vitamin B12",
                "status": "potential_concern",
                "recommendation": "Consider supplementation or increase consumption of fortified foods due to decreased absorption with age."
            })
            micronutrient_considerations.append({
                "nutrient": "Calcium",
                "status": "potential_concern",
                "recommendation": "Ensure adequate intake (1200mg/day) for bone health."
            })
            micronutrient_considerations.append({
                "nutrient": "Vitamin D",
                "status": "potential_concern",
                "recommendation": "Consider supplementation (800-1000 IU/day) especially with limited sun exposure."
            })
        
        # Women-specific considerations
        if patient["gender"] == "female" and patient["age"] < 50:
            micronutrient_considerations.append({
                "nutrient": "Iron",
                "status": "potential_concern",
                "recommendation": "Ensure adequate intake (18mg/day) to prevent deficiency, especially if menstruating."
            })
            micronutrient_considerations.append({
                "nutrient": "Folate",
                "status": "potential_concern",
                "recommendation": "Consume 400mcg/day through diet or supplementation, especially if pregnancy is possible."
            })
        
        # Diet-specific considerations
        if dietary_factors.get("dietaryRestrictions"):
            if "vegan" in dietary_factors["dietaryRestrictions"]:
                micronutrient_considerations.append({
                    "nutrient": "Vitamin B12",
                    "status": "potential_concern",
                    "recommendation": "Supplement with B12 (25-100mcg/day) or consume fortified foods."
                })
                micronutrient_considerations.append({
                    "nutrient": "Omega-3 fatty acids",
                    "status": "potential_concern",
                    "recommendation": "Include plant sources like flaxseed, chia seeds, and walnuts or consider algae-based supplement."
                })
            
            if "dairy_free" in dietary_factors["dietaryRestrictions"]:
                micronutrient_considerations.append({
                    "nutrient": "Calcium",
                    "status": "potential_concern",
                    "recommendation": "Ensure adequate calcium from non-dairy sources like fortified plant milks, tofu, and leafy greens."
                })
        
        # Medical condition considerations
        if medical_factors.get("existingConditions"):
            if "hypertension" in medical_factors["existingConditions"]:
                micronutrient_considerations.append({
                    "nutrient": "Sodium",
                    "status": "excessive",
                    "recommendation": "Limit sodium intake to <2300mg/day, ideally <1500mg/day."
                })
                micronutrient_considerations.append({
                    "nutrient": "Potassium",
                    "status": "potential_concern",
                    "recommendation": "Increase intake through fruits, vegetables, and legumes to support blood pressure management."
                })
        
        # Nutritional diagnoses based on assessment
        nutritional_diagnosis = []
        
        if bmi < 18.5:
            nutritional_diagnosis.append({
                "problem": "Inadequate energy intake",
                "etiology": "Related to insufficient food consumption",
                "signs": ["BMI below normal range", "Underweight classification"]
            })
        elif bmi >= 30:
            nutritional_diagnosis.append({
                "problem": "Excessive energy intake",
                "etiology": "Related to dietary pattern and activity level",
                "signs": ["BMI in obese range", f"Weight {round(patient['weight'] - ideal_body_weight)} kg above ideal body weight"]
            })
        
        if dietary_factors.get("currentDiet") and "skipping meals" in dietary_factors["currentDiet"]:
            nutritional_diagnosis.append({
                "problem": "Irregular meal pattern",
                "etiology": "Related to busy schedule and lack of meal planning",
                "signs": ["Reported meal skipping", "Energy fluctuations"]
            })
        
        # Generate recommendations if requested
        recommendations = None
        if args["includeRecommendations"]:
            if patient["goalType"] == "weight_loss":
                meal_frequency = "3 balanced meals with 1-2 planned snacks"
            elif patient["goalType"] == "athletic_performance":
                meal_frequency = "3 main meals with 2-3 planned snacks for fueling and recovery"
            else:
                meal_frequency = "3 balanced meals daily"
            
            specific_food_recommendations = []
            
            # Base recommendations on profile
            specific_food_recommendations.append("Include lean protein sources at each meal")
            specific_food_recommendations.append("Aim for at least 5 servings of fruits and vegetables daily")
            specific_food_recommendations.append("Choose whole grains over refined grains when possible")
            
            # Condition-specific recommendations
            if medical_factors.get("existingConditions"):
                if "diabetes" in medical_factors["existingConditions"]:
                    specific_food_recommendations.append("Distribute carbohydrates evenly throughout the day")
                    specific_food_recommendations.append("Focus on low glycemic index carbohydrates")
                
                if "hypertension" in medical_factors["existingConditions"]:
                    specific_food_recommendations.append("Follow DASH eating pattern principles")
                    specific_food_recommendations.append("Limit processed foods high in sodium")
            
            # Goal-specific recommendations
            if patient["goalType"] == "weight_loss":
                specific_food_recommendations.append("Incorporate high-fiber foods to promote satiety")
                specific_food_recommendations.append("Use portion control strategies for calorie-dense foods")
            elif patient["goalType"] == "athletic_performance":
                specific_food_recommendations.append("Time carbohydrate intake around exercise sessions")
                specific_food_recommendations.append("Include protein within 30-60 minutes post-workout")
            
            # Handle dietary restrictions
            if dietary_factors.get("dietaryRestrictions"):
                if "gluten_free" in dietary_factors["dietaryRestrictions"]:
                    specific_food_recommendations.append("Choose naturally gluten-free grains like rice, quinoa, and gluten-free oats")
                
                if "dairy_free" in dietary_factors["dietaryRestrictions"]:
                    specific_food_recommendations.append("Select calcium-fortified plant milks and other dairy alternatives")
            
            # Supplement recommendations
            supplement_recommendations = []
            
            if patient["age"] > 50:
                supplement_recommendations.append("Vitamin D3: 1000-2000 IU daily")
            
            if dietary_factors.get("dietaryRestrictions") and "vegan" in dietary_factors["dietaryRestrictions"]:
                supplement_recommendations.append("Vitamin B12: 25-100mcg daily or 1000mcg 2-3 times per week")
            
            educational_focus = []
            if patient["goalType"] == "weight_loss":
                educational_focus.append("Understanding energy balance and portion control")
                educational_focus.append("Meal planning strategies for calorie management")
            elif patient["goalType"] == "medical_management":
                educational_focus.append("Nutrition principles for managing existing medical conditions")
                educational_focus.append("Reading food labels for condition-specific concerns")
            elif patient["goalType"] == "athletic_performance":
                educational_focus.append("Nutrient timing for optimal athletic performance")
                educational_focus.append("Hydration strategies for activity level")
            
            recommendations = {
                "caloricTarget": round(target_intake),
                "macronutrientDistribution": f"{round(protein_percentage)}% protein, {carb_percentage}% carbohydrates, {round(fat_percentage)}% fat",
                "mealFrequency": meal_frequency,
                "specificFoodRecommendations": specific_food_recommendations,
                "supplementRecommendations": supplement_recommendations,
                "followUpTimeframe": "2-3 weeks" if args["assessmentType"] == "initial" else "1-2 months",
                "educationalFocus": educational_focus,
            }
        
        # Create the final result
        result = {
            "anthropometrics": {
                "bmi": round(bmi, 1),
                "bmiCategory": bmi_category,
                "idealBodyWeight": round(ideal_body_weight, 1),
            },
            "energyRequirements": {
                "basalMetabolicRate": round(bmr),
                "totalEnergyExpenditure": round(tee),
                "targetIntake": round(target_intake),
            },
            "macronutrientNeeds": {
                "protein": {
                    "grams": round(protein_grams),
                    "caloriePercentage": round(protein_percentage),
                    "gramsPerKg": protein_grams_per_kg,
                },
                "carbohydrates": {
                    "grams": round(carb_grams),
                    "caloriePercentage": carb_percentage,
                },
                "fats": {
                    "grams": round(fat_grams),
                    "caloriePercentage": round(fat_percentage),
                },
                "fiber": {
                    "grams": fiber_grams,
                },
            },
            "micronutrientConsiderations": micronutrient_considerations,
            "hydrationNeeds": {
                "totalFluidRequirement": round(base_fluid_requirement),
                "activityAdjustment": activity_adjustment,
            },
            "nutritionalDiagnosis": nutritional_diagnosis,
        }
        
        if recommendations:
            result["recommendations"] = recommendations
        
        return result
    
    def formatResult(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format the nutritional assessment results for display.
        
        Args:
            result: Nutritional assessment result
            
        Returns:
            Formatted result
        """
        text_summary = f"""
**Nutritional Assessment Results**

**Anthropometrics**
- BMI: {result["anthropometrics"]["bmi"]} ({result["anthropometrics"]["bmiCategory"]})
- Ideal Body Weight: {result["anthropometrics"]["idealBodyWeight"]} kg

**Energy Requirements**
- BMR: {result["energyRequirements"]["basalMetabolicRate"]} kcal/day
- Total Energy Expenditure: {result["energyRequirements"]["totalEnergyExpenditure"]} kcal/day
- Target Intake: {result["energyRequirements"]["targetIntake"]} kcal/day

**Macronutrient Needs**
- Protein: {result["macronutrientNeeds"]["protein"]["grams"]}g ({result["macronutrientNeeds"]["protein"]["caloriePercentage"]}%)
- Carbohydrates: {result["macronutrientNeeds"]["carbohydrates"]["grams"]}g ({result["macronutrientNeeds"]["carbohydrates"]["caloriePercentage"]}%)
- Fats: {result["macronutrientNeeds"]["fats"]["grams"]}g ({result["macronutrientNeeds"]["fats"]["caloriePercentage"]}%)
- Fiber: {result["macronutrientNeeds"]["fiber"]["grams"]}g

**Nutritional Diagnosis**
{chr(10).join([f"- {diagnosis['problem']} {diagnosis['etiology']}" for diagnosis in result["nutritionalDiagnosis"]])}

{f'''
**Key Recommendations**
- Caloric Target: {result["recommendations"]["caloricTarget"]} kcal/day
- Macronutrient Distribution: {result["recommendations"]["macronutrientDistribution"]}
- Selected Food Recommendations:
  {chr(10).join([f"  - {rec}" for rec in result["recommendations"]["specificFoodRecommendations"][:3]])}
''' if "recommendations" in result else ""}
        """.strip()
        
        return [
            {"type": "data", "data": result},
            {"type": "text", "text": text_summary},
        ]
    
    def validateInput(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the input arguments.
        
        Args:
            args: Tool arguments
            
        Returns:
            Validation result with issues if any
        """
        issues = []
        
        # Validate reasonable height values
        if args["patientProfile"]["height"] < 120 or args["patientProfile"]["height"] > 220:
            issues.append({
                "path": "patientProfile.height",
                "message": "Height value appears to be outside typical adult range (120-220 cm)",
                "severity": "warning",
                "standardReference": "NUTRITION_CARE_PROCESS",
            })
        
        # Check for reasonable weight values
        if args["patientProfile"]["weight"] < 30 or args["patientProfile"]["weight"] > 250:
            issues.append({
                "path": "patientProfile.weight",
                "message": "Weight value appears to be outside typical adult range (30-250 kg)",
                "severity": "warning",
                "standardReference": "NUTRITION_CARE_PROCESS",
            })
        
        # Validate age reasonability
        if args["patientProfile"]["age"] < 18:
            issues.append({
                "path": "patientProfile.age",
                "message": "This tool is designed for adults (18+). Pediatric assessments require specialized tools.",
                "severity": "error",
                "standardReference": "PEDIATRIC_NUTRITION_GUIDELINES",
            })
        
        # Ensure goals align with medical conditions if present
        if args.get("medicalFactors", {}).get("existingConditions"):
            if "anorexia" in args["medicalFactors"]["existingConditions"] and args["patientProfile"]["goalType"] == "weight_loss":
                issues.append({
                    "path": "patientProfile.goalType",
                    "message": "Weight loss goals are contraindicated for patients with anorexia",
                    "severity": "error",
                    "standardReference": "MEDICAL_NUTRITION_THERAPY",
                })
            
            if "kidney disease" in args["medicalFactors"]["existingConditions"] and not args["medicalFactors"].get("laboratoryValues"):
                issues.append({
                    "path": "medicalFactors.laboratoryValues",
                    "message": "Laboratory values are strongly recommended for accurate assessment with kidney disease",
                    "severity": "warning",
                    "standardReference": "RENAL_NUTRITION_GUIDELINES",
                })
        
        return {
            "valid": not any(issue["severity"] == "error" for issue in issues),
            "issues": issues,
        }
    
    def requiresHumanReview(self, args: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Determine if human review is required.
        
        Args:
            args: Tool arguments
            result: Tool result
            
        Returns:
            Boolean indicating if human review is required
        """
        # Trigger review for complex medical cases
        if args.get("medicalFactors", {}).get("existingConditions") and len(args["medicalFactors"]["existingConditions"]) > 2:
            print(f"HITL Review Required: Multiple medical conditions ({', '.join(args['medicalFactors']['existingConditions'])}) requiring complex nutritional management.")
            return True
        
        # Trigger review for severely underweight or overweight patients
        if result["anthropometrics"]["bmi"] < 16.5 or result["anthropometrics"]["bmi"] > 40:
            print(f"HITL Review Required: Extreme BMI value ({result['anthropometrics']['bmi']}) requires specialized care.")
            return True
        
        # Trigger review for pediatric cases that passed validation but need specialized attention
        if args["patientProfile"]["age"] < 21 and args["patientProfile"]["age"] >= 18:
            print(f"HITL Review Required: Young adult (age {args['patientProfile']['age']}) may require growth consideration.")
            return True
        
        return False


# Implement Meal Plan Generator Tool (simplified version)
class MealPlanGeneratorTool(StandardsCompliantMCPTool):
    """MCP-compliant tool for meal plan generation."""
    
    def __init__(self):
        """Initialize the meal plan generator tool."""
        super().__init__(
            name="meal_plan_generator",
            description="Creates personalized, nutritionally balanced meal plans based on dietary goals, restrictions, and preferences, with optional shopping lists.",
            schema_model=MealPlanGenerator,
            supported_standards=[
                "DIETARY_REFERENCE_INTAKES",
                "FOOD_SAFETY_STANDARDS",
                "MEDICAL_NUTRITION_THERAPY",
                "NUTRITION_LABELING_STANDARDS"
            ],
            domain="Nutrition and Dietetics",
            tool_metadata={
                "title": "Meal Plan Generator Tool",
                "readOnlyHint": True,
                "destructiveHint": False,
                "idempotentHint": False,  # Same inputs may generate different meal plans for variety
                "openWorldHint": False,
            }
        )
    
    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the meal plan generation.
        
        Args:
            args: Tool arguments
            
        Returns:
            Meal plan result
        """
        # This would be a complex implementation involving recipe databases,
        # nutrient composition tables, and meal planning algorithms
        # Here we'll create a simplified example
        
        nutritional_goals = args["nutritionalGoals"]
        dietary_patterns = args["dietaryPatterns"]
        medical_considerations = args.get("medicalConsiderations", {"conditions": []})
        planning_parameters = args["planningParameters"]
        
        # Determine calorie distribution for meals if not specified
        calorie_distribution = dietary_patterns.get("calorieDistribution", {
            "breakfast": 25,
            "lunch": 30,
            "dinner": 35,
            "snacks": 10
        })
        
        # Normalize distribution to 100%
        total_distribution = sum([val or 0 for val in calorie_distribution.values()])
        if total_distribution != 100:
            factor = 100 / total_distribution
            for key in calorie_distribution:
                calorie_distribution[key] = calorie_distribution[key] * factor
        
        # Simplified meal plan generation
        meal_plan = []
        days_to_generate = planning_parameters["durationDays"]
        
        # Sample recipe database (simplified)
        breakfast_options = [
            {
                "name": "Overnight Oats with Berries",
                "dietaryTags": ["vegetarian"],
                "nutritionPerServing": {
                    "calories": 350,
                    "protein": 12,
                    "carbohydrates": 60,
                    "fat": 8,
                    "fiber": 8
                },
                "baseIngredients": [
                    {"name": "rolled oats", "amount": 50, "unit": "g"},
                    {"name": "milk", "amount": 125, "unit": "ml"},
                    {"name": "yogurt", "amount": 50, "unit": "g"},
                    {"name": "berries", "amount": 75, "unit": "g"},
                    {"name": "chia seeds", "amount": 10, "unit": "g"}
                ],
                "preparationMethod": "Combine oats, milk, yogurt, and chia seeds in a jar. Refrigerate overnight. Top with berries before serving.",
                "preparationTime": 10
            },
            {
                "name": "Vegetable Omelette",
                "dietaryTags": ["gluten-free"],
                "nutritionPerServing": {
                    "calories": 320,
                    "protein": 20,
                    "carbohydrates": 8,
                    "fat": 22,
                    "fiber": 3
                },
                "baseIngredients": [
                    {"name": "eggs", "amount": 3, "unit": "whole"},
                    {"name": "bell pepper", "amount": 50, "unit": "g"},
                    {"name": "spinach", "amount": 30, "unit": "g"},
                    {"name": "mushrooms", "amount": 50, "unit": "g"},
                    {"name": "olive oil", "amount": 10, "unit": "ml"}
                ],
                "preparationMethod": "Whisk eggs. Sauté vegetables in olive oil until soft. Add eggs and cook until set.",
                "preparationTime": 15
            }
        ]
        
        lunch_options = [
            {
                "name": "Quinoa Salad Bowl",
                "dietaryTags": ["vegetarian", "gluten-free"],
                "nutritionPerServing": {
                    "calories": 420,
                    "protein": 15,
                    "carbohydrates": 65,
                    "fat": 12,
                    "fiber": 10
                },
                "baseIngredients": [
                    {"name": "cooked quinoa", "amount": 100, "unit": "g"},
                    {"name": "mixed vegetables", "amount": 150, "unit": "g"},
                    {"name": "chickpeas", "amount": 75, "unit": "g"},
                    {"name": "feta cheese", "amount": 30, "unit": "g"},
                    {"name": "olive oil dressing", "amount": 15, "unit": "ml"}
                ],
                "preparationMethod": "Combine cooked quinoa with vegetables and chickpeas. Top with crumbled feta and drizzle with dressing.",
                "preparationTime": 20
            },
            {
                "name": "Turkey and Avocado Wrap",
                "dietaryTags": [],
                "nutritionPerServing": {
                    "calories": 450,
                    "protein": 25,
                    "carbohydrates": 40,
                    "fat": 20,
                    "fiber": 8
                },
                "baseIngredients": [
                    {"name": "whole wheat wrap", "amount": 1, "unit": "piece"},
                    {"name": "turkey breast", "amount": 100, "unit": "g"},
                    {"name": "avocado", "amount": 50, "unit": "g"},
                    {"name": "mixed greens", "amount": 30, "unit": "g"},
                    {"name": "tomato", "amount": 50, "unit": "g"}
                ],
                "preparationMethod": "Layer ingredients on wrap. Roll tightly and slice in half.",
                "preparationTime": 10
            }
        ]
        
        dinner_options = [
            {
                "name": "Baked Salmon with Roasted Vegetables",
                "dietaryTags": ["gluten-free", "dairy-free"],
                "nutritionPerServing": {
                    "calories": 480,
                    "protein": 35,
                    "carbohydrates": 30,
                    "fat": 22,
                    "fiber": 6
                },
                "baseIngredients": [
                    {"name": "salmon fillet", "amount": 150, "unit": "g"},
                    {"name": "mixed vegetables", "amount": 200, "unit": "g"},
                    {"name": "olive oil", "amount": 15, "unit": "ml"},
                    {"name": "lemon", "amount": 0.5, "unit": "whole"},
                    {"name": "herbs", "amount": 5, "unit": "g"}
                ],
                "preparationMethod": "Season salmon and place on baking sheet with vegetables. Drizzle with oil and bake at 400°F for 20 minutes.",
                "preparationTime": 30
            },
            {
                "name": "Vegetable and Bean Chili",
                "dietaryTags": ["vegetarian", "vegan", "gluten-free"],
                "nutritionPerServing": {
                    "calories": 380,
                    "protein": 18,
                    "carbohydrates": 60,
                    "fat": 8,
                    "fiber": 16
                },
                "baseIngredients": [
                    {"name": "kidney beans", "amount": 100, "unit": "g"},
                    {"name": "black beans", "amount": 100, "unit": "g"},
                    {"name": "tomatoes", "amount": 200, "unit": "g"},
                    {"name": "bell peppers", "amount": 100, "unit": "g"},
                    {"name": "onion", "amount": 50, "unit": "g"}
                ],
                "preparationMethod": "Sauté onions and peppers. Add tomatoes, beans, and seasonings. Simmer for 25 minutes.",
                "preparationTime": 40
            }
        ]
        
        snack_options = [
            {
                "name": "Greek Yogurt with Honey",
                "dietaryTags": ["vegetarian", "gluten-free"],
                "nutritionPerServing": {
                    "calories": 150,
                    "protein": 15,
                    "carbohydrates": 12,
                    "fat": 4,
                    "fiber": 0
                },
                "baseIngredients": [
                    {"name": "Greek yogurt", "amount": 150, "unit": "g"},
                    {"name": "honey", "amount": 10, "unit": "g"}
                ],
                "preparationMethod": "Top yogurt with honey.",
                "preparationTime": 2
            },
            {
                "name": "Apple with Almond Butter",
                "dietaryTags": ["vegetarian", "vegan", "gluten-free", "dairy-free"],
                "nutritionPerServing": {
                    "calories": 200,
                    "protein": 5,
                    "carbohydrates": 25,
                    "fat": 10,
                    "fiber": 5
                },
                "baseIngredients": [
                    {"name": "apple", "amount": 1, "unit": "medium"},
                    {"name": "almond butter", "amount": 20, "unit": "g"}
                ],
                "preparationMethod": "Slice apple and serve with almond butter for dipping.",
                "preparationTime": 3
            }
        ]
        
        # Generate meal plan for each day
        for day in range(1, days_to_generate + 1):
            daily_plan = {
                "day": day,
                "totalNutrition": {
                    "calories": 0,
                    "protein": 0,
                    "carbohydrates": 0,
                    "fat": 0,
                    "fiber": 0
                },
                "meals": []
            }
            
            # Calculate meal types based on frequency
            meal_types = ["breakfast", "lunch", "dinner"]
            snack_count = dietary_patterns["mealFrequency"] - 3
            for i in range(snack_count):
                meal_types.append(f"snack{i+1}")
            
            # Select recipes for each meal
            # Breakfast
            breakfast_calories = nutritional_goals["caloricTarget"] * (calorie_distribution.get("breakfast", 25) / 100)
            breakfast_recipe = breakfast_options[day % len(breakfast_options)]
            breakfast_portions = breakfast_calories / breakfast_recipe["nutritionPerServing"]["calories"]
            
            breakfast = {
                "mealType": "breakfast",
                "recipes": [{
                    **breakfast_recipe,
                    "portions": round(breakfast_portions, 2),
                    "ingredients": [
                        {
                            **ingredient,
                            "amount": round(ingredient["amount"] * breakfast_portions, 1)
                        } for ingredient in breakfast_recipe["baseIngredients"]
                    ],
                    "dietaryNotes": breakfast_recipe["dietaryTags"]
                }]
            }
            
            daily_plan["totalNutrition"]["calories"] += breakfast_recipe["nutritionPerServing"]["calories"] * breakfast_portions
            daily_plan["totalNutrition"]["protein"] += breakfast_recipe["nutritionPerServing"]["protein"] * breakfast_portions
            daily_plan["totalNutrition"]["carbohydrates"] += breakfast_recipe["nutritionPerServing"]["carbohydrates"] * breakfast_portions
            daily_plan["totalNutrition"]["fat"] += breakfast_recipe["nutritionPerServing"]["fat"] * breakfast_portions
            daily_plan["totalNutrition"]["fiber"] += breakfast_recipe["nutritionPerServing"]["fiber"] * breakfast_portions
            
            daily_plan["meals"].append(breakfast)
            
            # Lunch
            lunch_calories = nutritional_goals["caloricTarget"] * (calorie_distribution.get("lunch", 30) / 100)
            lunch_recipe = lunch_options[(day + 1) % len(lunch_options)]
            lunch_portions = lunch_calories / lunch_recipe["nutritionPerServing"]["calories"]
            
            lunch = {
                "mealType": "lunch",
                "recipes": [{
                    **lunch_recipe,
                    "portions": round(lunch_portions, 2),
                    "ingredients": [
                        {
                            **ingredient,
                            "amount": round(ingredient["amount"] * lunch_portions, 1)
                        } for ingredient in lunch_recipe["baseIngredients"]
                    ],
                    "dietaryNotes": lunch_recipe["dietaryTags"]
                }]
            }
            
            daily_plan["totalNutrition"]["calories"] += lunch_recipe["nutritionPerServing"]["calories"] * lunch_portions
            daily_plan["totalNutrition"]["protein"] += lunch_recipe["nutritionPerServing"]["protein"] * lunch_portions
            daily_plan["totalNutrition"]["carbohydrates"] += lunch_recipe["nutritionPerServing"]["carbohydrates"] * lunch_portions
            daily_plan["totalNutrition"]["fat"] += lunch_recipe["nutritionPerServing"]["fat"] * lunch_portions
            daily_plan["totalNutrition"]["fiber"] += lunch_recipe["nutritionPerServing"]["fiber"] * lunch_portions
            
            daily_plan["meals"].append(lunch)
            
            # Dinner
            dinner_calories = nutritional_goals["caloricTarget"] * (calorie_distribution.get("dinner", 35) / 100)
            dinner_recipe = dinner_options[(day + 2) % len(dinner_options)]
            dinner_portions = dinner_calories / dinner_recipe["nutritionPerServing"]["calories"]
            
            dinner = {
                "mealType": "dinner",
                "recipes": [{
                    **dinner_recipe,
                    "portions": round(dinner_portions, 2),
                    "ingredients": [
                        {
                            **ingredient,
                            "amount": round(ingredient["amount"] * dinner_portions, 1)
                        } for ingredient in dinner_recipe["baseIngredients"]
                    ],
                    "dietaryNotes": dinner_recipe["dietaryTags"]
                }]
            }
            
            daily_plan["totalNutrition"]["calories"] += dinner_recipe["nutritionPerServing"]["calories"] * dinner_portions
            daily_plan["totalNutrition"]["protein"] += dinner_recipe["nutritionPerServing"]["protein"] * dinner_portions
            daily_plan["totalNutrition"]["carbohydrates"] += dinner_recipe["nutritionPerServing"]["carbohydrates"] * dinner_portions
            daily_plan["totalNutrition"]["fat"] += dinner_recipe["nutritionPerServing"]["fat"] * dinner_portions
            daily_plan["totalNutrition"]["fiber"] += dinner_recipe["nutritionPerServing"]["fiber"] * dinner_portions
            
            daily_plan["meals"].append(dinner)
            
            # Snacks if needed
            remaining_snack_calories = nutritional_goals["caloricTarget"] * (calorie_distribution.get("snacks", 10) / 100)
            for snack_num in range(1, snack_count + 1):
                snack_calories = remaining_snack_calories / (snack_count - (snack_num - 1))
                snack_recipe = snack_options[(day + snack_num) % len(snack_options)]
                snack_portions = snack_calories / snack_recipe["nutritionPerServing"]["calories"]
                
                snack = {
                    "mealType": f"snack{snack_num}",
                    "recipes": [{
                        **snack_recipe,
                        "portions": round(snack_portions, 2),
                        "ingredients": [
                            {
                                **ingredient,
                                "amount": round(ingredient["amount"] * snack_portions, 1)
                            } for ingredient in snack_recipe["baseIngredients"]
                        ],
                        "dietaryNotes": snack_recipe["dietaryTags"]
                    }]
                }
                
                daily_plan["totalNutrition"]["calories"] += snack_recipe["nutritionPerServing"]["calories"] * snack_portions
                daily_plan["totalNutrition"]["protein"] += snack_recipe["nutritionPerServing"]["protein"] * snack_portions
                daily_plan["totalNutrition"]["carbohydrates"] += snack_recipe["nutritionPerServing"]["carbohydrates"] * snack_portions
                daily_plan["totalNutrition"]["fat"] += snack_recipe["nutritionPerServing"]["fat"] * snack_portions
                daily_plan["totalNutrition"]["fiber"] += snack_recipe["nutritionPerServing"]["fiber"] * snack_portions
                
                daily_plan["meals"].append(snack)
                remaining_snack_calories -= snack_calories
            
            # Round nutritional values
            daily_plan["totalNutrition"]["calories"] = round(daily_plan["totalNutrition"]["calories"])
            daily_plan["totalNutrition"]["protein"] = round(daily_plan["totalNutrition"]["protein"])
            daily_plan["totalNutrition"]["carbohydrates"] = round(daily_plan["totalNutrition"]["carbohydrates"])
            daily_plan["totalNutrition"]["fat"] = round(daily_plan["totalNutrition"]["fat"])
            daily_plan["totalNutrition"]["fiber"] = round(daily_plan["totalNutrition"]["fiber"])
            
            meal_plan.append(daily_plan)
        
        # Calculate average nutritional values across the plan
        total_nutrition = {
            "calories": 0,
            "protein": 0,
            "carbohydrates": 0,
            "fat": 0,
            "fiber": 0
        }
        
        for day in meal_plan:
            total_nutrition["calories"] += day["totalNutrition"]["calories"]
            total_nutrition["protein"] += day["totalNutrition"]["protein"]
            total_nutrition["carbohydrates"] += day["totalNutrition"]["carbohydrates"]
            total_nutrition["fat"] += day["totalNutrition"]["fat"]
            total_nutrition["fiber"] += day["totalNutrition"]["fiber"]
        
        avg_calories = total_nutrition["calories"] / days_to_generate
        avg_protein = total_nutrition["protein"] / days_to_generate
        avg_carbs = total_nutrition["carbohydrates"] / days_to_generate
        avg_fat = total_nutrition["fat"] / days_to_generate
        avg_fiber = total_nutrition["fiber"] / days_to_generate
        
        # Calculate percentages
        avg_protein_calories = avg_protein * 4
        avg_carb_calories = avg_carbs * 4
        avg_fat_calories = avg_fat * 9
        
        protein_percentage = (avg_protein_calories / avg_calories) * 100
        carb_percentage = (avg_carb_calories / avg_calories) * 100
        fat_percentage = (avg_fat_calories / avg_calories) * 100
        
        # Calculate adherence to targets
        calorie_adherence = (avg_calories / nutritional_goals["caloricTarget"]) * 100
        protein_adherence = (avg_protein / nutritional_goals["proteinGrams"]) * 100
        carb_adherence = (avg_carbs / nutritional_goals["carbGrams"]) * 100
        fat_adherence = (avg_fat / nutritional_goals["fatGrams"]) * 100
        fiber_adherence = None
        if nutritional_goals.get("fiberGrams"):
            fiber_adherence = (avg_fiber / nutritional_goals["fiberGrams"]) * 100
        
        # Generate shopping list if requested
        shopping_list = None
        if planning_parameters["includeShopping"]:
            # Collect all ingredients from all recipes
            all_ingredients = {}
            
            for day in meal_plan:
                for meal in day["meals"]:
                    for recipe in meal["recipes"]:
                        for ingredient in recipe["ingredients"]:
                            if ingredient["name"] not in all_ingredients:
                                all_ingredients[ingredient["name"]] = {
                                    "amount": 0,
                                    "unit": ingredient["unit"]
                                }
                            
                            all_ingredients[ingredient["name"]]["amount"] += ingredient["amount"]
            
            # Categorize ingredients
            categorized_ingredients = {
                "Produce": [],
                "Protein": [],
                "Dairy": [],
                "Grains": [],
                "Pantry": [],
                "Other": []
            }
            
            # Simple categorization logic
            produce_items = ["apple", "berries", "bell pepper", "spinach", "mushrooms", "vegetables", "tomato", "lemon", "avocado", "onion", "mixed greens", "tomatoes"]
            protein_items = ["eggs", "turkey breast", "salmon fillet", "chicken", "beef", "beans", "kidney beans", "black beans", "chickpeas"]
            dairy_items = ["milk", "yogurt", "Greek yogurt", "cheese", "feta cheese"]
            grain_items = ["rolled oats", "quinoa", "wrap", "whole wheat", "bread", "rice", "couscous"]
            pantry_items = ["olive oil", "oil", "chia seeds", "almond butter", "honey", "herbs", "spices"]
            
            for name, details in all_ingredients.items():
                ingredient = {
                    "ingredient": name,
                    "amount": round(details["amount"], 1),
                    "unit": details["unit"]
                }
                
                if any(item in name for item in produce_items):
                    categorized_ingredients["Produce"].append(ingredient)
                elif any(item in name for item in protein_items):
                    categorized_ingredients["Protein"].append(ingredient)
                elif any(item in name for item in dairy_items):
                    categorized_ingredients["Dairy"].append(ingredient)
                elif any(item in name for item in grain_items):
                    categorized_ingredients["Grains"].append(ingredient)
                elif any(item in name for item in pantry_items):
                    categorized_ingredients["Pantry"].append(ingredient)
                else:
                    categorized_ingredients["Other"].append(ingredient)
            
            # Remove empty categories
            for category in list(categorized_ingredients.keys()):
                if not categorized_ingredients[category]:
                    del categorized_ingredients[category]
            
            # Add meal prep tips
            meal_prep_tips = [
                "Batch cook grains like quinoa and rice at the beginning of the week",
                "Pre-chop vegetables and store in airtight containers",
                "Prepare marinades ahead of time and freeze with proteins",
                "Make overnight oats in batches for several days"
            ]
            
            # Add storage suggestions
            storage_suggestions = [
                "Store leafy greens with a paper towel to absorb moisture",
                "Keep berries unwashed until ready to use",
                "Store herbs upright in a glass of water",
                "Keep cooked meals in the refrigerator for 3-4 days maximum"
            ]
            
            shopping_list = {
                "categorized": categorized_ingredients,
                "mealPrepTips": meal_prep_tips,
                "storageSuggestions": storage_suggestions
            }
        
        # Generate adherence strategies based on meal plan characteristics
        adherence_strategies = [
            "Prep breakfasts in advance for busy mornings",
            "Pack lunches the night before to avoid last-minute decisions",
            "Keep healthy snacks accessible for hunger between meals",
            "Use portion control containers to maintain serving sizes"
        ]
        
        # Generate customization suggestions
        customizations = [
            "Adjust spice levels based on personal preference",
            "Substitute alternative proteins if desired (tofu for chicken, etc.)",
            "Add extra vegetables to any meal for additional nutrients",
            "Modify cooking methods based on available equipment (grill vs. bake)"
        ]
        
        # Compile final result
        result = {
            "nutritionalSummary": {
                "averageDailyCalories": round(avg_calories),
                "macronutrientBreakdown": {
                    "protein": {
                        "grams": round(avg_protein),
                        "percentage": round(protein_percentage)
                    },
                    "carbohydrates": {
                        "grams": round(avg_carbs),
                        "percentage": round(carb_percentage)
                    },
                    "fat": {
                        "grams": round(avg_fat),
                        "percentage": round(fat_percentage)
                    },
                    "fiber": {
                        "grams": round(avg_fiber)
                    }
                },
                "adherenceToTarget": {
                    "calories": round(calorie_adherence),
                    "protein": round(protein_adherence),
                    "carbohydrates": round(carb_adherence),
                    "fat": round(fat_adherence)
                }
            },
            "mealPlan": meal_plan,
            "adherenceStrategies": adherence_strategies,
            "customizations": customizations
        }
        
        if fiber_adherence is not None:
            result["nutritionalSummary"]["adherenceToTarget"]["fiber"] = round(fiber_adherence)
        
        if shopping_list:
            result["shoppingList"] = shopping_list
        
        return result
    
    def formatResult(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format the meal plan results for display.
        
        Args:
            result: Meal plan result
            
        Returns:
            Formatted result
        """
        text_summary = f"""
**Meal Plan Summary**

**Nutritional Overview**
- Average Daily Calories: {result["nutritionalSummary"]["averageDailyCalories"]} kcal
- Macronutrient Breakdown: 
  - Protein: {result["nutritionalSummary"]["macronutrientBreakdown"]["protein"]["grams"]}g ({result["nutritionalSummary"]["macronutrientBreakdown"]["protein"]["percentage"]}%)
  - Carbohydrates: {result["nutritionalSummary"]["macronutrientBreakdown"]["carbohydrates"]["grams"]}g ({result["nutritionalSummary"]["macronutrientBreakdown"]["carbohydrates"]["percentage"]}%)
  - Fat: {result["nutritionalSummary"]["macronutrientBreakdown"]["fat"]["grams"]}g ({result["nutritionalSummary"]["macronutrientBreakdown"]["fat"]["percentage"]}%)
  - Fiber: {result["nutritionalSummary"]["macronutrientBreakdown"]["fiber"]["grams"]}g

**Plan Overview**
- Duration: {len(result["mealPlan"])} days
- Meals per day: {len(result["mealPlan"][0]["meals"])}
- Total recipes: {sum(len(day["meals"]) for day in result["mealPlan"])}

**Key Adherence Strategies**
{chr(10).join([f"- {strategy}" for strategy in result["adherenceStrategies"][:2]])}

*Full meal plan with recipes, shopping list, and preparation instructions available in the structured data.*
        """.strip()
        
        return [
            {"type": "data", "data": result},
            {"type": "text", "text": text_summary},
        ]
    
    def validateInput(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the input arguments.
        
        Args:
            args: Tool arguments
            
        Returns:
            Validation result with issues if any
        """
        issues = []
        
        # Check if calorie distribution adds up to approximately 100%
        if "calorieDistribution" in args["dietaryPatterns"]:
            total_distribution = sum([val or 0 for val in args["dietaryPatterns"]["calorieDistribution"].values()])
            
            if total_distribution < 95 or total_distribution > 105:
                issues.append({
                    "path": "dietaryPatterns.calorieDistribution",
                    "message": f"Calorie distribution should total approximately 100%, currently totals {round(total_distribution, 1)}%",
                    "severity": "warning",
                    "standardReference": "NUTRITION_PLANNING_STANDARDS",
                })
        
        # Check if macronutrient calorie distribution is reasonable
        protein_calories = args["nutritionalGoals"]["proteinGrams"] * 4
        carb_calories = args["nutritionalGoals"]["carbGrams"] * 4
        fat_calories = args["nutritionalGoals"]["fatGrams"] * 9
        total_calories_from_macros = protein_calories + carb_calories + fat_calories
        
        if abs(total_calories_from_macros - args["nutritionalGoals"]["caloricTarget"]) > args["nutritionalGoals"]["caloricTarget"] * 0.1:
            issues.append({
                "path": "nutritionalGoals",
                "message": f"Total calories from macronutrients ({round(total_calories_from_macros)}) differs by >10% from caloric target ({args['nutritionalGoals']['caloricTarget']})",
                "severity": "warning",
                "standardReference": "DIETARY_REFERENCE_INTAKES",
            })
        
        # Check if planning for too many days
        if args["planningParameters"]["durationDays"] > 7 and args["planningParameters"]["complexity"] == "complex":
            issues.append({
                "path": "planningParameters",
                "message": "Complex meal plans extending beyond 7 days may be challenging to adhere to",
                "severity": "warning",
                "standardReference": "NUTRITION_BEHAVIOR_GUIDELINES",
            })
        
        # Check for potentially problematic dietary restrictions
        if args["dietaryPatterns"].get("dietaryRestrictions") and len(args["dietaryPatterns"]["dietaryRestrictions"]) > 3:
            issues.append({
                "path": "dietaryPatterns.dietaryRestrictions",
                "message": "Multiple dietary restrictions may significantly limit food variety and nutritional adequacy",
                "severity": "warning",
                "standardReference": "NUTRITIONAL_ADEQUACY_STANDARDS",
            })
        
        return {
            "valid": not any(issue["severity"] == "error" for issue in issues),
            "issues": issues,
        }
    
    def requiresHumanReview(self, args: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Determine if human review is required.
        
        Args:
            args: Tool arguments
            result: Tool result
            
        Returns:
            Boolean indicating if human review is required
        """
        # Trigger review for complex medical conditions
        if args.get("medicalConsiderations", {}).get("conditions") and any(
            condition.lower() in ["kidney disease", "liver disease", "cancer", "cystic fibrosis", "eating disorder"]
            for condition in args["medicalConsiderations"]["conditions"]
        ):
            print("HITL Review Required: Meal plan for complex medical condition(s) requires specialist review.")
            return True
        
        # Trigger review for extreme caloric needs
        if args["nutritionalGoals"]["caloricTarget"] < 1200 or args["nutritionalGoals"]["caloricTarget"] > 3500:
            print(f"HITL Review Required: Extreme caloric target ({args['nutritionalGoals']['caloricTarget']} kcal) needs verification.")
            return True
        
        # Trigger review for poor adherence to targets
        calorie_adherence = result["nutritionalSummary"]["adherenceToTarget"]["calories"]
        if calorie_adherence < 85 or calorie_adherence > 115:
            print(f"HITL Review Required: Poor adherence to caloric target ({calorie_adherence:.1f}%) suggests planning challenges.")
            return True
        
        return False


# Implement Dietary Analysis Tool (placeholder implementation)
class DietaryAnalysisTool(StandardsCompliantMCPTool):
    """MCP-compliant tool for dietary analysis."""
    
    def __init__(self):
        """Initialize the dietary analysis tool."""
        super().__init__(
            name="dietary_analysis",
            description="Analyzes dietary patterns and food journals to identify nutritional adequacy, deficiencies, and opportunities for improvement.",
            schema_model=DietaryAnalysis,
            supported_standards=[
                "DIETARY_REFERENCE_INTAKES",
                "NUTRITION_ASSESSMENT_STANDARDS"
            ],
            domain="Nutrition and Dietetics",
            tool_metadata={
                "title": "Dietary Analysis Tool",
                "readOnlyHint": True,
                "destructiveHint": False,
                "idempotentHint": True,
                "openWorldHint": False,
            }
        )
    
    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the dietary analysis.
        
        Args:
            args: Tool arguments
            
        Returns:
            Dietary analysis result
        """
        # Placeholder implementation
        return {
            "message": "This is a placeholder for the Dietary Analysis Tool implementation. In a full implementation, this would analyze food journals and dietary patterns."
        }
    
    def formatResult(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format the dietary analysis results for display.
        
        Args:
            result: Dietary analysis result
            
        Returns:
            Formatted result
        """
        return [
            {"type": "data", "data": result},
            {"type": "text", "text": "Dietary analysis would be provided here in a full implementation."},
        ]


def register_nutrition_tools() -> List[str]:
    """Register all nutrition tools and return their names.
    
    Returns:
        List of registered tool names
    """
    # In a production environment, this would register the tools with a tool registry
    tools = [
        NutritionalAssessmentTool(),
        MealPlanGeneratorTool(),
        DietaryAnalysisTool(),
    ]
    
    return [tool.name for tool in tools]