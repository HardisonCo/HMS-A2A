# CI/CD Workflows

This directory contains GitHub Actions workflows for CI/CD operations in the Agency Implementation project.

## Available Workflows

### 1. Code Quality (`code-quality.yml`)

Performs code quality checks including:
- Python linting with flake8, black, isort, and mypy
- JavaScript linting with ESLint
- Rust formatting and linting with rustfmt and clippy

Runs on push to main/develop and on pull requests.

### 2. Tests (`tests.yml`)

Runs unit and integration tests:
- Python unit tests with multiple Python versions (3.8, 3.10)
- JavaScript unit tests
- Rust unit tests (when Rust code is present)
- Integration tests with PostgreSQL database

Runs on push to main/develop and on pull requests.

### 3. Build and Package (`build.yml`)

Builds and packages project components:
- Python packages
- NPM packages
- Rust packages
- Docker images

Runs on push to main/develop, pull requests, and when tags are pushed.
Packages are published to PyPI, npm, and crates.io when tagged releases are created.

### 4. Deployment (`deploy.yml`)

Deploys the foundation and implementation components to specified environments:
- Deploys foundation components first
- Then deploys selected implementation(s)
- Runs post-deployment smoke tests
- Sends notifications on completion

Triggered manually via workflow_dispatch with parameters for environment, implementation, and version.

### 5. Documentation (`docs.yml`)

Builds and deploys documentation:
- Main documentation with MkDocs
- API reference with Sphinx
- Publishes to GitHub Pages

Runs on push to main/develop and pull requests that modify documentation files.

### 6. Security Scanning (`security.yml`)

Performs security scans:
- Dependency review for pull requests
- Python security scanning with Bandit and Safety
- JavaScript security scanning with npm audit
- Rust security scanning with cargo-audit
- Docker image scanning with Trivy

Runs on push to main/develop, pull requests, and weekly.

### 7. Implementation Validation (`implementation-validation.yml`)

Validates implementation examples:
- Discovers and validates implementation structure
- Runs implementation-specific tests
- Tests integration with foundation components
- Tests example deployment

Runs on push to main/develop and pull requests that modify implementation or foundation files.

## Configuration

### Secrets Required

- `PYPI_API_TOKEN`: For publishing Python packages to PyPI
- `NPM_TOKEN`: For publishing JavaScript packages to npm
- `CRATES_IO_TOKEN`: For publishing Rust packages to crates.io
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`: For AWS deployments
- `API_BASE_URL`: Base URL for API smoke tests
- `SLACK_WEBHOOK_URL`: For sending deployment notifications

### Branch Protection

It's recommended to set up branch protection rules for the `main` and `develop` branches:

1. Require pull request reviews before merging
2. Require status checks to pass before merging:
   - Required checks: 
     - unit-tests-python
     - integration-tests
     - lint-python
     - dependency-review
     - validate-implementations
3. Require signed commits
4. Include administrators in branch protection

## Usage

### Automated Workflows

Most workflows run automatically on push events and pull requests.

### Manual Workflows

#### Deployment

To manually trigger a deployment:

1. Go to Actions > Deployment > Run workflow
2. Select:
   - Environment (staging or production)
   - Implementation (all, cdc, epa, or fema)
   - Version (tag or branch name)
3. Click "Run workflow"

#### Documentation

To manually rebuild and deploy documentation:

1. Go to Actions > Documentation > Run workflow
2. Use the default branch or select a specific branch
3. Click "Run workflow"

#### Implementation Validation

To manually validate specific implementations:

1. Go to Actions > Implementation Validation > Run workflow
2. Optionally enter a specific implementation name (e.g., "cdc")
3. Click "Run workflow"

## Local Development

You can run these workflows locally using [act](https://github.com/nektos/act):

```bash
# Run tests workflow
act -j unit-tests-python -W .github/workflows/tests.yml

# Run code quality checks
act -j lint-python -W .github/workflows/code-quality.yml
```

## Customizing Workflows

The workflows are designed to be modular and extensible. To customize:

1. Fork the repository
2. Modify workflow files as needed
3. Add/remove jobs or steps based on your requirements
4. Update action versions as new versions become available
5. Add additional secrets or variables in repository settings if required

## Troubleshooting

Common issues:

1. **Missing secrets**: Ensure all required secrets are configured in repository settings
2. **Failed tests**: Check test logs for specific failures
3. **Deployment issues**: Verify credentials and environment configurations
4. **Build failures**: Check compatibility between dependencies

For more detailed troubleshooting, review the workflow run logs in the Actions tab.