# Crohn's Disease Treatment System: Integration Points

This document details the key integration points between components of the Crohn's Disease Treatment System, including FFI interfaces, API definitions, and communication protocols.

## 1. Rust-Python FFI Integration (Genetic Engine ↔ HMS-A2A)

The genetic optimization engine is implemented in Rust for performance, while the HMS-A2A agent system is implemented in Python. This integration uses PyO3 to create Python bindings for the Rust code.

### Interface Definition

```rust
// src/coordination/genetic-engine/ffi.rs

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use std::sync::Arc;

use crate::genetic_engine::{GeneticEngine, TreatmentPlan, PatientData, GeneticConfig};

#[pyclass]
pub struct PyGeneticConfig {
    #[pyo3(get, set)]
    pub population_size: usize,
    #[pyo3(get, set)]
    pub generations: usize,
    #[pyo3(get, set)]
    pub mutation_rate: f64,
    #[pyo3(get, set)]
    pub crossover_rate: f64,
    #[pyo3(get, set)]
    pub elitism_count: usize,
    #[pyo3(get, set)]
    pub tournament_size: usize,
}

impl Default for PyGeneticConfig {
    fn default() -> Self {
        Self {
            population_size: 100,
            generations: 50,
            mutation_rate: 0.1,
            crossover_rate: 0.7,
            elitism_count: 5,
            tournament_size: 3,
        }
    }
}

impl From<PyGeneticConfig> for GeneticConfig {
    fn from(config: PyGeneticConfig) -> Self {
        GeneticConfig {
            population_size: config.population_size,
            generations: config.generations,
            mutation_rate: config.mutation_rate,
            crossover_rate: config.crossover_rate,
            elitism_count: config.elitism_count,
            tournament_size: config.tournament_size,
        }
    }
}

#[pymodule]
fn genetic_engine_ffi(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<CrohnsTreatmentOptimizer>()?;
    m.add_class::<PyGeneticConfig>()?;
    m.add_function(wrap_pyfunction!(optimize_treatment, m)?)?;
    m.add_function(wrap_pyfunction!(evaluate_biomarkers, m)?)?;
    m.add_function(wrap_pyfunction!(analyze_genetic_sequences, m)?)?;
    Ok(())
}

#[pyclass]
struct CrohnsTreatmentOptimizer {
    engine: Arc<GeneticEngine>,
    config: PyGeneticConfig,
}

#[pymethods]
impl CrohnsTreatmentOptimizer {
    #[new]
    fn new(config: Option<PyGeneticConfig>) -> Self {
        let config = config.unwrap_or_default();
        let engine = Arc::new(GeneticEngine::new(config.clone().into()));
        CrohnsTreatmentOptimizer { engine, config }
    }
    
    fn optimize_treatment(&self, py: Python, patient_data: PyObject) -> PyResult<PyObject> {
        // Convert PyObject to Rust PatientData
        let patient: PatientData = patient_data.extract(py)?;
        
        // Run optimization using genetic algorithm
        let treatment_plan = self.engine.optimize_treatment(patient);
        
        // Convert result back to Python dict
        Ok(treatment_plan.into_py(py))
    }
    
    fn evaluate_biomarkers(&self, py: Python, biomarker_data: PyObject) -> PyResult<PyObject> {
        let biomarkers = biomarker_data.extract(py)?;
        let result = self.engine.evaluate_biomarkers(biomarkers);
        Ok(result.into_py(py))
    }
    
    #[getter]
    fn get_config(&self) -> PyGeneticConfig {
        self.config.clone()
    }
    
    #[setter]
    fn set_config(&mut self, config: PyGeneticConfig) {
        self.config = config.clone();
        self.engine = Arc::new(GeneticEngine::new(config.into()));
    }
}

#[pyfunction]
fn optimize_treatment(py: Python, patient_data: PyObject, config: Option<PyGeneticConfig>) -> PyResult<PyObject> {
    let optimizer = CrohnsTreatmentOptimizer::new(config);
    optimizer.optimize_treatment(py, patient_data)
}

#[pyfunction]
fn evaluate_biomarkers(py: Python, biomarker_data: PyObject, config: Option<PyGeneticConfig>) -> PyResult<PyObject> {
    let optimizer = CrohnsTreatmentOptimizer::new(config);
    optimizer.evaluate_biomarkers(py, biomarker_data)
}

#[pyfunction]
fn analyze_genetic_sequences(py: Python, sequence_data: PyObject) -> PyResult<PyObject> {
    // Convert PyObject to Rust GeneticSequenceData
    let sequences = sequence_data.extract(py)?;
    
    // Analyze sequences using Rust implementation
    let result = crate::genetic_engine::analyze_sequences(sequences);
    
    // Convert back to Python dict
    Ok(result.into_py(py))
}
```

### Python Integration

```python
# src/coordination/a2a-integration/genetic_engine_ffi.py

from typing import Dict, Any, List, Optional
import json
import asyncio
from .event_bus import EventBus

# Import the Rust FFI module
from genetic_engine_ffi import (
    CrohnsTreatmentOptimizer, 
    PyGeneticConfig,
    optimize_treatment,
    evaluate_biomarkers,
    analyze_genetic_sequences
)

class GeneticEngineIntegration:
    """Integration class for the Rust-based genetic engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, event_bus: Optional[EventBus] = None):
        """Initialize the genetic engine integration
        
        Args:
            config: Configuration parameters for the genetic algorithm
            event_bus: Event bus for publishing events
        """
        # Create PyGeneticConfig from dict if provided
        py_config = None
        if config:
            py_config = PyGeneticConfig(
                population_size=config.get("population_size", 100),
                generations=config.get("generations", 50),
                mutation_rate=config.get("mutation_rate", 0.1),
                crossover_rate=config.get("crossover_rate", 0.7),
                elitism_count=config.get("elitism_count", 5),
                tournament_size=config.get("tournament_size", 3)
            )
            
        # Initialize the Rust optimizer
        self.optimizer = CrohnsTreatmentOptimizer(py_config)
        self.event_bus = event_bus
        
    async def optimize_patient_treatment(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize treatment for a specific patient using genetic algorithm
        
        Args:
            patient_data: Patient data including demographics, biomarkers, and history
            
        Returns:
            Optimized treatment plan with fitness score and explanations
        """
        # Transform patient data into the format expected by the Rust FFI
        transformed_data = self._transform_patient_data(patient_data)
        
        # Call the Rust implementation (run in thread pool to avoid blocking)
        loop = asyncio.get_event_loop()
        treatment_plan = await loop.run_in_executor(
            None, 
            lambda: self.optimizer.optimize_treatment(transformed_data)
        )
        
        # Transform the result back to the format expected by the HMS-A2A system
        result = self._transform_treatment_plan(treatment_plan)
        
        # Publish event if event_bus is available
        if self.event_bus:
            await self.event_bus.publish(
                "treatment_optimized",
                {
                    "patient_id": patient_data.get("patient_id"),
                    "treatment_plan": result
                }
            )
            
        return result
        
    async def evaluate_patient_biomarkers(self, biomarker_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate biomarkers for therapeutic significance
        
        Args:
            biomarker_data: Patient biomarker data
            
        Returns:
            Biomarker evaluation results
        """
        loop = asyncio.get_event_loop()
        evaluation = await loop.run_in_executor(
            None,
            lambda: self.optimizer.evaluate_biomarkers(biomarker_data)
        )
        
        return evaluation
        
    async def analyze_genetic_data(self, sequence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze genetic sequence data for Crohn's disease variants
        
        Args:
            sequence_data: Genetic sequence data for analysis
            
        Returns:
            Analysis results including variants and recommendations
        """
        loop = asyncio.get_event_loop()
        analysis = await loop.run_in_executor(
            None,
            lambda: analyze_genetic_sequences(sequence_data)
        )
        
        return analysis
        
    def update_config(self, config: Dict[str, Any]) -> None:
        """Update the genetic algorithm configuration
        
        Args:
            config: New configuration parameters
        """
        py_config = PyGeneticConfig(
            population_size=config.get("population_size", 100),
            generations=config.get("generations", 50),
            mutation_rate=config.get("mutation_rate", 0.1),
            crossover_rate=config.get("crossover_rate", 0.7),
            elitism_count=config.get("elitism_count", 5),
            tournament_size=config.get("tournament_size", 3)
        )
        
        self.optimizer.set_config(py_config)
        
    def _transform_patient_data(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform patient data into format expected by Rust FFI"""
        # Implement the transformation logic here
        # This might involve flattening nested structures, converting units, etc.
        return {
            "patient_id": patient_data.get("patient_id", ""),
            "age": patient_data.get("demographics", {}).get("age", 0),
            "sex": patient_data.get("demographics", {}).get("sex", ""),
            "weight": patient_data.get("demographics", {}).get("weight", 0),
            "height": patient_data.get("demographics", {}).get("height", 0),
            "crohns_type": patient_data.get("clinical_data", {}).get("crohns_type", ""),
            "disease_activity": {
                "cdai": patient_data.get("clinical_data", {}).get("disease_activity", {}).get("CDAI", 0),
                "ses_cd": patient_data.get("clinical_data", {}).get("disease_activity", {}).get("SES-CD", 0),
                "fecal_calprotectin": patient_data.get("clinical_data", {}).get("disease_activity", {}).get("fecal_calprotectin", 0)
            },
            "genetic_markers": [
                {
                    "gene": marker.get("gene", ""),
                    "variant": marker.get("variant", ""),
                    "zygosity": marker.get("zygosity", "")
                }
                for marker in patient_data.get("biomarkers", {}).get("genetic_markers", [])
            ],
            "treatment_history": [
                {
                    "medication": treatment.get("medication", ""),
                    "response": treatment.get("response", ""),
                    "adverse_events": treatment.get("adverse_events", [])
                }
                for treatment in patient_data.get("treatment_history", [])
            ]
        }
        
    def _transform_treatment_plan(self, treatment_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Transform treatment plan from Rust FFI format to HMS-A2A format"""
        # Implement the transformation logic here
        return {
            "treatment_plan": [
                {
                    "medication": med.get("medication", ""),
                    "dosage": med.get("dosage", 0),
                    "unit": med.get("unit", ""),
                    "frequency": med.get("frequency", ""),
                    "duration": med.get("duration", 0)
                }
                for med in treatment_plan.get("treatment_plan", [])
            ],
            "fitness": treatment_plan.get("fitness", 0),
            "confidence": treatment_plan.get("confidence", 0),
            "explanations": treatment_plan.get("explanations", []),
            "biomarker_influences": treatment_plan.get("biomarker_influences", {})
        }
```

## 2. WebAssembly Integration (Treatment Verification ↔ Web Interface)

The treatment verification component is exposed to web interfaces using WebAssembly.

### Rust WebAssembly Module

```rust
// src/coordination/genetic-engine/wasm_bindings.rs

use wasm_bindgen::prelude::*;
use serde::{Serialize, Deserialize};
use serde_json;

use crate::genetic_engine::{GeneticEngine, TreatmentPlan, TreatmentVerification};

#[wasm_bindgen]
pub struct CrohnsTreatmentVerifier {
    engine: GeneticEngine,
}

#[derive(Serialize, Deserialize)]
pub struct VerificationResult {
    pub is_valid: bool,
    pub safety_score: f64,
    pub efficacy_score: f64,
    pub warnings: Vec<String>,
    pub recommendations: Vec<String>,
}

#[wasm_bindgen]
impl CrohnsTreatmentVerifier {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        CrohnsTreatmentVerifier {
            engine: GeneticEngine::default(),
        }
    }
    
    pub fn verify_treatment_plan(&self, treatment_json: String) -> Result<String, JsValue> {
        // Parse the treatment plan from JSON
        let treatment: TreatmentPlan = serde_json::from_str(&treatment_json)
            .map_err(|e| JsValue::from_str(&format!("Error parsing treatment plan: {}", e)))?;
        
        // Verify the treatment plan
        let verification = self.engine.verify_treatment(treatment);
        
        // Create verification result
        let result = VerificationResult {
            is_valid: verification.is_valid,
            safety_score: verification.safety_score,
            efficacy_score: verification.efficacy_score,
            warnings: verification.warnings,
            recommendations: verification.recommendations,
        };
        
        // Return the result as JSON
        serde_json::to_string(&result)
            .map_err(|e| JsValue::from_str(&format!("Error serializing result: {}", e)))
    }
    
    pub fn simulate_treatment_outcome(
        &self, 
        patient_json: String, 
        treatment_json: String
    ) -> Result<String, JsValue> {
        // Parse patient data
        let patient = serde_json::from_str(&patient_json)
            .map_err(|e| JsValue::from_str(&format!("Error parsing patient data: {}", e)))?;
            
        // Parse treatment plan
        let treatment = serde_json::from_str(&treatment_json)
            .map_err(|e| JsValue::from_str(&format!("Error parsing treatment plan: {}", e)))?;
            
        // Simulate treatment outcome
        let outcome = self.engine.simulate_treatment_outcome(patient, treatment);
        
        // Return the outcome as JSON
        serde_json::to_string(&outcome)
            .map_err(|e| JsValue::from_str(&format!("Error serializing outcome: {}", e)))
    }
    
    pub fn get_treatment_alternatives(&self, treatment_json: String) -> Result<String, JsValue> {
        // Parse treatment plan
        let treatment = serde_json::from_str(&treatment_json)
            .map_err(|e| JsValue::from_str(&format!("Error parsing treatment plan: {}", e)))?;
            
        // Get alternative treatments
        let alternatives = self.engine.get_treatment_alternatives(treatment);
        
        // Return the alternatives as JSON
        serde_json::to_string(&alternatives)
            .map_err(|e| JsValue::from_str(&format!("Error serializing alternatives: {}", e)))
    }
}
```

### TypeScript Integration

```typescript
// src/visualization/treatment_verification.ts

interface TreatmentPlan {
  treatment_plan: Array<{
    medication: string;
    dosage: number;
    unit: string;
    frequency: string;
    duration: number;
  }>;
  fitness?: number;
  confidence?: number;
  explanations?: string[];
  biomarker_influences?: Record<string, number>;
}

interface VerificationResult {
  is_valid: boolean;
  safety_score: number;
  efficacy_score: number;
  warnings: string[];
  recommendations: string[];
}

interface PatientData {
  patient_id: string;
  demographics: {
    age: number;
    sex: string;
    ethnicity: string;
    weight: number;
    height: number;
  };
  clinical_data: {
    crohns_type: string;
    disease_activity: {
      CDAI: number;
      SES_CD: number;
      fecal_calprotectin: number;
    };
  };
  biomarkers: {
    genetic_markers: Array<{
      gene: string;
      variant: string;
      zygosity: string;
    }>;
  };
  treatment_history: Array<{
    medication: string;
    response: string;
    adverse_events: string[];
  }>;
}

export class TreatmentVerificationService {
  private verifier: any; // CrohnsTreatmentVerifier from WebAssembly
  private isInitialized: boolean = false;
  private initializationPromise: Promise<void> | null = null;
  
  constructor() {
    this.initializationPromise = this.initialize();
  }
  
  private async initialize(): Promise<void> {
    try {
      // Import the WebAssembly module
      const wasmModule = await import('./wasm/treatment_verifier');
      
      // Create the verifier
      this.verifier = new wasmModule.CrohnsTreatmentVerifier();
      this.isInitialized = true;
    } catch (error) {
      console.error('Failed to initialize treatment verifier:', error);
      throw error;
    }
  }
  
  private async ensureInitialized(): Promise<void> {
    if (!this.isInitialized) {
      if (this.initializationPromise) {
        await this.initializationPromise;
      } else {
        this.initializationPromise = this.initialize();
        await this.initializationPromise;
      }
    }
  }
  
  async verifyTreatment(treatmentPlan: TreatmentPlan): Promise<VerificationResult> {
    await this.ensureInitialized();
    
    try {
      // Convert treatment plan to JSON
      const treatmentJson = JSON.stringify(treatmentPlan);
      
      // Call the WebAssembly module
      const resultJson = await this.verifier.verify_treatment_plan(treatmentJson);
      
      // Parse and return the result
      return JSON.parse(resultJson);
    } catch (error) {
      console.error('Error verifying treatment plan:', error);
      throw error;
    }
  }
  
  async simulateTreatmentOutcome(
    patientData: PatientData, 
    treatmentPlan: TreatmentPlan
  ): Promise<any> {
    await this.ensureInitialized();
    
    try {
      // Convert to JSON
      const patientJson = JSON.stringify(patientData);
      const treatmentJson = JSON.stringify(treatmentPlan);
      
      // Call the WebAssembly module
      const outcomeJson = await this.verifier.simulate_treatment_outcome(patientJson, treatmentJson);
      
      // Parse and return the result
      return JSON.parse(outcomeJson);
    } catch (error) {
      console.error('Error simulating treatment outcome:', error);
      throw error;
    }
  }
  
  async getTreatmentAlternatives(treatmentPlan: TreatmentPlan): Promise<TreatmentPlan[]> {
    await this.ensureInitialized();
    
    try {
      // Convert to JSON
      const treatmentJson = JSON.stringify(treatmentPlan);
      
      // Call the WebAssembly module
      const alternativesJson = await this.verifier.get_treatment_alternatives(treatmentJson);
      
      // Parse and return the result
      return JSON.parse(alternativesJson);
    } catch (error) {
      console.error('Error getting treatment alternatives:', error);
      throw error;
    }
  }
}
```

## 3. HMS-EHR FHIR Integration

This integration connects the system with Electronic Health Record systems using the FHIR standard.

### FHIR Client

```python
# src/data-layer/ehr-integration/fhir_client.py

import httpx
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from .patient_model import Patient, Observation, MedicationRequest

class FHIRClient:
    """Client for interacting with FHIR-compliant EHR systems"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, token: Optional[str] = None):
        """Initialize the FHIR client
        
        Args:
            base_url: Base URL of the FHIR server
            api_key: Optional API key for authentication
            token: Optional OAuth token for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json'
        }
        
        if api_key:
            self.headers['X-API-Key'] = api_key
            
        if token:
            self.headers['Authorization'] = f'Bearer {token}'
            
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=30.0
        )
        
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
        
    async def search_patients(
        self, 
        identifier: Optional[str] = None,
        family: Optional[str] = None,
        given: Optional[str] = None,
        gender: Optional[str] = None,
        birthdate: Optional[str] = None,
        _count: int = 10
    ) -> List[Patient]:
        """Search for patients matching criteria
        
        Args:
            identifier: Patient identifier (e.g., MRN)
            family: Family name
            given: Given name
            gender: Gender
            birthdate: Birth date (YYYY-MM-DD)
            _count: Number of results to return
            
        Returns:
            List of matching patients
        """
        params = {'_count': _count}
        
        if identifier:
            params['identifier'] = identifier
        if family:
            params['family'] = family
        if given:
            params['given'] = given
        if gender:
            params['gender'] = gender
        if birthdate:
            params['birthdate'] = birthdate
            
        response = await self.client.get('/Patient', params=params)
        response.raise_for_status()
        
        data = response.json()
        patients = []
        
        for entry in data.get('entry', []):
            resource = entry.get('resource', {})
            patients.append(Patient.from_fhir(resource))
            
        return patients
        
    async def get_patient(self, patient_id: str) -> Patient:
        """Get a patient by ID
        
        Args:
            patient_id: FHIR resource ID for the patient
            
        Returns:
            Patient data
        """
        response = await self.client.get(f'/Patient/{patient_id}')
        response.raise_for_status()
        
        data = response.json()
        return Patient.from_fhir(data)
        
    async def get_patient_observations(
        self, 
        patient_id: str,
        code: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        _count: int = 100
    ) -> List[Observation]:
        """Get observations for a patient
        
        Args:
            patient_id: FHIR resource ID for the patient
            code: Observation code (LOINC or SNOMED)
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            _count: Number of results to return
            
        Returns:
            List of observations
        """
        params = {
            'subject': f'Patient/{patient_id}',
            '_count': _count,
            '_sort': '-date'
        }
        
        if code:
            params['code'] = code
            
        if date_from:
            if date_to:
                params['date'] = f'ge{date_from}&date=le{date_to}'
            else:
                params['date'] = f'ge{date_from}'
        elif date_to:
            params['date'] = f'le{date_to}'
            
        response = await self.client.get('/Observation', params=params)
        response.raise_for_status()
        
        data = response.json()
        observations = []
        
        for entry in data.get('entry', []):
            resource = entry.get('resource', {})
            observations.append(Observation.from_fhir(resource))
            
        return observations
        
    async def get_medication_requests(
        self,
        patient_id: str,
        status: Optional[str] = None,
        _count: int = 100
    ) -> List[MedicationRequest]:
        """Get medication requests for a patient
        
        Args:
            patient_id: FHIR resource ID for the patient
            status: Status filter (active, completed, etc.)
            _count: Number of results to return
            
        Returns:
            List of medication requests
        """
        params = {
            'subject': f'Patient/{patient_id}',
            '_count': _count,
            '_sort': '-authored'
        }
        
        if status:
            params['status'] = status
            
        response = await self.client.get('/MedicationRequest', params=params)
        response.raise_for_status()
        
        data = response.json()
        medication_requests = []
        
        for entry in data.get('entry', []):
            resource = entry.get('resource', {})
            medication_requests.append(MedicationRequest.from_fhir(resource))
            
        return medication_requests
        
    async def create_medication_request(self, medication_request: Dict[str, Any]) -> str:
        """Create a new medication request
        
        Args:
            medication_request: FHIR MedicationRequest resource
            
        Returns:
            ID of the created resource
        """
        response = await self.client.post('/MedicationRequest', json=medication_request)
        response.raise_for_status()
        
        location = response.headers.get('Location', '')
        if location:
            # Extract ID from location header
            parts = location.split('/')
            return parts[-1]
            
        # If location header not available, try to get ID from response
        data = response.json()
        return data.get('id', '')
        
    async def update_medication_request(self, medication_request_id: str, medication_request: Dict[str, Any]) -> None:
        """Update an existing medication request
        
        Args:
            medication_request_id: ID of the medication request to update
            medication_request: Updated FHIR MedicationRequest resource
        """
        response = await self.client.put(f'/MedicationRequest/{medication_request_id}', json=medication_request)
        response.raise_for_status()
```

### Patient Model

```python
# src/data-layer/ehr-integration/patient_model.py

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime

@dataclass
class Address:
    """Patient address"""
    line: List[str] = field(default_factory=list)
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    
    @classmethod
    def from_fhir(cls, data: Dict[str, Any]) -> 'Address':
        """Create Address from FHIR data"""
        return cls(
            line=data.get('line', []),
            city=data.get('city'),
            state=data.get('state'),
            postal_code=data.get('postalCode'),
            country=data.get('country')
        )

@dataclass
class Identifier:
    """Patient identifier"""
    system: str
    value: str
    
    @classmethod
    def from_fhir(cls, data: Dict[str, Any]) -> 'Identifier':
        """Create Identifier from FHIR data"""
        return cls(
            system=data.get('system', ''),
            value=data.get('value', '')
        )

@dataclass
class Patient:
    """Patient model matching FHIR Patient resource"""
    id: Optional[str] = None
    identifiers: List[Identifier] = field(default_factory=list)
    family_name: Optional[str] = None
    given_names: List[str] = field(default_factory=list)
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    addresses: List[Address] = field(default_factory=list)
    telecom: List[Dict[str, str]] = field(default_factory=list)
    marital_status: Optional[str] = None
    communication: List[Dict[str, Any]] = field(default_factory=list)
    extensions: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_fhir(cls, data: Dict[str, Any]) -> 'Patient':
        """Create Patient from FHIR data"""
        identifiers = [Identifier.from_fhir(ident) for ident in data.get('identifier', [])]
        
        # Extract name components
        name = data.get('name', [{}])[0] if data.get('name') else {}
        family_name = name.get('family')
        given_names = name.get('given', [])
        
        # Extract addresses
        addresses = [Address.from_fhir(addr) for addr in data.get('address', [])]
        
        return cls(
            id=data.get('id'),
            identifiers=identifiers,
            family_name=family_name,
            given_names=given_names,
            gender=data.get('gender'),
            birth_date=data.get('birthDate'),
            addresses=addresses,
            telecom=data.get('telecom', []),
            marital_status=data.get('maritalStatus', {}).get('coding', [{}])[0].get('code'),
            communication=data.get('communication', []),
            extensions={ext.get('url'): ext.get('valueString') 
                       for ext in data.get('extension', [])}
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'identifiers': [{'system': i.system, 'value': i.value} for i in self.identifiers],
            'name': {
                'family': self.family_name,
                'given': self.given_names
            },
            'gender': self.gender,
            'birthDate': self.birth_date,
            'addresses': [
                {
                    'line': a.line,
                    'city': a.city,
                    'state': a.state,
                    'postalCode': a.postal_code,
                    'country': a.country
                }
                for a in self.addresses
            ],
            'telecom': self.telecom,
            'maritalStatus': self.marital_status,
            'communication': self.communication,
            'extensions': self.extensions
        }

@dataclass
class Observation:
    """Observation model matching FHIR Observation resource"""
    id: Optional[str] = None
    status: Optional[str] = None
    code: Dict[str, Any] = field(default_factory=dict)
    subject_id: Optional[str] = None
    effective_date: Optional[str] = None
    issued: Optional[str] = None
    value_quantity: Optional[Dict[str, Any]] = None
    value_string: Optional[str] = None
    value_code: Optional[Dict[str, Any]] = None
    reference_range: List[Dict[str, Any]] = field(default_factory=list)
    
    @classmethod
    def from_fhir(cls, data: Dict[str, Any]) -> 'Observation':
        """Create Observation from FHIR data"""
        subject_id = None
        if data.get('subject', {}).get('reference'):
            subject_ref = data.get('subject', {}).get('reference', '')
            if subject_ref.startswith('Patient/'):
                subject_id = subject_ref[8:]  # Remove 'Patient/'
                
        effective_date = None
        if data.get('effectiveDateTime'):
            effective_date = data.get('effectiveDateTime')
        elif data.get('effectivePeriod', {}).get('start'):
            effective_date = data.get('effectivePeriod', {}).get('start')
            
        value_quantity = None
        if data.get('valueQuantity'):
            value_quantity = data.get('valueQuantity')
            
        value_string = None
        if data.get('valueString'):
            value_string = data.get('valueString')
            
        value_code = None
        if data.get('valueCodeableConcept'):
            value_code = data.get('valueCodeableConcept')
            
        return cls(
            id=data.get('id'),
            status=data.get('status'),
            code=data.get('code', {}),
            subject_id=subject_id,
            effective_date=effective_date,
            issued=data.get('issued'),
            value_quantity=value_quantity,
            value_string=value_string,
            value_code=value_code,
            reference_range=data.get('referenceRange', [])
        )

@dataclass
class MedicationRequest:
    """MedicationRequest model matching FHIR MedicationRequest resource"""
    id: Optional[str] = None
    status: Optional[str] = None
    intent: Optional[str] = None
    medication: Dict[str, Any] = field(default_factory=dict)
    subject_id: Optional[str] = None
    authored_on: Optional[str] = None
    requester: Dict[str, Any] = field(default_factory=dict)
    dosage_instructions: List[Dict[str, Any]] = field(default_factory=list)
    
    @classmethod
    def from_fhir(cls, data: Dict[str, Any]) -> 'MedicationRequest':
        """Create MedicationRequest from FHIR data"""
        subject_id = None
        if data.get('subject', {}).get('reference'):
            subject_ref = data.get('subject', {}).get('reference', '')
            if subject_ref.startswith('Patient/'):
                subject_id = subject_ref[8:]  # Remove 'Patient/'
                
        medication = {}
        if data.get('medicationCodeableConcept'):
            medication = data.get('medicationCodeableConcept')
        elif data.get('medicationReference'):
            medication = data.get('medicationReference')
            
        return cls(
            id=data.get('id'),
            status=data.get('status'),
            intent=data.get('intent'),
            medication=medication,
            subject_id=subject_id,
            authored_on=data.get('authoredOn'),
            requester=data.get('requester', {}),
            dosage_instructions=data.get('dosageInstruction', [])
        )
```

## 4. API Gateway Integration

The API Gateway provides a unified entry point for all external communication with the system.

### Authentication Service

```python
# src/api-gateway/auth_service.py

import jwt
import time
import uuid
from typing import Dict, Any, Optional, List, Tuple
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext

# Models
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    roles: List[str] = []

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    roles: List[str] = []

# Setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key for JWT
SECRET_KEY = "a-secure-secret-key-that-should-be-replaced-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password for secure storage"""
    return pwd_context.hash(password)

def authenticate_user(db, username: str, password: str) -> Optional[UserInDB]:
    """Authenticate user with username and password"""
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
    """Create JWT access token with optional expiration"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = time.time() + expires_delta
    else:
        expire = time.time() + ACCESS_TOKEN_EXPIRE_MINUTES * 60
        
    to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        token_data = TokenData(username=username, roles=payload.get("roles", []))
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def has_role(required_roles: List[str]) -> Callable:
    """Check if user has required roles"""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        for role in required_roles:
            if role in current_user.roles:
                return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return role_checker

# Fake DB for demonstration purposes
fake_users_db = {
    "researcher": {
        "username": "researcher",
        "full_name": "Research User",
        "email": "researcher@example.com",
        "hashed_password": get_password_hash("researcherpassword"),
        "disabled": False,
        "roles": ["researcher"]
    },
    "provider": {
        "username": "provider",
        "full_name": "Provider User",
        "email": "provider@example.com",
        "hashed_password": get_password_hash("providerpassword"),
        "disabled": False,
        "roles": ["provider"]
    },
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": get_password_hash("adminpassword"),
        "disabled": False,
        "roles": ["admin", "researcher", "provider"]
    }
}

def get_user(db, username: str) -> Optional[UserInDB]:
    """Get user from database"""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

# Example API endpoints
app = FastAPI()

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Generate JWT token from username and password"""
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(
        data={"sub": user.username, "roles": user.roles}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user

@app.get("/users/me/roles")
async def read_own_roles(current_user: User = Depends(get_current_active_user)):
    """Get current user roles"""
    return {"roles": current_user.roles}

@app.get("/admin")
async def admin_only(current_user: User = Depends(has_role(["admin"]))):
    """Admin-only endpoint"""
    return {"message": "Admin access granted"}

@app.get("/researcher")
async def researcher_only(current_user: User = Depends(has_role(["researcher"]))):
    """Researcher-only endpoint"""
    return {"message": "Researcher access granted"}

@app.get("/provider")
async def provider_only(current_user: User = Depends(has_role(["provider"]))):
    """Provider-only endpoint"""
    return {"message": "Provider access granted"}
```

## 5. Inter-Service Communication

The system uses a message broker for reliable inter-service communication.

### Event Bus Service

```python
# src/coordination/a2a-integration/event_bus.py

import json
import uuid
import asyncio
import logging
from typing import Dict, List, Callable, Any, Awaitable, Optional
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class EventBus:
    """Event bus for inter-service communication using Kafka"""
    
    def __init__(self, bootstrap_servers: str, client_id: str):
        """Initialize the event bus
        
        Args:
            bootstrap_servers: Kafka bootstrap servers (comma-separated)
            client_id: Client ID for this service
        """
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id
        self.producer = None
        self.consumers = {}
        self.handlers = {}
        self.running = False
        
    async def start(self):
        """Start the event bus"""
        # Initialize producer
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            client_id=f"{self.client_id}-producer",
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        await self.producer.start()
        self.running = True
        
    async def stop(self):
        """Stop the event bus"""
        self.running = False
        
        # Stop all consumers
        for consumer in self.consumers.values():
            await consumer.stop()
            
        # Stop producer
        if self.producer:
            await self.producer.stop()
            
    async def publish(self, topic: str, data: Dict[str, Any], key: Optional[str] = None) -> None:
        """Publish an event to a topic
        
        Args:
            topic: Kafka topic
            data: Event data
            key: Optional message key for partitioning
        """
        if not self.running:
            raise RuntimeError("Event bus not started")
            
        # Create the event object
        event = {
            'id': str(uuid.uuid4()),
            'type': topic,
            'data': data,
            'timestamp': self._get_timestamp(),
            'source': self.client_id
        }
        
        # Encode key if provided
        encoded_key = key.encode('utf-8') if key else None
        
        # Send the event
        try:
            await self.producer.send_and_wait(topic, event, key=encoded_key)
            logger.debug(f"Published event to {topic}: {event['id']}")
        except Exception as e:
            logger.error(f"Error publishing event to {topic}: {e}")
            raise
            
    async def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], Awaitable[None]], group_id: Optional[str] = None) -> None:
        """Subscribe to events on a topic
        
        Args:
            topic: Kafka topic
            handler: Async function to handle events
            group_id: Consumer group ID (defaults to client_id)
        """
        if not self.running:
            raise RuntimeError("Event bus not started")
            
        # Use client_id as group_id if not provided
        group_id = group_id or self.client_id
        
        # Store handler
        if topic not in self.handlers:
            self.handlers[topic] = []
        self.handlers[topic].append(handler)
        
        # Create consumer if not exists for this topic
        if topic not in self.consumers:
            consumer = AIOKafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                client_id=f"{self.client_id}-consumer-{topic}",
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                enable_auto_commit=False
            )
            
            await consumer.start()
            self.consumers[topic] = consumer
            
            # Start consumer task
            asyncio.create_task(self._consume(topic, consumer))
            
    async def _consume(self, topic: str, consumer: AIOKafkaConsumer) -> None:
        """Consume events from a topic
        
        Args:
            topic: Kafka topic
            consumer: Kafka consumer
        """
        try:
            async for msg in consumer:
                try:
                    event = msg.value
                    logger.debug(f"Received event from {topic}: {event.get('id')}")
                    
                    # Call all handlers for this topic
                    if topic in self.handlers:
                        for handler in self.handlers[topic]:
                            try:
                                await handler(event)
                            except Exception as e:
                                logger.error(f"Error in handler for {topic}: {e}")
                                
                    # Commit offset
                    await consumer.commit()
                except Exception as e:
                    logger.error(f"Error processing message from {topic}: {e}")
        except Exception as e:
            logger.error(f"Consumer error for {topic}: {e}")
        finally:
            await consumer.stop()
            
    def _get_timestamp(self) -> int:
        """Get current timestamp in milliseconds"""
        import time
        return int(time.time() * 1000)
        
    @asynccontextmanager
    async def connection(self):
        """Context manager for event bus connection"""
        await self.start()
        try:
            yield self
        finally:
            await self.stop()
```

## 6. Self-Healing Integration

The self-healing system integrates with all components to provide resilience.

### Health Monitoring Service

```rust
// src/self-healing/monitoring.rs

use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use std::time::{Duration, Instant};
use tokio::time::interval;
use serde::{Serialize, Deserialize};
use thiserror::Error;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ComponentStatus {
    Healthy,
    Degraded,
    Unhealthy,
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HealthCheck {
    pub status: ComponentStatus,
    pub message: Option<String>,
    pub details: Option<HashMap<String, String>>,
    pub last_check: u64,
    pub response_time: u64,
}

#[derive(Debug, Error)]
pub enum MonitoringError {
    #[error("Health check failed: {0}")]
    HealthCheckFailed(String),
    #[error("Component not found: {0}")]
    ComponentNotFound(String),
    #[error("Timeout while checking component: {0}")]
    Timeout(String),
}

pub struct HealthMonitor {
    checks: Arc<RwLock<HashMap<String, HealthCheck>>>,
    check_interval: Duration,
    timeout: Duration,
}

impl HealthMonitor {
    pub fn new(check_interval: Duration, timeout: Duration) -> Self {
        HealthMonitor {
            checks: Arc::new(RwLock::new(HashMap::new())),
            check_interval,
            timeout,
        }
    }
    
    pub async fn start(&self, mut rx: tokio::sync::mpsc::Receiver<()>) {
        let checks = self.checks.clone();
        let mut interval = interval(self.check_interval);
        
        tokio::spawn(async move {
            loop {
                tokio::select! {
                    _ = rx.recv() => {
                        // Shutdown signal received
                        break;
                    }
                    _ = interval.tick() => {
                        // Run health checks
                        for (component, check) in checks.read().unwrap().iter() {
                            if check.status == ComponentStatus::Unhealthy {
                                // Trigger healing for unhealthy component
                                Self::trigger_healing(component, check);
                            }
                        }
                    }
                }
            }
        });
    }
    
    pub fn register_component(&self, component: String) {
        let mut checks = self.checks.write().unwrap();
        checks.insert(component, HealthCheck {
            status: ComponentStatus::Unknown,
            message: None,
            details: None,
            last_check: 0,
            response_time: 0,
        });
    }
    
    pub fn update_health(&self, component: &str, status: ComponentStatus, message: Option<String>, details: Option<HashMap<String, String>>, response_time: u64) {
        let mut checks = self.checks.write().unwrap();
        
        if let Some(check) = checks.get_mut(component) {
            *check = HealthCheck {
                status,
                message,
                details,
                last_check: std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_secs(),
                response_time,
            };
        }
    }
    
    pub async fn check_component(&self, component: &str, check_fn: impl FnOnce() -> Result<(), String>) -> Result<(), MonitoringError> {
        if !self.checks.read().unwrap().contains_key(component) {
            return Err(MonitoringError::ComponentNotFound(component.to_string()));
        }
        
        let start = Instant::now();
        
        match tokio::time::timeout(self.timeout, async {
            match check_fn() {
                Ok(()) => Ok(()),
                Err(msg) => Err(MonitoringError::HealthCheckFailed(msg)),
            }
        }).await {
            Ok(result) => {
                let response_time = start.elapsed().as_millis() as u64;
                
                match result {
                    Ok(()) => {
                        self.update_health(
                            component,
                            ComponentStatus::Healthy,
                            None,
                            None,
                            response_time,
                        );
                        Ok(())
                    }
                    Err(err) => {
                        self.update_health(
                            component,
                            ComponentStatus::Unhealthy,
                            Some(format!("{}", err)),
                            None,
                            response_time,
                        );
                        Err(err)
                    }
                }
            }
            Err(_) => {
                self.update_health(
                    component,
                    ComponentStatus::Unhealthy,
                    Some(format!("Timeout after {}ms", self.timeout.as_millis())),
                    None,
                    self.timeout.as_millis() as u64,
                );
                Err(MonitoringError::Timeout(component.to_string()))
            }
        }
    }
    
    pub fn get_component_status(&self, component: &str) -> Option<HealthCheck> {
        let checks = self.checks.read().unwrap();
        checks.get(component).cloned()
    }
    
    pub fn get_all_statuses(&self) -> HashMap<String, HealthCheck> {
        let checks = self.checks.read().unwrap();
        checks.clone()
    }
    
    fn trigger_healing(component: &str, check: &HealthCheck) {
        // This would integrate with the healing system to trigger appropriate recovery actions
        println!("Triggering healing for component: {}", component);
    }
}
```

### Healing Service

```rust
// src/self-healing/healing.rs

use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::Mutex;
use serde::{Serialize, Deserialize};
use thiserror::Error;

use crate::monitoring::{ComponentStatus, HealthCheck};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum HealingStrategy {
    Restart,
    Failover,
    Reconfigure,
    ScaleUp,
    ScaleDown,
    RollbackDeployment,
    Custom(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum HealingStatus {
    NotStarted,
    InProgress,
    Succeeded,
    Failed,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HealingAction {
    pub component: String,
    pub strategy: HealingStrategy,
    pub status: HealingStatus,
    pub started_at: Option<u64>,
    pub completed_at: Option<u64>,
    pub error: Option<String>,
    pub details: Option<HashMap<String, String>>,
}

#[derive(Debug, Error)]
pub enum HealingError {
    #[error("Healing failed: {0}")]
    Failed(String),
    #[error("Component not found: {0}")]
    ComponentNotFound(String),
    #[error("Strategy not supported for component: {0}")]
    StrategyNotSupported(String),
    #[error("Healing already in progress for component: {0}")]
    AlreadyInProgress(String),
}

struct HealingStrategies {
    strategies: HashMap<String, HashMap<HealingStrategy, Box<dyn Fn() -> Result<(), String> + Send + Sync>>>,
}

impl HealingStrategies {
    fn new() -> Self {
        HealingStrategies {
            strategies: HashMap::new(),
        }
    }
    
    fn register_strategy<F>(&mut self, component: &str, strategy: HealingStrategy, action: F)
    where
        F: Fn() -> Result<(), String> + Send + Sync + 'static,
    {
        let component_strategies = self.strategies
            .entry(component.to_string())
            .or_insert_with(HashMap::new);
            
        component_strategies.insert(strategy, Box::new(action));
    }
    
    fn get_strategy(&self, component: &str, strategy: &HealingStrategy) -> Option<&Box<dyn Fn() -> Result<(), String> + Send + Sync>> {
        self.strategies
            .get(component)
            .and_then(|strategies| strategies.get(strategy))
    }
}

pub struct HealingSystem {
    strategies: Arc<Mutex<HealingStrategies>>,
    actions: Arc<Mutex<Vec<HealingAction>>>,
}

impl HealingSystem {
    pub fn new() -> Self {
        HealingSystem {
            strategies: Arc::new(Mutex::new(HealingStrategies::new())),
            actions: Arc::new(Mutex::new(Vec::new())),
        }
    }
    
    pub async fn register_strategy<F>(&self, component: &str, strategy: HealingStrategy, action: F)
    where
        F: Fn() -> Result<(), String> + Send + Sync + 'static,
    {
        let mut strategies = self.strategies.lock().await;
        strategies.register_strategy(component, strategy, action);
    }
    
    pub async fn heal_component(&self, component: &str, strategy: HealingStrategy) -> Result<HealingAction, HealingError> {
        // Check if healing is already in progress
        {
            let actions = self.actions.lock().await;
            for action in &*actions {
                if action.component == component && action.status == HealingStatus::InProgress {
                    return Err(HealingError::AlreadyInProgress(component.to_string()));
                }
            }
        }
        
        // Create healing action
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();
            
        let mut action = HealingAction {
            component: component.to_string(),
            strategy: strategy.clone(),
            status: HealingStatus::NotStarted,
            started_at: Some(now),
            completed_at: None,
            error: None,
            details: None,
        };
        
        // Add to actions list
        {
            let mut actions = self.actions.lock().await;
            actions.push(action.clone());
        }
        
        // Execute healing strategy
        let strategies = self.strategies.lock().await;
        let strategy_fn = strategies
            .get_strategy(component, &strategy)
            .ok_or_else(|| {
                HealingError::StrategyNotSupported(format!("{:?} for {}", strategy, component))
            })?;
            
        action.status = HealingStatus::InProgress;
        self.update_action(&action).await;
        
        match strategy_fn() {
            Ok(()) => {
                action.status = HealingStatus::Succeeded;
                action.completed_at = Some(std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_secs());
                self.update_action(&action).await;
                Ok(action)
            }
            Err(err) => {
                action.status = HealingStatus::Failed;
                action.error = Some(err);
                action.completed_at = Some(std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_secs());
                self.update_action(&action).await;
                Err(HealingError::Failed(err))
            }
        }
    }
    
    async fn update_action(&self, action: &HealingAction) {
        let mut actions = self.actions.lock().await;
        for a in &mut *actions {
            if a.component == action.component && a.started_at == action.started_at {
                *a = action.clone();
                break;
            }
        }
    }
    
    pub async fn get_actions_for_component(&self, component: &str) -> Vec<HealingAction> {
        let actions = self.actions.lock().await;
        actions
            .iter()
            .filter(|a| a.component == component)
            .cloned()
            .collect()
    }
    
    pub async fn get_all_actions(&self) -> Vec<HealingAction> {
        let actions = self.actions.lock().await;
        actions.clone()
    }
}
```

## Additional Integration Notes

### Cross-Component Error Handling

All components should use a consistent error handling approach:

1. **Domain-Specific Errors**: Define domain-specific errors using enums in Rust or exception classes in Python
2. **Error Translation**: Translate errors at integration boundaries
3. **Error Propagation**: Use Result/Option in Rust, exceptions in Python, and Promise rejections in TypeScript
4. **Error Logging**: Log errors with context before translating

### Security at Integration Points

1. **Authentication**: Apply mutual TLS for service-to-service communication
2. **Authorization**: Validate service permissions at integration points
3. **Input Validation**: Validate all cross-component inputs
4. **Output Sanitization**: Ensure outputs don't leak sensitive information
5. **Rate Limiting**: Apply rate limits to protect services from overload

### Versioning Strategy

1. **API Versioning**: Use explicit versioning in URLs (e.g., `/v1/api/patients`)
2. **Schema Versioning**: Include version in message schemas
3. **Compatibility Policy**: Maintain backward compatibility for at least one major version
4. **Deprecation Process**: Mark deprecated endpoints and allow transition period

### Integration Testing

1. **Component Tests**: Test each component in isolation with mocks
2. **Integration Tests**: Test interactions between components
3. **Contract Tests**: Verify API contracts are maintained
4. **End-to-End Tests**: Test complete workflows through all components