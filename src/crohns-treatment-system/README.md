# Crohn's Disease Treatment System

A comprehensive platform for optimizing Crohn's disease treatment through adaptive clinical trials, genetic algorithms, multi-agent coordination, and abstraction analysis.

## Overview

The Crohn's Disease Treatment System integrates advanced research capabilities with genetic optimization to provide personalized treatment recommendations. It leverages the HMS component architecture to create a flexible and powerful platform for researchers, healthcare providers, and patients. The system utilizes abstraction and relationship analysis to identify patterns in clinical trial data and enhance treatment recommendations.

## Key Features

- **Personalized Treatment Optimization**: Uses genetic algorithms to optimize treatment plans based on patient biomarkers
- **Adaptive Clinical Trials**: Manages adaptive clinical trials that evolve based on interim results
- **Genetic Analysis**: Analyzes genetic sequences for Crohn's disease variants and treatment implications
- **Abstraction Analysis**: Identifies key abstractions and relationships in clinical trial data
- **Relationship-Enhanced Treatment**: Leverages relationship analysis to improve treatment recommendations
- **Integration with EHR Systems**: Connects with electronic health records using FHIR standards
- **Research-Driven Approach**: Incorporates latest research findings into treatment recommendations
- **Multi-Agent Coordination**: Orchestrates interactions between different system components

## System Architecture

The system consists of the following key components:

- **Abstraction Analysis Engine**: Identifies key abstractions and relationships in clinical trial data
- **Enhanced Genetic Engine**: Optimizes treatment plans leveraging abstraction and relationship insights
- **Enhanced Adaptive Trial Framework**: Designs adaptive trials with biomarker stratification based on abstractions
- **HMS-AGX Research Engine**: Provides deep research capabilities for Crohn's disease treatments, biomarkers, and clinical evidence
- **HMS-A2A Agent Coordination**: Orchestrates communication between different system components
- **Genetic Engine**: Optimizes treatment plans for individual patients using genetic algorithms
- **Adaptive Clinical Trial Framework**: Manages adaptive clinical trials for testing and validating treatments
- **HMS-EHR/EMR Integration**: Connects to electronic health records and medical records systems
- **HMS-KNO**: Knowledge base with CoRT (Chain of Recursive Thoughts)
- **Prover-Orchestrator**: Formal verification of treatment protocols
- **Self-Healing System**: Detection and recovery from system failures
- **HMS-UHC**: Health insurance coordination and eligibility verification

## Implementation Status

The project is currently in the Foundation Phase (Phase 1) with approximately 60% completion:

- Abstraction analysis engine: 100% complete
- Enhanced genetic engine: 100% complete
- Enhanced adaptive trial framework: 100% complete
- Research component (HMS-AGX): 80% complete
- Agent coordination (HMS-A2A): 70% complete
- Genetic optimization engine: 50% complete
- Adaptive clinical trial framework: 60% complete
- FFI integration: 70% complete

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Rust (version 1.73 or later)
- Python (version 3.11 or later)
- Node.js (version 18 or later)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/crohns-treatment-system.git
   cd crohns-treatment-system
   ```

2. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

3. Start the development environment:
   ```bash
   make setup-dev
   ```

### Usage

#### Running the System

Start all services:
```bash
make start
```

Run the demo:
```bash
make run-demo
```

Run the abstraction analysis demo:
```bash
python run_abstraction_demo.py
```

#### Development Commands

Build Docker images:
```bash
make build
```

Run tests:
```bash
make test
```

Format code:
```bash
make format
```

## Project Structure

```
crohns-treatment-system/
├── src/
│   ├── analysis/              # Abstraction analysis components
│   │   ├── abstraction_analysis.py  # Core abstraction analysis
│   │   └── node.py            # Base node for analysis pipeline
│   ├── api_gateway/           # API endpoints
│   │   ├── app.py             # Main application entry point
│   │   └── abstraction_analysis_controller.py  # API controller for abstractions
│   ├── coordination/          # Agent coordination components
│   │   ├── a2a-integration/   # HMS-A2A integration
│   │   │   └── enhanced_adaptive_trial.py  # Enhanced adaptive trial framework
│   │   ├── genetic-engine/    # Genetic optimization engine
│   │   │   └── enhanced_genetic_engine.py  # Abstraction-enhanced genetic engine
│   │   └── controllers/       # Core controllers
│   ├── data-layer/            # Data access components
│   │   ├── ehr-integration/   # EHR integration
│   │   └── trial-data/        # Trial data processing
│   ├── research/              # Research components
│   │   └── agx-integration/   # HMS-AGX integration
│   └── visualization/         # Visualization components
│       ├── trial_results_visualizer.py  # Trial result visualizations
│       └── abstraction_visualizer.py    # Abstraction visualizations
├── docs/                      # Documentation
│   ├── architecture/          # Architecture documentation
│   ├── deployment/            # Deployment documentation
│   └── ENHANCED-ANALYSIS-IMPLEMENTATION-PLAN.md  # Implementation plan
├── tests/                     # Tests
│   ├── data/                  # Test data
│   └── test_abstraction_analysis.py  # Abstraction analysis tests
├── infrastructure/            # Infrastructure configuration
├── run_abstraction_demo.py    # Abstraction analysis demo script
└── demo/                      # Demo scripts and data
```

## Documentation

Detailed documentation can be found in the following files:

- [Enhanced Analysis Implementation Plan](/docs/ENHANCED-ANALYSIS-IMPLEMENTATION-PLAN.md): Plan for abstraction analysis integration
- [Deployment Strategy](/docs/deployment/DEPLOYMENT-STRATEGY.md): Comprehensive deployment approach
- [CI/CD Pipeline](/docs/deployment/CI-CD-PIPELINE.md): Continuous integration and deployment setup
- [Kubernetes Deployment](/docs/deployment/KUBERNETES-DEPLOYMENT.md): Kubernetes configuration and management
- [FFI Integration Plan](/docs/architecture/FFI-INTEGRATION-PLAN.md): Details of component integration
- [Adaptive Trial Framework](/docs/protocols/ADAPTIVE-TRIAL-FRAMEWORK.md): Design of the clinical trial system
- [Implementation Plan](/docs/IMPLEMENTATION-PLAN.md): Project roadmap and tracking
- [Technical Architecture](/docs/architecture/TECHNICAL-ARCHITECTURE.md): System architecture and design
- [Integration Points](/docs/architecture/INTEGRATION-POINTS.md): Detailed integration specifications

## Project Timeline

- **Phase 1: Foundation** (Months 1-3): Basic infrastructure and interfaces
- **Phase 2: Core Implementation** (Months 4-6): Key system functionality
- **Phase 3: Integration** (Months 7-9): Component connections
- **Phase 4: Validation** (Months 10-12): System testing
- **Phase 5: Clinical Deployment** (Months 13-24): Real-world deployment

## Contributing

This project follows a structured implementation plan. Before contributing, please review the implementation plan and roadmap to understand the current priorities and development approach.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.