# Agency Implementation Utilities

This directory contains utility modules that provide common functionality across all agency implementations.

## Available Utilities

### Configuration Management (`config.js`)
- Load configurations from files or environment variables
- Access configurations with dot notation support
- Validate configurations against schemas

### Logging (`logger.js`)
- Standardized logging with multiple log levels
- Timestamps and metadata support
- Configurable output targets

### Error Handling (`error-handler.js`) 
- Custom error types for common scenarios
- Standardized error format
- Express error handler middleware

### Date and Time Operations (`date-time.js`)
- Date formatting and parsing
- Date calculations and comparisons
- Fiscal year and quarter calculations

### Geographic Calculations (`geo.js`)
- Distance calculations using Haversine formula
- Geocoding helpers
- State/region identification
- FIPS code utilities

### Cryptography (`crypto.js`)
- Secure random string generation
- Hashing and HMAC functions
- Encryption/decryption utilities
- Password hashing and verification
- Token generation

### Data Validation (`validation.js`)
- Common format validations (email, phone, ZIP)
- Agency-specific validations (EIN, DUNS, CAGE, UEI)
- Date and URL validation

### HTTP Client (`http-client.js`)
- Standardized HTTP request handling
- Consistent error handling
- Request/response logging
- Authentication helpers

### File Utilities (`file-utils.js`)
- Asynchronous file operations
- Directory management
- File listing and filtering
- File hashing and verification
- CSV parsing

## Usage

You can import specific utilities:

```javascript
const { ConfigManager } = require('./utilities');

const config = new ConfigManager('./config.json');
config.loadFromFile();
const apiKey = config.get('api.key');
```

Or import all utilities:

```javascript
const Utils = require('./utilities');

const logger = new Utils.Logger({ level: 'info' });
logger.info('Application started');

const isValid = Utils.ValidationUtils.isValidEIN('12-3456789');
```

## Additional Features

These utilities provide a foundation for agency implementations and include:

1. Standardized error handling for consistent user experiences
2. Secure cryptographic functions for handling sensitive data
3. Government-specific validation rules (EIN, DUNS, CAGE, UEI)
4. Fiscal calendar support for government reporting periods
5. Geospatial utilities for location-based services
6. Configuration management with schema validation
7. Structured logging for auditing and debugging