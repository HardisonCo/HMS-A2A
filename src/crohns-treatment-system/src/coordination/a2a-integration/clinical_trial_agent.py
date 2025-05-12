#!/usr/bin/env python3
"""
Clinical Trial Agent for the Crohn's Disease Treatment System

This module provides a specialized agent for managing adaptive clinical trials,
including patient allocation, trial design, and treatment assignment.
"""

import os
import sys
import json
import logging
import asyncio
import random
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import datetime

from core import Agent, AgentRole, MessageType, AgentMessage

class TrialPhase(Enum):
    """Clinical trial phases"""
    PLANNING = "planning"
    ENROLLMENT = "enrollment"
    TREATMENT = "treatment"
    ANALYSIS = "analysis"
    COMPLETED = "completed"
    TERMINATED = "terminated"

class TrialDesign(Enum):
    """Types of adaptive trial designs"""
    MAMS = "multi_arm_multi_stage"
    RESPONSE_ADAPTIVE = "response_adaptive"
    SEAMLESS = "seamless_phase_2_3"
    SAMPLE_SIZE = "sample_size_reestimation"
    ENRICHMENT = "population_enrichment"
    PLATFORM = "platform_trial"

class AllocationStrategy(Enum):
    """Patient allocation strategies"""
    FIXED = "fixed_ratio"
    THOMPSON = "thompson_sampling"
    BAR = "bayesian_adaptive_randomization"
    GITTINS = "gittins_index"
    COHORT = "cohort_based"

class PatientStatus(Enum):
    """Status of patients in the trial"""
    SCREENING = "screening"
    ENROLLED = "enrolled"
    TREATMENT = "treatment"
    FOLLOW_UP = "follow_up"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"

@dataclass
class TreatmentArm:
    """Represents a treatment arm in the clinical trial"""
    arm_id: str
    name: str
    description: str
    active: bool = True
    treatments: List[Dict[str, Any]] = field(default_factory=list)
    enrollment_count: int = 0
    response_rate: float = 0.0
    safety_issues: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "arm_id": self.arm_id,
            "name": self.name,
            "description": self.description,
            "active": self.active,
            "treatments": self.treatments,
            "enrollment_count": self.enrollment_count,
            "response_rate": self.response_rate,
            "safety_issues": self.safety_issues
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TreatmentArm':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class Patient:
    """Represents a patient in the clinical trial"""
    patient_id: str
    demographics: Dict[str, Any]
    biomarkers: Dict[str, Any]
    medical_history: Dict[str, Any]
    status: PatientStatus = PatientStatus.SCREENING
    assigned_arm: Optional[str] = None
    enrollment_date: Optional[str] = None
    treatments: List[Dict[str, Any]] = field(default_factory=list)
    outcomes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "patient_id": self.patient_id,
            "demographics": self.demographics,
            "biomarkers": self.biomarkers,
            "medical_history": self.medical_history,
            "status": self.status.value,
            "assigned_arm": self.assigned_arm,
            "enrollment_date": self.enrollment_date,
            "treatments": self.treatments,
            "outcomes": self.outcomes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Patient':
        """Create from dictionary"""
        if "status" in data and isinstance(data["status"], str):
            data["status"] = PatientStatus(data["status"])
        return cls(**data)

class ClinicalTrialAgent(Agent):
    """Agent responsible for managing adaptive clinical trials"""
    
    def __init__(self, agent_id: str, name: Optional[str] = None):
        super().__init__(agent_id, AgentRole.CLINICAL, name)
        
        # Register message handlers
        self.register_handler(MessageType.COMMAND, self._handle_command)
        self.register_handler(MessageType.QUERY, self._handle_query)
        self.register_handler(MessageType.DATA, self._handle_data)
        
        # Trial data
        self.trials: Dict[str, Dict[str, Any]] = {}
        
        self.logger = logging.getLogger(f'hms-a2a.clinical-trial')
    
    async def _handle_command(self, message: AgentMessage):
        """Handle command messages"""
        command = message.content.get('command')
        
        if command == 'create_trial':
            # Create a new clinical trial
            trial_id = str(uuid.uuid4())
            trial_data = message.content.get('trial_data', {})
            
            # Create the trial
            self.trials[trial_id] = {
                'trial_id': trial_id,
                'name': trial_data.get('name', f'Trial {trial_id[:8]}'),
                'description': trial_data.get('description', ''),
                'design': TrialDesign(trial_data.get('design', TrialDesign.MAMS.value)),
                'allocation_strategy': AllocationStrategy(trial_data.get('allocation_strategy', AllocationStrategy.FIXED.value)),
                'phase': TrialPhase.PLANNING,
                'arms': {},
                'patients': {},
                'current_analysis': None,
                'analyses_history': [],
                'adaptations': [],
                'created_at': datetime.datetime.now().isoformat(),
                'updated_at': datetime.datetime.now().isoformat(),
                'creator': message.sender_id
            }
            
            # Add treatment arms if provided
            if 'arms' in trial_data:
                for arm_data in trial_data['arms']:
                    arm_id = str(uuid.uuid4())
                    arm = TreatmentArm(
                        arm_id=arm_id,
                        name=arm_data.get('name', f'Arm {arm_id[:8]}'),
                        description=arm_data.get('description', ''),
                        treatments=arm_data.get('treatments', [])
                    )
                    self.trials[trial_id]['arms'][arm_id] = arm
            
            # Send response
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {
                    'status': 'created',
                    'trial_id': trial_id
                },
                correlation_id=message.message_id
            )
        
        elif command == 'start_enrollment':
            # Start the enrollment phase for a trial
            trial_id = message.content.get('trial_id')
            if trial_id not in self.trials:
                await self.send_error(message, f'Trial {trial_id} not found')
                return
            
            trial = self.trials[trial_id]
            if trial['phase'] != TrialPhase.PLANNING:
                await self.send_error(message, f'Trial {trial_id} is not in planning phase')
                return
            
            # Update trial phase
            trial['phase'] = TrialPhase.ENROLLMENT
            trial['enrollment_start'] = datetime.datetime.now().isoformat()
            trial['updated_at'] = datetime.datetime.now().isoformat()
            
            # Send response
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {
                    'status': 'enrollment_started',
                    'trial_id': trial_id
                },
                correlation_id=message.message_id
            )
        
        elif command == 'add_patient':
            # Add a patient to the trial
            trial_id = message.content.get('trial_id')
            patient_data = message.content.get('patient_data', {})
            
            if trial_id not in self.trials:
                await self.send_error(message, f'Trial {trial_id} not found')
                return
            
            trial = self.trials[trial_id]
            if trial['phase'] != TrialPhase.ENROLLMENT and trial['phase'] != TrialPhase.TREATMENT:
                await self.send_error(message, f'Trial {trial_id} is not in enrollment or treatment phase')
                return
            
            # Create patient
            patient_id = patient_data.get('patient_id', str(uuid.uuid4()))
            patient = Patient(
                patient_id=patient_id,
                demographics=patient_data.get('demographics', {}),
                biomarkers=patient_data.get('biomarkers', {}),
                medical_history=patient_data.get('medical_history', {})
            )
            
            # Add patient to trial
            trial['patients'][patient_id] = patient
            
            # Allocate patient to treatment arm
            allocation_result = await self._allocate_patient(trial_id, patient_id)
            
            # Send response
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {
                    'status': 'patient_added',
                    'trial_id': trial_id,
                    'patient_id': patient_id,
                    'allocation': allocation_result
                },
                correlation_id=message.message_id
            )
        
        elif command == 'record_outcome':
            # Record patient outcome
            trial_id = message.content.get('trial_id')
            patient_id = message.content.get('patient_id')
            outcome_data = message.content.get('outcome_data', {})
            
            if trial_id not in self.trials:
                await self.send_error(message, f'Trial {trial_id} not found')
                return
            
            trial = self.trials[trial_id]
            if patient_id not in trial['patients']:
                await self.send_error(message, f'Patient {patient_id} not found in trial {trial_id}')
                return
            
            # Update patient outcomes
            patient = trial['patients'][patient_id]
            patient.outcomes.update(outcome_data)
            
            # Update trial statistics
            await self._update_trial_statistics(trial_id)
            
            # Send response
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {
                    'status': 'outcome_recorded',
                    'trial_id': trial_id,
                    'patient_id': patient_id
                },
                correlation_id=message.message_id
            )
        
        elif command == 'run_interim_analysis':
            # Run an interim analysis
            trial_id = message.content.get('trial_id')
            analysis_params = message.content.get('analysis_params', {})
            
            if trial_id not in self.trials:
                await self.send_error(message, f'Trial {trial_id} not found')
                return
            
            # Start analysis
            analysis_id = await self._run_interim_analysis(trial_id, analysis_params)
            
            # Send response
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {
                    'status': 'analysis_started',
                    'trial_id': trial_id,
                    'analysis_id': analysis_id
                },
                correlation_id=message.message_id
            )
        
        elif command == 'adapt_trial':
            # Adapt the trial based on analysis
            trial_id = message.content.get('trial_id')
            adaptations = message.content.get('adaptations', [])
            
            if trial_id not in self.trials:
                await self.send_error(message, f'Trial {trial_id} not found')
                return
            
            # Apply adaptations
            adaptation_results = await self._adapt_trial(trial_id, adaptations)
            
            # Send response
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {
                    'status': 'trial_adapted',
                    'trial_id': trial_id,
                    'adaptation_results': adaptation_results
                },
                correlation_id=message.message_id
            )
    
    async def _handle_query(self, message: AgentMessage):
        """Handle query messages"""
        query_type = message.content.get('query')
        
        if query_type == 'trial_info':
            # Get trial information
            trial_id = message.content.get('trial_id')
            if trial_id not in self.trials:
                await self.send_error(message, f'Trial {trial_id} not found')
                return
            
            # Prepare trial info
            trial = self.trials[trial_id]
            trial_info = {
                'trial_id': trial['trial_id'],
                'name': trial['name'],
                'description': trial['description'],
                'design': trial['design'].value,
                'allocation_strategy': trial['allocation_strategy'].value,
                'phase': trial['phase'].value,
                'arms': {arm_id: arm.to_dict() for arm_id, arm in trial['arms'].items()},
                'patient_count': len(trial['patients']),
                'created_at': trial['created_at'],
                'updated_at': trial['updated_at']
            }
            
            # Send response
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {
                    'trial_info': trial_info
                },
                correlation_id=message.message_id
            )
        
        elif query_type == 'patient_info':
            # Get patient information
            trial_id = message.content.get('trial_id')
            patient_id = message.content.get('patient_id')
            
            if trial_id not in self.trials:
                await self.send_error(message, f'Trial {trial_id} not found')
                return
            
            trial = self.trials[trial_id]
            if patient_id not in trial['patients']:
                await self.send_error(message, f'Patient {patient_id} not found in trial {trial_id}')
                return
            
            # Prepare patient info
            patient = trial['patients'][patient_id]
            patient_info = patient.to_dict()
            
            # Send response
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {
                    'patient_info': patient_info
                },
                correlation_id=message.message_id
            )
        
        elif query_type == 'analysis_result':
            # Get analysis result
            trial_id = message.content.get('trial_id')
            analysis_id = message.content.get('analysis_id')
            
            if trial_id not in self.trials:
                await self.send_error(message, f'Trial {trial_id} not found')
                return
            
            trial = self.trials[trial_id]
            
            # Find analysis
            analysis = None
            if trial['current_analysis'] and trial['current_analysis']['analysis_id'] == analysis_id:
                analysis = trial['current_analysis']
            else:
                for past_analysis in trial['analyses_history']:
                    if past_analysis['analysis_id'] == analysis_id:
                        analysis = past_analysis
                        break
            
            if not analysis:
                await self.send_error(message, f'Analysis {analysis_id} not found for trial {trial_id}')
                return
            
            # Send response
            await self.send_message(
                message.sender_id,
                MessageType.RESPONSE,
                {
                    'analysis_result': analysis
                },
                correlation_id=message.message_id
            )
    
    async def _handle_data(self, message: AgentMessage):
        """Handle data messages"""
        data_type = message.content.get('data_type')
        
        if data_type == 'patient_outcome':
            # Process patient outcome data
            trial_id = message.content.get('trial_id')
            patient_id = message.content.get('patient_id')
            outcome_data = message.content.get('outcome_data', {})
            
            if trial_id not in self.trials:
                self.logger.warning(f'Received outcome data for unknown trial {trial_id}')
                return
            
            trial = self.trials[trial_id]
            if patient_id not in trial['patients']:
                self.logger.warning(f'Received outcome data for unknown patient {patient_id} in trial {trial_id}')
                return
            
            # Update patient outcomes
            patient = trial['patients'][patient_id]
            patient.outcomes.update(outcome_data)
            
            # Update trial statistics
            await self._update_trial_statistics(trial_id)
    
    async def send_error(self, original_message: AgentMessage, error_text: str):
        """Send an error response"""
        await self.send_message(
            original_message.sender_id,
            MessageType.ERROR,
            {
                'error': error_text
            },
            correlation_id=original_message.message_id
        )
    
    async def _allocate_patient(self, trial_id: str, patient_id: str) -> Dict[str, Any]:
        """Allocate a patient to a treatment arm"""
        trial = self.trials[trial_id]
        patient = trial['patients'][patient_id]
        
        # Get active arms
        active_arms = {arm_id: arm for arm_id, arm in trial['arms'].items() if arm.active}
        if not active_arms:
            self.logger.error(f'No active arms in trial {trial_id}')
            return {'status': 'error', 'error': 'No active arms in trial'}
        
        # Allocate based on strategy
        arm_id = None
        if trial['allocation_strategy'] == AllocationStrategy.FIXED:
            # Simple random allocation with equal probabilities
            arm_id = random.choice(list(active_arms.keys()))
        
        elif trial['allocation_strategy'] == AllocationStrategy.THOMPSON:
            # Thompson sampling - allocate based on success probabilities
            arm_successes = {}
            arm_failures = {}
            
            for arm_id, arm in active_arms.items():
                # Start with uniform prior
                arm_successes[arm_id] = 1
                arm_failures[arm_id] = 1
                
                # Count successes and failures
                for pat_id, pat in trial['patients'].items():
                    if pat.assigned_arm == arm_id and 'clinical_response' in pat.outcomes:
                        if pat.outcomes['clinical_response']:
                            arm_successes[arm_id] += 1
                        else:
                            arm_failures[arm_id] += 1
            
            # Sample from beta distributions
            arm_samples = {}
            for arm_id in active_arms:
                arm_samples[arm_id] = random.betavariate(
                    arm_successes[arm_id],
                    arm_failures[arm_id]
                )
            
            # Select arm with highest sample
            arm_id = max(arm_samples, key=arm_samples.get)
        
        else:
            # Default to random allocation
            arm_id = random.choice(list(active_arms.keys()))
        
        # Update patient and arm
        patient.assigned_arm = arm_id
        patient.status = PatientStatus.ENROLLED
        patient.enrollment_date = datetime.datetime.now().isoformat()
        
        active_arms[arm_id].enrollment_count += 1
        
        return {
            'status': 'success',
            'assigned_arm': arm_id,
            'arm_name': active_arms[arm_id].name
        }
    
    async def _update_trial_statistics(self, trial_id: str):
        """Update trial statistics based on patient outcomes"""
        trial = self.trials[trial_id]
        
        # Reset arm statistics
        for arm_id, arm in trial['arms'].items():
            arm.response_rate = 0.0
            arm.safety_issues = 0
        
        # Count responses and safety issues
        arm_responses = {}
        arm_patients = {}
        
        for patient_id, patient in trial['patients'].items():
            if patient.assigned_arm:
                arm_id = patient.assigned_arm
                
                # Initialize counters if needed
                if arm_id not in arm_responses:
                    arm_responses[arm_id] = 0
                    arm_patients[arm_id] = 0
                
                # Count patients with outcomes
                if 'clinical_response' in patient.outcomes:
                    arm_patients[arm_id] += 1
                    if patient.outcomes['clinical_response']:
                        arm_responses[arm_id] += 1
                
                # Count safety issues
                if 'adverse_events' in patient.outcomes:
                    trial['arms'][arm_id].safety_issues += len(patient.outcomes['adverse_events'])
        
        # Calculate response rates
        for arm_id in arm_responses:
            if arm_patients[arm_id] > 0:
                trial['arms'][arm_id].response_rate = arm_responses[arm_id] / arm_patients[arm_id]
    
    async def _run_interim_analysis(self, trial_id: str, analysis_params: Dict[str, Any]) -> str:
        """Run an interim analysis of the trial"""
        trial = self.trials[trial_id]
        
        # Create analysis record
        analysis_id = str(uuid.uuid4())
        analysis = {
            'analysis_id': analysis_id,
            'trial_id': trial_id,
            'timestamp': datetime.datetime.now().isoformat(),
            'params': analysis_params,
            'status': 'running',
            'results': None,
            'recommendations': []
        }
        
        # Store as current analysis
        trial['current_analysis'] = analysis
        
        # In a real implementation, this would call out to statistical analysis services
        # For now, we'll simulate a simple analysis with a delay
        asyncio.create_task(self._simulate_analysis(trial_id, analysis_id))
        
        return analysis_id
    
    async def _simulate_analysis(self, trial_id: str, analysis_id: str):
        """Simulate running an analysis (for demonstration)"""
        await asyncio.sleep(2)  # Simulate processing time
        
        trial = self.trials[trial_id]
        if trial['current_analysis'] is None or trial['current_analysis']['analysis_id'] != analysis_id:
            self.logger.warning(f'Analysis {analysis_id} no longer current for trial {trial_id}')
            return
        
        analysis = trial['current_analysis']
        
        # Generate simple analysis results
        arm_results = {}
        for arm_id, arm in trial['arms'].items():
            arm_results[arm_id] = {
                'arm_id': arm_id,
                'name': arm.name,
                'enrollment_count': arm.enrollment_count,
                'response_rate': arm.response_rate,
                'safety_issues': arm.safety_issues,
                'estimated_effect': arm.response_rate - 0.3,  # Assuming 30% baseline
                'confidence_interval': [arm.response_rate - 0.15, arm.response_rate + 0.15]
            }
        
        # Generate recommendations
        recommendations = []
        
        # Check for poorly performing arms
        for arm_id, result in arm_results.items():
            if result['response_rate'] < 0.2 and result['enrollment_count'] >= 10:
                recommendations.append({
                    'type': 'drop_arm',
                    'arm_id': arm_id,
                    'reason': 'Low response rate',
                    'priority': 'high'
                })
            elif result['safety_issues'] > result['enrollment_count'] * 0.5:
                recommendations.append({
                    'type': 'drop_arm',
                    'arm_id': arm_id,
                    'reason': 'High rate of safety issues',
                    'priority': 'high'
                })
        
        # Check for sample size adjustment
        total_enrolled = sum(arm.enrollment_count for arm in trial['arms'].values())
        if total_enrolled >= 30 and len(recommendations) == 0:
            best_arm_id = max(arm_results, key=lambda aid: arm_results[aid]['response_rate'])
            best_arm = arm_results[best_arm_id]
            
            if best_arm['response_rate'] > 0.4:
                recommendations.append({
                    'type': 'increase_allocation',
                    'arm_id': best_arm_id,
                    'reason': 'Promising efficacy',
                    'priority': 'medium'
                })
        
        # Update analysis record
        analysis['status'] = 'completed'
        analysis['results'] = {
            'arm_results': arm_results,
            'overall_enrollment': total_enrolled,
            'analysis_time': datetime.datetime.now().isoformat()
        }
        analysis['recommendations'] = recommendations
        
        # Move to history
        trial['analyses_history'].append(analysis)
        trial['current_analysis'] = None
        
        # Notify interested parties (we'll just log for now)
        self.logger.info(f'Analysis {analysis_id} completed for trial {trial_id} with {len(recommendations)} recommendations')
    
    async def _adapt_trial(self, trial_id: str, adaptations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply adaptations to the trial"""
        trial = self.trials[trial_id]
        results = []
        
        for adaptation in adaptations:
            adaptation_type = adaptation.get('type')
            result = {'type': adaptation_type, 'status': 'failed'}
            
            if adaptation_type == 'drop_arm':
                arm_id = adaptation.get('arm_id')
                if arm_id in trial['arms']:
                    arm = trial['arms'][arm_id]
                    arm.active = False
                    result['status'] = 'success'
                    result['arm_id'] = arm_id
                    result['message'] = f'Arm {arm.name} dropped from trial'
                else:
                    result['message'] = f'Arm {arm_id} not found'
            
            elif adaptation_type == 'add_arm':
                arm_data = adaptation.get('arm_data', {})
                arm_id = str(uuid.uuid4())
                arm = TreatmentArm(
                    arm_id=arm_id,
                    name=arm_data.get('name', f'Arm {arm_id[:8]}'),
                    description=arm_data.get('description', ''),
                    treatments=arm_data.get('treatments', [])
                )
                trial['arms'][arm_id] = arm
                result['status'] = 'success'
                result['arm_id'] = arm_id
                result['message'] = f'Added new arm {arm.name} to trial'
            
            elif adaptation_type == 'change_allocation':
                # In a real implementation, this would modify the allocation probabilities
                result['status'] = 'success'
                result['message'] = 'Allocation strategy updated'
            
            elif adaptation_type == 'end_trial':
                trial['phase'] = TrialPhase.COMPLETED
                trial['completion_date'] = datetime.datetime.now().isoformat()
                trial['updated_at'] = datetime.datetime.now().isoformat()
                result['status'] = 'success'
                result['message'] = 'Trial marked as completed'
            
            else:
                result['message'] = f'Unknown adaptation type: {adaptation_type}'
            
            results.append(result)
            
            # Record the adaptation
            trial['adaptations'].append({
                'timestamp': datetime.datetime.now().isoformat(),
                'adaptation': adaptation,
                'result': result
            })
        
        return results

# Example usage
async def main():
    # Create a clinical trial agent
    agent_id = str(uuid.uuid4())
    trial_agent = ClinicalTrialAgent(agent_id, "crohns_trial_manager")
    
    # Start the agent
    await trial_agent.start()
    
    try:
        # Simulate creating a trial
        trial_data = {
            'name': 'Crohn\'s Disease Adaptive Trial',
            'description': 'Multi-arm trial of JAK inhibitors and IL-23 inhibitors for moderate-to-severe Crohn\'s disease',
            'design': TrialDesign.MAMS.value,
            'allocation_strategy': AllocationStrategy.THOMPSON.value,
            'arms': [
                {
                    'name': 'Upadacitinib',
                    'description': 'JAK inhibitor arm',
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
                    'name': 'Risankizumab',
                    'description': 'IL-23 inhibitor arm',
                    'treatments': [
                        {
                            'medication': 'Risankizumab',
                            'dosage': 600.0,
                            'unit': 'mg',
                            'frequency': 'monthly',
                            'duration': 16
                        }
                    ]
                },
                {
                    'name': 'Combination',
                    'description': 'Combination therapy arm',
                    'treatments': [
                        {
                            'medication': 'Upadacitinib',
                            'dosage': 7.5,
                            'unit': 'mg',
                            'frequency': 'daily',
                            'duration': 16
                        },
                        {
                            'medication': 'Risankizumab',
                            'dosage': 300.0,
                            'unit': 'mg',
                            'frequency': 'monthly',
                            'duration': 16
                        }
                    ]
                }
            ]
        }
        
        # Create a message to simulate command
        create_message = AgentMessage(
            sender_id='test',
            receiver_id=agent_id,
            message_type=MessageType.COMMAND,
            content={
                'command': 'create_trial',
                'trial_data': trial_data
            }
        )
        
        # Process the message directly
        await trial_agent.receive_message(create_message)
        
        # Wait for processing
        await asyncio.sleep(1)
        
        # In a real system, we would receive responses via the outbox
        
    finally:
        # Stop the agent
        await trial_agent.stop()

if __name__ == "__main__":
    asyncio.run(main())