# Crohn's Treatment System CLI Usage

This document provides detailed instructions for using the Crohn's Disease Treatment System Command Line Interface (CLI).

## Overview

The CLI provides a convenient way to interact with the system for common operations:

- Treatment optimization for individual patients
- Running adaptive clinical trials
- Monitoring system health
- Generating visualizations and reports

## Installation

The CLI is automatically installed when you set up the system:

```bash
# Set up the system
./foundation-setup.sh
```

## Basic Usage

The CLI follows a consistent command syntax:

```bash
python cli.py <command> <arguments> [options]
```

For help with any command:

```bash
python cli.py <command> --help
```

## Available Commands

### 1. Treatment Optimization

Optimize treatment for a patient based on their data:

```bash
python cli.py optimize <patient_file> [options]
```

#### Arguments:
- `patient_file`: Path to the patient data file (JSON format)

#### Options:
- `-o, --output <file>`: Output file for the treatment plan (default: `output/treatment_plan.json`)
- `--max-medications <num>`: Maximum number of medications in the plan (default: 3)
- `--optimization-mode <mode>`: Optimization mode (`efficacy`, `safety`, or `balanced`, default: `balanced`)
- `--include-alternatives`: Include alternative treatment plans in the output

#### Example:
```bash
# Optimize treatment with efficacy focus and include alternatives
python cli.py optimize data/patient_example.json -o output/treatment_plan.json --optimization-mode efficacy --include-alternatives
```

### 2. Adaptive Trial Execution

Run an adaptive clinical trial with a specified protocol and patient cohort:

```bash
python cli.py trial <protocol_file> <patient_file> [options]
```

#### Arguments:
- `protocol_file`: Path to the trial protocol file (JSON format)
- `patient_file`: Path to the patient cohort file (JSON or CSV format)

#### Options:
- `-o, --output <file>`: Output file for the trial results (default: `output/trial_results.json`)
- `-v, --visualize`: Generate visualizations of trial results
- `--max-adaptations <num>`: Maximum number of adaptations to perform (default: 5)
- `--interim-analysis <points>`: Comma-separated list of interim analysis points (e.g., `0.25,0.5,0.75`)
- `--simulate-only`: Run in simulation mode only (no actual adaptations)

#### Example:
```bash
# Run a trial with visualizations and custom interim analysis points
python cli.py trial data/trial_protocol.json data/patient_cohort.csv -o output/trial_results.json -v --interim-analysis 0.3,0.6
```

### 3. System Health Monitoring

Monitor and report on system health:

```bash
python cli.py health [options]
```

#### Options:
- `-o, --output <file>`: Output file for the health report (optional)
- `--components <list>`: Comma-separated list of components to check (default: all)
- `--detailed`: Include detailed information in the report
- `--fix`: Attempt to fix any issues found

#### Example:
```bash
# Check health with detailed report and attempt to fix issues
python cli.py health -o output/health_report.json --detailed --fix
```

### 4. Visualization Generation

Generate visualizations from trial results:

```bash
python cli.py visualize <results_file> [options]
```

#### Arguments:
- `results_file`: Path to the trial results file (JSON format)

#### Options:
- `-o, --output-dir <dir>`: Output directory for visualizations (default: `output/visualizations`)
- `--type <types>`: Comma-separated list of visualization types to generate (default: all)
- `--format <format>`: Output format (`png`, `svg`, or `html`, default: `png`)
- `--theme <theme>`: Visualization theme (`light` or `dark`, default: `light`)

#### Example:
```bash
# Generate SVG visualizations with dark theme
python cli.py visualize output/trial_results.json -o output/visualization_report --format svg --theme dark
```

### 5. Biomarker Analysis

Analyze biomarker correlations with treatment response:

```bash
python cli.py analyze-biomarkers <results_file> [options]
```

#### Arguments:
- `results_file`: Path to the trial results file (JSON format)

#### Options:
- `-o, --output-dir <dir>`: Output directory for analysis (default: `output/biomarker_analysis`)
- `--biomarkers <list>`: Comma-separated list of biomarkers to analyze (default: all)
- `--correlation-method <method>`: Correlation method (`pearson`, `spearman`, or `kendall`, default: `pearson`)
- `--visualize`: Generate visualizations of correlations

#### Example:
```bash
# Analyze specific biomarkers with Spearman correlation
python cli.py analyze-biomarkers output/trial_results.json -o output/biomarkers --biomarkers NOD2,IL23R,CRP --correlation-method spearman --visualize
```

### 6. Data Import

Import patient data from various sources:

```bash
python cli.py import <source> <output_file> [options]
```

#### Arguments:
- `source`: Data source (`csv`, `json`, `ehr`, or `fhir`)
- `output_file`: Output file for the imported data

#### Options:
- `--input <file>`: Input file path (for CSV/JSON sources)
- `--ehr-config <file>`: EHR configuration file (for EHR source)
- `--fhir-url <url>`: FHIR server URL (for FHIR source)
- `--fhir-token <token>`: FHIR authentication token (for FHIR source)
- `--format <format>`: Output format (`json` or `csv`, default: `json`)

#### Example:
```bash
# Import from CSV file
python cli.py import csv output/patients.json --input data/patients.csv

# Import from FHIR server
python cli.py import fhir output/patients.json --fhir-url https://fhir.example.com/api --fhir-token TOKEN
```

### 7. Data Export

Export patient data or trial results to various formats:

```bash
python cli.py export <file> <format> [options]
```

#### Arguments:
- `file`: Input file to export
- `format`: Export format (`csv`, `json`, `fhir`, or `ehr`)

#### Options:
- `-o, --output <file>`: Output file (default: based on input file and format)
- `--ehr-config <file>`: EHR configuration file (for EHR format)
- `--fhir-url <url>`: FHIR server URL (for FHIR format)
- `--fhir-token <token>`: FHIR authentication token (for FHIR format)

#### Example:
```bash
# Export trial results to CSV
python cli.py export output/trial_results.json csv -o output/trial_results.csv

# Export patient data to FHIR
python cli.py export output/patients.json fhir --fhir-url https://fhir.example.com/api --fhir-token TOKEN
```

## Advanced Usage

### Running Multiple Commands

You can run multiple commands in sequence using bash:

```bash
# Run trial and then visualize results
python cli.py trial data/protocol.json data/patients.csv -o output/results.json && \
python cli.py visualize output/results.json -o output/visualizations
```

### Using Environment Variables

You can use environment variables to configure the CLI:

```bash
# Set configuration via environment variables
export CROHNS_OUTPUT_DIR=my_output
export CROHNS_LOG_LEVEL=DEBUG
export CROHNS_CONFIG_FILE=config/custom_config.json

# Run command with environment-based configuration
python cli.py optimize data/patient.json
```

### Input/Output Redirection

You can use standard input/output redirection:

```bash
# Pipe output to another command
python cli.py health | grep -i error

# Use output as input for another command
python cli.py optimize data/patient.json | python cli.py export - csv -o patient_treatment.csv
```

## Examples

### Example 1: Complete Patient Analysis Workflow

```bash
# Import patient data from CSV
python cli.py import csv output/patients.json --input data/patients.csv

# Optimize treatment for each patient
for patient in output/patients/*.json; do
  python cli.py optimize $patient -o output/treatments/$(basename $patient)
done

# Generate summary report
python cli.py summarize output/treatments/*.json -o output/treatment_summary.json --visualize
```

### Example 2: Adaptive Trial with Analysis

```bash
# Run adaptive trial
python cli.py trial data/protocol.json data/patients.csv -o output/trial_results.json -v

# Analyze biomarkers
python cli.py analyze-biomarkers output/trial_results.json -o output/biomarker_analysis --visualize

# Generate comprehensive report
python cli.py report output/trial_results.json output/biomarker_analysis -o output/trial_report.html
```

### Example 3: System Maintenance

```bash
# Check system health
python cli.py health -o output/health_report.json --detailed

# Fix issues
python cli.py health --fix

# Verify fixes
python cli.py health -o output/health_report_after.json --detailed
```

## Error Handling

The CLI provides detailed error messages with suggestions for resolution:

```bash
# Example error output
$ python cli.py optimize nonexistent_file.json
Error: Could not open file 'nonexistent_file.json': File not found
Suggestions:
- Check if the file exists and the path is correct
- Use the 'import' command to create patient data files
- See examples in the 'data' directory
```

## Logging

You can control logging with the `--log-level` option:

```bash
# Enable debug logging
python cli.py optimize data/patient.json --log-level DEBUG
```

Available log levels:
- `DEBUG`: Detailed debugging information
- `INFO`: Informational messages about progress
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors that prevent execution

## Configuration

The CLI can be configured through a configuration file:

```bash
# Specify a configuration file
python cli.py --config config/custom_config.json optimize data/patient.json
```

Example configuration file (`config/custom_config.json`):
```json
{
  "output_dir": "custom_output",
  "log_level": "INFO",
  "genetic_engine": {
    "population_size": 200,
    "max_generations": 100,
    "mutation_rate": 0.1,
    "crossover_rate": 0.8
  },
  "visualization": {
    "theme": "dark",
    "format": "svg",
    "dpi": 300
  }
}
```

## Performance Tips

1. **Batch Processing**: For large datasets, use batch processing:
   ```bash
   python cli.py trial data/protocol.json data/patients.csv --batch-size 100
   ```

2. **Parallel Processing**: Enable parallel processing for faster execution:
   ```bash
   python cli.py optimize data/patient.json --parallel
   ```

3. **Limit Output**: Reduce output for faster processing:
   ```bash
   python cli.py trial data/protocol.json data/patients.csv --minimal-output
   ```

## Conclusion

The Crohn's Disease Treatment System CLI provides a powerful and flexible interface for working with the system. By combining various commands and options, you can perform complex operations and workflows to optimize treatment, run trials, and analyze results.