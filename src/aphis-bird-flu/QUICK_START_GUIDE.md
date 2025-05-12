# APHIS Bird Flu Tracking System: Quick Start Guide

This guide provides step-by-step instructions for setting up and running the APHIS Bird Flu Tracking System.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/aphis-bird-flu.git
   cd aphis-bird-flu
   ```

2. **Set up a virtual environment (recommended):**

   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Running the System

### Starting the API Server

1. **Start the FastAPI server:**

   ```bash
   cd src
   uvicorn system-supervisors.animal_health.api:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API documentation:**

   Open your browser and navigate to:
   http://localhost:8000/docs

   This will display the Swagger UI with all available API endpoints.

### Running the Demo

The system includes a comprehensive demonstration script that shows all major features:

1. **Run the full demo:**

   ```bash
   cd demo
   python demo_script.py --all
   ```

2. **Run specific component demos:**

   ```bash
   # Adaptive sampling demo
   python demo_script.py --sampling
   
   # Outbreak detection demo
   python demo_script.py --detection
   
   # Predictive modeling demo
   python demo_script.py --prediction
   
   # Notification system demo
   python demo_script.py --notification
   
   # Visualization services demo
   python demo_script.py --visualization
   
   # Genetic analysis demo
   python demo_script.py --genetic
   ```

## Testing the API

The system includes a test script for verifying API functionality:

```bash
python test_genetic_api.py
```

You can specify a different host or port with:

```bash
python test_genetic_api.py --host another-host --port 9000
```

## System Components

The APHIS Bird Flu Tracking System consists of six main components:

1. **Adaptive Sampling:** Optimization of surveillance resource allocation
2. **Outbreak Detection:** Statistical methods for early outbreak detection
3. **Predictive Modeling:** Forecasting disease spread using ensemble approaches
4. **Notification System:** Multi-channel alerts to stakeholders
5. **Visualization Services:** Maps, charts, and dashboards for situation awareness
6. **Genetic Analysis:** Viral genomics and transmission dynamics analysis

## Directory Structure

- `src/` - Source code for the system
  - `system-supervisors/` - Main system components using the system-supervisor pattern
    - `animal_health/` - Animal health supervisor for avian influenza tracking
      - `adapters/` - External system adapters
      - `controllers/` - API endpoint controllers
      - `models/` - Domain models
      - `services/` - Core services by component
- `demo/` - Demonstration scripts and sample data
- `tests/` - System tests

## Configuration

Configuration files are located in:

```
src/system-supervisors/animal_health/config/
```

Key configuration files include:

- `notification_config.json` - Notification channel settings
- `sampling_config.json` - Adaptive sampling parameters
- `detection_config.json` - Outbreak detection parameters

## Next Steps

After getting the system running, consider:

1. **Configuring External Services:**
   - Set up email/SMS for notifications
   - Configure GIS service for mapping

2. **Loading Your Data:**
   - Import surveillance site data
   - Import case history
   - Import genetic sequence data

3. **Customizing Models:**
   - Adjust detection thresholds
   - Configure prediction models
   - Set genetic analysis parameters

## Troubleshooting

If you encounter issues:

1. **API server won't start:**
   - Ensure you have the correct Python version
   - Verify all dependencies are installed
   - Check port availability

2. **Demo script errors:**
   - Ensure the data directory has required files
   - Install optional dependencies like matplotlib

3. **API testing issues:**
   - Verify the API server is running
   - Check the host and port settings
   - Examine server logs for errors

## Additional Resources

For more information, see:

- `SYSTEM_OVERVIEW.md` - Comprehensive system overview
- `demo/README.md` - Detailed demo documentation
- `API_REFERENCE.md` - API endpoint reference

## Getting Help

If you need assistance:

- Submit issues on GitHub
- Contact the development team at support@example.com
- Consult the detailed documentation in the `docs/` directory