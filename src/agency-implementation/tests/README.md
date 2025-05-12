# Agency Implementation Integration Tests

This directory contains integration tests for the agency implementation foundation components. These tests verify that the foundation components work correctly with each other and with example implementations.

## Test Structure

The tests are organized as follows:

- **API Layer Tests**: Verify that the API framework components (controllers, routers, app factory) work together correctly.
- **Service Integration Tests**: Verify that core services (detection, prediction, notification) integrate properly.
- **Data Federation Tests**: Verify that the data federation system enables cross-agency data sharing.
- **Extension Mechanisms Tests**: Verify that extension points work correctly for customization.
- **Implementation Integration Tests**: Verify that the example implementations (CDC, EPA, FEMA) correctly implement and extend the foundation.

## Running the Tests

### Prerequisites

- Python 3.8+
- pytest

### Installation

```bash
pip install pytest pytest-mock
```

### Running All Tests

From the agency-implementation directory:

```bash
pytest tests/
```

### Running Specific Test Categories

```bash
# Run API integration tests
pytest tests/integration/test_api_integration.py

# Run service integration tests
pytest tests/integration/test_service_integration.py

# Run data federation tests
pytest tests/integration/test_data_federation.py

# Run extension mechanism tests
pytest tests/integration/test_extension_mechanisms.py

# Run implementation integration tests
pytest tests/integration/test_implementation_integration.py
```

## Test Fixtures

Common test fixtures are defined in `conftest.py`, including:

- `mock_api_client`: Mock API client for testing API integrations
- `sample_detection_data`: Sample data for testing detection services
- `mock_federation_gateway`: Mock federation gateway for testing data sharing
- `mock_extension_registry`: Mock extension registry for testing extension points

## Skipped Tests

Some tests may be skipped if the required modules are not available. For example, implementation-specific tests will be skipped if the corresponding implementation modules cannot be imported.

## Adding New Tests

When adding new tests, follow these guidelines:

1. Create test files in the appropriate directory (`integration/` for integration tests).
2. Use the standard unittest.TestCase class or pytest fixtures as needed.
3. Use descriptive test method names that explain what is being tested.
4. Include docstrings for test classes and methods to explain their purpose.
5. Use appropriate mocks and patches to isolate the components being tested.
6. Update this README.md file to document the new tests.

## Mocking Strategy

These integration tests use a combination of real components and mocks:

- When testing interactions between foundation components, use real instances when possible.
- When testing external dependencies (e.g., databases, APIs), use mocks.
- When testing interactions with implementation-specific components, use mocks if the components are not available.

## Test Coverage

The integration tests aim to cover:

1. **Component Interactions**: Verify that components work together as expected.
2. **Error Handling**: Verify that errors are properly propagated and handled.
3. **Configuration**: Verify that components can be configured properly.
4. **Extensibility**: Verify that components can be extended and customized.
5. **Federation**: Verify that data can be shared between agencies.