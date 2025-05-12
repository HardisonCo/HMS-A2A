# APHIS Bird Flu Tracking System Demo

This directory contains a demonstration of the APHIS Bird Flu Tracking System, showcasing its key capabilities including adaptive sampling, outbreak detection, predictive modeling, notifications, visualizations, and genetic analysis.

## Demo Overview

The demonstration script simulates the core functionalities of the system using mock data and API responses. It provides a guided tour through each major component, showing how they work together to form a comprehensive surveillance and response platform.

## Running the Demo

### Prerequisites

- Python 3.10+
- Required packages: matplotlib, numpy (for sample image generation)

### Setup

1. Ensure you have the required Python packages:
   ```bash
   pip install matplotlib numpy
   ```

2. Make sure the demo script is executable:
   ```bash
   chmod +x demo_script.py
   ```

### Execution

Run the full demonstration:
```bash
./demo_script.py --all
```

Or run specific component demonstrations:
```bash
./demo_script.py --sampling     # Adaptive sampling demonstration
./demo_script.py --detection    # Outbreak detection demonstration
./demo_script.py --prediction   # Predictive modeling demonstration
./demo_script.py --notification # Notification system demonstration
./demo_script.py --visualization # Visualization services demonstration
./demo_script.py --genetic      # Genetic analysis demonstration
```

## Demo Data

The `data` directory contains sample data used by the demonstration:

- `demo_cases.json`: Sample avian influenza case data
- `demo_surveillance_sites.json`: Sample surveillance site information
- `demo_regions.json`: Sample geographic region data
- `sample_map.png`: Sample map visualization (generated on first run)
- `sample_chart.png`: Sample chart visualization (generated on first run)

## Demo Output

The demonstration outputs are saved to the `output` directory:
- JSON files with detailed results from each component
- PNG files with generated visualizations

## Demo Components

### 1. Adaptive Sampling

Demonstrates how the system optimizes surveillance resource allocation using response-adaptive sampling strategies derived from clinical trials.

### 2. Outbreak Detection

Shows the statistical methods used for early outbreak detection, including Sequential Probability Ratio Test (SPRT), Group Sequential Testing, CUSUM, and spatial cluster detection.

### 3. Predictive Modeling

Illustrates how the system forecasts disease spread using ensemble models that combine distance-based, network-based, and Gaussian Process spatiotemporal approaches.

### 4. Notification System

Demonstrates the multi-channel notification capabilities for alerting stakeholders about outbreaks and high-risk predictions.

### 5. Visualization Services

Showcases the system's ability to generate maps, charts, and comprehensive dashboards for situation awareness.

### 6. Genetic Analysis

Demonstrates the system's capabilities for analyzing viral genetic sequences, identifying mutations, determining lineages, assessing antigenic properties, evaluating zoonotic potential, and analyzing transmission pathways between cases.

## Notes

- This is a simulated demonstration that does not require an active API server
- The demonstration uses mock responses to simulate API calls
- Sample visualizations are generated using matplotlib if available
- For a real system demonstration, you would need to configure the API_BASE_URL in the script