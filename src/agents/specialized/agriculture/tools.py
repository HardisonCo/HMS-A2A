"""
Agriculture Tools

This module provides MCP-compliant tools for agriculture professionals.
"""

from typing import Dict, Any, List, Optional, Type, Union
from pydantic import BaseModel, Field
from enum import Enum
import json
import re

# Import the base MCP tool class
from specialized_agents.collaboration.mcp_tool import StandardsCompliantMCPTool
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
            domain: Industry domain (e.g., "Agriculture")
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


# Schema definitions for agriculture tools
class SoilSample(BaseModel):
    """Schema for soil sample analysis."""
    soilSampleLocation: str = Field(description="Location where the soil sample was collected")
    cropType: Optional[str] = Field(None, description="Type of crop intended for planting")
    previousCrops: Optional[List[str]] = Field(None, description="Previous crops planted in this soil")
    testingParameters: Optional[List[str]] = Field(None, description="Specific parameters to test for")


class SoilHealth(BaseModel):
    """Schema for soil health information."""
    pH: float
    nutrientLevels: Dict[str, Dict[str, Union[float, str]]]
    organicMatter: Dict[str, Union[float, str]]
    texture: str
    drainageAssessment: str


class SoilRecommendations(BaseModel):
    """Schema for soil management recommendations."""
    fertilization: List[str]
    amendments: List[str]
    cropSuitability: List[str]
    sustainablePractices: List[str]


class SoilComplianceNotes(BaseModel):
    """Schema for soil compliance notes."""
    organicFarming: Optional[bool] = None
    regulatoryConsiderations: List[str]


class SoilAnalysisResult(BaseModel):
    """Schema for complete soil analysis result."""
    soilHealth: SoilHealth
    recommendations: SoilRecommendations
    complianceNotes: SoilComplianceNotes


class FarmingSystem(str, Enum):
    """Farming system types."""
    CONVENTIONAL = "conventional"
    ORGANIC = "organic"
    INTEGRATED = "integrated"
    REGENERATIVE = "regenerative"
    PRECISION = "precision"


class CropManagement(BaseModel):
    """Schema for crop management."""
    cropType: str = Field(description="Type of crop to be managed")
    acreage: float = Field(description="Number of acres or hectares")
    location: str = Field(description="Geographic location for climate context")
    soilType: Optional[str] = Field(None, description="Type of soil in the field")
    farmingSystem: FarmingSystem = Field(description="The farming system being used")
    currentGrowthStage: Optional[str] = Field(None, description="Current growth stage of the crop")
    concerns: Optional[List[str]] = Field(None, description="Specific concerns or issues to address")


class CropIrrigation(BaseModel):
    """Schema for crop irrigation recommendations."""
    schedule: str
    methods: List[str]
    waterConservation: List[str]


class CropNutrition(BaseModel):
    """Schema for crop nutrition recommendations."""
    fertilizers: List[str]
    application: str
    timing: str


class CropPestManagement(BaseModel):
    """Schema for crop pest management recommendations."""
    monitoring: List[str]
    preventionMethods: List[str]
    treatment: List[str]


class CropRecommendations(BaseModel):
    """Schema for crop management recommendations."""
    planting: List[str]
    irrigation: CropIrrigation
    nutrition: CropNutrition
    pestManagement: CropPestManagement
    harvestTimeline: str


class CropManagementResult(BaseModel):
    """Schema for complete crop management result."""
    recommendations: CropRecommendations
    sustainabilityPractices: List[str]
    regulatoryConsiderations: List[str]
    expectedYield: str
    riskFactors: List[str]


class InfestationLevel(str, Enum):
    """Pest infestation severity levels."""
    LOW = "low"
    MODERATE = "moderate"
    SEVERE = "severe"


class WeatherConditions(BaseModel):
    """Schema for weather conditions."""
    temperature: Optional[float] = Field(None, description="Current temperature in Celsius or Fahrenheit")
    windSpeed: Optional[float] = Field(None, description="Wind speed in mph or km/h")
    precipitationForecast: Optional[bool] = Field(None, description="Whether precipitation is forecast in the next 24-48 hours")


class PesticideApplication(BaseModel):
    """Schema for pesticide application."""
    cropType: str = Field(description="Type of crop to be treated")
    pestType: str = Field(description="Type of pest being targeted")
    infestationLevel: InfestationLevel = Field(description="Severity of the infestation")
    fieldSize: float = Field(description="Size of the field in acres or hectares")
    proximityToWaterBodies: bool = Field(description="Whether the field is near water bodies")
    farmingSystem: FarmingSystem = Field(description="The farming system being used")
    weatherConditions: Optional[WeatherConditions] = Field(None, description="Current and forecasted weather conditions")


class PesticideTreatment(BaseModel):
    """Schema for pesticide treatment recommendations."""
    product: Optional[str] = None
    activeIngredient: Optional[str] = None
    applicationRate: str
    applicationMethod: str
    timing: str
    safetyInterval: str


class PesticideSafety(BaseModel):
    """Schema for pesticide safety protocols."""
    personalProtectiveEquipment: List[str]
    applicationPrecautions: List[str]
    reentryInterval: str
    environmentalSafeguards: List[str]


class PesticideRegulatory(BaseModel):
    """Schema for pesticide regulatory information."""
    registrationStatus: str
    restrictions: List[str]
    recordKeepingRequirements: List[str]


class PesticideIPM(BaseModel):
    """Schema for integrated pest management information."""
    preventionStrategies: List[str]
    monitoringApproach: str
    biologicalControls: List[str]


class PesticideApplicationResult(BaseModel):
    """Schema for complete pesticide application result."""
    recommendedTreatments: List[PesticideTreatment]
    alternativeMethods: List[str]
    safetyProtocols: PesticideSafety
    regulatoryInformation: PesticideRegulatory
    integratedPestManagement: PesticideIPM


# Implement the specific agriculture tools
class SoilAnalysisTool(StandardsCompliantMCPTool):
    """MCP-compliant tool for soil analysis and recommendation in agriculture."""
    
    def __init__(self):
        """Initialize the soil analysis tool."""
        super().__init__(
            name="soil_analysis",
            description="Analyzes soil samples and provides detailed nutrient, pH, and structure information with recommendations for soil management",
            schema_model=SoilSample,
            supported_standards=[
                "SUSTAINABLE_FARMING_PRACTICES",
                "ORGANIC_CERTIFICATION_REQUIREMENTS",
                "USDA_REGULATIONS"
            ],
            domain="Agriculture",
            tool_metadata={
                "title": "Soil Analysis Tool",
                "readOnlyHint": False,
                "destructiveHint": False,
                "idempotentHint": True,
                "openWorldHint": False
            }
        )
    
    async def execute(self, args: Dict[str, Any]) -> SoilAnalysisResult:
        """Execute the soil analysis and generate recommendations.
        
        Args:
            args: Tool arguments
            
        Returns:
            Soil analysis result
        """
        # In a real implementation, this would likely call out to a soil analysis service
        # or use stored data/models to generate recommendations based on soil parameters
        
        # Sample implementation
        crop_type = args.get("cropType", "most common crops")
        farming_system = args.get("farmingSystem", "conventional")
        is_organic = farming_system == "organic"
        
        return SoilAnalysisResult(
            soilHealth=SoilHealth(
                pH=6.8,
                nutrientLevels={
                    "nitrogen": {"value": 25, "unit": "ppm", "status": "optimal"},
                    "phosphorus": {"value": 15, "unit": "ppm", "status": "optimal"},
                    "potassium": {"value": 180, "unit": "ppm", "status": "optimal"},
                    "calcium": {"value": 1500, "unit": "ppm", "status": "optimal"},
                    "magnesium": {"value": 200, "unit": "ppm", "status": "optimal"},
                    "sulfur": {"value": 12, "unit": "ppm", "status": "deficient"}
                },
                organicMatter={
                    "percentage": 3.2,
                    "assessment": "Good organic matter content, supports soil biodiversity and water retention"
                },
                texture="Loam with good structure",
                drainageAssessment="Good drainage with moderate water retention capacity"
            ),
            recommendations=SoilRecommendations(
                fertilization=[
                    "Apply sulfur amendments to address deficiency",
                    "Maintain current nitrogen levels with cover crops or light application of composted manure",
                    "No immediate need for phosphorus or potassium amendments"
                ],
                amendments=[
                    "Consider adding gypsum to improve soil structure if compaction becomes an issue",
                    "Incorporate cover crops to maintain organic matter"
                ],
                cropSuitability=[
                    f"Soil well-suited for {crop_type}",
                    "Consider nitrogen-fixing cover crops in rotation"
                ],
                sustainablePractices=[
                    "Implement minimum tillage to preserve soil structure",
                    "Use cover crops during off-season to prevent erosion",
                    "Rotate crops to maintain soil health"
                ]
            ),
            complianceNotes=SoilComplianceNotes(
                organicFarming=is_organic,
                regulatoryConsiderations=[
                    "All recommended amendments comply with USDA regulations",
                    "Document all soil amendments applied for record-keeping requirements",
                    "Ensure all inputs meet organic certification requirements" if is_organic else "Standard USDA regulations apply to amendment applications"
                ]
            )
        )
    
    def formatResult(self, result: SoilAnalysisResult) -> List[Dict[str, Any]]:
        """Format the soil analysis results for display.
        
        Args:
            result: Soil analysis result
            
        Returns:
            Formatted result
        """
        return [
            {
                "type": "data",
                "data": result.model_dump()
            },
            {
                "type": "text",
                "text": f"""
Soil Analysis Results:
pH: {result.soilHealth.pH} - {"Acidic" if result.soilHealth.pH < 6.5 else ("Alkaline" if result.soilHealth.pH > 7.5 else "Neutral")}
Texture: {result.soilHealth.texture}
Drainage: {result.soilHealth.drainageAssessment}
Organic Matter: {result.soilHealth.organicMatter["percentage"]}% - {result.soilHealth.organicMatter["assessment"]}

Key Nutrient Findings:
{chr(10).join([f"- {nutrient.capitalize()}: {data['value']} {data['unit']} ({data['status']})" for nutrient, data in result.soilHealth.nutrientLevels.items()])}

Recommendations:
1. Fertilization:
{chr(10).join([f"   - {rec}" for rec in result.recommendations.fertilization])}

2. Soil Amendments:
{chr(10).join([f"   - {rec}" for rec in result.recommendations.amendments])}

3. Crop Suitability:
{chr(10).join([f"   - {rec}" for rec in result.recommendations.cropSuitability])}

4. Sustainable Practices:
{chr(10).join([f"   - {rec}" for rec in result.recommendations.sustainablePractices])}

Regulatory Considerations:
{chr(10).join([f"- {note}" for note in result.complianceNotes.regulatoryConsiderations])}
                """.strip()
            }
        ]
    
    def requiresHumanReview(self, args: Dict[str, Any], result: SoilAnalysisResult) -> bool:
        """Determine if the tool results require human review.
        
        Args:
            args: Tool arguments
            result: Tool execution result
            
        Returns:
            Boolean indicating if human review is required
        """
        # Require human review if:
        # 1. Multiple severe nutrient deficiencies or excesses exist
        # 2. pH is extremely acidic or alkaline
        
        deficient_nutrients = sum(1 for _, data in result.soilHealth.nutrientLevels.items() 
                                 if data["status"] == "deficient")
        
        excessive_nutrients = sum(1 for _, data in result.soilHealth.nutrientLevels.items() 
                                 if data["status"] == "excessive")
        
        extreme_pH = result.soilHealth.pH < 5.0 or result.soilHealth.pH > 8.5
        
        return (deficient_nutrients > 2) or (excessive_nutrients > 2) or extreme_pH


class CropManagementTool(StandardsCompliantMCPTool):
    """MCP-compliant tool for crop management recommendations."""
    
    def __init__(self):
        """Initialize the crop management tool."""
        super().__init__(
            name="crop_management",
            description="Provides comprehensive crop management recommendations including planting, irrigation, nutrition, pest management, and harvest planning",
            schema_model=CropManagement,
            supported_standards=[
                "SUSTAINABLE_FARMING_PRACTICES",
                "FOOD_SAFETY_REGULATIONS",
                "AGRICULTURAL_SAFETY_STANDARDS",
                "ORGANIC_CERTIFICATION_REQUIREMENTS",
                "USDA_REGULATIONS"
            ],
            domain="Agriculture",
            tool_metadata={
                "title": "Crop Management Tool",
                "readOnlyHint": False,
                "destructiveHint": False,
                "idempotentHint": False,
                "openWorldHint": False
            }
        )
    
    async def execute(self, args: Dict[str, Any]) -> CropManagementResult:
        """Execute the crop management tool and generate recommendations.
        
        Args:
            args: Tool arguments
            
        Returns:
            Crop management result
        """
        # In a real implementation, this would use crop databases, regional models,
        # and weather data to generate customized recommendations
        
        crop_type = args["cropType"]
        is_organic = args["farmingSystem"] == "organic"
        
        # Sample implementation
        return CropManagementResult(
            recommendations=CropRecommendations(
                planting=[
                    f"{crop_type} should be planted at a spacing of [appropriate spacing] with {'organic' if is_organic else 'treated'} seeds",
                    "Plant when soil temperature reaches [optimal temperature] and after last frost date",
                    "Consider [companion plants] to enhance growth and reduce pest pressure"
                ],
                irrigation=CropIrrigation(
                    schedule="Irrigate based on growth stage needs and soil moisture monitoring",
                    methods=[
                        "Drip irrigation recommended for water efficiency",
                        "Apply water at crop root zone to minimize waste and disease"
                    ],
                    waterConservation=[
                        "Use soil moisture sensors to optimize irrigation timing",
                        "Apply mulch to reduce evaporation",
                        "Consider rainwater harvesting where permitted by local regulations"
                    ]
                ),
                nutrition=CropNutrition(
                    fertilizers=(
                        ["Compost", "Composted manure", "Approved organic fertilizers"] if is_organic 
                        else ["Balanced NPK fertilizer", "Micronutrient supplements as needed"]
                    ),
                    application="Split application recommended to match crop growth stages",
                    timing="Apply main fertilizer before planting, with scheduled supplements during key growth phases"
                ),
                pestManagement=CropPestManagement(
                    monitoring=[
                        "Implement weekly scouting for early pest detection",
                        "Use pheromone traps for monitoring specific pest populations",
                        "Track degree-days for prediction of pest emergence"
                    ],
                    preventionMethods=[
                        "Crop rotation to break pest cycles",
                        "Use resistant varieties when available",
                        "Maintain field sanitation by removing crop residues"
                    ],
                    treatment=(
                        [
                            "Beneficial insects for biological control",
                            "OMRI-listed organic pesticides when necessary",
                            "Physical barriers like row covers"
                        ] if is_organic else [
                            "Integrated Pest Management approach prioritizing least-toxic solutions",
                            "Targeted pesticide applications only when thresholds are exceeded",
                            "Rotate pesticide classes to prevent resistance"
                        ]
                    )
                ),
                harvestTimeline=f"{crop_type} typically ready for harvest approximately [timeframe] after planting"
            ),
            sustainabilityPractices=[
                "Implement cover cropping during off-season",
                "Minimize soil disturbance through reduced tillage",
                "Create habitat for beneficial insects and pollinators",
                "Use crop rotation to improve soil health and break pest cycles"
            ],
            regulatoryConsiderations=[
                "Maintain organic certification records of all inputs and practices" if is_organic else "Follow label instructions for all agricultural chemicals",
                "Document worker training for compliance with Agricultural Worker Protection Standards",
                "Maintain buffer zones near waterways",
                "Keep detailed application records for all treatments"
            ],
            expectedYield=f"For {crop_type} in your region with {args['farmingSystem']} methods, expected yield range: [yield range]",
            riskFactors=[
                "Weather extremes, particularly [regional weather concerns]",
                f"Common regional pests including [specific pests]",
                "Potential for nutrient leaching in sandy soils",
                "Market price volatility"
            ]
        )
    
    def formatResult(self, result: CropManagementResult) -> List[Dict[str, Any]]:
        """Format the crop management results for display.
        
        Args:
            result: Crop management result
            
        Returns:
            Formatted result
        """
        return [
            {
                "type": "data",
                "data": result.model_dump()
            },
            {
                "type": "text",
                "text": f"""
Crop Management Recommendations:

PLANTING:
{chr(10).join([f"- {rec}" for rec in result.recommendations.planting])}

IRRIGATION:
- Schedule: {result.recommendations.irrigation.schedule}
- Methods:
{chr(10).join([f"  * {method}" for method in result.recommendations.irrigation.methods])}
- Water Conservation:
{chr(10).join([f"  * {practice}" for practice in result.recommendations.irrigation.waterConservation])}

NUTRITION:
- Recommended fertilizers: {', '.join(result.recommendations.nutrition.fertilizers)}
- Application: {result.recommendations.nutrition.application}
- Timing: {result.recommendations.nutrition.timing}

PEST MANAGEMENT:
- Monitoring:
{chr(10).join([f"  * {strategy}" for strategy in result.recommendations.pestManagement.monitoring])}
- Prevention:
{chr(10).join([f"  * {method}" for method in result.recommendations.pestManagement.preventionMethods])}
- Treatment:
{chr(10).join([f"  * {treatment}" for treatment in result.recommendations.pestManagement.treatment])}

HARVEST TIMELINE:
{result.recommendations.harvestTimeline}

SUSTAINABILITY PRACTICES:
{chr(10).join([f"- {practice}" for practice in result.sustainabilityPractices])}

REGULATORY CONSIDERATIONS:
{chr(10).join([f"- {consideration}" for consideration in result.regulatoryConsiderations])}

EXPECTED YIELD:
{result.expectedYield}

RISK FACTORS TO MONITOR:
{chr(10).join([f"- {risk}" for risk in result.riskFactors])}
                """.strip()
            }
        ]
    
    def requiresHumanReview(self, args: Dict[str, Any], result: CropManagementResult) -> bool:
        """Determine if the tool results require human review.
        
        Args:
            args: Tool arguments
            result: Tool execution result
            
        Returns:
            Boolean indicating if human review is required
        """
        # Require human review for:
        # 1. Organic operations requiring stricter compliance
        # 2. Large acreage operations (higher risk)
        # 3. Crops with specific regulatory requirements
        
        high_risk_crops = ["cannabis", "hemp", "tobacco", "cotton"]
        large_operation = args["acreage"] > 100
        is_organic = args["farmingSystem"] == "organic"
        is_high_risk_crop = args["cropType"].lower() in high_risk_crops
        
        return (is_organic and large_operation) or is_high_risk_crop


class PesticideApplicationTool(StandardsCompliantMCPTool):
    """MCP-compliant tool for pesticide application guidance."""
    
    def __init__(self):
        """Initialize the pesticide application tool."""
        super().__init__(
            name="pesticide_application",
            description="Provides guidance on pesticide selection, application methods, safety protocols, and regulatory compliance for agricultural pest management",
            schema_model=PesticideApplication,
            supported_standards=[
                "PESTICIDE_USAGE_GUIDELINES",
                "AGRICULTURAL_SAFETY_STANDARDS",
                "FOOD_SAFETY_REGULATIONS",
                "SUSTAINABLE_FARMING_PRACTICES",
                "USDA_REGULATIONS"
            ],
            domain="Agriculture",
            tool_metadata={
                "title": "Pesticide Application Tool",
                "readOnlyHint": False,
                "destructiveHint": False,
                "idempotentHint": False,
                "openWorldHint": False
            }
        )
    
    async def execute(self, args: Dict[str, Any]) -> PesticideApplicationResult:
        """Execute the pesticide application tool and generate recommendations.
        
        Args:
            args: Tool arguments
            
        Returns:
            Pesticide application result
        """
        # In a real implementation, this would:
        # 1. Check pesticide databases for registered products
        # 2. Verify weather conditions for application safety
        # 3. Calculate appropriate application rates
        # 4. Determine safety intervals based on the crop and product
        
        is_organic = args["farmingSystem"] == "organic"
        is_near_water = args["proximityToWaterBodies"]
        
        # Sample implementation
        return PesticideApplicationResult(
            recommendedTreatments=[
                PesticideTreatment(
                    product="OMRI-listed botanical insecticide" if is_organic else "EPA-registered conventional pesticide",
                    activeIngredient="Pyrethrin" if is_organic else "Appropriate active ingredient for target pest",
                    applicationRate="Apply at labeled rate for organic production" if is_organic else "Apply at labeled rate based on crop stage and pest pressure",
                    applicationMethod="Fine mist foliar spray with proper droplet size" if is_organic else "Boom sprayer with calibrated nozzles",
                    timing="Apply in early morning or evening when bees are not active" if is_organic else "Apply when weather conditions minimize drift risk",
                    safetyInterval="Observe pre-harvest interval of [X] days per organic standards" if is_organic else "Observe pre-harvest interval of [X] days per product label"
                )
            ],
            alternativeMethods=[
                "Beneficial insects or biological controls",
                "Cultural practices including crop rotation",
                "Physical barriers such as row covers",
                "Trap crops to draw pests away from main crop"
            ],
            safetyProtocols=PesticideSafety(
                personalProtectiveEquipment=[
                    "Chemical-resistant gloves",
                    "Long-sleeved shirt and long pants",
                    "Protective eyewear",
                    "Respirator if required by product label",
                    "Chemical-resistant footwear"
                ],
                applicationPrecautions=[
                    "Calibrate equipment before application",
                    "Check wind conditions - do not apply if winds exceed 10 mph",
                    "Maintain buffer zones near sensitive areas",
                    "Establish extended buffer zones around water bodies" if is_near_water else "Standard buffer zones required",
                    "Notify workers of application and re-entry intervals"
                ],
                reentryInterval="Restrict field entry for [X] hours after application per label requirements",
                environmentalSafeguards=[
                    "Prevent drift to non-target areas",
                    "Dispose of containers properly according to label instructions",
                    "Clean equipment away from water sources",
                    "Monitor for environmental impacts post-application"
                ]
            ),
            regulatoryInformation=PesticideRegulatory(
                registrationStatus="All recommended products must be registered for use on target crop in your state",
                restrictions=[
                    "Follow all federal, state, and local regulations",
                    "Observe endangered species protections if applicable",
                    "Special restrictions apply for applications near water bodies" if is_near_water else "Standard application restrictions apply",
                    "Weather restrictions may limit application timing"
                ],
                recordKeepingRequirements=[
                    "Document application date, time, and weather conditions",
                    "Record product used, rate, and method of application",
                    "Maintain records for minimum of two years",
                    "Document applicator certification if restricted-use pesticides are used"
                ]
            ),
            integratedPestManagement=PesticideIPM(
                preventionStrategies=[
                    "Crop rotation to break pest cycles",
                    "Resistant varieties when available",
                    "Proper spacing and air circulation",
                    "Field sanitation practices"
                ],
                monitoringApproach="Regular scouting to establish economic threshold before treatment",
                biologicalControls=[
                    "Predatory insects",
                    "Microbial treatments",
                    "Conservation of natural enemies"
                ]
            )
        )
    
    def formatResult(self, result: PesticideApplicationResult) -> List[Dict[str, Any]]:
        """Format the pesticide application results for display.
        
        Args:
            result: Pesticide application result
            
        Returns:
            Formatted result
        """
        return [
            {
                "type": "data",
                "data": result.model_dump()
            },
            {
                "type": "text",
                "text": f"""
Pesticide Application Guidance:

RECOMMENDED TREATMENTS:
{chr(10).join([f"""
- Product: {treatment.product or 'Based on local availability'}
- Active Ingredient: {treatment.activeIngredient or 'Select based on target pest'}
- Application Rate: {treatment.applicationRate}
- Method: {treatment.applicationMethod}
- Timing: {treatment.timing}
- Safety Interval: {treatment.safetyInterval}
""" for treatment in result.recommendedTreatments])}

ALTERNATIVE METHODS:
{chr(10).join([f"- {method}" for method in result.alternativeMethods])}

SAFETY PROTOCOLS:
1. Required Personal Protective Equipment:
{chr(10).join([f"   - {ppe}" for ppe in result.safetyProtocols.personalProtectiveEquipment])}

2. Application Precautions:
{chr(10).join([f"   - {precaution}" for precaution in result.safetyProtocols.applicationPrecautions])}

3. Re-Entry Interval:
   {result.safetyProtocols.reentryInterval}

4. Environmental Safeguards:
{chr(10).join([f"   - {safeguard}" for safeguard in result.safetyProtocols.environmentalSafeguards])}

REGULATORY INFORMATION:
- Registration Status: {result.regulatoryInformation.registrationStatus}
- Restrictions:
{chr(10).join([f"  * {restriction}" for restriction in result.regulatoryInformation.restrictions])}
- Record-Keeping Requirements:
{chr(10).join([f"  * {requirement}" for requirement in result.regulatoryInformation.recordKeepingRequirements])}

INTEGRATED PEST MANAGEMENT:
- Prevention Strategies:
{chr(10).join([f"  * {strategy}" for strategy in result.integratedPestManagement.preventionStrategies])}
- Monitoring Approach: {result.integratedPestManagement.monitoringApproach}
- Biological Controls:
{chr(10).join([f"  * {control}" for control in result.integratedPestManagement.biologicalControls])}

⚠️ IMPORTANT: Always read and follow the pesticide product label. The label is the law.
                """.strip()
            }
        ]
    
    def requiresHumanReview(self, args: Dict[str, Any], result: PesticideApplicationResult) -> bool:
        """Determine if the tool results require human review.
        
        Args:
            args: Tool arguments
            result: Tool execution result
            
        Returns:
            Boolean indicating if human review is required
        """
        # Always require human review for:
        # 1. High-risk scenarios like severe infestations
        # 2. Applications near water bodies
        # 3. Large-scale applications
        
        severe_infestation = args["infestationLevel"] == "severe"
        large_field = args["fieldSize"] > 50
        environmentally_sensitive = args["proximityToWaterBodies"]
        
        # Check for restricted-use pesticides in recommendations
        has_restricted_use_pesticides = any(
            "restricted-use" in (treatment.product or "").lower() or
            "restricted-use" in (treatment.activeIngredient or "").lower()
            for treatment in result.recommendedTreatments
        )
        
        return severe_infestation or (large_field and environmentally_sensitive) or has_restricted_use_pesticides


def register_agriculture_tools() -> List[str]:
    """Register all agriculture tools and return their names.
    
    Returns:
        List of registered tool names
    """
    # In a production environment, this would register the tools with a tool registry
    tools = [
        SoilAnalysisTool(),
        CropManagementTool(),
        PesticideApplicationTool()
    ]
    
    return [tool.name for tool in tools]