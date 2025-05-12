# Unified Notification System

A centralized system for aggregating and distributing alerts from CDC, EPA, and FEMA federal agencies using federation components.

## Overview

The Unified Notification System collects alerts from multiple federal agencies, prioritizes them based on severity and relevance, and distributes them to appropriate stakeholders via multiple channels (email, SMS, API webhooks).

## Features

- **Multi-Agency Alert Collection**: Collects alerts from CDC, EPA, FEMA, and other agencies
- **Alert Prioritization**: Prioritizes alerts based on severity, relevance, and other factors
- **Deduplication**: Prevents duplicate alerts from being sent
- **Multi-Channel Distribution**: Distributes alerts via email, SMS, webhooks, and more
- **Stakeholder Targeting**: Sends alerts only to relevant stakeholders based on subscriptions
- **Federation Support**: Connects to federation components to share alerts across systems
- **Extensible Architecture**: Easily add new alert sources and notification channels

## Components

- **Core System**: Central system for coordinating alert collection, prioritization, and distribution
- **Agency Adapters**: Adapters for connecting to different agency alert sources
- **Notification Channels**: Implementations for different notification methods (email, SMS, webhooks)
- **Federation Client**: Client for connecting to federation components
- **Models**: Data models for alerts, stakeholders, etc.

## Prerequisites

- Python 3.8 or higher
- AsyncIO support
- Network access to agency APIs

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/example/unified-notification-system.git
   cd unified-notification-system
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the system by editing `config/notification_config.json` with your API keys and settings.

## Usage

### Running the System

```bash
# Run with default configuration
python main.py

# Run with a specific configuration file
python main.py --config /path/to/config.json

# Run once and exit (useful for cron jobs)
python main.py --once

# Set log level
python main.py --log-level DEBUG
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t unified-notification-system .

# Run the container
docker run -v /path/to/config:/app/config unified-notification-system
```

## Configuration

The system is configured using a JSON configuration file. Here's an example:

```json
{
  "processing_interval_seconds": 300,
  "federation": {
    "base_url": "http://localhost:8000/api",
    "api_key": "YOUR_API_KEY_HERE"
  },
  "channels": {
    "email": {
      "type": "email",
      "enabled": true,
      "smtp_host": "smtp.example.com",
      "smtp_port": 587,
      "smtp_user": "user",
      "smtp_password": "password"
    },
    "sms": {
      "type": "sms",
      "enabled": true
    },
    "webhook": {
      "type": "webhook",
      "enabled": true
    }
  },
  "adapters": {
    "cdc": {
      "type": "cdc",
      "api_url": "https://api.cdc.gov/alerts",
      "api_key": "YOUR_CDC_API_KEY"
    },
    "epa": {
      "type": "epa",
      "api_url": "https://api.epa.gov/alerts",
      "api_key": "YOUR_EPA_API_KEY"
    },
    "fema": {
      "type": "fema",
      "api_url": "https://api.fema.gov/alerts",
      "api_key": "YOUR_FEMA_API_KEY"
    }
  }
}
```

## Extending the System

### Adding a New Agency Adapter

1. Create a new file in the `adapters` directory (e.g., `noaa_adapter.py`)
2. Implement the `AlertAdapter` interface
3. Register your adapter with the `@AlertAdapter.register_adapter("noaa")` decorator
4. Add configuration in the config file

### Adding a New Notification Channel

1. Create a new file in the `channels` directory (e.g., `slack_channel.py`)
2. Implement the `NotificationChannelExtensionPoint` interface
3. Add configuration in the config file

## Alert Prioritization

Alerts are prioritized based on the following factors:

1. **Severity Level**: Critical > High > Medium > Low > Informational
2. **Age**: Newer alerts get higher priority
3. **Affected Population**: Larger affected populations get higher priority
4. **Geographic Relevance**: Alerts affecting stakeholder regions get higher priority

## Federation Integration

The system can connect to a federation service to share alerts with other systems:

1. **Alert Collection**: Collects alerts from federation components
2. **Stakeholder Information**: Retrieves stakeholder details from federation
3. **Subscription Management**: Manages stakeholder alert subscriptions via federation

## API Endpoints

The system provides the following API endpoints:

- `GET /api/alerts`: Get active alerts
- `GET /api/alerts/history`: Get alert history
- `POST /api/alerts/acknowledge/{id}`: Acknowledge an alert
- `POST /api/alerts/close/{id}`: Close an alert
- `POST /api/subscriptions`: Manage stakeholder subscriptions

## Troubleshooting

- **Connection Issues**: Check API keys and network connectivity
- **Alert Distribution Failures**: Verify channel configurations and credentials
- **Missing Alerts**: Check adapter configurations and API status

## License

This project is licensed under the MIT License - see the LICENSE file for details.