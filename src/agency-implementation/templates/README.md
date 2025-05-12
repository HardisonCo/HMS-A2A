# Agency Implementation Templates

This directory contains templates for implementing new agencies within the HMS system. These templates provide a standardized structure and example implementations that can be customized for specific agency needs.

## Directory Structure

```
templates/
├── config/              # Configuration templates and examples
├── docs/                # Documentation templates
│   ├── customization/   # Guides for customizing templates
│   ├── integration/     # Integration documentation
│   └── setup/           # Setup instructions
├── src/                 # Source code templates
│   ├── api/             # API endpoint templates
│   ├── integrations/    # Integration templates for other HMS components
│   ├── models/          # Data model templates
│   └── services/        # Service layer templates
└── tests/               # Test templates and examples
```

## Getting Started

1. Copy the entire templates directory to create a new agency implementation:
   ```bash
   cp -r templates/ [AGENCY-CODE]
   ```

2. Follow the setup instructions in `docs/setup/GETTING_STARTED.md`

3. Customize the implementation according to your agency's specific requirements using the guides in `docs/customization/`

4. Implement the required integrations following the documentation in `docs/integration/`

## Agency Implementation Requirements

Each agency implementation must include:

1. Core data models specific to the agency
2. Service implementations for agency-specific business logic
3. API endpoints that conform to the HMS API standards
4. Integration points with other HMS components
5. Comprehensive test coverage
6. Complete documentation

## Support

For questions or assistance with agency implementations, refer to the main HMS documentation or contact the HMS development team.