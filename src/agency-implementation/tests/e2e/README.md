# End-to-End Integration Tests

This directory contains end-to-end integration tests for the agency implementation system. These tests verify the correct operation of the entire system, including agency implementations, federation components, unified dashboard, and notification system.

## Test Structure

The tests are organized into several key files:

- `conftest.py` - Contains test fixtures and setup for all E2E tests
- `test_system_workflow.py` - Tests complete system workflows across all components
- `test_agency_implementations.py` - Tests agency-specific implementations (CDC, EPA, FEMA)
- `test_federation_system.py` - Tests the federation system's functionality
- `test_notification_system.py` - Tests the unified notification system
- `test_unified_dashboard.py` - Tests the dashboard integration with other components

## Test Scenarios

The tests cover the following key scenarios:

1. **Complete System Workflow**
   - Outbreak detection to notification delivery
   - Cross-agency coordination
   - Data federation between agencies
   - Dashboard updates with integrated data

2. **Agency-Specific Functionality**
   - CDC disease surveillance and outbreak detection
   - EPA environmental assessment and monitoring
   - FEMA emergency response planning and resource allocation

3. **Federation System**
   - Data sharing between agencies
   - Governance rule enforcement
   - Synchronization of shared data
   - Auditing of data access and modifications

4. **Notification System**
   - Multi-channel notifications (email, SMS, webhook, console)
   - Agency-specific notification adapters
   - Notification status tracking
   - Recipient targeting and delivery confirmation

5. **Unified Dashboard**
   - Data integration from multiple agencies
   - Visualization components (maps, charts, timelines)
   - Integration with federation and notification systems
   - User customization and preferences

## Running the Tests

To run all E2E tests:

```bash
pytest tests/e2e/ -v
```

To run a specific test file:

```bash
pytest tests/e2e/test_system_workflow.py -v
```

To run a specific test function:

```bash
pytest tests/e2e/test_system_workflow.py::test_complete_workflow -v
```

## Test Environment

The tests are designed to either:

1. Run against a fully deployed system by specifying the base URL:

```bash
API_BASE_URL=https://agency-implementation.example.com pytest tests/e2e/ -v
```

2. Run in mock mode (default) which simulates expected API responses for CI/CD purposes

## Adding New Tests

When adding new E2E tests:

1. Focus on cross-component interactions and full system workflows
2. Ensure tests can run both against real systems and in mock mode
3. Use the existing fixtures provided in `conftest.py`
4. Mock external dependencies appropriately
5. Follow the pattern of testing both success and failure scenarios