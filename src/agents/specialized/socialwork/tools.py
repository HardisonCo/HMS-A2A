"""
Social Work Tools

This module provides MCP-compliant tools for social work professionals.
"""

from typing import Dict, Any, List, Optional, Type, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

from specialized_agents.tools_base import (
    StandardsCompliantTool,
    ContentPart,
    ToolMetadata,
    create_tool_input_model
)
from specialized_agents.standards_validation import StandardsValidator

#
# Case Management Assessment Tool
#

class AssessmentArea(str, Enum):
    """Assessment areas for case management."""
    MENTAL_HEALTH = "mental_health"
    PHYSICAL_HEALTH = "physical_health"
    HOUSING = "housing"
    FINANCES = "finances"
    EMPLOYMENT = "employment"
    EDUCATION = "education"
    RELATIONSHIPS = "relationships"
    SUBSTANCE_USE = "substance_use"
    LEGAL = "legal"
    SAFETY = "safety"
    TRAUMA = "trauma"
    STRENGTHS = "strengths"

class RiskLevel(str, Enum):
    """Risk levels for assessment."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

# Create the Case Management Assessment Input Schema
CaseManagementAssessmentInputSchema = create_tool_input_model(
    "CaseManagementAssessmentInput",
    {
        # Client information
        "client_identifier": (str, Field(description="Anonymized identifier for the client (no personally identifiable information)")),
        "client_age_range": (str, Field(description="Age range of the client (e.g., '18-24', '25-40', '65+')")),
        "client_gender": (Optional[str], Field(None, description="Gender of the client (optional)")),
        "assessment_purpose": (str, Field(description="Purpose of conducting this assessment")),
        
        # Assessment areas
        "assessment_areas": (List[AssessmentArea], Field(description="Areas to be included in the assessment")),
        
        # Assessment details
        "assessment_details": (Dict[str, Any], Field(description="Detailed information for each assessment area")),
        
        # Risk assessment options
        "conduct_risk_assessment": (bool, Field(description="Whether to include a risk assessment")),
        "risk_factors": (Optional[List[str]], Field(None, description="Specific risk factors to consider")),
        
        # Strengths assessment options
        "conduct_strengths_assessment": (bool, Field(description="Whether to include a strengths assessment")),
        
        # Cultural considerations
        "cultural_factors": (Optional[Dict[str, Any]], Field(None, description="Cultural factors to consider in the assessment")),
        
        # Resource needs
        "resource_needs": (Optional[List[str]], Field(None, description="Resources potentially needed by the client")),
    },
    """Input schema for case management assessment tool."""
)

class AssessmentFinding(BaseModel):
    """Assessment finding for a specific area."""
    area: AssessmentArea
    summary: str
    strengths: List[str]
    challenges: List[str]
    recommendations: List[str]
    risk_level: Optional[RiskLevel] = None
    priority: int  # 1 = highest priority, 5 = lowest

class ResourceReferral(BaseModel):
    """Resource referral recommendation."""
    resource_type: str
    description: str
    rationale: str
    urgency: str  # "immediate", "soon", "when available"
    contact_information: Optional[str] = None

class SafetyPlan(BaseModel):
    """Safety plan for high-risk situations."""
    risk_factors: List[str]
    warning_signs: List[str]
    coping_strategies: List[str]
    support_contacts: List[str]
    emergency_protocol: str
    follow_up_plan: str

class CaseManagementAssessmentResult(BaseModel):
    """Case management assessment result."""
    assessment_id: str
    timestamp: str
    summary: str
    findings: List[AssessmentFinding]
    resource_referrals: List[ResourceReferral]
    recommended_follow_up: str
    safety_plan: Optional[SafetyPlan] = None
    human_review_recommended: bool
    disclaimer: str

class CaseManagementAssessmentTool(StandardsCompliantTool[CaseManagementAssessmentInputSchema, CaseManagementAssessmentResult]):
    """A standards-compliant tool for case management assessment."""
    
    def __init__(self):
        """Initialize the case management assessment tool."""
        super().__init__(
            name="case_management_assessment",
            description="Conducts comprehensive case management assessments across multiple domains, identifying client needs, strengths, and appropriate resources",
            input_schema=CaseManagementAssessmentInputSchema,
            supported_standards=[
                "NASW_CODE_OF_ETHICS",
                "HIPAA",
                "CLIENT_CONFIDENTIALITY",
                "CULTURAL_COMPETENCE"
            ],
            domain="SocialWork",
            metadata=ToolMetadata(
                title="Case Management Assessment Tool",
                read_only=True,
                destructive=False,
                idempotent=True,
                open_world=False,
                description="Standards-compliant social work case management assessment"
            )
        )
    
    async def execute(self, args: CaseManagementAssessmentInputSchema, session_context: Optional[Dict[str, Any]] = None) -> CaseManagementAssessmentResult:
        """Execute the case management assessment.
        
        Args:
            args: Validated input arguments
            session_context: Optional session context
            
        Returns:
            Case management assessment result
        """
        print(f"Conducting case management assessment for {args.client_identifier}")
        
        # Generate assessment ID and timestamp
        assessment_id = f"ASSESS-{datetime.now().strftime('%Y%m%d')}-{hash(args.client_identifier) % 10000:04d}"
        timestamp = datetime.now().isoformat()
        
        # Prepare findings based on assessment areas
        findings = []
        for area in args.assessment_areas:
            finding = self._generate_finding_for_area(area, args.assessment_details.get(area, {}))
            findings.append(finding)
        
        # Sort findings by priority
        findings.sort(key=lambda f: f.priority)
        
        # Generate resource referrals
        resource_referrals = self._generate_resource_referrals(args.resource_needs, findings)
        
        # Determine if human review is recommended
        human_review_recommended = self._determine_if_human_review_needed(findings, args)
        
        # Generate safety plan if needed
        safety_plan = None
        if any(finding.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] for finding in findings):
            safety_plan = self._generate_safety_plan(findings, args)
        
        # Generate recommended follow-up
        recommended_follow_up = self._generate_follow_up_recommendation(findings)
        
        # Generate overall summary
        summary = self._generate_assessment_summary(findings, args)
        
        # Prepare standard disclaimer
        disclaimer = (
            "This assessment is a preliminary tool to support professional social work practice and "
            "should not replace professional judgment. The assessment should be reviewed by a qualified "
            "social work professional before finalizing any intervention plans. Information contained in "
            "this assessment should be treated as confidential and protected in accordance with relevant "
            "privacy laws and professional standards. No personally identifiable information should be "
            "included in assessment details."
        )
        
        # Construct the result
        result = CaseManagementAssessmentResult(
            assessment_id=assessment_id,
            timestamp=timestamp,
            summary=summary,
            findings=findings,
            resource_referrals=resource_referrals,
            recommended_follow_up=recommended_follow_up,
            safety_plan=safety_plan,
            human_review_recommended=human_review_recommended,
            disclaimer=disclaimer
        )
        
        return result
    
    def format_result(self, result: CaseManagementAssessmentResult) -> List[ContentPart]:
        """Format the result for display.
        
        Args:
            result: Case management assessment result
            
        Returns:
            List of content parts
        """
        # Create a data part with the full result
        data_part = ContentPart(
            type=ContentPart.ContentType.DATA,
            content=result.model_dump()
        )
        
        # Format the assessment for text display
        text_output = f"""
# Case Management Assessment

**Assessment ID:** {result.assessment_id}  
**Date/Time:** {result.timestamp}  
**Human Review Recommended:** {'YES' if result.human_review_recommended else 'No'}

## Summary
{result.summary}

## Key Findings
"""
        
        # Add findings by priority
        for finding in result.findings:
            risk_text = f" (Risk: {finding.risk_level.value.upper()})" if finding.risk_level else ""
            text_output += f"""
### {finding.area.value.replace('_', ' ').title()}{risk_text}
{finding.summary}

**Strengths:**
{chr(10).join([f"- {strength}" for strength in finding.strengths])}

**Challenges:**
{chr(10).join([f"- {challenge}" for challenge in finding.challenges])}

**Recommendations:**
{chr(10).join([f"- {recommendation}" for recommendation in finding.recommendations])}
"""
        
        # Add resource referrals
        if result.resource_referrals:
            text_output += "\n## Resource Referrals\n"
            for referral in result.resource_referrals:
                text_output += f"""
### {referral.resource_type} (Urgency: {referral.urgency})
**Description:** {referral.description}
**Rationale:** {referral.rationale}
"""
                if referral.contact_information:
                    text_output += f"**Contact:** {referral.contact_information}\n"
        
        # Add safety plan if present
        if result.safety_plan:
            text_output += """
## Safety Plan
"""
            text_output += f"""
**Risk Factors:** {', '.join(result.safety_plan.risk_factors)}

**Warning Signs:**
{chr(10).join([f"- {sign}" for sign in result.safety_plan.warning_signs])}

**Coping Strategies:**
{chr(10).join([f"- {strategy}" for strategy in result.safety_plan.coping_strategies])}

**Support Contacts:**
{chr(10).join([f"- {contact}" for contact in result.safety_plan.support_contacts])}

**Emergency Protocol:**
{result.safety_plan.emergency_protocol}

**Follow-up Plan:**
{result.safety_plan.follow_up_plan}
"""
        
        # Add recommended follow-up
        text_output += f"""
## Recommended Follow-up
{result.recommended_follow_up}

## Disclaimer
{result.disclaimer}
"""
        
        text_part = ContentPart(
            type=ContentPart.ContentType.TEXT,
            content=text_output.strip()
        )
        
        return [data_part, text_part]
    
    def _generate_finding_for_area(self, area: AssessmentArea, details: Dict[str, Any]) -> AssessmentFinding:
        """Generate a finding for a specific assessment area."""
        # Default values
        strengths = []
        challenges = []
        recommendations = []
        risk_level = RiskLevel.NONE
        priority = 3  # Default medium priority
        
        # Process based on area
        if area == AssessmentArea.MENTAL_HEALTH:
            # Extract key information
            diagnoses = details.get("diagnoses", [])
            symptoms = details.get("symptoms", [])
            treatment = details.get("current_treatment", "None")
            history = details.get("history", "")
            
            # Generate strengths
            if details.get("medication_adherence"):
                strengths.append("Consistent with medication regimen")
            if details.get("insight"):
                strengths.append("Demonstrates insight into mental health needs")
            if details.get("treatment_engagement"):
                strengths.append("Engaged in treatment process")
            if details.get("coping_skills"):
                strengths.append("Has developed effective coping mechanisms")
            
            # Generate challenges
            if diagnoses:
                challenges.append(f"Managing symptoms of {', '.join(diagnoses)}")
            if details.get("medication_issues"):
                challenges.append("Difficulties with medication management")
            if details.get("treatment_barriers"):
                challenges.append("Barriers to accessing consistent mental health care")
            if symptoms:
                challenges.append(f"Currently experiencing {', '.join(symptoms)}")
            
            # Generate recommendations
            if not treatment and (diagnoses or symptoms):
                recommendations.append("Referral for mental health assessment")
                recommendations.append("Explore treatment options appropriate for client needs")
            if treatment:
                recommendations.append("Continue current mental health treatment")
            if details.get("medication_issues"):
                recommendations.append("Medication management support")
            if details.get("coping_skills") is False:
                recommendations.append("Skills development for emotional regulation and distress tolerance")
            
            # Determine risk level
            if details.get("suicidal_ideation") or details.get("homicidal_ideation"):
                risk_level = RiskLevel.CRITICAL
                priority = 1
            elif details.get("crisis") or details.get("severe_symptoms"):
                risk_level = RiskLevel.HIGH
                priority = 1
            elif diagnoses and (not treatment or details.get("treatment_barriers")):
                risk_level = RiskLevel.MODERATE
                priority = 2
            elif diagnoses and treatment:
                risk_level = RiskLevel.LOW
                priority = 3
            
            # Generate summary
            summary = f"Client "
            if diagnoses:
                summary += f"has reported mental health condition(s): {', '.join(diagnoses)}. "
            if symptoms:
                summary += f"Currently experiencing: {', '.join(symptoms)}. "
            if treatment:
                summary += f"Current treatment includes: {treatment}. "
            else:
                summary += "Not currently engaged in mental health treatment. "
            if details.get("suicidal_ideation") or details.get("homicidal_ideation"):
                summary += "IMMEDIATE ATTENTION REQUIRED due to safety concerns. "
            
        elif area == AssessmentArea.HOUSING:
            # Extract key information
            housing_status = details.get("status", "Unknown")
            stability = details.get("stability", "Unknown")
            barriers = details.get("barriers", [])
            
            # Generate strengths
            if housing_status in ["stable", "permanent"]:
                strengths.append("Currently has stable housing")
            if details.get("affordability") in ["good", "adequate"]:
                strengths.append("Housing is affordable given current income")
            if details.get("safety") in ["good", "adequate"]:
                strengths.append("Current housing environment is safe")
            if details.get("housing_skills"):
                strengths.append("Possesses skills to maintain housing")
            
            # Generate challenges
            if housing_status in ["homeless", "temporary", "unstable"]:
                challenges.append(f"Currently experiencing {housing_status} housing")
            if details.get("affordability") == "poor":
                challenges.append("Housing costs exceed 50% of income")
            if details.get("safety") == "poor":
                challenges.append("Current housing presents safety concerns")
            for barrier in barriers:
                challenges.append(f"Housing barrier: {barrier}")
            
            # Generate recommendations
            if housing_status in ["homeless", "temporary"]:
                recommendations.append("Immediate referral to housing assistance programs")
                recommendations.append("Explore emergency shelter options if needed")
            if housing_status == "unstable":
                recommendations.append("Housing stabilization services")
            if details.get("affordability") == "poor":
                recommendations.append("Financial assistance or subsidy programs")
            if barriers:
                recommendations.append("Address specific housing barriers through targeted interventions")
            
            # Determine risk level
            if housing_status == "homeless":
                risk_level = RiskLevel.HIGH
                priority = 1
            elif housing_status == "temporary":
                risk_level = RiskLevel.MODERATE
                priority = 2
            elif housing_status == "unstable":
                risk_level = RiskLevel.MODERATE
                priority = 2
            elif details.get("safety") == "poor":
                risk_level = RiskLevel.HIGH
                priority = 1
            elif housing_status == "stable" and details.get("affordability") == "poor":
                risk_level = RiskLevel.MODERATE
                priority = 2
            
            # Generate summary
            summary = f"Client's housing status is {housing_status}. "
            if stability:
                summary += f"Housing stability is {stability}. "
            if barriers:
                summary += f"Main housing barriers include: {', '.join(barriers)}. "
            if details.get("safety") == "poor":
                summary += "Current housing presents safety concerns requiring attention. "
            
        else:
            # Generic handling for other assessment areas
            # This would be expanded for each area in a full implementation
            summary = f"Assessment of {area.value.replace('_', ' ')} completed. "
            
            # Extract available information
            for key, value in details.items():
                if isinstance(value, list):
                    summary += f"{key.replace('_', ' ').title()}: {', '.join(value)}. "
                elif isinstance(value, bool):
                    if value:
                        summary += f"{key.replace('_', ' ').title()}: Yes. "
                    else:
                        summary += f"{key.replace('_', ' ').title()}: No. "
                elif value:
                    summary += f"{key.replace('_', ' ').title()}: {value}. "
            
            # Generate generic strengths
            positives = [k for k, v in details.items() if (isinstance(v, bool) and v) or 
                        (isinstance(v, str) and v.lower() in ["good", "yes", "adequate", "strong"])]
            for positive in positives[:3]:  # Limit to 3 strengths
                strengths.append(f"{positive.replace('_', ' ').title()}")
            
            # Generate generic challenges
            negatives = [k for k, v in details.items() if (isinstance(v, bool) and not v) or 
                        (isinstance(v, str) and v.lower() in ["poor", "no", "inadequate", "weak", "none"])]
            for negative in negatives[:3]:  # Limit to 3 challenges
                challenges.append(f"Challenges with {negative.replace('_', ' ')}")
            
            # Generate generic recommendations
            for negative in negatives[:3]:  # Limit to 3 recommendations
                recommendations.append(f"Address {negative.replace('_', ' ')} through appropriate services")
            
            # Determine generic risk level
            if "crisis" in details or "emergency" in details:
                risk_level = RiskLevel.HIGH
                priority = 1
            elif len(negatives) > len(positives):
                risk_level = RiskLevel.MODERATE
                priority = 2
            elif negatives:
                risk_level = RiskLevel.LOW
                priority = 3
            
        # Return the finding
        return AssessmentFinding(
            area=area,
            summary=summary,
            strengths=strengths,
            challenges=challenges,
            recommendations=recommendations,
            risk_level=risk_level,
            priority=priority
        )
    
    def _generate_resource_referrals(self, resource_needs: Optional[List[str]], findings: List[AssessmentFinding]) -> List[ResourceReferral]:
        """Generate resource referrals based on assessment findings."""
        referrals = []
        
        # Map assessment areas to resource types
        resource_type_map = {
            AssessmentArea.MENTAL_HEALTH: "Mental Health Services",
            AssessmentArea.PHYSICAL_HEALTH: "Healthcare Services",
            AssessmentArea.HOUSING: "Housing Assistance",
            AssessmentArea.FINANCES: "Financial Resources",
            AssessmentArea.EMPLOYMENT: "Employment Services",
            AssessmentArea.EDUCATION: "Educational Resources",
            AssessmentArea.SUBSTANCE_USE: "Substance Use Treatment",
            AssessmentArea.LEGAL: "Legal Services",
            AssessmentArea.SAFETY: "Safety Resources",
            AssessmentArea.TRAUMA: "Trauma Services"
        }
        
        # Generate referrals based on high-priority findings
        for finding in findings:
            if finding.risk_level in [RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.CRITICAL]:
                resource_type = resource_type_map.get(finding.area, f"{finding.area.value.replace('_', ' ').title()} Resources")
                
                # Determine urgency based on risk level
                if finding.risk_level == RiskLevel.CRITICAL:
                    urgency = "immediate"
                elif finding.risk_level == RiskLevel.HIGH:
                    urgency = "immediate"
                else:
                    urgency = "soon"
                
                # Create referral
                referral = ResourceReferral(
                    resource_type=resource_type,
                    description=f"Professional {resource_type.lower()} to address identified needs",
                    rationale=f"Based on {finding.area.value.replace('_', ' ')} assessment indicating {finding.risk_level.value} risk level",
                    urgency=urgency,
                    contact_information=None  # Would be populated with actual resources in a real implementation
                )
                
                # Check if this type of referral already exists
                if not any(r.resource_type == resource_type for r in referrals):
                    referrals.append(referral)
        
        # Add any explicitly requested resources not already covered
        if resource_needs:
            for resource in resource_needs:
                resource_type = f"{resource.title()} Resources"
                
                # Skip if we already have this type
                if any(r.resource_type == resource_type for r in referrals):
                    continue
                
                # Create referral
                referral = ResourceReferral(
                    resource_type=resource_type,
                    description=f"Resources to address {resource.lower()} needs",
                    rationale="Based on identified resource needs",
                    urgency="when available",
                    contact_information=None
                )
                
                referrals.append(referral)
        
        return referrals
    
    def _determine_if_human_review_needed(self, findings: List[AssessmentFinding], args: CaseManagementAssessmentInputSchema) -> bool:
        """Determine if human review is needed based on risk levels and complexity."""
        # Always recommend human review for critical or high risks
        if any(finding.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH] for finding in findings):
            return True
        
        # Count moderate risks
        moderate_risks = sum(1 for finding in findings if finding.risk_level == RiskLevel.MODERATE)
        
        # Recommend human review for multiple moderate risks
        if moderate_risks >= 2:
            return True
        
        # Check for specific high-risk assessment areas
        high_risk_areas = [
            AssessmentArea.SAFETY,
            AssessmentArea.TRAUMA,
            AssessmentArea.SUBSTANCE_USE
        ]
        
        if any(finding.area in high_risk_areas for finding in findings):
            return True
        
        # Check for cultural factors that might require specialized expertise
        if args.cultural_factors and len(args.cultural_factors) > 0:
            return True
        
        # Check total number of assessment areas (complex cases)
        if len(args.assessment_areas) >= 5:
            return True
        
        return False
    
    def _generate_safety_plan(self, findings: List[AssessmentFinding], args: CaseManagementAssessmentInputSchema) -> SafetyPlan:
        """Generate a safety plan for high-risk situations."""
        # Collect risk factors from high-risk findings
        risk_factors = []
        for finding in findings:
            if finding.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                for challenge in finding.challenges:
                    risk_factors.append(challenge)
        
        # Generate warning signs (simplified for this example)
        warning_signs = [
            "Increased thoughts of hopelessness or being a burden",
            "Withdrawal from social activities and supports",
            "Increased substance use",
            "Talk about wanting to die or not be around",
            "Giving away possessions or saying goodbye",
            "Increased agitation or mood swings"
        ]
        
        # Generate coping strategies (simplified for this example)
        coping_strategies = [
            "Use grounding techniques (5-4-3-2-1 sensory awareness)",
            "Practice deep breathing exercises",
            "Call a trusted friend or family member",
            "Use distraction with safe activities",
            "Utilize positive self-talk and affirmations",
            "Engage in physical activity if possible"
        ]
        
        # Generate support contacts (would be client-specific in real implementation)
        support_contacts = [
            "Personal support: [Client to identify trusted person and contact information]",
            "Crisis line: National Suicide Prevention Lifeline 988 or 1-800-273-8255",
            "Local crisis response: [Local number to be provided]",
            "Emergency services: 911"
        ]
        
        # Generate emergency protocol
        emergency_protocol = (
            "If experiencing a mental health crisis or thoughts of harm to self or others:\n"
            "1. Call crisis hotline or 911 if immediate danger\n"
            "2. Go to nearest emergency room if able to do so safely\n"
            "3. Contact on-call mental health provider if available"
        )
        
        # Generate follow-up plan
        follow_up_plan = (
            "Schedule follow-up assessment within 48 hours.\n"
            "Connect with mental health provider within one week.\n"
            "Review and update safety plan at each subsequent contact."
        )
        
        return SafetyPlan(
            risk_factors=risk_factors,
            warning_signs=warning_signs,
            coping_strategies=coping_strategies,
            support_contacts=support_contacts,
            emergency_protocol=emergency_protocol,
            follow_up_plan=follow_up_plan
        )
    
    def _generate_follow_up_recommendation(self, findings: List[AssessmentFinding]) -> str:
        """Generate a follow-up recommendation based on assessment findings."""
        # Determine highest risk level
        risk_levels = [finding.risk_level for finding in findings if finding.risk_level]
        
        if RiskLevel.CRITICAL in risk_levels:
            return (
                "URGENT: Immediate follow-up required within 24 hours. "
                "Consider emergency services or crisis response if indicated. "
                "Develop comprehensive safety plan and monitoring protocol."
            )
        elif RiskLevel.HIGH in risk_levels:
            return (
                "HIGH PRIORITY: Follow-up within 2-3 days. "
                "Ensure immediate needs are addressed and safety plan is in place. "
                "Schedule comprehensive service planning session within one week."
            )
        elif RiskLevel.MODERATE in risk_levels:
            return (
                "MODERATE PRIORITY: Follow-up within 1 week. "
                "Address identified needs through appropriate referrals. "
                "Develop initial service plan with client input."
            )
        elif RiskLevel.LOW in risk_levels:
            return (
                "ROUTINE: Follow-up within 2 weeks. "
                "Monitor progress on referrals and resource connections. "
                "Assess for changes in needs or circumstances."
            )
        else:
            return (
                "MAINTENANCE: Follow-up within 30 days. "
                "Check in on progress and any emerging needs. "
                "Provide support for maintaining stability."
            )
    
    def _generate_assessment_summary(self, findings: List[AssessmentFinding], args: CaseManagementAssessmentInputSchema) -> str:
        """Generate an overall assessment summary."""
        # Count findings by risk level
        risk_count = {
            RiskLevel.CRITICAL: 0,
            RiskLevel.HIGH: 0,
            RiskLevel.MODERATE: 0,
            RiskLevel.LOW: 0,
            RiskLevel.NONE: 0
        }
        
        for finding in findings:
            if finding.risk_level:
                risk_count[finding.risk_level] += 1
        
        # Determine overall risk level
        overall_risk = RiskLevel.NONE
        if risk_count[RiskLevel.CRITICAL] > 0:
            overall_risk = RiskLevel.CRITICAL
        elif risk_count[RiskLevel.HIGH] > 0:
            overall_risk = RiskLevel.HIGH
        elif risk_count[RiskLevel.MODERATE] > 0:
            overall_risk = RiskLevel.MODERATE
        elif risk_count[RiskLevel.LOW] > 0:
            overall_risk = RiskLevel.LOW
        
        # Generate primary concerns
        primary_concerns = []
        for finding in findings:
            if finding.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                primary_concerns.append(f"{finding.area.value.replace('_', ' ').title()}: {finding.summary}")
        
        # Generate key strengths
        key_strengths = []
        for finding in findings:
            key_strengths.extend(finding.strengths[:2])  # Take top 2 strengths from each finding
        
        # Generate cultural considerations if applicable
        cultural_considerations = ""
        if args.cultural_factors and len(args.cultural_factors) > 0:
            cultural_considerations = "\n\nCultural factors requiring consideration include: "
            cultural_considerations += ", ".join([f"{k}: {v}" for k, v in args.cultural_factors.items()])
        
        # Generate summary text
        summary = f"Comprehensive assessment completed across {len(findings)} domains with overall risk level of {overall_risk.value.upper()}. "
        
        if risk_count[RiskLevel.CRITICAL] > 0:
            summary += f"IMMEDIATE ATTENTION REQUIRED for {risk_count[RiskLevel.CRITICAL]} critical risk area(s). "
        
        if primary_concerns:
            summary += "\n\nPrimary concerns: \n- " + "\n- ".join(primary_concerns)
        
        if key_strengths:
            summary += "\n\nKey strengths: \n- " + "\n- ".join(key_strengths[:5])  # Limit to top 5 strengths
        
        summary += cultural_considerations
        
        return summary
    
    def requires_human_review(self, args: CaseManagementAssessmentInputSchema, result: CaseManagementAssessmentResult) -> bool:
        """Determine if human review is required for this assessment.
        
        Args:
            args: The validated arguments
            result: The tool result
            
        Returns:
            Boolean indicating if human review is required
        """
        # The result already contains this determination
        return result.human_review_recommended


#
# Intervention Planning Tool
#

class InterventionModality(str, Enum):
    """Treatment modalities for interventions."""
    INDIVIDUAL = "individual"
    GROUP = "group"
    FAMILY = "family"
    COMMUNITY = "community"
    CASE_MANAGEMENT = "case_management"
    CRISIS_INTERVENTION = "crisis_intervention"

class InterventionApproach(str, Enum):
    """Intervention approaches."""
    COGNITIVE_BEHAVIORAL = "cognitive_behavioral"
    SOLUTION_FOCUSED = "solution_focused"
    MOTIVATIONAL_INTERVIEWING = "motivational_interviewing"
    TRAUMA_INFORMED = "trauma_informed"
    STRENGTHS_BASED = "strengths_based"
    FAMILY_SYSTEMS = "family_systems"
    PSYCHOEDUCATIONAL = "psychoeducational"
    HARM_REDUCTION = "harm_reduction"

class InterventionFrequency(str, Enum):
    """Intervention frequency."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    AS_NEEDED = "as_needed"

# Create the Intervention Planning Input Schema
InterventionPlanningInputSchema = create_tool_input_model(
    "InterventionPlanningInput",
    {
        # Client information
        "client_identifier": (str, Field(description="Anonymized identifier for the client (no personally identifiable information)")),
        "assessment_id": (Optional[str], Field(None, description="ID of the assessment this plan is based on")),
        
        # Intervention basics
        "primary_concerns": (List[str], Field(description="Primary concerns to be addressed")),
        "intervention_goals": (List[Dict[str, Any]], Field(description="Goals for the intervention plan")),
        "client_strengths": (List[str], Field(description="Client strengths to leverage")),
        
        # Intervention details
        "preferred_modalities": (List[InterventionModality], Field(description="Preferred intervention modalities")),
        "preferred_approaches": (List[InterventionApproach], Field(description="Preferred intervention approaches")),
        "recommended_frequency": (InterventionFrequency, Field(description="Recommended intervention frequency")),
        
        # Contextual factors
        "cultural_factors": (Optional[Dict[str, Any]], Field(None, description="Cultural factors to consider")),
        "resource_constraints": (Optional[List[str]], Field(None, description="Resource or access constraints")),
        "client_preferences": (Optional[Dict[str, Any]], Field(None, description="Client preferences for intervention")),
        
        # Additional considerations
        "risk_factors": (Optional[List[str]], Field(None, description="Risk factors to address")),
        "existing_supports": (Optional[List[str]], Field(None, description="Existing support systems"))
    },
    """Input schema for intervention planning tool."""
)

class InterventionGoal(BaseModel):
    """Intervention goal with objectives and strategies."""
    goal_statement: str
    objectives: List[str]
    strategies: List[str]
    timeframe: str
    measurement: str
    progress_indicators: List[str]

class InterventionStrategy(BaseModel):
    """Specific intervention strategy."""
    name: str
    description: str
    approach: InterventionApproach
    modality: InterventionModality
    implementation_steps: List[str]
    required_resources: List[str]
    evidence_basis: str

class InterventionPlanningResult(BaseModel):
    """Intervention planning result."""
    plan_id: str
    timestamp: str
    summary: str
    goals: List[InterventionGoal]
    core_strategies: List[InterventionStrategy]
    recommended_services: List[str]
    recommended_schedule: str
    cultural_considerations: List[str]
    collaboration_recommendations: List[str]
    review_schedule: str
    human_review_recommended: bool
    disclaimer: str

class InterventionPlanningTool(StandardsCompliantTool[InterventionPlanningInputSchema, InterventionPlanningResult]):
    """A standards-compliant tool for intervention planning."""
    
    def __init__(self):
        """Initialize the intervention planning tool."""
        super().__init__(
            name="intervention_planning",
            description="Develops comprehensive social work intervention plans addressing client needs, leveraging strengths, and incorporating evidence-based approaches",
            input_schema=InterventionPlanningInputSchema,
            supported_standards=[
                "NASW_CODE_OF_ETHICS",
                "HIPAA",
                "CLIENT_CONFIDENTIALITY",
                "CULTURAL_COMPETENCE"
            ],
            domain="SocialWork",
            metadata=ToolMetadata(
                title="Intervention Planning Tool",
                read_only=True,
                destructive=False,
                idempotent=True,
                open_world=False,
                description="Standards-compliant social work intervention planning"
            )
        )
    
    async def execute(self, args: InterventionPlanningInputSchema, session_context: Optional[Dict[str, Any]] = None) -> InterventionPlanningResult:
        """Execute the intervention planning.
        
        Args:
            args: Validated input arguments
            session_context: Optional session context
            
        Returns:
            Intervention planning result
        """
        print(f"Developing intervention plan for {args.client_identifier}")
        
        # Generate plan ID and timestamp
        plan_id = f"PLAN-{datetime.now().strftime('%Y%m%d')}-{hash(args.client_identifier) % 10000:04d}"
        timestamp = datetime.now().isoformat()
        
        # Develop intervention goals
        goals = []
        for goal_input in args.intervention_goals:
            goal = self._develop_intervention_goal(goal_input, args)
            goals.append(goal)
        
        # Develop core intervention strategies
        core_strategies = self._develop_core_strategies(args)
        
        # Generate recommended services
        recommended_services = self._generate_recommended_services(args, goals)
        
        # Generate recommended schedule
        recommended_schedule = self._generate_recommended_schedule(args)
        
        # Generate cultural considerations
        cultural_considerations = self._generate_cultural_considerations(args)
        
        # Generate collaboration recommendations
        collaboration_recommendations = self._generate_collaboration_recommendations(args, goals)
        
        # Generate review schedule
        review_schedule = self._generate_review_schedule(args)
        
        # Determine if human review is recommended
        human_review_recommended = self._determine_if_human_review_needed(args, goals)
        
        # Generate plan summary
        summary = self._generate_plan_summary(args, goals, core_strategies)
        
        # Prepare standard disclaimer
        disclaimer = (
            "This intervention plan is a preliminary tool to support professional social work practice and "
            "should not replace professional judgment. The plan should be reviewed by a qualified "
            "social work professional before implementation. The plan should be developed collaboratively "
            "with the client and adapted based on ongoing assessment of needs and progress. Information contained "
            "in this plan should be treated as confidential and protected in accordance with relevant "
            "privacy laws and professional standards. No personally identifiable information should be "
            "included in plan details."
        )
        
        # Construct the result
        result = InterventionPlanningResult(
            plan_id=plan_id,
            timestamp=timestamp,
            summary=summary,
            goals=goals,
            core_strategies=core_strategies,
            recommended_services=recommended_services,
            recommended_schedule=recommended_schedule,
            cultural_considerations=cultural_considerations,
            collaboration_recommendations=collaboration_recommendations,
            review_schedule=review_schedule,
            human_review_recommended=human_review_recommended,
            disclaimer=disclaimer
        )
        
        return result
    
    def format_result(self, result: InterventionPlanningResult) -> List[ContentPart]:
        """Format the result for display.
        
        Args:
            result: Intervention planning result
            
        Returns:
            List of content parts
        """
        # Create a data part with the full result
        data_part = ContentPart(
            type=ContentPart.ContentType.DATA,
            content=result.model_dump()
        )
        
        # Format the plan for text display
        text_output = f"""
# Intervention Plan

**Plan ID:** {result.plan_id}  
**Date/Time:** {result.timestamp}  
**Human Review Recommended:** {'YES' if result.human_review_recommended else 'No'}

## Summary
{result.summary}

## Goals and Objectives
"""
        
        # Add goals
        for i, goal in enumerate(result.goals, 1):
            text_output += f"""
### Goal {i}: {goal.goal_statement}
**Timeframe:** {goal.timeframe}
**Measurement:** {goal.measurement}

**Objectives:**
{chr(10).join([f"- {objective}" for objective in goal.objectives])}

**Strategies:**
{chr(10).join([f"- {strategy}" for strategy in goal.strategies])}

**Progress Indicators:**
{chr(10).join([f"- {indicator}" for indicator in goal.progress_indicators])}
"""
        
        # Add core strategies
        text_output += "\n## Core Intervention Strategies\n"
        for i, strategy in enumerate(result.core_strategies, 1):
            text_output += f"""
### {i}. {strategy.name}
**Description:** {strategy.description}
**Approach:** {strategy.approach.value.replace('_', ' ').title()}
**Modality:** {strategy.modality.value.replace('_', ' ').title()}
**Evidence Basis:** {strategy.evidence_basis}

**Implementation Steps:**
{chr(10).join([f"- {step}" for step in strategy.implementation_steps])}

**Required Resources:**
{chr(10).join([f"- {resource}" for resource in strategy.required_resources])}
"""
        
        # Add recommended services
        if result.recommended_services:
            text_output += "\n## Recommended Services\n"
            for service in result.recommended_services:
                text_output += f"- {service}\n"
        
        # Add recommended schedule
        text_output += f"\n## Recommended Schedule\n{result.recommended_schedule}\n"
        
        # Add cultural considerations
        if result.cultural_considerations:
            text_output += "\n## Cultural Considerations\n"
            for consideration in result.cultural_considerations:
                text_output += f"- {consideration}\n"
        
        # Add collaboration recommendations
        text_output += "\n## Collaboration Recommendations\n"
        for recommendation in result.collaboration_recommendations:
            text_output += f"- {recommendation}\n"
        
        # Add review schedule
        text_output += f"\n## Review Schedule\n{result.review_schedule}\n"
        
        # Add disclaimer
        text_output += f"\n## Disclaimer\n{result.disclaimer}"
        
        text_part = ContentPart(
            type=ContentPart.ContentType.TEXT,
            content=text_output.strip()
        )
        
        return [data_part, text_part]
    
    def _develop_intervention_goal(self, goal_input: Dict[str, Any], args: InterventionPlanningInputSchema) -> InterventionGoal:
        """Develop a structured intervention goal from input."""
        # Extract goal components
        goal_statement = goal_input.get("statement", "")
        area = goal_input.get("area", "")
        
        # Develop objectives based on goal statement
        objectives = goal_input.get("objectives", [])
        if not objectives and goal_statement:
            # Generate objectives if none provided
            objectives = [
                f"Increase {area} skills and knowledge",
                f"Reduce barriers to {area} improvement",
                f"Develop sustainable strategies for maintaining progress"
            ]
        
        # Develop strategies based on approaches and modalities
        strategies = goal_input.get("strategies", [])
        if not strategies:
            # Generate strategies if none provided
            for approach in args.preferred_approaches[:2]:  # Use top 2 approaches
                strategy = self._generate_strategy_for_approach(approach, goal_statement)
                strategies.append(strategy)
                
            for modality in args.preferred_modalities[:2]:  # Use top 2 modalities
                strategy = self._generate_strategy_for_modality(modality, goal_statement)
                strategies.append(strategy)
        
        # Generate timeframe
        timeframe = goal_input.get("timeframe", "")
        if not timeframe:
            if "emergency" in goal_statement.lower() or "crisis" in goal_statement.lower():
                timeframe = "Immediate (1-2 weeks)"
            elif "short-term" in goal_statement.lower():
                timeframe = "Short-term (1-3 months)"
            else:
                timeframe = "Medium-term (3-6 months)"
        
        # Generate measurement method
        measurement = goal_input.get("measurement", "")
        if not measurement:
            if "increase" in goal_statement.lower() or "improve" in goal_statement.lower():
                measurement = "Self-report scale (1-10) and periodic assessment of progress"
            elif "reduce" in goal_statement.lower() or "decrease" in goal_statement.lower():
                measurement = "Frequency tracking and self-monitoring log"
            else:
                measurement = "Goal attainment scaling and progress review"
        
        # Generate progress indicators
        progress_indicators = goal_input.get("progress_indicators", [])
        if not progress_indicators:
            progress_indicators = [
                "Client reports improvement in target area",
                "Observable changes in client behavior or situation",
                "Achievement of specific objectives",
                "Increased utilization of identified strategies"
            ]
        
        return InterventionGoal(
            goal_statement=goal_statement,
            objectives=objectives,
            strategies=strategies,
            timeframe=timeframe,
            measurement=measurement,
            progress_indicators=progress_indicators
        )
    
    def _generate_strategy_for_approach(self, approach: InterventionApproach, goal: str) -> str:
        """Generate a strategy based on intervention approach."""
        if approach == InterventionApproach.COGNITIVE_BEHAVIORAL:
            return f"Use cognitive restructuring to identify and modify unhelpful thoughts related to {goal.lower()}"
        elif approach == InterventionApproach.SOLUTION_FOCUSED:
            return f"Identify exceptions when {goal.lower()} is less of a problem and amplify these solutions"
        elif approach == InterventionApproach.MOTIVATIONAL_INTERVIEWING:
            return f"Explore ambivalence about changing behaviors related to {goal.lower()} using MI techniques"
        elif approach == InterventionApproach.TRAUMA_INFORMED:
            return f"Apply trauma-informed principles to address underlying trauma affecting {goal.lower()}"
        elif approach == InterventionApproach.STRENGTHS_BASED:
            return f"Leverage client strengths and resources to make progress toward {goal.lower()}"
        elif approach == InterventionApproach.FAMILY_SYSTEMS:
            return f"Explore family patterns and dynamics that influence {goal.lower()}"
        elif approach == InterventionApproach.PSYCHOEDUCATIONAL:
            return f"Provide education and resources about {goal.lower()} to increase knowledge and skills"
        elif approach == InterventionApproach.HARM_REDUCTION:
            return f"Implement practical strategies to reduce harmful consequences related to {goal.lower()}"
        else:
            return f"Apply evidence-based techniques to address {goal.lower()}"
    
    def _generate_strategy_for_modality(self, modality: InterventionModality, goal: str) -> str:
        """Generate a strategy based on intervention modality."""
        if modality == InterventionModality.INDIVIDUAL:
            return f"One-on-one sessions focusing on personal experiences and strategies related to {goal.lower()}"
        elif modality == InterventionModality.GROUP:
            return f"Group-based skills development and peer support addressing {goal.lower()}"
        elif modality == InterventionModality.FAMILY:
            return f"Family sessions to develop shared understanding and strategies for {goal.lower()}"
        elif modality == InterventionModality.COMMUNITY:
            return f"Community-based resources and support systems to address {goal.lower()}"
        elif modality == InterventionModality.CASE_MANAGEMENT:
            return f"Coordination of services and resources to support progress toward {goal.lower()}"
        elif modality == InterventionModality.CRISIS_INTERVENTION:
            return f"Crisis planning and immediate intervention strategies for urgent aspects of {goal.lower()}"
        else:
            return f"Structured activities and interventions targeting {goal.lower()}"
    
    def _develop_core_strategies(self, args: InterventionPlanningInputSchema) -> List[InterventionStrategy]:
        """Develop core intervention strategies."""
        strategies = []
        
        # Create strategy for each preferred approach (limit to top 3)
        for approach in args.preferred_approaches[:3]:
            strategy = self._create_strategy_for_approach(approach, args)
            strategies.append(strategy)
        
        return strategies
    
    def _create_strategy_for_approach(self, approach: InterventionApproach, args: InterventionPlanningInputSchema) -> InterventionStrategy:
        """Create a detailed strategy for a specific approach."""
        # Define strategy content based on approach
        if approach == InterventionApproach.COGNITIVE_BEHAVIORAL:
            strategy = InterventionStrategy(
                name="Cognitive-Behavioral Intervention",
                description="Structured approach to identify and modify unhelpful thoughts and behaviors",
                approach=InterventionApproach.COGNITIVE_BEHAVIORAL,
                modality=args.preferred_modalities[0] if args.preferred_modalities else InterventionModality.INDIVIDUAL,
                implementation_steps=[
                    "Identify cognitive distortions related to identified concerns",
                    "Teach thought monitoring and recording techniques",
                    "Develop cognitive restructuring skills",
                    "Practice behavioral experiments to test new thoughts",
                    "Develop skills for maintaining changes and preventing relapse"
                ],
                required_resources=[
                    "CBT workbooks or worksheets",
                    "Thought records",
                    "Skills practice assignments"
                ],
                evidence_basis="Extensive research support for CBT across multiple problems including depression, anxiety, and behavior change"
            )
        elif approach == InterventionApproach.SOLUTION_FOCUSED:
            strategy = InterventionStrategy(
                name="Solution-Focused Brief Therapy",
                description="Goal-directed approach focusing on solutions rather than problems",
                approach=InterventionApproach.SOLUTION_FOCUSED,
                modality=args.preferred_modalities[0] if args.preferred_modalities else InterventionModality.INDIVIDUAL,
                implementation_steps=[
                    "Identify exceptions when problems are less severe or absent",
                    "Use scaling questions to measure progress",
                    "Develop concrete, measurable goals",
                    "Ask miracle question to envision desired future",
                    "Build on existing strengths and resources"
                ],
                required_resources=[
                    "Goal-setting worksheets",
                    "Solution-focused question guide",
                    "Progress tracking tools"
                ],
                evidence_basis="Research supports effectiveness for brief intervention, particularly for goal achievement and client empowerment"
            )
        elif approach == InterventionApproach.MOTIVATIONAL_INTERVIEWING:
            strategy = InterventionStrategy(
                name="Motivational Interviewing",
                description="Collaborative conversation to strengthen motivation for positive change",
                approach=InterventionApproach.MOTIVATIONAL_INTERVIEWING,
                modality=args.preferred_modalities[0] if args.preferred_modalities else InterventionModality.INDIVIDUAL,
                implementation_steps=[
                    "Express empathy through reflective listening",
                    "Develop discrepancy between goals and current behavior",
                    "Roll with resistance by avoiding argumentation",
                    "Support self-efficacy and change talk",
                    "Help client develop change plan when ready"
                ],
                required_resources=[
                    "Decisional balance worksheets",
                    "Readiness ruler",
                    "Values clarification exercises"
                ],
                evidence_basis="Strong evidence base for enhancing motivation to change, particularly with substance use and health behaviors"
            )
        elif approach == InterventionApproach.TRAUMA_INFORMED:
            strategy = InterventionStrategy(
                name="Trauma-Informed Approach",
                description="Intervention recognizing the impact of trauma and paths to recovery",
                approach=InterventionApproach.TRAUMA_INFORMED,
                modality=args.preferred_modalities[0] if args.preferred_modalities else InterventionModality.INDIVIDUAL,
                implementation_steps=[
                    "Ensure physical and emotional safety throughout intervention",
                    "Build trust through transparency and consistency",
                    "Provide opportunities for choice and control",
                    "Use strengths-based approach to build resilience",
                    "Recognize cultural factors in trauma experiences"
                ],
                required_resources=[
                    "Grounding techniques guide",
                    "Safety planning tools",
                    "Trauma education materials"
                ],
                evidence_basis="Research supports trauma-informed approaches for improving engagement and outcomes across various settings"
            )
        elif approach == InterventionApproach.STRENGTHS_BASED:
            strategy = InterventionStrategy(
                name="Strengths-Based Intervention",
                description="Approach focusing on identifying and building upon client strengths and resources",
                approach=InterventionApproach.STRENGTHS_BASED,
                modality=args.preferred_modalities[0] if args.preferred_modalities else InterventionModality.INDIVIDUAL,
                implementation_steps=[
                    "Identify client strengths, abilities, and resources",
                    "Reframe challenges in context of strengths",
                    "Develop strategies that leverage existing capabilities",
                    "Connect client with community resources that support strengths",
                    "Build confidence through recognition of successes"
                ],
                required_resources=[
                    "Strengths assessment tools",
                    "Resource mapping worksheet",
                    "Success journal"
                ],
                evidence_basis="Evidence supports improved outcomes and engagement when interventions build on client strengths"
            )
        else:
            # Generic strategy for other approaches
            strategy = InterventionStrategy(
                name=f"{approach.value.replace('_', ' ').title()} Intervention",
                description=f"Structured approach using {approach.value.replace('_', ' ')} principles",
                approach=approach,
                modality=args.preferred_modalities[0] if args.preferred_modalities else InterventionModality.INDIVIDUAL,
                implementation_steps=[
                    "Assess client's specific needs related to this approach",
                    "Develop tailored intervention plan",
                    "Implement core techniques of this approach",
                    "Monitor progress and adjust as needed",
                    "Support transition to maintenance and sustainability"
                ],
                required_resources=[
                    "Assessment tools",
                    "Intervention materials",
                    "Progress tracking resources"
                ],
                evidence_basis=f"Research supports efficacy of {approach.value.replace('_', ' ')} for addressing identified concerns"
            )
        
        return strategy
    
    def _generate_recommended_services(self, args: InterventionPlanningInputSchema, goals: List[InterventionGoal]) -> List[str]:
        """Generate recommended services based on goals and needs."""
        services = []
        
        # Map common concerns to services
        concern_service_map = {
            "mental health": ["Mental health counseling", "Psychiatric services"],
            "depression": ["Depression treatment", "Mood management services"],
            "anxiety": ["Anxiety treatment", "Stress management services"],
            "trauma": ["Trauma-specific therapy", "Trauma recovery services"],
            "substance": ["Substance use treatment", "Recovery support services"],
            "housing": ["Housing assistance", "Shelter services"],
            "homeless": ["Housing first programs", "Emergency shelter"],
            "employment": ["Employment services", "Job training programs"],
            "education": ["Educational support", "Academic assistance"],
            "financial": ["Financial counseling", "Benefits assistance"],
            "food": ["Food assistance", "Nutrition services"],
            "legal": ["Legal aid", "Legal advocacy"],
            "domestic violence": ["Domestic violence services", "Safety planning"],
            "child": ["Child welfare services", "Parenting support"],
            "elder": ["Elder services", "Aging support programs"],
            "disability": ["Disability services", "Accessibility resources"]
        }
        
        # Add services based on primary concerns
        for concern in args.primary_concerns:
            concern_lower = concern.lower()
            for keyword, related_services in concern_service_map.items():
                if keyword in concern_lower:
                    for service in related_services:
                        if service not in services:
                            services.append(service)
        
        # Add modality-specific services
        modality_service_map = {
            InterventionModality.INDIVIDUAL: ["Individual counseling/therapy"],
            InterventionModality.GROUP: ["Group therapy/support groups"],
            InterventionModality.FAMILY: ["Family therapy/counseling"],
            InterventionModality.COMMUNITY: ["Community support programs"],
            InterventionModality.CASE_MANAGEMENT: ["Case management services"],
            InterventionModality.CRISIS_INTERVENTION: ["Crisis intervention services", "Crisis hotline access"]
        }
        
        for modality in args.preferred_modalities:
            for service in modality_service_map.get(modality, []):
                if service not in services:
                    services.append(service)
        
        # Add services to address resource constraints if specified
        if args.resource_constraints:
            for constraint in args.resource_constraints:
                constraint_lower = constraint.lower()
                if "transport" in constraint_lower:
                    services.append("Transportation assistance")
                if "child" in constraint_lower and "care" in constraint_lower:
                    services.append("Childcare resources")
                if "language" in constraint_lower:
                    services.append("Interpreter/translation services")
                if "financial" in constraint_lower or "cost" in constraint_lower:
                    services.append("Financial assistance programs")
        
        return services
    
    def _generate_recommended_schedule(self, args: InterventionPlanningInputSchema) -> str:
        """Generate a recommended intervention schedule."""
        # Base schedule on recommended frequency
        if args.recommended_frequency == InterventionFrequency.DAILY:
            base_schedule = "Daily check-ins or interventions"
        elif args.recommended_frequency == InterventionFrequency.WEEKLY:
            base_schedule = "Weekly sessions"
        elif args.recommended_frequency == InterventionFrequency.BIWEEKLY:
            base_schedule = "Sessions every two weeks"
        elif args.recommended_frequency == InterventionFrequency.MONTHLY:
            base_schedule = "Monthly sessions"
        else:  # As needed
            base_schedule = "Flexible scheduling based on client needs"
        
        # Adjust based on modalities
        modality_schedules = []
        for modality in args.preferred_modalities:
            if modality == InterventionModality.INDIVIDUAL:
                modality_schedules.append(f"{base_schedule} for individual therapy/counseling")
            elif modality == InterventionModality.GROUP:
                modality_schedules.append(f"Weekly group sessions")
            elif modality == InterventionModality.FAMILY:
                modality_schedules.append(f"Family sessions {args.recommended_frequency.value}")
            elif modality == InterventionModality.CASE_MANAGEMENT:
                modality_schedules.append(f"Case management check-ins {args.recommended_frequency.value}")
            elif modality == InterventionModality.COMMUNITY:
                modality_schedules.append(f"Community-based activities {args.recommended_frequency.value}")
            elif modality == InterventionModality.CRISIS_INTERVENTION:
                modality_schedules.append("Immediate access to crisis services as needed")
        
        # Adjust for resource constraints
        schedule_notes = []
        if args.resource_constraints:
            for constraint in args.resource_constraints:
                constraint_lower = constraint.lower()
                if "transport" in constraint_lower:
                    schedule_notes.append("Consider virtual sessions or providing transportation assistance")
                if "child" in constraint_lower and "care" in constraint_lower:
                    schedule_notes.append("Schedule sessions during times when childcare is available")
                if "work" in constraint_lower:
                    schedule_notes.append("Offer evening or weekend appointments to accommodate work schedule")
        
        # Compile the full schedule recommendation
        full_schedule = "\n".join(modality_schedules)
        
        if schedule_notes:
            full_schedule += "\n\nScheduling considerations:\n- " + "\n- ".join(schedule_notes)
        
        return full_schedule
    
    def _generate_cultural_considerations(self, args: InterventionPlanningInputSchema) -> List[str]:
        """Generate cultural considerations for the intervention plan."""
        considerations = []
        
        # Add standard cultural considerations
        standard_considerations = [
            "Ensure all interventions are culturally responsive and appropriate",
            "Consider how cultural factors might influence understanding of problems and solutions",
            "Respect the client's cultural identity and incorporate cultural strengths"
        ]
        considerations.extend(standard_considerations)
        
        # Add specific considerations based on provided cultural factors
        if args.cultural_factors:
            for factor, value in args.cultural_factors.items():
                factor_lower = factor.lower()
                
                if "language" in factor_lower:
                    considerations.append(f"Address language needs through {value}")
                elif "religion" in factor_lower or "spiritual" in factor_lower:
                    considerations.append(f"Respect and incorporate {value} beliefs and practices where appropriate")
                elif "famil" in factor_lower:
                    considerations.append(f"Consider {value} family structure and dynamics in intervention planning")
                elif "communit" in factor_lower:
                    considerations.append(f"Engage with {value} community resources and supports")
                elif "gender" in factor_lower:
                    considerations.append(f"Ensure gender-sensitive approach accounting for {value}")
                elif "generation" in factor_lower or "age" in factor_lower:
                    considerations.append(f"Address generational or age-related factors regarding {value}")
                else:
                    considerations.append(f"Consider impact of {factor}: {value} on intervention approach")
        
        return considerations
    
    def _generate_collaboration_recommendations(self, args: InterventionPlanningInputSchema, goals: List[InterventionGoal]) -> List[str]:
        """Generate recommendations for collaboration with other providers."""
        recommendations = [
            "Maintain regular communication with all service providers involved in care",
            "Obtain appropriate releases of information for coordination of care",
            "Include client in all collaborative discussions and decisions"
        ]
        
        # Add recommendations based on common needs
        concern_collaboration_map = {
            "mental health": ["Collaborate with mental health providers on treatment coordination"],
            "substance": ["Coordinate with substance use treatment providers"],
            "medical": ["Consult with healthcare providers regarding medical needs"],
            "housing": ["Partner with housing specialists or case managers"],
            "legal": ["Coordinate with legal advocates or attorneys as needed"],
            "education": ["Collaborate with educational professionals"],
            "employment": ["Partner with vocational rehabilitation or employment specialists"],
            "benefits": ["Coordinate with benefits counselors or case managers"],
            "child": ["Consult with child welfare professionals as appropriate"],
            "famil": ["Engage family members in the intervention process with client consent"]
        }
        
        # Check primary concerns for relevant collaborations
        for concern in args.primary_concerns:
            concern_lower = concern.lower()
            for keyword, collab_recommendations in concern_collaboration_map.items():
                if keyword in concern_lower:
                    for recommendation in collab_recommendations:
                        if recommendation not in recommendations:
                            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_review_schedule(self, args: InterventionPlanningInputSchema) -> str:
        """Generate a schedule for reviewing the intervention plan."""
        # Determine base review frequency based on intervention frequency
        if args.recommended_frequency == InterventionFrequency.DAILY:
            base_review = "Review progress weekly initially, then biweekly as stabilization occurs"
        elif args.recommended_frequency == InterventionFrequency.WEEKLY:
            base_review = "Conduct formal progress review every 30 days"
        elif args.recommended_frequency == InterventionFrequency.BIWEEKLY:
            base_review = "Conduct formal progress review every 60 days"
        elif args.recommended_frequency == InterventionFrequency.MONTHLY:
            base_review = "Conduct formal progress review every 90 days"
        else:  # As needed
            base_review = "Review progress after every 4-6 contacts"
        
        # Add crisis contingency if risk factors present
        crisis_review = ""
        if args.risk_factors:
            crisis_review = "\n\nImmediately review and update plan if any crisis occurs or risk level increases. "
            
        # Add complete plan review timeframe
        complete_review = "\n\nConduct comprehensive assessment and plan revision every 6 months or when significant changes occur in client circumstances."
        
        return base_review + crisis_review + complete_review
    
    def _determine_if_human_review_needed(self, args: InterventionPlanningInputSchema, goals: List[InterventionGoal]) -> bool:
        """Determine if human review is needed for this intervention plan."""
        # Check for high-risk concerns
        high_risk_keywords = [
            "suicid", "self-harm", "harm to others", "violence", "abuse", "neglect",
            "crisis", "emergency", "severe", "critical", "hospitalization"
        ]
        
        for concern in args.primary_concerns:
            if any(keyword in concern.lower() for keyword in high_risk_keywords):
                return True
        
        # Check for risk factors if provided
        if args.risk_factors:
            for factor in args.risk_factors:
                if any(keyword in factor.lower() for keyword in high_risk_keywords):
                    return True
        
        # Check for complex cultural factors
        if args.cultural_factors and len(args.cultural_factors) >= 3:
            return True
        
        # Check for multiple modalities (complex intervention)
        if len(args.preferred_modalities) >= 3:
            return True
        
        # Check for multiple goals (complex case)
        if len(args.intervention_goals) >= 4:
            return True
        
        # Check for limited resources with high needs
        if args.resource_constraints and len(args.primary_concerns) >= 3:
            return True
        
        return False
    
    def requires_human_review(self, args: InterventionPlanningInputSchema, result: InterventionPlanningResult) -> bool:
        """Determine if human review is required for this intervention plan.
        
        Args:
            args: The validated arguments
            result: The tool result
            
        Returns:
            Boolean indicating if human review is required
        """
        # The result already contains this determination
        return result.human_review_recommended


def register_socialwork_tools() -> List[str]:
    """Register all social work tools and return their names.
    
    Returns:
        List of registered tool names
    """
    # In a production environment, this would register the tools with a tool registry
    tools = [
        CaseManagementAssessmentTool(),
        InterventionPlanningTool()
    ]
    
    return [tool.name for tool in tools]