# APHIS Bird Flu HMS-MFE Integration Tests

This directory contains integration tests for the APHIS Bird Flu HMS-MFE components. These tests validate that the components correctly integrate with:

1. The APHIS Bird Flu API
2. The Federation Hub for cross-agency data sharing
3. The HMS-MFE framework

## Test Structure

The tests are organized by component and functionality:

- **Dashboard View Tests** - Test the surveillance dashboard functionality, API integration, federation capabilities, and filtering
- **Genetic Analysis Tests** - Test sequence input, analysis, and visualization of genetic sequence data
- **Transmission Network Tests** - Test network visualization, parameter controls, and transmission pattern analysis
- **Federation Integration Tests** - Test cross-agency data sharing and agency selection
- **HMS-MFE Integration Tests** - Test navigation, styling, and overall HMS-MFE framework integration

## Running Tests

### Prerequisites

- Node.js 16+
- npm
- Playwright browsers installed (`npx playwright install`)

For Docker mode:
- Docker
- Docker Compose

### Using the run-tests.sh script

We provide a convenient script to run tests in either local or CI mode:

```bash
# Run all tests locally
./run-tests.sh

# Run with browser UI visible
./run-tests.sh --headed

# Run just dashboard tests
./run-tests.sh --component dashboard

# Run in CI mode with Docker
./run-tests.sh --ci

# Get help
./run-tests.sh --help
```

### Manual Test Execution

You can also run tests directly using npm scripts:

```bash
# Install dependencies
cd tests
npm install

# Run all tests
npm test

# Run specific test groups
npm run test:dashboard
npm run test:genetic
npm run test:transmission
npm run test:federation

# Run tests with UI
npm run test:ui

# Run tests with browser visible
npm run test:headful

# Show test report
npm run test:report
```

## CI/CD Integration

These tests are automatically run in the CI pipeline using GitHub Actions. The workflow is defined in `.github/workflows/integration-tests.yml`.

The CI workflow:

1. Builds the HMS-MFE with APHIS components
2. Starts the mock API and Federation Hub services
3. Runs all integration tests
4. Archives test reports as artifacts

## Test Configuration

Tests can be configured using environment variables:

- `HMS_MFE_URL` - URL of the HMS-MFE application (default: http://localhost:3000)
- `API_URL` - URL of the APHIS Bird Flu API (default: http://localhost:8000)
- `FEDERATION_URL` - URL of the Federation Hub (default: http://localhost:9000)

## Debugging Failed Tests

When tests fail, Playwright creates snapshots of the failed test state:

1. Screenshots are captured at the point of failure
2. Traces record the test execution for playback
3. Browser console logs are recorded

To view these artifacts:

```bash
npm run test:report
```

This opens an HTML report where you can:
- See error messages and stack traces
- View screenshots at the point of failure
- Replay the test execution step by step
- Review network requests and responses

## Mock Services

For testing purposes, mock implementations of the API and Federation Hub are provided:

- **Mock API** - Implements the APHIS Bird Flu API endpoints with realistic sample data
- **Federation Hub** - Simulates the cross-agency federation capabilities

These services are automatically started when running tests, both in local and Docker modes.

## Writing New Tests

When adding new components or functionality to the HMS-MFE, please add corresponding integration tests:

1. Add new test cases in the appropriate test file sections
2. Follow the existing patterns for page object interactions
3. Add both happy path tests and error cases
4. Ensure tests validate both UI state and API interactions
5. Add new mock data as needed in the `mock-data` directory

## Federation Testing

Federation tests verify that the APHIS Bird Flu components can share data with other agencies:

- CDC (Centers for Disease Control)
- EPA (Environmental Protection Agency)
- FEMA (Federal Emergency Management Agency)

The tests validate:
- Agency discovery
- Data aggregation
- Filtering and visualization of federated data
- Cross-agency outbreak correlation

## License

Same as the main project license.