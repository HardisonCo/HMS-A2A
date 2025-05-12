# Crohn's Disease Treatment System: Testing Framework

This directory contains the testing framework for the Crohn's Disease Treatment System. The testing framework is designed to validate the functionality of the system and ensure that all components work together correctly.

## Test Categories

The testing framework is organized into several categories:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test interactions between components
3. **End-to-End Tests**: Test complete workflows through all components
4. **Protocol Tests**: Test communication protocols between components
5. **Agent Conversation Tests**: Test agent conversation flows and interactions
6. **FFI Tests**: Test Foreign Function Interface integrations
7. **Monitoring Tests**: Test monitoring and health check systems

## Running Tests

### Basic Test Execution

To run all tests:

```bash
cd crohns-treatment-system
pytest
```

To run specific test categories:

```bash
# Run unit tests
pytest tests/test_*.py -k "not integration and not end_to_end"

# Run integration tests
pytest tests/test_integration.py

# Run with coverage report
pytest --cov=src tests/
```

### Running HMS Integration Tests

The HMS integration tests can be run using the dedicated test runners:

```bash
# Run all integration tests
python tests/run_integration_tests.py

# Run only doc_integration tests
python tests/run_integration_tests.py --modules doc_integration

# Run with verbose output
python tests/run_integration_tests.py --verbose

# Run a specific integration test module directly
python tests/integration/doc_integration/run_doc_integration_tests.py
```

### Running Comprehensive Tests

For comprehensive testing including FFI, monitoring, and agent conversations:

```bash
# Run all comprehensive tests
python tests/run_comprehensive_tests.py

# Run specific component tests
python tests/run_comprehensive_tests.py --components doc_integration genetic_engine

# Run specific protocol tests
python tests/run_comprehensive_tests.py --protocols agent_protocol message_bus

# Include FFI tests
python tests/run_comprehensive_tests.py --ffi

# Include monitoring tests
python tests/run_comprehensive_tests.py --monitoring

# Include agent conversation tests
python tests/run_comprehensive_tests.py --agent-conversations

# Run tests in parallel
python tests/run_comprehensive_tests.py --parallel

# Run with verbose output
python tests/run_comprehensive_tests.py --verbose

# Specify report file location
python tests/run_comprehensive_tests.py --report-file "/path/to/report.json"

# Run everything with all options
python tests/run_comprehensive_tests.py --components all --protocols all --ffi --monitoring --agent-conversations --parallel --verbose
```

## Test Structure

The testing framework is organized into the following directory structure:

```
tests/
├── __init__.py
├── conftest.py                    # Common test fixtures and configuration
├── run_comprehensive_tests.py     # Comprehensive test runner
├── run_integration_tests.py       # Integration test runner
├── data/                          # Test data files
│   ├── sample_trial_data.json
│   └── doc_integration_test_data.json
├── agents/                        # Agent conversation tests
│   └── test_agent_conversations.py
├── protocols/                     # Protocol tests
│   ├── agent_protocol/
│   │   └── test_agent_protocol.py
│   ├── component_protocol/
│   └── message_bus/
├── integration/                   # Integration tests
│   ├── doc_integration/
│   │   ├── run_doc_integration_tests.py
│   │   ├── test_doc_integration_service.py
│   │   ├── test_integration_coordinator.py
│   │   └── test_doc_integration_controller.py
│   ├── ffi_bridge/
│   │   └── test_ffi_bridge.py
│   ├── monitoring/
│   │   └── test_monitoring_integration.py
│   ├── test_codex_rs_integration.py
│   ├── test_ehr_sync.py
│   └── test_research_to_treatment.py
├── test_a2a_integration.py
├── test_abstraction_analysis.py
├── test_genetic_engine.py
└── test_integration.py
```

## Key Test Components

### HMS Integration Tests

These tests validate the functionality of the integration between the Crohn's Treatment System, HMS-DOC, and HMS-MFE components. They cover:

1. **DocIntegrationService**: Core service for interacting with HMS-DOC and HMS-MFE
2. **IntegrationCoordinator**: Orchestration layer for scheduling and managing integration tasks
3. **API Controller**: REST API endpoints for client integration

### FFI Bridge Tests

Tests for Foreign Function Interface integration with Rust components:

1. **Genetic Engine**: Tests for the genetic algorithm engine
2. **Monitoring System**: Tests for the monitoring system
3. **Self-Healing**: Tests for the self-healing system

### Protocol Tests

Tests for the communication protocols between components:

1. **Agent Protocol**: Tests for agent-to-agent communication
2. **Component Protocol**: Tests for component-to-component communication
3. **Message Bus**: Tests for the message bus protocol

### Agent Conversation Tests

Tests for agent conversations and interactions:

1. **Conversation Structure**: Tests that conversation logs have required fields
2. **Conversation Flow**: Tests that conversation flows are valid
3. **Intent Analysis**: Tests that agent intents are valid
4. **Conversation Analysis**: Tests for conversation analysis functionality

### Monitoring Tests

Tests for the monitoring and health check systems:

1. **Monitor Log Structure**: Tests that monitor log entries have expected structure
2. **Component Status**: Tests that component statuses are valid
3. **Health Analysis**: Tests component health analysis
4. **Alert Triggering**: Tests alert triggering mechanism
5. **Health Checks**: Tests running health checks

## Test Environments

The comprehensive test runner sets up special environments for specific test types:

### FFI Test Environment

A dedicated environment for FFI component testing:

1. Creates temporary directories for FFI components
2. Creates mock executables for testing FFI integration
3. Sets environment variables for test scripts

### Monitoring Test Environment

A dedicated environment for monitoring system testing:

1. Creates a mock monitoring process
2. Generates synthetic monitoring logs
3. Sets environment variables for test scripts

### Agent Conversation Test Environment

A dedicated environment for agent conversation testing:

1. Creates mock conversation logs for testing
2. Sets environment variables for test scripts

## Fixtures

The testing framework provides several fixtures that can be used in tests:

- `event_bus`: A mock event bus for testing event-driven communication
- `genetic_engine_integration`: A mock genetic engine integration for testing
- `clinical_trial_agent`: A mock clinical trial agent for testing
- `fhir_client`: A mock FHIR client for testing EHR integration
- `trial_data_transformer`: A mock trial data transformer for testing
- `sample_patient_data`: Sample patient data for testing
- `sample_treatment_plan`: Sample treatment plan for testing
- `sample_trial_protocol`: Sample trial protocol for testing
- `sample_genetic_data`: Sample genetic sequence data for testing
- `test_data_dir`: A temporary directory with test data files

## Test Reports

The comprehensive test runner generates detailed test reports:

1. **JSON Reports**: Structured reports with detailed test results
2. **Summary Output**: Console output with test summary
3. **Component-Specific Results**: Results broken down by component
4. **Failure Details**: Detailed information about test failures
5. **Performance Metrics**: Test duration and execution statistics

## Mock Implementation

Since some components may not be fully implemented yet, the testing framework provides mock implementations that can be used to test other components. These mocks are defined in `conftest.py` and automatically used when the actual implementations are not available.

## Adding New Tests

When adding new tests, follow these guidelines:

1. Use the appropriate test category (unit, integration, protocol, agent, etc.)
2. Use fixtures from `conftest.py` where possible
3. Use descriptive test names that indicate what is being tested
4. Add proper assertions to verify expected behavior
5. Skip tests that require not-yet-implemented components using `@pytest.mark.skipif`

Example:

```python
@pytest.mark.skipif(not HAS_COMPONENT, reason="Component not available")
def test_my_feature():
    # Test implementation
    result = my_function()
    assert result is not None
    assert "expected_key" in result
```

## Test Data

Test data is provided through fixtures in `conftest.py` and files in the `tests/data/` directory.

For the HMS integration tests, test data is stored in:

- `sample_trial_data.json`: Sample clinical trial data
- `doc_integration_test_data.json`: Test data for HMS-DOC and HMS-MFE integration

## Notes for Testing FFI Components

Testing components that use FFI (Foreign Function Interface) requires special consideration:

1. Use `@pytest.mark.skipif` to skip tests that require the actual Rust library
2. Use mocks to simulate the behavior of the FFI components
3. Test the interface contract rather than the actual implementation
4. Use integration tests to verify that the FFI components work together correctly

The comprehensive test runner provides a dedicated FFI test environment that creates mock executables for testing FFI integration.

## Continuous Integration

The tests run automatically in CI for every pull request. Make sure all tests pass before merging your changes.

## Integration Test Approach

The integration tests use a combination of real and mock components:

1. **Test Environment**: Creates temporary directories for HMS-DOC and HMS-MFE components
2. **Mock Components**: Simulates HMS-DOC and HMS-MFE functionality for testing
3. **Patching**: Uses `unittest.mock` to patch external calls for isolated testing
4. **API Testing**: Tests REST API endpoints using Flask's test client

This approach allows testing the integration logic without requiring the actual HMS components to be fully implemented or available.