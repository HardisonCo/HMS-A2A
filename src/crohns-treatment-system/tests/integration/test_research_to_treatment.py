#!/usr/bin/env python3
"""
Integration Test for Research to Treatment Workflow

This test demonstrates the end-to-end workflow from HMS-AGX research
through HMS-A2A coordination to treatment optimization using the
genetic engine.
"""

import os
import sys
import json
import asyncio
import logging
import uuid
from typing import Dict, Any

# Add src directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/coordination/a2a-integration'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/research/agx-integration'))

# Import components
from core import AgentSystem, AgentRole, MessageType, AgentMessage
from research_agent import ResearchAgent, ResearchTopic, ResearchDepth
from clinical_trial_agent import ClinicalTrialAgent
from genetic_engine_ffi import genetic_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('integration-test')

async def run_integration_test():
    """Run the integration test"""
    # Initialize agent system
    logger.info("Initializing agent system")
    agent_system = AgentSystem()
    
    # Create coordinator agent
    coordinator = agent_system.create_agent(AgentRole.COORDINATOR, "test_coordinator")
    
    # Create research agent
    research_agent_id = str(uuid.uuid4())
    research_agent = ResearchAgent(research_agent_id, "test_research_agent")
    agent_system.directory.register_agent(research_agent)
    
    # Create clinical trial agent
    trial_agent_id = str(uuid.uuid4())
    trial_agent = ClinicalTrialAgent(trial_agent_id, "test_trial_agent")
    agent_system.directory.register_agent(trial_agent)
    
    # Start the agent system
    await agent_system.start()
    logger.info("Agent system started")
    
    try:
        # Initialize genetic engine
        await genetic_engine.initialize()
        logger.info("Genetic engine initialized")
        
        # Step 1: Research a treatment
        logger.info("Step 1: Researching treatment")
        research_message = AgentMessage(
            message_id=str(uuid.uuid4()),
            sender_id=coordinator.agent_id,
            receiver_id=research_agent.agent_id,
            message_type=MessageType.COMMAND,
            content={
                'command': 'research_treatment',
                'medication': 'upadacitinib',
                'depth': ResearchDepth.MODERATE,
                'topics': [ResearchTopic.TREATMENT_EFFICACY, ResearchTopic.SIDE_EFFECT_PROFILE]
            }
        )
        
        await coordinator.send_message(
            research_agent.agent_id,
            MessageType.COMMAND,
            {
                'command': 'research_treatment',
                'medication': 'upadacitinib',
                'depth': ResearchDepth.MODERATE,
                'topics': [ResearchTopic.TREATMENT_EFFICACY, ResearchTopic.SIDE_EFFECT_PROFILE]
            }
        )
        
        # Wait for research to complete
        research_response = None
        for _ in range(10):
            if not coordinator.inbox.empty():
                message = await coordinator.inbox.get()
                if message.sender_id == research_agent.agent_id:
                    research_response = message
                    break
            await asyncio.sleep(0.5)
        
        if not research_response:
            logger.error("No research response received")
            return False
        
        research_job_id = research_response.content.get('job_id')
        logger.info(f"Research job created: {research_job_id}")
        
        # Wait for research job to complete
        research_result = None
        for _ in range(10):
            await coordinator.send_message(
                research_agent.agent_id,
                MessageType.QUERY,
                {
                    'query': 'research_status',
                    'job_id': research_job_id
                }
            )
            
            await asyncio.sleep(1)
            
            if not coordinator.inbox.empty():
                message = await coordinator.inbox.get()
                if message.sender_id == research_agent.agent_id:
                    if message.content.get('status') == 'completed':
                        research_result = message.content.get('results')
                        break
        
        if not research_result:
            logger.error("Research did not complete")
            return False
        
        logger.info(f"Research complete: {json.dumps(research_result.get('key_takeaways', []), indent=2)}")
        
        # Step 2: Create a clinical trial
        logger.info("Step 2: Creating clinical trial")
        trial_data = {
            'name': 'Upadacitinib Adaptive Trial',
            'description': 'Adaptive trial for upadacitinib in moderate-to-severe Crohn\'s disease',
            'design': 'multi_arm_multi_stage',
            'allocation_strategy': 'thompson_sampling',
            'arms': [
                {
                    'name': 'Upadacitinib Standard',
                    'description': 'JAK inhibitor arm - standard dose',
                    'treatments': [
                        {
                            'medication': 'Upadacitinib',
                            'dosage': 15.0,
                            'unit': 'mg',
                            'frequency': 'daily',
                            'duration': 16
                        }
                    ]
                },
                {
                    'name': 'Upadacitinib High',
                    'description': 'JAK inhibitor arm - high dose',
                    'treatments': [
                        {
                            'medication': 'Upadacitinib',
                            'dosage': 30.0,
                            'unit': 'mg',
                            'frequency': 'daily',
                            'duration': 16
                        }
                    ]
                }
            ]
        }
        
        await coordinator.send_message(
            trial_agent.agent_id,
            MessageType.COMMAND,
            {
                'command': 'create_trial',
                'trial_data': trial_data
            }
        )
        
        # Wait for trial creation response
        trial_response = None
        for _ in range(5):
            if not coordinator.inbox.empty():
                message = await coordinator.inbox.get()
                if message.sender_id == trial_agent.agent_id:
                    trial_response = message
                    break
            await asyncio.sleep(0.5)
        
        if not trial_response:
            logger.error("No trial creation response received")
            return False
        
        trial_id = trial_response.content.get('trial_id')
        logger.info(f"Trial created: {trial_id}")
        
        # Step 3: Add a patient to trial
        logger.info("Step 3: Adding patient to trial")
        patient_data = {
            'patient_id': 'P12345',
            'demographics': {
                'age': 45,
                'sex': 'male',
                'weight': 70.5
            },
            'biomarkers': {
                'genetic_markers': {
                    'NOD2': 'variant',
                    'ATG16L1': 'normal',
                    'IL23R': 'variant'
                },
                'fecal_calprotectin': 350,
                'crp': 15.2
            },
            'medical_history': {
                'crohns_type': 'ileocolonic',
                'disease_duration': 5,
                'prior_treatments': [
                    {
                        'medication': 'Infliximab',
                        'response': 'partial'
                    }
                ]
            }
        }
        
        await coordinator.send_message(
            trial_agent.agent_id,
            MessageType.COMMAND,
            {
                'command': 'add_patient',
                'trial_id': trial_id,
                'patient_data': patient_data
            }
        )
        
        # Wait for patient addition response
        patient_response = None
        for _ in range(5):
            if not coordinator.inbox.empty():
                message = await coordinator.inbox.get()
                if message.sender_id == trial_agent.agent_id:
                    patient_response = message
                    break
            await asyncio.sleep(0.5)
        
        if not patient_response:
            logger.error("No patient addition response received")
            return False
        
        allocation = patient_response.content.get('allocation')
        logger.info(f"Patient allocated: {json.dumps(allocation, indent=2)}")
        
        # Step 4: Optimize patient-specific treatment
        logger.info("Step 4: Optimizing patient-specific treatment")
        treatment_result = await genetic_engine.optimize_treatment(patient_data)
        
        logger.info(f"Treatment optimized: {json.dumps(treatment_result, indent=2)}")
        
        # Test passed
        logger.info("Integration test passed successfully!")
        return True
        
    finally:
        # Shutdown genetic engine
        await genetic_engine.shutdown()
        
        # Stop the agent system
        await agent_system.stop()
        logger.info("Agent system stopped")

async def main():
    """Main entry point"""
    try:
        success = await run_integration_test()
        print(f"Integration test {'PASSED' if success else 'FAILED'}")
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Integration test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())