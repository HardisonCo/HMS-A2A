# HMS Integration Demo Guide

This document provides a step-by-step demonstration of the integration between the Crohn's Treatment System, HMS-DOC, and HMS-MFE. Follow these instructions to showcase the core functionality of the integration system.

## Prerequisites

1. Crohn's Treatment System installed and running
2. HMS-DOC component available at `/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-DOC`
3. HMS-MFE component available at `/Users/arionhardison/Desktop/Codify/SYSTEM-COMPONENTS/HMS-MFE`
4. Web browser for accessing the user interface

## Demo Walkthrough

### 1. System Overview Demo (5 minutes)

#### Step 1: Launch the Integration Dashboard

```bash
# Start the application
cd /Users/arionhardison/Desktop/Codify/crohns-treatment-system
python -m src.api_gateway.app
```

Then navigate to `http://localhost:8000/dashboard` in your web browser.

#### Step 2: Explain Key Components

Highlight the main sections of the dashboard:

- **System Status**: Shows the connection status of HMS-DOC and HMS-MFE
- **Publication Metrics**: Displays counts of publications for each system
- **Integration Actions**: Buttons for performing integration operations
- **Publication Tabs**: Switch between HMS-DOC and HMS-MFE publications

#### Step 3: Check System Status

Click the refresh button to check the current status of the integration system. Explain the meaning of the connection indicators.

### 2. Abstraction Analysis Demo (10 minutes)

#### Step 1: Run Abstraction Analysis

Navigate to the Clinical Trial Publisher interface:

1. Click "Select Clinical Trials"
2. Choose the "Adaptive Trial of JAK Inhibitors" trial
3. Click "Run Abstraction Analysis"
4. Monitor progress of the analysis

#### Step 2: Review Abstractions

Once the analysis completes:

1. Examine the identified abstractions
2. Point out key abstractions such as:
   - "Biomarker Response Patterns"
   - "Treatment Efficacy Correlations"
   - "JAK Inhibitor Mechanisms"
3. Highlight the confidence scores and evidence sources
4. Select 3-4 abstractions for the next step

#### Step 3: Explore Relationships

1. Click the "Relationships" tab
2. Show the automatically generated relationships between abstractions
3. Explain how these relationships form the basis for documentation structure

### 3. HMS-DOC Integration Demo (15 minutes)

#### Step 1: Export Abstractions to HMS-DOC

1. With the selected abstractions, click "Publish to HMS-DOC"
2. Enter a project name: "Crohns-JAK-Abstractions-Demo"
3. Click "Generate Documentation"
4. Show the progress indicator during processing

#### Step 2: View Generated Documentation

Once the documentation is generated:

1. Navigate to the output path shown in the success message
2. Open the `index.md` file
3. Show the generated documentation structure:
   - Project summary
   - Abstraction details
   - Relationship maps
   - Chapter organization

#### Step 3: Explain HMS-DOC Integration Points

Walk through the key integration points:

1. Data transformation from abstractions to HMS-DOC format
2. Relationship mapping for documentation structure
3. Document generation process
4. Output file organization

### 4. HMS-MFE Integration Demo (15 minutes)

#### Step 1: Publish Clinical Trial to HMS-MFE

1. Navigate back to the Clinical Trial Publisher
2. Ensure the "Adaptive Trial of JAK Inhibitors" trial is selected
3. Also select related abstractions
4. Click "Publish to HMS-MFE"
5. Enter a title: "JAK Inhibitor Trial Analysis"
6. Click "Publish"

#### Step 2: Open in HMS-MFE Writer

Once published:

1. Click "Open in Writer" from the success message
2. Show the HMS-MFE writer component with the loaded content
3. Demonstrate the editing capabilities:
   - Markdown editing
   - Format adjustments
   - Adding visualizations

#### Step 3: Explain HMS-MFE Integration Points

Walk through the key integration points:

1. Data transformation from clinical trials to HMS-MFE format
2. Writer component integration
3. Content structure and formatting
4. Handling of visualizations and metadata

### 5. Integrated Documentation Demo (10 minutes)

#### Step 1: Navigate to Integration Dashboard

1. Go back to the Integration Dashboard
2. Click the "Generate Comprehensive Documentation" button
3. Select both abstractions and clinical trials
4. Enter a project name: "Integrated-Crohns-JAK-Demo"
5. Click "Generate"

#### Step 2: Review Integrated Output

Once generated:

1. Show the HMS-DOC documentation component
2. Show the HMS-MFE publications
3. Explain how they are cross-referenced and linked

#### Step 3: Explain the Coordination Flow

Walk through the coordination process:

1. Data preparation for both systems
2. Parallel processing of both outputs
3. Cross-referencing between systems
4. Integrated navigation structure

### 6. Task Monitoring and Management Demo (5 minutes)

#### Step 1: View Active Tasks

1. Click the "Tasks" tab in the Integration Dashboard
2. Show any active tasks
3. Explain the task states: scheduled, running, completed, failed

#### Step 2: Schedule a New Task

1. Click "Schedule Task"
2. Select "Export Abstractions to HMS-DOC"
3. Configure the task parameters
4. Submit the task

#### Step 3: Monitor Task Progress

1. Watch the task status update
2. Explain the background processing architecture
3. Show task history and error handling

### 7. API Overview (5 minutes)

#### Step 1: Show API Documentation

Navigate to `http://localhost:8000/api/docs` to show the API documentation.

#### Step 2: Demonstrate Example API Calls

Show example API calls for key operations:

```bash
# Check system status
curl http://localhost:8000/api/doc-integration/status

# List publications
curl http://localhost:8000/api/doc-integration/publications

# Export abstractions (simplified example)
curl -X POST http://localhost:8000/api/doc-integration/export-abstractions \
  -H "Content-Type: application/json" \
  -d '{"abstractions": [...], "relationships": [...]}'
```

#### Step 3: Explain API Architecture

Brief explanation of:
- RESTful design
- JSON data formats
- Error handling
- Authentication (if applicable)

## Interactive Demonstration

### Scenario: Analyze and Publish New Trial Data

Walk through a complete end-to-end scenario:

1. Import a new clinical trial dataset
2. Run abstraction analysis
3. Review and select relevant abstractions
4. Generate comprehensive documentation
5. View results in both HMS-DOC and HMS-MFE
6. Make edits in the HMS-MFE writer
7. Regenerate documentation with updates

## Key Talking Points

Throughout the demo, emphasize these key points:

1. **Seamless Integration**: The system bridges between different HMS components
2. **Data Transformation**: Complex transformations handled automatically
3. **Comprehensive Documentation**: Complete documentation from analysis to publication
4. **User Experience**: Intuitive interface for researchers without technical background
5. **Extensibility**: System can be extended to support additional HMS components
6. **Performance**: Background processing for long-running tasks
7. **Error Handling**: Robust error handling and recovery

## Fallback Options

If any component is unavailable during the demo:

1. **HMS-DOC Unavailable**: Use simulation mode to show documentations structure
2. **HMS-MFE Unavailable**: Show JSON output and explain writer integration
3. **Network Issues**: Use cached data from previous runs

## Demo Conclusion

Summarize the demonstration with:

1. Review of the key integration points
2. Benefits for researchers and clinicians
3. Future development roadmap
4. Q&A session

## Resources

- [HMS Integration Specifications](./HMS-INTEGRATION-SPECS.md)
- [HMS Integration User Guide](./HMS-INTEGRATION-GUIDE.md)
- [API Documentation](http://localhost:8000/api/docs)
- [Crohn's Treatment System Documentation](../README.md)