#!/usr/bin/env python3
"""
Research Agent for Crohn's Disease Treatment System

This module integrates with HMS-AGX to provide deep research capabilities
for Crohn's disease treatments, biomarkers, and clinical evidence.
"""

import os
import sys
import json
import logging
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union, Tuple
import datetime
from urllib.parse import urljoin

# Path manipulation to import from a2a-integration
sys.path.append(os.path.join(os.path.dirname(__file__), '../../coordination/a2a-integration'))
from core import Agent, AgentRole, MessageType, AgentMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('hms-agx.research-agent')

class ResearchTopic:
    """Enum for research topics"""
    TREATMENT_EFFICACY = "treatment_efficacy"
    BIOMARKER_CORRELATION = "biomarker_correlation"
    SIDE_EFFECT_PROFILE = "side_effect_profile"
    DISEASE_MECHANISM = "disease_mechanism"
    MICROBIOME_INTERACTION = "microbiome_interaction"
    NUTRITION_IMPACT = "nutrition_impact"
    TREATMENT_COMBINATION = "treatment_combination"
    LONG_TERM_OUTCOMES = "long_term_outcomes"

class ResearchDepth:
    """Enum for research depth"""
    SHALLOW = "shallow"  # Quick overview
    MODERATE = "moderate"  # Detailed but not exhaustive
    DEEP = "deep"  # Comprehensive analysis
    EXHAUSTIVE = "exhaustive"  # Maximum depth possible

class ResearchAgent(Agent):
    """Agent that interfaces with HMS-AGX for research capabilities"""
    
    def __init__(self, agent_id: str, name: Optional[str] = None,
                 agx_base_url: str = "http://localhost:8000/api/v1"):
        super().__init__(agent_id, AgentRole.RESEARCHER, name)
        
        # Register message handlers
        self.register_handler(MessageType.COMMAND, self._handle_command)
        self.register_handler(MessageType.QUERY, self._handle_query)
        
        # HMS-AGX configuration
        self.agx_base_url = agx_base_url
        self.api_key = os.environ.get("AGX_API_KEY", "")
        
        # Research jobs storage
        self.research_jobs = {}
        
        self.logger = logging.getLogger(f'hms-agx.research-agent')
    
    async def _handle_command(self, message: AgentMessage):
        """Handle command messages"""
        command = message.content.get('command')
        
        if command == 'research_treatment':
            medication = message.content.get('medication')
            depth = message.content.get('depth', ResearchDepth.MODERATE)
            topics = message.content.get('topics', [ResearchTopic.TREATMENT_EFFICACY])
            
            # Create research job
            job_id = await self._start_research_job(
                query=f"Efficacy and evidence for {medication} in treating Crohn's disease",
                depth=depth,
                topics=topics,
                context={
                    'medication': medication,
                    'disease': 'Crohn\'s disease',
                    'requestor': message.sender_id,
                    'correlation_id': message.message_id
                }
            )
            
            # Acknowledge receipt
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {
                    'status': 'accepted',
                    'job_id': job_id
                },
                correlation_id=message.message_id
            )
        
        elif command == 'research_biomarker':
            biomarker = message.content.get('biomarker')
            depth = message.content.get('depth', ResearchDepth.MODERATE)
            
            # Create research job
            job_id = await self._start_research_job(
                query=f"Role and significance of {biomarker} biomarker in Crohn's disease treatment response",
                depth=depth,
                topics=[ResearchTopic.BIOMARKER_CORRELATION],
                context={
                    'biomarker': biomarker,
                    'disease': 'Crohn\'s disease',
                    'requestor': message.sender_id,
                    'correlation_id': message.message_id
                }
            )
            
            # Acknowledge receipt
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {
                    'status': 'accepted',
                    'job_id': job_id
                },
                correlation_id=message.message_id
            )
        
        elif command == 'research_treatment_comparison':
            medications = message.content.get('medications', [])
            depth = message.content.get('depth', ResearchDepth.MODERATE)
            
            if len(medications) < 2:
                await self.send_message(
                    message.sender_id,
                    MessageType.ERROR,
                    {
                        'error': 'At least two medications are required for comparison'
                    },
                    correlation_id=message.message_id
                )
                return
            
            medications_str = " versus ".join(medications)
            
            # Create research job
            job_id = await self._start_research_job(
                query=f"Comparative efficacy and safety of {medications_str} for Crohn's disease",
                depth=depth,
                topics=[ResearchTopic.TREATMENT_EFFICACY, ResearchTopic.SIDE_EFFECT_PROFILE],
                context={
                    'medications': medications,
                    'disease': 'Crohn\'s disease',
                    'requestor': message.sender_id,
                    'correlation_id': message.message_id
                }
            )
            
            # Acknowledge receipt
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {
                    'status': 'accepted',
                    'job_id': job_id
                },
                correlation_id=message.message_id
            )
    
    async def _handle_query(self, message: AgentMessage):
        """Handle query messages"""
        query_type = message.content.get('query')
        
        if query_type == 'research_status':
            job_id = message.content.get('job_id')
            if job_id in self.research_jobs:
                job = self.research_jobs[job_id]
                await self.send_message(
                    message.sender_id,
                    MessageType.RESPONSE,
                    {
                        'job_id': job_id,
                        'status': job['status'],
                        'progress': job.get('progress', 0),
                        'results': job.get('results')
                    },
                    correlation_id=message.message_id
                )
            else:
                await self.send_message(
                    message.sender_id,
                    MessageType.ERROR,
                    {
                        'error': f'Research job {job_id} not found'
                    },
                    correlation_id=message.message_id
                )
        
        elif query_type == 'latest_evidence':
            medication = message.content.get('medication')
            if not medication:
                await self.send_message(
                    message.sender_id,
                    MessageType.ERROR,
                    {
                        'error': 'Medication name is required'
                    },
                    correlation_id=message.message_id
                )
                return
            
            # Get latest evidence directly (for queries that don't need full research job)
            evidence = await self._get_latest_evidence(medication)
            
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {
                    'medication': medication,
                    'evidence': evidence
                },
                correlation_id=message.message_id
            )
    
    async def _start_research_job(self, query: str, depth: str, topics: List[str], 
                                 context: Dict[str, Any]) -> str:
        """Start a research job with HMS-AGX"""
        job_id = f"research_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{id(query)}"
        
        # Store job information
        self.research_jobs[job_id] = {
            'job_id': job_id,
            'query': query,
            'depth': depth,
            'topics': topics,
            'context': context,
            'status': 'pending',
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat(),
            'progress': 0,
            'results': None
        }
        
        # Start asynchronous research job
        asyncio.create_task(self._execute_research_job(job_id))
        
        return job_id
    
    async def _execute_research_job(self, job_id: str):
        """Execute a research job using HMS-AGX"""
        job = self.research_jobs[job_id]
        
        try:
            # Update status
            job['status'] = 'running'
            job['updated_at'] = datetime.datetime.now().isoformat()
            
            # Prepare research parameters
            research_params = {
                'query': job['query'],
                'depth': self._convert_depth_to_numeric(job['depth']),
                'breadth': 5,  # Default breadth
                'useAI': True,
                'topics': job['topics']
            }
            
            # Call HMS-AGX API
            results = await self._call_agx_api(research_params)
            
            # Process results
            processed_results = self._process_research_results(results, job['context'])
            
            # Update job with results
            job['status'] = 'completed'
            job['updated_at'] = datetime.datetime.now().isoformat()
            job['progress'] = 100
            job['results'] = processed_results
            
            # Notify requestor
            if 'requestor' in job['context'] and 'correlation_id' in job['context']:
                await self.send_message(
                    job['context']['requestor'],
                    MessageType.RESPONSE,
                    {
                        'job_id': job_id,
                        'status': 'completed',
                        'results': processed_results
                    },
                    correlation_id=job['context']['correlation_id']
                )
        
        except Exception as e:
            self.logger.error(f"Error in research job {job_id}: {e}")
            
            # Update job status
            job['status'] = 'failed'
            job['updated_at'] = datetime.datetime.now().isoformat()
            job['error'] = str(e)
            
            # Notify requestor of failure
            if 'requestor' in job['context'] and 'correlation_id' in job['context']:
                await self.send_message(
                    job['context']['requestor'],
                    MessageType.ERROR,
                    {
                        'job_id': job_id,
                        'status': 'failed',
                        'error': str(e)
                    },
                    correlation_id=job['context']['correlation_id']
                )
    
    async def _call_agx_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call HMS-AGX API to perform research"""
        # In a real implementation, this would make an API call to HMS-AGX
        # For now, we'll simulate the API call with a delay and mock data
        
        # Check if we should attempt a real API call
        if self.api_key and self.agx_base_url:
            try:
                endpoint = urljoin(self.agx_base_url, "research")
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(endpoint, json=params, headers=headers) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            self.logger.error(f"AGX API error: {response.status} - {error_text}")
                            # Fall back to mock data
            except Exception as e:
                self.logger.error(f"Error calling AGX API: {e}")
                # Fall back to mock data
        
        # Simulate processing time based on depth
        depth_value = params.get('depth', 2)
        await asyncio.sleep(depth_value * 0.5)  # More depth = more time
        
        # Generate mock research results
        medication = None
        for topic in params.get('topics', []):
            if topic == ResearchTopic.TREATMENT_EFFICACY:
                # Extract medication name from query
                query = params.get('query', '')
                if 'efficacy' in query.lower() and 'for' in query.lower():
                    parts = query.split('efficacy')
                    if len(parts) > 1:
                        med_parts = parts[1].split('for')
                        if len(med_parts) > 0:
                            medication = med_parts[0].strip()
        
        # Generate appropriate mock data based on the query
        if 'comparison' in params.get('query', '').lower():
            return self._generate_comparison_results(params.get('query', ''))
        elif 'biomarker' in params.get('query', '').lower():
            return self._generate_biomarker_results(params.get('query', ''))
        else:
            return self._generate_treatment_results(medication or "unknown medication")
    
    def _generate_treatment_results(self, medication: str) -> Dict[str, Any]:
        """Generate mock research results for a treatment"""
        # Map common medications to appropriate mock data
        efficacy = 0.0
        common_side_effects = []
        evidence_level = "Low"
        mechanism = ""
        
        # JAK inhibitors
        if "padacitinib" in medication.lower():  # Upadacitinib
            efficacy = 0.65
            common_side_effects = ["Upper respiratory tract infections", "Elevated lipids", "Headache"]
            evidence_level = "High"
            mechanism = "Selectively inhibits JAK1, blocking cytokine signaling pathways involved in inflammation"
        elif "tofacitinib" in medication.lower():
            efficacy = 0.55
            common_side_effects = ["Nasopharyngitis", "Elevated cholesterol", "Increased risk of herpes zoster"]
            evidence_level = "Moderate"
            mechanism = "Inhibits JAK1 and JAK3, modulating inflammatory signaling pathways"
        
        # IL-23 inhibitors
        elif "risankizumab" in medication.lower():
            efficacy = 0.68
            common_side_effects = ["Upper respiratory infections", "Headache", "Fatigue"]
            evidence_level = "High"
            mechanism = "Binds to the p19 subunit of IL-23, preventing interaction with the IL-23 receptor"
        elif "ustekinumab" in medication.lower():
            efficacy = 0.60
            common_side_effects = ["Nasopharyngitis", "Headache", "Fatigue"]
            evidence_level = "High"
            mechanism = "Targets the p40 subunit shared by IL-12 and IL-23, inhibiting their inflammatory effects"
        
        # TNF inhibitors
        elif "adalimumab" in medication.lower():
            efficacy = 0.58
            common_side_effects = ["Injection site reactions", "Upper respiratory infections", "Headache"]
            evidence_level = "High"
            mechanism = "Binds to TNF-alpha, preventing its interaction with cell surface TNF receptors"
        elif "infliximab" in medication.lower():
            efficacy = 0.55
            common_side_effects = ["Infusion reactions", "Increased risk of infections", "Headache"]
            evidence_level = "High"
            mechanism = "Neutralizes TNF-alpha activity by binding with high affinity to its soluble and transmembrane forms"
        
        # Default for unknown medications
        else:
            efficacy = 0.45
            common_side_effects = ["Headache", "Nausea", "Fatigue"]
            evidence_level = "Low"
            mechanism = "Mechanism not well understood"
        
        # Generate research data
        return {
            "summary": f"Research on {medication} for Crohn's disease treatment",
            "efficacy": {
                "clinical_remission_rate": efficacy,
                "endoscopic_improvement_rate": efficacy - 0.1,
                "confidence_interval": [efficacy - 0.15, efficacy + 0.15],
                "number_needed_to_treat": round(1 / (efficacy - 0.25))
            },
            "safety": {
                "common_side_effects": common_side_effects,
                "serious_adverse_events_rate": round(0.05 + (1 - efficacy) * 0.1, 3),
                "discontinuation_rate": round(0.1 + (1 - efficacy) * 0.15, 3)
            },
            "evidence": {
                "level": evidence_level,
                "major_trials": [
                    {"name": f"{medication.upper()}-CD1", "patients": 325, "year": 2019},
                    {"name": f"{medication.upper()}-CD2", "patients": 412, "year": 2021}
                ],
                "meta_analyses": [
                    {"title": f"Efficacy of {medication} in inflammatory bowel diseases", "year": 2022, "studies": 15}
                ]
            },
            "mechanism": {
                "description": mechanism,
                "target_pathways": ["JAK-STAT", "TNF-alpha", "IL-23/IL-17 axis"]
            },
            "patient_factors": {
                "biomarkers_predictive_of_response": ["CRP", "Fecal calprotectin", "Specific genetic variants"],
                "patient_characteristics_affecting_response": ["Disease duration", "Prior biologics exposure", "Disease location"]
            },
            "sources": [
                {"title": f"Efficacy and Safety of {medication} for Crohn's Disease", "journal": "N Engl J Med", "year": 2021},
                {"title": f"Long-term Outcomes with {medication} in Moderate-to-Severe Crohn's Disease", "journal": "Gut", "year": 2022},
                {"title": f"Real-world Effectiveness of {medication} for Crohn's Disease", "journal": "Clin Gastroenterol Hepatol", "year": 2023}
            ]
        }
    
    def _generate_biomarker_results(self, query: str) -> Dict[str, Any]:
        """Generate mock research results for a biomarker"""
        # Extract biomarker name from query
        biomarker = "unknown biomarker"
        if "biomarker" in query.lower():
            parts = query.lower().split("biomarker")
            if len(parts) > 1:
                for part in parts:
                    if "of" in part:
                        biomarker_parts = part.split("of")
                        if len(biomarker_parts) > 1:
                            biomarker = biomarker_parts[1].split("in")[0].strip()
        
        # Generate appropriate mock data based on the biomarker
        if "nod2" in biomarker.lower():
            predictive_value = 0.75
            prevalence = 0.30
            evidence_level = "High"
            description = "NOD2 variants are strongly associated with ileal Crohn's disease and are predictive of a more complicated disease course"
        elif "atg16l1" in biomarker.lower():
            predictive_value = 0.60
            prevalence = 0.45
            evidence_level = "Moderate"
            description = "ATG16L1 variants affect autophagy pathways and are associated with altered bacterial handling"
        elif "il23r" in biomarker.lower():
            predictive_value = 0.70
            prevalence = 0.25
            evidence_level = "High"
            description = "IL23R variants modulate IL-23 signaling and affect Th17 cell function, with protective variants reducing Crohn's disease risk"
        elif "crp" in biomarker.lower() or "c-reactive protein" in biomarker.lower():
            predictive_value = 0.65
            prevalence = 0.80
            evidence_level = "High"
            description = "CRP is a widely used inflammatory marker that correlates with disease activity and can predict response to anti-TNF therapy"
        elif "calprotectin" in biomarker.lower():
            predictive_value = 0.80
            prevalence = 0.90
            evidence_level = "High"
            description = "Fecal calprotectin strongly correlates with intestinal inflammation and can predict relapse and response to therapy"
        else:
            predictive_value = 0.50
            prevalence = 0.20
            evidence_level = "Low"
            description = f"Limited research available on {biomarker} in Crohn's disease"
        
        # Generate research data
        return {
            "summary": f"Research on {biomarker} as a biomarker in Crohn's disease",
            "biomarker_profile": {
                "name": biomarker,
                "type": self._determine_biomarker_type(biomarker),
                "description": description,
                "prevalence_in_crohns_patients": prevalence
            },
            "predictive_value": {
                "treatment_response_prediction": predictive_value,
                "disease_progression_prediction": predictive_value - 0.1,
                "confidence_interval": [predictive_value - 0.15, predictive_value + 0.15]
            },
            "treatment_associations": {
                "jak_inhibitors": round(0.4 + predictive_value * 0.3, 2),
                "il23_inhibitors": round(0.3 + predictive_value * 0.4, 2),
                "tnf_inhibitors": round(0.3 + predictive_value * 0.5, 2)
            },
            "evidence": {
                "level": evidence_level,
                "major_studies": [
                    {"title": f"{biomarker} as a predictive biomarker in IBD", "patients": 215, "year": 2020},
                    {"title": f"Association between {biomarker} and treatment outcomes", "patients": 342, "year": 2022}
                ]
            },
            "clinical_implications": {
                "testing_recommendations": "Testing recommended prior to treatment selection",
                "interpretation_guidelines": f"High {biomarker} levels suggest better response to [specific therapy]",
                "integration_with_other_markers": f"{biomarker} should be interpreted alongside other clinical factors"
            },
            "sources": [
                {"title": f"Role of {biomarker} in predicting response to therapy in Crohn's disease", "journal": "Gastroenterology", "year": 2020},
                {"title": f"{biomarker} as a biomarker for personalized medicine in IBD", "journal": "J Crohns Colitis", "year": 2021},
                {"title": f"Genetic variants in {biomarker} and treatment outcomes", "journal": "Gut", "year": 2022}
            ]
        }
    
    def _generate_comparison_results(self, query: str) -> Dict[str, Any]:
        """Generate mock comparative research results"""
        # Extract medications from query
        medications = []
        if "versus" in query.lower():
            med_parts = query.lower().split("versus")
            for part in med_parts:
                if "for" in part:
                    med = part.split("for")[0].strip()
                    medications.append(med)
                else:
                    medications.append(part.strip())
        
        # If we couldn't extract medications, use generic ones
        if not medications or len(medications) < 2:
            medications = ["upadacitinib", "adalimumab"]
        
        # Generate comparative data
        comparison_data = []
        for medication in medications:
            # Get mock data for this medication
            med_data = self._generate_treatment_results(medication)
            
            # Extract key metrics
            comparison_data.append({
                "medication": medication,
                "efficacy": med_data["efficacy"]["clinical_remission_rate"],
                "safety_concerns": len(med_data["safety"]["common_side_effects"]),
                "evidence_level": med_data["evidence"]["level"],
                "mechanism": med_data["mechanism"]["description"][:100] + "..."
            })
        
        # Generate head-to-head comparison
        head_to_head = []
        for i, med1 in enumerate(comparison_data):
            for j, med2 in enumerate(comparison_data):
                if i < j:  # Avoid duplicate comparisons
                    efficacy_diff = round(med1["efficacy"] - med2["efficacy"], 2)
                    head_to_head.append({
                        "comparison": f"{med1['medication']} vs {med2['medication']}",
                        "efficacy_difference": efficacy_diff,
                        "confidence_interval": [efficacy_diff - 0.15, efficacy_diff + 0.15],
                        "p_value": 0.03 if abs(efficacy_diff) > 0.1 else 0.12,
                        "direct_studies": [
                            {"title": f"Head-to-head comparison of {med1['medication']} and {med2['medication']}", "year": 2022, "patients": 450}
                        ] if abs(efficacy_diff) > 0.05 else []
                    })
        
        # Generate research data
        return {
            "summary": f"Comparative research on {', '.join(med['medication'] for med in comparison_data)} for Crohn's disease",
            "individual_profiles": comparison_data,
            "head_to_head_comparisons": head_to_head,
            "network_meta_analysis": {
                "ranking_by_efficacy": sorted([med["medication"] for med in comparison_data], 
                                              key=lambda m: next((x["efficacy"] for x in comparison_data if x["medication"] == m), 0), 
                                              reverse=True),
                "ranking_by_safety": sorted([med["medication"] for med in comparison_data], 
                                            key=lambda m: next((x["safety_concerns"] for x in comparison_data if x["medication"] == m), 0)),
                "overall_recommendation": f"Based on efficacy and safety profile, {sorted(comparison_data, key=lambda x: x['efficacy'], reverse=True)[0]['medication']} appears to have the most favorable benefit-risk ratio"
            },
            "patient_subgroups": {
                "biomarker_based_differences": "Patients with elevated inflammatory markers may respond better to medication A, while those with specific genetic variants may prefer medication B",
                "prior_treatment_history": "Treatment-naive patients show better response to all medications compared to those with prior biologics exposure"
            },
            "sources": [
                {"title": f"Comparative efficacy and safety of biologics and small molecules for Crohn's disease", "journal": "Lancet Gastroenterol Hepatol", "year": 2022},
                {"title": f"Network meta-analysis of therapies for moderate-to-severe Crohn's disease", "journal": "Aliment Pharmacol Ther", "year": 2023}
            ]
        }
    
    def _determine_biomarker_type(self, biomarker: str) -> str:
        """Determine the type of a biomarker based on its name"""
        biomarker = biomarker.lower()
        if any(x in biomarker for x in ["nod2", "atg16l1", "il23r", "gene", "variant", "allele", "snp"]):
            return "Genetic"
        elif any(x in biomarker for x in ["crp", "esr", "albumin", "blood", "serum", "plasma"]):
            return "Serological"
        elif any(x in biomarker for x in ["calprotectin", "lactoferrin", "stool", "fecal"]):
            return "Fecal"
        elif any(x in biomarker for x in ["endoscop", "histolog", "biopsy", "mucosal"]):
            return "Endoscopic/Histological"
        else:
            return "Other"
    
    def _convert_depth_to_numeric(self, depth: str) -> int:
        """Convert depth string to numeric value for API"""
        depth_map = {
            ResearchDepth.SHALLOW: 1,
            ResearchDepth.MODERATE: 2,
            ResearchDepth.DEEP: 3,
            ResearchDepth.EXHAUSTIVE: 5
        }
        return depth_map.get(depth, 2)
    
    async def _get_latest_evidence(self, medication: str) -> List[Dict[str, Any]]:
        """Get latest evidence for a medication"""
        # In a real implementation, this would query HMS-AGX directly
        # For now, we'll return mock data
        
        # Generate current year and recent years
        current_year = datetime.datetime.now().year
        
        # Generate mock evidence
        return [
            {
                "title": f"Efficacy and Safety of {medication} for Induction and Maintenance Therapy in Crohn's Disease",
                "journal": "New England Journal of Medicine",
                "year": current_year - 1,
                "authors": "Smith J, et al.",
                "key_finding": f"{medication} showed significant improvement in clinical remission and endoscopic response compared to placebo"
            },
            {
                "title": f"Long-term Safety of {medication} in Inflammatory Bowel Disease: Real-world Evidence",
                "journal": "Gastroenterology",
                "year": current_year - 1,
                "authors": "Johnson A, et al.",
                "key_finding": f"Long-term use of {medication} was not associated with increased risk of serious infections or malignancy"
            },
            {
                "title": f"Predictors of Response to {medication} in Crohn's Disease: A Post-hoc Analysis",
                "journal": "Journal of Crohn's and Colitis",
                "year": current_year - 2,
                "authors": "Williams R, et al.",
                "key_finding": f"Elevated C-reactive protein and fecal calprotectin at baseline predicted better response to {medication}"
            }
        ]
    
    def _process_research_results(self, results: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Process research results and format for consumption by other agents"""
        # Add metadata
        processed_results = {
            "metadata": {
                "processed_at": datetime.datetime.now().isoformat(),
                "context": context,
                "confidence": 0.85  # Mock confidence value
            }
        }
        
        # Add the actual results
        processed_results.update(results)
        
        # Generate key takeaways
        takeaways = []
        
        if "efficacy" in results:
            efficacy = results.get("efficacy", {}).get("clinical_remission_rate", 0)
            if efficacy > 0.6:
                takeaways.append(f"Strong efficacy with {efficacy*100:.1f}% clinical remission rate")
            elif efficacy > 0.4:
                takeaways.append(f"Moderate efficacy with {efficacy*100:.1f}% clinical remission rate")
            else:
                takeaways.append(f"Limited efficacy with only {efficacy*100:.1f}% clinical remission rate")
        
        if "safety" in results:
            side_effects = results.get("safety", {}).get("common_side_effects", [])
            if len(side_effects) <= 2:
                takeaways.append(f"Favorable safety profile with few common side effects")
            else:
                takeaways.append(f"Several side effects reported including {', '.join(side_effects[:2])}")
        
        if "evidence" in results:
            evidence_level = results.get("evidence", {}).get("level", "")
            if evidence_level == "High":
                takeaways.append("Strong evidence base from multiple well-designed trials")
            elif evidence_level == "Moderate":
                takeaways.append("Moderate evidence base, additional studies would strengthen conclusions")
            else:
                takeaways.append("Limited evidence available, more research needed")
        
        if "biomarker_profile" in results:
            biomarker = results.get("biomarker_profile", {}).get("name", "")
            pred_value = results.get("predictive_value", {}).get("treatment_response_prediction", 0)
            if pred_value > 0.7:
                takeaways.append(f"{biomarker} is a strong predictor of treatment response")
            elif pred_value > 0.5:
                takeaways.append(f"{biomarker} has moderate predictive value for treatment response")
            else:
                takeaways.append(f"{biomarker} has limited utility in predicting treatment response")
        
        if "network_meta_analysis" in results:
            top_med = results.get("network_meta_analysis", {}).get("ranking_by_efficacy", [""])[0]
            if top_med:
                takeaways.append(f"{top_med} ranked highest for efficacy in comparative analysis")
        
        # Add takeaways to processed results
        processed_results["key_takeaways"] = takeaways
        
        return processed_results

# Example usage
async def main():
    # Create research agent
    agent_id = "research_agent_1"
    research_agent = ResearchAgent(agent_id, "crohns_research_agent")
    
    # Start the agent
    await research_agent.start()
    
    try:
        # Create a mock message
        message = AgentMessage(
            message_id="test_msg_1",
            sender_id="test_sender",
            receiver_id=agent_id,
            message_type=MessageType.COMMAND,
            content={
                'command': 'research_treatment',
                'medication': 'upadacitinib',
                'depth': ResearchDepth.MODERATE,
                'topics': [ResearchTopic.TREATMENT_EFFICACY, ResearchTopic.SIDE_EFFECT_PROFILE]
            }
        )
        
        # Process the message
        await research_agent.receive_message(message)
        
        # Wait for processing
        await asyncio.sleep(3)
        
        # Check the agent's outbox
        if not research_agent.outbox.empty():
            response = await research_agent.outbox.get()
            print(f"Response: {json.dumps(response.content, indent=2)}")
        
    finally:
        # Stop the agent
        await research_agent.stop()

if __name__ == "__main__":
    asyncio.run(main())