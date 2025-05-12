# Contributing to the Agency Implementation Framework

Thank you for your interest in contributing to the Agency Implementation Framework! This document provides guidelines and instructions for contributing to the project.

## Ways to Contribute

There are several ways you can contribute to the Agency Implementation Framework:

1. **Code Contributions**: Implement new features, fix bugs, or improve existing functionality
2. **Documentation**: Enhance or correct documentation, add examples or tutorials
3. **Testing**: Write tests, report bugs, or validate fixes
4. **Use Cases**: Share agency-specific use cases and implementation examples
5. **Extensions**: Develop reusable extensions that can benefit multiple agencies

## Contribution Process

### 1. Find or Create an Issue

- Before starting work, check the [issue tracker](https://github.com/hms-gov/agency-implementation/issues) to see if your issue already exists
- If your issue isn't listed, create a new issue describing the problem or enhancement
- For significant changes, discuss the approach with the maintainers before implementation

### 2. Fork the Repository

- Fork the repository to your GitHub account
- Clone your fork locally:
  ```bash
  git clone https://github.com/your-username/agency-implementation.git
  cd agency-implementation
  ```

### 3. Create a Branch

- Create a branch for your work:
  ```bash
  git checkout -b feature/your-feature-name
  ```
- Use descriptive branch names (e.g., `feature/adaptive-sampling-enhancement`, `fix/api-authentication-issue`)

### 4. Make Changes

- Make your changes following the [coding standards](#coding-standards)
- Include tests for new functionality or bug fixes
- Update documentation to reflect your changes
- Keep your changes focused and related to the issue you're addressing

### 5. Test Your Changes

- Run the existing test suite to ensure you haven't broken anything:
  ```bash
  python -m pytest
  ```
- Add tests for your changes when applicable
- Verify your changes work as expected

### 6. Commit Your Changes

- Use clear, descriptive commit messages
- Reference the issue number in your commit message:
  ```
  Add adaptive sampling configuration options (#123)
  ```
- Follow the [commit message guidelines](#commit-message-guidelines)

### 7. Push and Create a Pull Request

- Push your changes to your fork:
  ```bash
  git push origin feature/your-feature-name
  ```
- Create a pull request from your branch to the main repository
- Provide a clear description of your changes in the pull request
- Link the pull request to the related issue

### 8. Respond to Feedback

- Address any feedback or requested changes from the code review
- Make additional commits to your branch as needed
- Keep the pull request updated

## Coding Standards

### Python Code

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use type hints where appropriate
- Write docstrings for all functions, classes, and modules
- Aim for 100% test coverage for new code

### JavaScript/TypeScript Code

- Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use TypeScript for new frontend components
- Ensure proper error handling
- Include JSDoc comments for functions and classes

### Rust Code

- Follow [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- Use the `rustfmt` tool to format code
- Run `cargo clippy` to catch common mistakes
- Write comprehensive documentation for public APIs

## Commit Message Guidelines

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or fewer
- Reference issues and pull requests after the first line
- Consider using a structured format:
  ```
  <type>(<scope>): <subject>
  
  <body>
  
  <footer>
  ```
- Common types: feat, fix, docs, style, refactor, test, chore

## Documentation Guidelines

- Keep documentation up-to-date with code changes
- Use Markdown for all documentation files
- Include examples for new features or configurations
- Follow the existing documentation structure
- Add diagrams where they help explain complex concepts
- Ensure links between documents work correctly

## License and Legal

By contributing to the Agency Implementation Framework, you agree that your contributions will be licensed under the project's [Apache License 2.0](LICENSE).

## Questions or Need Help?

If you have questions about contributing or need help with the process, please:
- Reach out in the #agency-implementation-framework Slack channel
- Contact the project maintainers
- Post on the [community forum](https://forums.hms-gov.org/agency-implementation)

Thank you for contributing to the Agency Implementation Framework!