# APHIS Bird Flu Tracking System - User Guide

## 1. Introduction

Welcome to the APHIS Bird Flu Tracking System, a comprehensive platform for monitoring, detecting, and responding to avian influenza outbreaks. This guide will help you understand the system's capabilities and how to effectively use its features.

### 1.1 Purpose of the System

The APHIS Bird Flu Tracking System applies advanced adaptive methodologies from clinical trials to:

- Optimize surveillance resource allocation
- Detect outbreaks earlier and more reliably
- Forecast disease spread with greater accuracy
- Coordinate rapid response efforts
- Visualize critical data for decision support

### 1.2 Target Audience

This guide is intended for:

- **Field personnel** conducting surveillance activities
- **Epidemiologists** analyzing outbreak patterns
- **Laboratory coordinators** managing testing workflows
- **Emergency responders** coordinating interventions
- **Program managers** overseeing surveillance efforts
- **Policy makers** requiring situational awareness

### 1.3 System Requirements

To access the system, you need:

- A modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connectivity
- Authorized user credentials
- For field use: mobile device with GPS capabilities

## 2. Getting Started

### 2.1 Accessing the System

1. Navigate to: `https://aphis-birdflue.usda.gov`
2. Enter your username and password
3. Complete two-factor authentication if enabled
4. You will be directed to the dashboard appropriate for your role

### 2.2 User Interface Overview

The system interface is organized into several key areas:

- **Navigation Menu**: Access different system modules
- **Dashboard**: View summary statistics and visualizations
- **Maps View**: Explore geospatial data
- **Reports**: Generate and view standardized reports
- **Admin Panel**: Manage system settings (admin users only)

### 2.3 User Roles and Permissions

The system supports several user roles with different permissions:

| Role | Description | Key Permissions |
|------|-------------|----------------|
| Viewer | Read-only access | View dashboards and reports |
| Field User | Surveillance data collection | Submit data, view local reports |
| Analyst | Data analysis and visualization | Create custom visualizations, export data |
| Coordinator | Response coordination | Manage alerts, view all regions |
| Administrator | System management | Configure settings, manage users |

### 2.4 Help and Support

For assistance using the system:

- Click the "Help" icon (?) in the top menu
- Contact the support team at `aphis-support@usda.gov`
- Call the help desk at 1-800-XXX-XXXX

## 3. Core Modules

### 3.1 Dashboard

The dashboard provides a high-level overview of the current situation.

#### 3.1.1 Accessing the Dashboard

1. Select "Dashboard" from the main navigation menu
2. Choose "National" or select a specific region/state
3. Adjust the date range using the calendar control

#### 3.1.2 Dashboard Components

- **Case Summary**: Total, recent, and active cases
- **Surveillance Activity**: Sampling events and positivity rates
- **Risk Assessment**: Current high-risk areas
- **Trend Visualization**: Case trends over time
- **Subtype Distribution**: Breakdown of virus subtypes
- **Geographic Heat Map**: Case distribution by region

#### 3.1.3 Customizing the Dashboard

1. Click "Customize" in the top-right corner
2. Select/deselect dashboard components
3. Arrange components by dragging and dropping
4. Save your custom layout

### 3.2 Maps and Geospatial Analysis

#### 3.2.1 Accessing the Maps Module

1. Select "Maps" from the main navigation menu
2. Choose a map type from the dropdown menu
3. Set filters for date range, case types, etc.

#### 3.2.2 Available Map Types

- **Case Distribution Map**: Shows confirmed and suspected cases
- **Risk Prediction Map**: Displays forecast risk levels by region
- **Surveillance Coverage Map**: Shows sampling locations and intensity
- **Transmission Network**: Visualizes likely spread patterns

#### 3.2.3 Map Controls

- Zoom in/out using the scroll wheel or +/- buttons
- Pan by clicking and dragging
- Select regions by clicking on them
- Toggle layers using the layer control panel
- Use the legend to interpret colors and symbols

#### 3.2.4 Advanced Map Features

- **Animation**: View case progression over time
- **Cluster Analysis**: Identify statistically significant clusters
- **Buffer Analysis**: View cases within a specified distance
- **Export**: Save map as image or download as GeoJSON

### 3.3 Surveillance Management

#### 3.3.1 Accessing Surveillance Management

1. Select "Surveillance" from the main navigation menu
2. Choose a function (Sites, Plans, Events, Allocation)

#### 3.3.2 Managing Surveillance Sites

- **View Sites**: Browse all surveillance sites
- **Add Site**: Register a new surveillance location
- **Edit Site**: Update site information
- **Deactivate Site**: Mark a site as inactive

#### 3.3.3 Planning Surveillance Activities

1. Navigate to "Surveillance > Plans"
2. Select "Create New Plan" or choose an existing plan
3. Set parameters:
   - Time period
   - Target regions
   - Sampling strategy
   - Resource constraints
4. Run allocation algorithm
5. Review and adjust allocations
6. Finalize and distribute plan

#### 3.3.4 Recording Surveillance Events

1. Navigate to "Surveillance > Events"
2. Select "Record New Event"
3. Enter event details:
   - Date and location
   - Samples collected
   - Field observations
   - Test results (if available)
4. Submit the event

### 3.4 Outbreak Detection

#### 3.4.1 Accessing Outbreak Detection

1. Select "Detection" from the main navigation menu
2. Choose detection method or "Run All"

#### 3.4.2 Detection Methods

- **Sequential Testing**: Early detection of significant changes
- **Group Sequential**: Multiple testing with controlled error rates
- **CUSUM**: Detecting shifts in baseline rates
- **Spatial Scan**: Identifying geographic clusters

#### 3.4.3 Configuring Detection Parameters

1. Select the detection method
2. Adjust parameters:
   - Significance level
   - Power/sensitivity
   - Baseline period
   - Geographic resolution
3. Run the analysis

#### 3.4.4 Interpreting Results

- **Signals Table**: Detected signals with statistical significance
- **Signal Details**: In-depth information about each detection
- **Cluster Map**: Visualization of detected clusters
- **Statistical Summary**: Key metrics and p-values

### 3.5 Predictive Modeling

#### 3.5.1 Accessing Predictive Modeling

1. Select "Predictions" from the main navigation menu
2. Choose forecast horizon (7, 14, 30 days)

#### 3.5.2 Available Models

- **Distance-Based**: Proximity-based transmission
- **Network-Based**: Spread through connected networks
- **Gaussian Process**: Spatiotemporal pattern modeling
- **Ensemble**: Combined approach for optimal accuracy

#### 3.5.3 Generating Forecasts

1. Select model(s) to use
2. Set forecast parameters:
   - Time horizon
   - Geographic scope
   - Environmental factors to include
3. Run the forecast
4. Review results

#### 3.5.4 Interpreting Forecasts

- **Risk Map**: Geographical visualization of risk
- **Predicted Cases**: Estimated new cases by region
- **Confidence Intervals**: Uncertainty in predictions
- **High-Risk Regions**: Areas of concern requiring attention

### 3.6 Notifications and Alerting

#### 3.6.1 Accessing Notification Settings

1. Select "Notifications" from the main navigation menu
2. Choose "Settings" or "History"

#### 3.6.2 Configuring Notifications

1. Select notification types to receive:
   - Outbreak detections
   - Risk predictions
   - Surveillance updates
   - System notifications
2. Set delivery channels:
   - Email
   - SMS
   - Mobile app
   - Web browser
3. Configure thresholds for alerts
4. Set schedule and frequency

#### 3.6.3 Reviewing Alert History

1. Navigate to "Notifications > History"
2. Filter by date range, type, or status
3. View delivery status and recipient information
4. Access related data for each notification

#### 3.6.4 Creating Manual Alerts

1. Navigate to "Notifications > Create Alert"
2. Select alert type and severity
3. Choose recipients or recipient groups
4. Compose alert message
5. Add attachments if needed
6. Send immediately or schedule for later

### 3.7 Reports and Analytics

#### 3.7.1 Accessing Reports

1. Select "Reports" from the main navigation menu
2. Choose a report type

#### 3.7.2 Standard Reports

- **Situational Awareness**: Current status overview
- **Weekly Summary**: Activity from the past 7 days
- **Monthly Review**: Trends and patterns for the month
- **Surveillance Performance**: Effectiveness metrics
- **Laboratory Testing**: Sample processing statistics

#### 3.7.3 Custom Reports

1. Select "Reports > Custom Report"
2. Choose data elements to include
3. Set filters and parameters
4. Select visualization types
5. Generate and preview the report
6. Save, export, or schedule for regular delivery

#### 3.7.4 Data Export

1. Navigate to "Reports > Data Export"
2. Select data type and date range
3. Choose export format (CSV, Excel, JSON)
4. Apply any necessary filters
5. Generate and download the export

## 4. Advanced Features

### 4.1 Mobile Field Application

The mobile field application allows surveillance teams to:
- Record sampling events
- Submit data offline
- Receive optimized sampling plans
- View local risk maps
- Get real-time alerts

#### 4.1.1 Installing the Mobile App

1. Download from App Store (iOS) or Google Play (Android)
2. Login with your system credentials
3. Complete initial synchronization

#### 4.1.2 Using the Mobile App

- **Sampling**: Record sampling events and results
- **Maps**: View local cases and risk levels
- **Tasks**: Check assigned surveillance activities
- **Sync**: Upload new data when connected

### 4.2 Administrative Functions

#### 4.2.1 User Management

1. Navigate to "Admin > Users"
2. View, add, edit, or deactivate users
3. Assign roles and permissions
4. Reset passwords if needed

#### 4.2.2 System Configuration

1. Navigate to "Admin > Configuration"
2. Adjust system parameters
3. Configure integration settings
4. Manage reference data

#### 4.2.3 Audit Logs

1. Navigate to "Admin > Audit Logs"
2. Review system activity
3. Filter by user, action, or date
4. Export logs for record-keeping

### 4.3 API Integration

The system provides APIs for integration with other platforms.

#### 4.3.1 API Documentation

1. Navigate to "Help > API Documentation"
2. Browse available endpoints
3. View request/response formats
4. Test API calls in the interactive console

#### 4.3.2 API Keys

1. Navigate to "Admin > API Keys"
2. Generate new API keys
3. Assign permissions to keys
4. Revoke keys if needed

## 5. Best Practices

### 5.1 Data Quality

To ensure high-quality data:
- Complete all required fields
- Use standardized formats for dates and locations
- Verify information before submission
- Report any data inconsistencies

### 5.2 Effective Surveillance Planning

For optimal surveillance:
- Review allocation recommendations carefully
- Balance targeted and routine surveillance
- Maintain consistent sampling frequency
- Document deviations from the sampling plan

### 5.3 Interpreting Predictions

When using predictive models:
- Consider confidence intervals, not just point estimates
- Use ensemble model results for important decisions
- Understand the limitations of each model type
- Compare predictions with actual outcomes to assess accuracy

### 5.4 Response Coordination

For effective response:
- Use the notification system for official communications
- Document response activities in the system
- Update case status promptly
- Share relevant information with stakeholders

## 6. Troubleshooting

### 6.1 Common Issues

| Issue | Possible Solution |
|-------|-------------------|
| Login failure | Check username/password, contact IT if persistent |
| Slow map loading | Reduce geographic scope or simplify layers |
| Missing data | Check filters, ensure data synchronization |
| Export errors | Try a different format or reduce data volume |
| Mobile app sync issues | Check internet connection, try manual sync |

### 6.2 Error Messages

Common error messages and their meanings:
- "Unauthorized Access": Login required or insufficient permissions
- "Data Validation Failed": Check required fields and formats
- "Service Unavailable": System maintenance or connectivity issues
- "Synchronization Error": Version mismatch or connectivity problem

### 6.3 Getting Help

For assistance:
- Consult this user guide
- Use the built-in help feature
- Contact the support team
- Check the knowledge base
- Attend scheduled training sessions

## 7. Glossary

| Term | Definition |
|------|------------|
| APHIS | Animal and Plant Health Inspection Service |
| Case | Confirmed or suspected instance of avian influenza |
| CUSUM | Cumulative Sum - statistical method for detecting changes |
| Ensemble Model | Combination of multiple predictive models |
| HPAI | Highly Pathogenic Avian Influenza |
| LPAI | Low Pathogenic Avian Influenza |
| Sentinel Site | Strategic location for ongoing surveillance |
| SPRT | Sequential Probability Ratio Test |
| Surveillance | Systematic collection of samples and data |

## 8. Appendices

### 8.1 Keyboard Shortcuts

| Function | Shortcut |
|----------|----------|
| Open Dashboard | Alt+D |
| Open Maps | Alt+M |
| Search | Ctrl+F |
| Help | F1 |
| Export Current View | Ctrl+E |
| Refresh Data | F5 |

### 8.2 Mobile App Features

| Feature | Description |
|---------|-------------|
| Offline Mode | Collect data without internet connection |
| GPS Integration | Automatically capture location data |
| Barcode Scanning | Quickly enter sample IDs |
| Photo Attachments | Document field conditions |
| Push Notifications | Receive alerts and updates |

### 8.3 Report Templates

| Template | Use Case |
|----------|----------|
| Situation Report | Daily status overview |
| Outbreak Summary | Detailed information on specific outbreak |
| Surveillance Report | Weekly monitoring activities and results |
| Performance Dashboard | Monitoring system effectiveness |
| Executive Briefing | High-level summary for leadership |