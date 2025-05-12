# Crohn's Disease Treatment System: Quick Start Guide

This guide provides step-by-step instructions for getting started with the Crohn's Disease Treatment System.

## 1. Installation

### Prerequisites

- Python 3.11+
- Rust 1.73+
- Node.js 18+ (for web components)
- Docker and Docker Compose
- Git
- 8+ GB RAM, 4+ core CPU recommended

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/organization/crohns-treatment-system.git
   cd crohns-treatment-system
   ```

2. **Copy the environment file**:
   ```bash
   cp .env.example .env
   ```

3. **Run the setup script**:
   ```bash
   ./foundation-setup.sh
   ```
   This script will:
   - Install required dependencies
   - Set up the Python environment
   - Build Rust components
   - Configure the system

4. **Start the development system**:
   ```bash
   ./start-dev.sh
   ```
   This will start all necessary services and components in development mode.

5. **Alternative: Using Docker Compose**:
   ```bash
   make start
   ```
   This command starts all system components in Docker containers.

## 2. Running the Demo

The system includes a comprehensive demo that showcases its key capabilities:

```bash
./start-demo.sh
```

Or with Docker:

```bash
make run-demo
```

This interactive demo allows you to explore:
- Treatment optimization for individual patients
- Adaptive clinical trial execution
- Self-healing system capabilities
- System health monitoring

Follow the on-screen prompts to navigate through the demo.

## 3. Basic Usage

### Treatment Optimization

To optimize treatment for a patient:

```python
from src.coordination.a2a_integration.codex_rs_integration import codex_integration
from src.data_layer.trial_data.trial_data_transformer import TrialDataTransformer

async def optimize_treatment():
    # Initialize components
    await codex_integration.initialize()
    transformer = TrialDataTransformer()
    
    # Load patient data (from file, EHR, etc.)
    with open('data/patient_example.json', 'r') as f:
        patient_data = json.load(f)
    
    # Transform for genetic engine
    genetic_format = transformer.transform_patient_for_genetic_engine(patient_data)
    
    # Optimize treatment
    treatment_plan = await codex_integration.optimize_patient_treatment(genetic_format)
    
    # Print results
    print(f"Optimized treatment plan: {treatment_plan}")
    
    # Cleanup
    await codex_integration.shutdown()

# Run the function
import asyncio
asyncio.run(optimize_treatment())
```

### Running an Adaptive Trial

To run an adaptive clinical trial:

```python
from src.coordination.a2a_integration.codex_rs_integration import codex_integration
from src.data_layer.trial_data.trial_data_transformer import TrialDataTransformer

async def run_trial():
    # Initialize components
    await codex_integration.initialize()
    transformer = TrialDataTransformer()
    
    # Load patient cohort
    patient_cohort = transformer.csv_to_patient_profiles('data/patient_cohort.csv')
    
    # Load trial protocol
    with open('data/trial_protocol.json', 'r') as f:
        trial_protocol = json.load(f)
    
    # Transform patient data
    trial_patients = []
    for patient in patient_cohort:
        genetic_format = transformer.transform_patient_for_genetic_engine(patient)
        trial_patients.append(genetic_format)
    
    # Run the trial
    trial_results = await codex_integration.run_adaptive_trial(trial_protocol, trial_patients)
    
    # Print results
    print(f"Trial completed with {len(trial_results['patient_outcomes'])} patients")
    
    # Cleanup
    await codex_integration.shutdown()

# Run the function
import asyncio
asyncio.run(run_trial())
```

### Visualizing Results

To generate visualizations from trial results:

```python
from src.visualization.trial_results_visualizer import TrialResultsVisualizer
import json
import os

# Load trial results
with open('data/trial_results.json', 'r') as f:
    trial_results = json.load(f)

# Create visualizer
visualizer = TrialResultsVisualizer()

# Generate visualizations
visualizations = visualizer.create_trial_summary_dashboard(trial_results)

# Save visualizations
os.makedirs('output/visualizations', exist_ok=True)
visualizer.save_visualizations(visualizations, 'output/visualizations')

# Generate HTML report
visualizer.generate_html_report(trial_results, 'output/trial_report.html')

print("Visualizations generated successfully")
```

## 4. Using the REST API

The system provides a RESTful API for accessing its functionality:

### Treatment Optimization

```bash
curl -X POST http://localhost:8000/api/v1/treatment/optimize \
  -H "Content-Type: application/json" \
  -d @data/patient_example.json
```

### Creating a Clinical Trial

```bash
curl -X POST http://localhost:8000/api/v1/trials \
  -H "Content-Type: application/json" \
  -d @data/trial_protocol.json
```

### Enrolling a Patient in a Trial

```bash
curl -X POST http://localhost:8000/api/v1/trials/CROHNS-001/patients \
  -H "Content-Type: application/json" \
  -d @data/patient_enrollment.json
```

### Running an Interim Analysis

```bash
curl -X POST http://localhost:8000/api/v1/trials/CROHNS-001/interim-analysis
```

### Getting Trial Results

```bash
curl http://localhost:8000/api/v1/trials/CROHNS-001/results
```

## 5. Using the Web Interfaces

The system provides web interfaces for different types of users:

### Patient Portal

- URL: `http://localhost:3000`
- Features:
  - View treatment plan
  - Report symptoms and outcomes
  - Track disease progression
  - Participate in clinical trials

### Researcher Dashboard

- URL: `http://localhost:3001`
- Features:
  - Design and manage clinical trials
  - Analyze trial results
  - Explore biomarker data
  - Generate reports

### Administration Console

- URL: `http://localhost:8000/admin`
- Features:
  - User management
  - System configuration
  - Monitoring and logging
  - Security settings

## 6. Working with Patient Data

### Supported Data Formats

The system supports multiple patient data formats:

1. **JSON Format**:
   ```json
   {
     "patient_id": "P12345",
     "demographics": {
       "age": 42,
       "sex": "female",
       "ethnicity": "Caucasian"
     },
     "clinical_data": {
       "crohns_type": "ileocolonic",
       "diagnosis_date": "2019-03-15",
       "disease_activity": {
         "CDAI": 220,
         "SES_CD": 12,
         "fecal_calprotectin": 280
       }
     },
     "biomarkers": {
       "genetic_markers": [
         {
           "gene": "NOD2",
           "variant": "variant",
           "zygosity": "heterozygous"
         }
       ]
     }
   }
   ```

2. **CSV Format**: See `examples/patient_cohort.csv` for an example.

3. **FHIR Format**: Standard FHIR patient resources with extensions for Crohn's-specific data.

4. **EHR Integration**: The system can connect to EHR systems via:
   - FHIR API integration
   - Direct database connections
   - CSV/JSON export files

### Data Transformation

To transform data between formats:

```python
from src.data_layer.trial_data.trial_data_transformer import TrialDataTransformer

# Create transformer
transformer = TrialDataTransformer()

# CSV to patient profiles
patient_profiles = transformer.csv_to_patient_profiles('data/patient_cohort.csv')

# EHR to patient profile
patient_profile = transformer.hms_ehr_to_patient_profile(ehr_data)

# Patient profile to genetic engine format
genetic_format = transformer.transform_patient_for_genetic_engine(patient_profile)
```

## 7. Monitoring and Management

### System Monitoring

The system provides comprehensive monitoring:

- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3002` (default login: admin/admin)
- **Kafka UI**: `http://localhost:8080`

### Health Checks

Check the health of system components:

```bash
curl http://localhost:8000/api/v1/health
```

Or use the CLI:

```bash
python cli.py health
```

### Logs

View system logs:

```bash
# API Gateway logs
docker-compose logs api-gateway

# HMS-A2A logs
docker-compose logs a2a-service

# All logs
docker-compose logs
```

## 8. Configuration Options

Configuration is managed through:

1. **Environment Variables**:
   ```bash
   # Example .env file
   LOG_LEVEL=debug
   GENETIC_ENGINE_MOCK=true
   DATABASE_URL=postgresql://postgres:postgres@postgres:5432/crohns_treatment
   ```

2. **Configuration Files**:
   - `config/system_config.json`: System-wide configuration
   - `config/genetic_engine_config.json`: Genetic engine parameters
   - `config/visualization_config.json`: Visualization settings

3. **Makefile Commands**:
   ```bash
   # Build the system
   make build

   # Start all services
   make start

   # Run tests
   make test

   # Clean up
   make clean
   ```

## 9. Development Workflow

For developers contributing to the system:

1. **Set up development environment**:
   ```bash
   make dev-env
   ```

2. **Run tests**:
   ```bash
   make test
   ```

3. **Format code**:
   ```bash
   make format
   ```

4. **Build the genetic engine**:
   ```bash
   make build-genetic-engine
   ```

5. **Test the genetic engine**:
   ```bash
   make test-genetic-engine
   ```

6. **Run integration tests**:
   ```bash
   make integration-test
   ```

## 10. Troubleshooting

### FFI Integration Issues

If you encounter FFI integration issues:

1. Verify that Rust components are built:
   ```bash
   cd src/coordination/genetic-engine
   cargo build --release
   ```

2. Check library paths:
   ```bash
   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/target/release
   ```

3. Confirm PyO3 installation:
   ```bash
   pip install maturin
   maturin develop --release
   ```

### Data Transformation Issues

If data transformation fails:

1. Validate input data format:
   ```bash
   python -m src.data_layer.trial_data.validate_data data/patient_example.json
   ```

2. Check for missing fields:
   ```bash
   python -m src.data_layer.trial_data.check_required_fields data/patient_example.json
   ```

3. Enable debug logging:
   ```bash
   export LOG_LEVEL=debug
   ```

### Docker Issues

If Docker containers fail to start:

1. Check Docker logs:
   ```bash
   docker-compose logs
   ```

2. Check Docker Compose configuration:
   ```bash
   docker-compose config
   ```

3. Rebuild containers:
   ```bash
   docker-compose build --no-cache
   ```

## 11. Next Steps

After getting started, explore these advanced topics:

1. **Technical Architecture**: Read the [Technical Architecture](architecture/TECHNICAL-ARCHITECTURE.md) document to understand the system design.

2. **Integration Points**: Explore the [Integration Points](architecture/INTEGRATION-POINTS.md) document to learn how to integrate with other systems.

3. **Adaptive Trial Framework**: Learn about the [Adaptive Trial Framework](ADAPTIVE-TRIAL-FRAMEWORK.md) to design effective clinical trials.

4. **Implementation Plan**: Review the [Implementation Plan](IMPLEMENTATION-PLAN-2025.md) to understand the development roadmap.

5. **Custom Extensions**: Extend the system with custom components, algorithms, or integrations.

For more information, refer to the [Integration Guide](INTEGRATION-GUIDE.md) and [Usage Examples](USAGE-EXAMPLES.md).