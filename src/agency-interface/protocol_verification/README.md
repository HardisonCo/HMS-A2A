# Protocol Verification System

The Protocol Verification System provides a robust framework for verifying the safety, coherence, and compliance of clinical trial protocols, with a specific focus on Crohn's disease adaptive trials.

## Components

- **ProtocolVerifier**: The main entry point for protocol verification
- **ProverClient**: Connects to the theorem prover service for formal verification
- **VerificationConfig**: Configuration for verification operations
- **VerificationResult**: Contains the results of protocol verification
- **TheoremResult**: Results of individual theorem verification
- **TreatmentVerificationResult**: Results of treatment safety verification
- **RiskAssessment**: Assessment of risks identified during verification
- **TreatmentOutcomePrediction**: Prediction of treatment outcomes
- **FFI Components**: Foreign Function Interface to the Rust genetic algorithm engine

## Usage Examples

### Basic Protocol Verification

```php
use HMS\AgencyInterface\ProtocolVerification\ProtocolVerificationFactory;

// Get the factory from the service container
$factory = app(ProtocolVerificationFactory::class);

// Create a protocol verifier
$verifier = $factory->createProtocolVerifier();

// Load a protocol
$protocol = Protocol::find($protocolId);

// Verify the protocol
$result = $verifier->verifyProtocol($protocol);

// Check if the protocol is valid
if ($result->isValid()) {
    // Protocol is valid
    echo "Protocol verification passed";
} else {
    // Protocol failed verification
    echo "Protocol verification failed: " . $result->getMessage();
    
    // Analyze failing theorems
    foreach ($result->getTheoremResults() as $theoremResult) {
        if ($theoremResult->getStatus() === VerificationStatus::FAILED) {
            echo "Failed theorem: " . $theoremResult->getTheoremName();
            
            // Counter-example provides details about the failure
            if ($counterExample = $theoremResult->getCounterExample()) {
                print_r($counterExample);
            }
        }
    }
}
```

### Verifying Protocol Adaptations

```php
// Define an adaptation to the protocol
$adaptation = [
    'type' => 'DROP_ARM',
    'armId' => 'arm-123',
];

// Verify the adaptation
$result = $verifier->verifyAdaptation($protocol, $adaptation);

if ($result->isValid()) {
    // Adaptation is valid, can be applied to the protocol
    echo "Protocol adaptation is valid";
} else {
    // Adaptation failed verification
    echo "Protocol adaptation failed verification: " . $result->getMessage();
}
```

### Checking Treatment Safety for a Patient

```php
// Define the treatment plan
$treatment = [
    'name' => 'Upadacitinib',
    'activeIngredients' => ['upadacitinib'],
    'dosage' => 30,  // mg
    'frequency' => 'daily',
    'duration' => 12 // weeks
];

// Patient profile
$patientProfile = [
    'age' => 42,
    'weight' => 75, // kg
    'allergies' => ['penicillin'],
    'conditions' => ['Crohn\'s disease', 'hypertension'],
    'biomarkers' => ['LRRK2_MUC19' => 'positive'],
    'medications' => ['amlodipine']
];

// Additional context
$context = [
    'protocolId' => $protocol->id,
    'currentCDAIScore' => 320
];

// Verify treatment safety
$safetyResult = $verifier->verifyTreatmentSafety($treatment, $patientProfile, $context);

if ($safetyResult->getStatus() === VerificationStatus::VERIFIED) {
    // Treatment is safe for this patient
    echo "Treatment is safe for this patient";
    
    // Check if there are any risks to monitor
    if (count($safetyResult->getRisks()) > 0) {
        echo "Risks to monitor:";
        foreach ($safetyResult->getRisks() as $risk) {
            echo "- " . $risk->getDescription() . " (Severity: " . $risk->getSeverity() . ")";
            
            // Display mitigation strategies
            foreach ($risk->getMitigationStrategies() as $strategy) {
                echo "  - " . $strategy;
            }
        }
    }
    
    // Check treatment outcome prediction
    if ($outcome = $safetyResult->getOutcomePrediction()) {
        echo "Predicted efficacy: " . ($outcome->getEfficacy() * 100) . "% (Confidence: " . ($outcome->getConfidence() * 100) . "%)";
    }
} else {
    // Treatment is not safe for this patient
    echo "Treatment is NOT safe for this patient: " . $safetyResult->getMessage();
}
```

### Predicting Treatment Outcomes

```php
// Predict treatment outcome
$outcomeResult = $verifier->predictTreatmentOutcome($treatment, $patientProfile, $context);

echo "Predicted efficacy: " . ($outcomeResult->getEfficacy() * 100) . "%";
echo "Confidence: " . ($outcomeResult->getConfidence() * 100) . "%";

// Display factors affecting the prediction
echo "Factors affecting prediction:";
foreach ($outcomeResult->getFactors() as $factor) {
    echo "- " . $factor;
}
```

### Generating Formal Proofs

```php
// After obtaining a verification result, generate formal proofs
$formalProofs = $verifier->generateFormalProofs($result);

echo "Formal proofs in Lean format:";
foreach ($formalProofs as $theoremId => $proof) {
    echo "Theorem: " . $theoremId;
    echo "Proof: " . $proof;
}
```

### Using Custom Verification Configuration

```php
// Create a custom configuration
$config = $factory->createVerificationConfig(
    true,  // verifySafety
    true,  // verifyStatistical
    true,  // verifyCoherence
    true,  // verifyDomainSpecific
    true,  // useCaching
    3600   // cacheTTL (seconds)
);

// Verify with custom configuration
$result = $verifier->verifyProtocol($protocol, $config);
```

### Using Genetic Algorithm Optimization

```php
use HMS\AgencyInterface\ProtocolVerification\FFI\GeneticAlgorithmAdapter;

// Get the genetic algorithm adapter from the service container
$gaAdapter = app(GeneticAlgorithmAdapter::class);

// Check if genetic algorithm FFI is available
if (!$gaAdapter->isAvailable()) {
    echo "Genetic algorithm functionality is not available. Please check the configuration.";
    return;
}

// Optimize a protocol
$constraints = [
    'maxDuration' => 52,  // weeks
    'maxArms' => 4,
    'minParticipants' => 100,
    'maxParticipants' => 500,
    'primaryEndpoint' => 'remission',
    'biomarkerStratification' => true
];

$optimizationResult = $gaAdapter->optimizeProtocol($protocol, $constraints);

if ($optimizationResult) {
    // Display optimized protocol parameters
    echo "Optimized protocol parameters:";
    echo "Duration: " . $optimizationResult['duration'] . " weeks";
    echo "Number of arms: " . count($optimizationResult['arms']);
    echo "Total participants: " . $optimizationResult['totalParticipants'];
    echo "Expected power: " . ($optimizationResult['expectedPower'] * 100) . "%";
    
    // Display optimized arms
    echo "Optimized arms:";
    foreach ($optimizationResult['arms'] as $arm) {
        echo "- " . $arm['name'] . ": " . $arm['allocation'] . "% allocation";
    }
}
```

## Class Hierarchy

```
ProtocolVerifier
    └── ProverClient (implements ProverClientInterface)
            ├── TheoremResult
            ├── VerificationResult
            ├── TreatmentVerificationResult
            │       ├── RiskAssessment
            │       └── TreatmentOutcomePrediction
            └── VerificationConfig

FFI
    ├── GeneticAlgorithmFFI
    ├── GeneticAlgorithmAdapter
    └── FFIServiceProvider
```

## Integration with HMS-CDF Theorem Prover

The Protocol Verification System connects to the HMS-CDF theorem prover service for formal verification of protocol properties and treatment safety. The service provides several verification endpoints:

- `/api/prover/verify`: Verifies theorems against protocols
- `/api/prover/applicable-theorems`: Gets applicable theorems for a protocol
- `/api/prover/verify-treatment`: Verifies treatment safety for a patient
- `/api/prover/generate-formal-proofs`: Generates formal proofs for verified theorems

The system includes fallback local verification for basic properties when the service is unavailable.

## FFI Integration

The verification system includes FFI (Foreign Function Interface) capabilities to interact directly with the Rust-based genetic algorithm optimization engine. The FFI integration provides:

- Protocol optimization using genetic algorithms
- Enhanced protocol verification using genetic algorithms
- Treatment outcome prediction using genetic algorithms

### FFI Components

- **GeneticAlgorithmFFI**: Low-level FFI wrapper for the genetic algorithm shared library
- **GeneticAlgorithmAdapter**: High-level adapter for integrating the FFI with the verification system
- **FFIServiceProvider**: Service provider for registering FFI components with the Laravel container

### FFI Configuration

The FFI integration can be configured through the `agency_ffi.php` configuration file:

```php
// Path to the genetic algorithm shared library
'genetic_algorithm_library_path' => env('GENETIC_ALGORITHM_LIBRARY_PATH', null),

// Enable/disable FFI features
'enable_ffi' => env('ENABLE_FFI', false),

// Genetic algorithm parameters
'genetic_algorithm' => [
    'population_size' => env('GENETIC_ALGORITHM_POPULATION_SIZE', 100),
    'max_generations' => env('GENETIC_ALGORITHM_MAX_GENERATIONS', 50),
    // ...
],

// FFI cache configuration
'ffi_cache' => [
    'enabled' => env('FFI_CACHE_ENABLED', true),
    'ttl' => env('FFI_CACHE_TTL', 3600),
    // ...
]
```

## Testing

Unit tests are provided for all components to ensure correct functioning:

- `ProtocolVerifierTest`: Tests the main verification functionality
- `ProverClientTest`: Tests communication with the theorem prover service
- `GeneticAlgorithmFFITest`: Tests the FFI integration with the genetic algorithm engine
- `ProtocolVerificationIntegrationTest`: Integration tests for the complete verification system

## Caching

The system includes a caching mechanism to optimize verification performance. Verification results are cached based on protocol ID and can be configured with a custom TTL (time-to-live).