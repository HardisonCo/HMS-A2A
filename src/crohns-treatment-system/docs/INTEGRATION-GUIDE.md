# Crohn's Disease Treatment System Integration Guide

## Overview

This document provides a comprehensive guide to the integration between codex-rs, supervisors, and domains with the Crohn's disease adaptive trial framework. The system uses a Foreign Function Interface (FFI) approach to connect components written in different languages, creating a unified platform for Crohn's disease treatment optimization.

## System Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                      Crohn's Integration System                        │
├───────────────┬───────────────────┬────────────────┬──────────────────┤
│ codex-rs Core │ HMS Supervisors   │ Domain Models  │ Trial Data       │
│ Integration   │ Integration       │ Integration    │ Processing       │
└───────┬───────┴────────┬──────────┴────────┬───────┴────────┬─────────┘
        │                │                   │                │
        ▼                ▼                   ▼                ▼
┌───────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ Rust Core     │  │ Supervisor     │  │ HMS-EHR/EMR    │  │ Adaptive Trial │
│ Components    │  │ Framework      │  │ Components     │  │ Framework      │
└───────┬───────┘  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘
        │                   │                   │                   │
        └───────────────────┼───────────────────┼───────────────────┘
                            │                   │                   
                            ▼                   ▼                   
                 ┌─────────────────────┐   ┌────────────────────┐   
                 │  Genetic Engine     │   │  Self-Healing      │   
                 │  Integration        │   │  System            │   
                 └─────────────────────┘   └────────────────────┘   
```

### Key Components

1. **codex-rs Core Integration**: Connects to the Rust-based core libraries including genetic algorithms and economic engines.
2. **HMS Supervisors Integration**: Integrates with the supervisor framework for system orchestration.
3. **Domain Models Integration**: Connects to domain-specific models in HMS-EHR/EMR for patient data.
4. **Trial Data Processing**: Processes and transforms Crohn's trial data for use in the system.
5. **Genetic Engine Integration**: Provides optimization of treatment plans based on patient biomarkers.
6. **Self-Healing System**: Monitors system health and automatically recovers from failures.

## Integration Approaches

### Foreign Function Interface (FFI)

The system uses several FFI approaches to connect components written in different languages:

1. **Rust to Python (PyO3)**: Connects the genetic engine written in Rust to the HMS-A2A coordination system written in Python.
2. **Rust to TypeScript/JavaScript (WebAssembly)**: Provides interfaces for web-based components to interact with the treatment verification system.
3. **Rust to C ABI**: Provides a stable interface that can be used from multiple languages including Go (for HMS-EMR) and Ruby (for HMS-UHC).

### Data Exchange Formats

Data exchange between components uses standardized formats:

1. **Patient Treatment Profile**: JSON schema for patient data exchange.
2. **Trial Protocol Message Format**: Structured format for communicating trial protocols.
3. **Health Monitoring Format**: Format for reporting system health status.

## Component Interactions

### Genetic Engine and HMS-A2A Integration

The Genetic Engine (written in Rust) exposes treatment optimization capabilities to HMS-A2A (written in Python) through PyO3 bindings:

```rust
// In Rust (crohns_integration.rs)
#[pyclass]
pub struct CrohnsTreatmentOptimizer {
    // Implementation details
}

#[pymethods]
impl CrohnsTreatmentOptimizer {
    #[new]
    fn new() -> Self {
        // Implementation
    }
    
    fn optimize_treatment(&mut self, patient_data: PyObject) -> PyResult<PyObject> {
        // Optimization implementation
    }
}
```

```python
# In Python (genetic_engine_ffi.py)
from crohns_genetic_engine import CrohnsTreatmentOptimizer

# Create optimizer instance
optimizer = CrohnsTreatmentOptimizer()

# Optimize treatment
treatment_plan = optimizer.optimize_treatment(patient_data)
```

### Treatment Verification and HMS-EHR Integration

The Treatment Verification system (written in Rust) is exposed to HMS-EHR (written in TypeScript) through WebAssembly:

```rust
// In Rust (treatment_verification.rs)
#[wasm_bindgen]
pub struct CrohnsTreatmentVerifier {
    // Implementation details
}

#[wasm_bindgen]
impl CrohnsTreatmentVerifier {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        // Implementation
    }
    
    pub fn verify_treatment_plan(&self, treatment_json: String) -> Result<String, JsValue> {
        // Verification implementation
    }
}
```

```typescript
// In TypeScript
import * as wasm from 'treatment-verifier';

export class TreatmentVerificationService {
  private verifier: wasm.CrohnsTreatmentVerifier;
  
  constructor() {
    this.verifier = new wasm.CrohnsTreatmentVerifier();
  }
  
  async verifyTreatment(treatmentPlan: any): Promise<VerificationResult> {
    const treatmentJson = JSON.stringify(treatmentPlan);
    const result = await this.verifier.verify_treatment_plan(treatmentJson);
    return JSON.parse(result);
  }
}
```

### Data Transformation Layer

The Data Transformation Layer converts between various data formats:

```python
# In Python (trial_data_transformer.py)
class TrialDataTransformer:
    def csv_to_patient_profiles(self, csv_path: str) -> List[Dict[str, Any]]:
        # Implementation
    
    def transform_patient_for_genetic_engine(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
    
    def hms_ehr_to_patient_profile(self, ehr_data: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
```

### Visualization Component

The Visualization Component provides insights into trial results:

```python
# In Python (trial_results_visualizer.py)
class TrialResultsVisualizer:
    def create_trial_summary_dashboard(self, trial_results: Dict[str, Any]) -> Dict[str, str]:
        # Implementation
    
    def visualize_response_by_arm(self, df: pd.DataFrame) -> str:
        # Implementation
    
    def generate_html_report(self, trial_results: Dict[str, Any], output_file: str) -> None:
        # Implementation
```

## Self-Healing System

The Self-Healing System monitors component health and automatically recovers from failures:

```python
# In Python (codex_rs_integration.py)
class CodexRsIntegration:
    async def _apply_self_healing(self, results: Dict[str, Any],
                                 trial_protocol: Dict[str, Any],
                                 patient_cohort: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Self-healing implementation
    
    async def monitor_system_health(self) -> Dict[str, Any]:
        # Health monitoring implementation
```

## Usage Examples

### Example 1: Optimizing Treatment for a Patient

```python
from src.coordination.a2a_integration.codex_rs_integration import codex_integration
from src.data_layer.trial_data.trial_data_transformer import TrialDataTransformer

async def optimize_patient_treatment():
    # Initialize components
    await codex_integration.initialize()
    transformer = TrialDataTransformer()
    
    try:
        # Load patient data from EHR
        ehr_data = {
            "patient": {"id": "P12345", "birthDate": "1975-08-23", "gender": "female"},
            "conditions": [
                {"name": "Crohn's disease, ileocolonic", "onsetDate": "2018-03-15"}
            ],
            "medications": [
                {"name": "Infliximab", "dose": "5", "unit": "mg/kg", 
                 "frequency": "every 8 weeks", "startDate": "2018-05-01", 
                 "endDate": "2019-06-15", "response": "partial"}
            ],
            "labs": [
                {"name": "CRP", "value": 15.5, "date": "2023-01-15"},
                {"name": "ESR", "value": 25, "date": "2023-01-15"},
                {"name": "Fecal Calprotectin", "value": 350, "date": "2023-01-15"}
            ],
            "genetics": [
                {"gene": "NOD2", "variant": "variant", "zygosity": "heterozygous"},
                {"gene": "IL23R", "variant": "variant", "zygosity": "heterozygous"}
            ]
        }
        
        # Transform EHR data to patient profile
        patient_profile = transformer.hms_ehr_to_patient_profile(ehr_data)
        
        # Transform to genetic engine format
        genetic_format = transformer.transform_patient_for_genetic_engine(patient_profile)
        
        # Optimize treatment
        treatment_plan = await codex_integration.optimize_patient_treatment(genetic_format)
        
        # Process and display the result
        print(f"Optimized treatment plan for patient {patient_profile['patient_id']}:")
        for med in treatment_plan['treatment_plan']:
            print(f"- {med['medication']} {med['dosage']}{med['unit']} {med['frequency']} for {med['duration']} days")
        print(f"Treatment fitness: {treatment_plan['fitness']:.2f}")
        
    finally:
        # Shutdown
        await codex_integration.shutdown()

# Run the example
import asyncio
asyncio.run(optimize_patient_treatment())
```

### Example 2: Running an Adaptive Trial

```python
from src.coordination.a2a_integration.codex_rs_integration import codex_integration
from src.data_layer.trial_data.trial_data_transformer import TrialDataTransformer
from src.visualization.trial_results_visualizer import TrialResultsVisualizer

async def run_adaptive_trial():
    # Initialize components
    await codex_integration.initialize()
    transformer = TrialDataTransformer()
    visualizer = TrialResultsVisualizer()
    
    try:
        # Load patient cohort from CSV
        patient_cohort = transformer.csv_to_patient_profiles('data/patient_cohort.csv')
        
        # Define trial protocol
        trial_protocol = {
            "trial_id": "CROHNS-001",
            "title": "Adaptive Trial of JAK Inhibitors in Crohn's Disease",
            "phase": 2,
            "arms": [
                {
                    "armId": "ARM-001",
                    "name": "Upadacitinib 15mg",
                    "treatment": {
                        "medication": "Upadacitinib",
                        "dosage": "15",
                        "unit": "mg",
                        "frequency": "daily"
                    },
                    "biomarkerStratification": [
                        {
                            "biomarker": "NOD2",
                            "criteria": "variant"
                        }
                    ]
                },
                {
                    "armId": "ARM-002",
                    "name": "Upadacitinib 30mg",
                    "treatment": {
                        "medication": "Upadacitinib",
                        "dosage": "30",
                        "unit": "mg",
                        "frequency": "daily"
                    },
                    "biomarkerStratification": [
                        {
                            "biomarker": "NOD2",
                            "criteria": "variant"
                        }
                    ]
                },
                {
                    "armId": "ARM-003",
                    "name": "Placebo",
                    "treatment": {
                        "medication": "Placebo",
                        "dosage": "0",
                        "unit": "mg",
                        "frequency": "daily"
                    },
                    "biomarkerStratification": []
                }
            ],
            "adaptiveRules": [
                {
                    "triggerCondition": "interim_analysis_1",
                    "action": "response_adaptive_randomization",
                    "parameters": {
                        "min_allocation": 0.1
                    }
                }
            ]
        }
        
        # Transform patient data for trial
        trial_patients = []
        for patient in patient_cohort:
            genetic_format = transformer.transform_patient_for_genetic_engine(patient)
            trial_patients.append(genetic_format)
        
        # Run the trial
        trial_results = await codex_integration.run_adaptive_trial(trial_protocol, trial_patients)
        
        # Generate visualizations
        visualizations = visualizer.create_trial_summary_dashboard(trial_results)
        
        # Generate HTML report
        visualizer.generate_html_report(trial_results, 'output/trial_report.html')
        
        print(f"Trial completed. Report generated at 'output/trial_report.html'")
        
    finally:
        # Shutdown
        await codex_integration.shutdown()

# Run the example
import asyncio
asyncio.run(run_adaptive_trial())
```

### Example 3: Monitoring System Health

```python
from src.coordination.a2a_integration.codex_rs_integration import codex_integration

async def monitor_system_health():
    # Initialize components
    await codex_integration.initialize()
    
    try:
        # Monitor system health
        health = await codex_integration.monitor_system_health()
        
        # Display health status
        print(f"System health status: {health['status']}")
        
        # Display component health
        for component, data in health['components'].items():
            status = data['status']
            emoji = "✅" if status == 'healthy' else "❌"
            print(f"{emoji} {component}: {status}")
        
    finally:
        # Shutdown
        await codex_integration.shutdown()

# Run the example
import asyncio
asyncio.run(monitor_system_health())
```

## Common Integration Patterns

### Pattern 1: Data Transformation Pipeline

1. Load data from source (CSV, EHR, etc.)
2. Transform to standardized patient profile format
3. Transform to genetic engine specific format
4. Process data through core components
5. Transform results back to desired output format

### Pattern 2: Self-Healing Recovery

1. Detect issues using health monitoring
2. Apply self-healing strategies
3. Recover and continue processing
4. Log and report healing actions

### Pattern 3: Visualization Pipeline

1. Process trial results
2. Generate individual visualizations
3. Combine into comprehensive dashboard
4. Generate shareable HTML report

## Best Practices

### 1. Error Handling

Always implement proper error handling across language boundaries:

```python
try:
    # Call FFI function
    result = await genetic_engine.optimize_treatment(patient_data)
except Exception as e:
    # Handle error and provide fallback
    logger.error(f"Error in genetic engine: {e}")
    result = fallback_treatment_plan(patient_data)
```

### 2. Resource Management

Ensure resources are properly cleaned up, especially across language boundaries:

```python
try:
    # Initialize resources
    await genetic_engine.initialize()
    
    # Use resources
    # ...
    
finally:
    # Clean up resources
    await genetic_engine.shutdown()
```

### 3. Data Validation

Always validate data before passing it across language boundaries:

```python
def transform_patient_for_genetic_engine(self, patient: Dict[str, Any]) -> Dict[str, Any]:
    # Validate required fields
    if 'patient_id' not in patient:
        raise ValueError("Missing required field 'patient_id'")
    
    # Transform and return
    # ...
```

### 4. Testing Across Boundaries

Test integration points thoroughly:

```python
@patch('src.coordination.a2a_integration.genetic_engine_ffi.genetic_engine.optimize_treatment')
@patch('src.coordination.a2a_integration.genetic_engine_ffi.genetic_engine.initialize')
async def test_optimize_patient_treatment(self, mock_initialize, mock_optimize):
    # Set up mocks
    mock_initialize.return_value = None
    mock_optimize.return_value = self.mock_treatment_response
    
    # Call the method
    result = await self.integration.optimize_patient_treatment(self.patient_data)
    
    # Assertions
    mock_initialize.assert_called_once()
    mock_optimize.assert_called_once()
    self.assertIn('treatment_plan', result)
```

## Troubleshooting

### Common Issues and Solutions

1. **FFI Binding Failures**
   - **Issue**: Failure to load shared libraries (.so, .dll, .dylib)
   - **Solution**: Ensure library paths are correctly set and libraries are compiled for the correct platform

2. **Data Serialization Errors**
   - **Issue**: Data structure mismatch between languages
   - **Solution**: Use simple data types (numbers, strings) and structured formats (JSON) for cross-language communication

3. **Memory Management Issues**
   - **Issue**: Memory leaks when passing data between languages
   - **Solution**: Ensure proper cleanup on both sides of the FFI boundary

4. **Performance Bottlenecks**
   - **Issue**: Slow performance due to frequent FFI calls
   - **Solution**: Batch operations and minimize the number of FFI boundary crossings

## Conclusion

This integration approach connects disparate components written in different languages into a cohesive system for Crohn's disease treatment optimization. By using FFI techniques, standardized data formats, and self-healing capabilities, the system provides robust performance and reliability.

Follow the patterns and examples in this guide to effectively work with the integrated system and extend it with new capabilities.