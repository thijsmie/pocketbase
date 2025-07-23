# Contributing

Thank you for considering contributing to pocketbase-async! This project follows standard open source contribution practices.

## Quick Links

- **Bug Reports**: [GitHub Issues](https://github.com/thijsmie/pocketbase-async/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/thijsmie/pocketbase-async/discussions) 
- **Security Issues**: See [Security Policy](#security-policy) below

## Code of Conduct

--8<-- "CODE_OF_CONDUCT.md"

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/pocketbase-async.git
   cd pocketbase-async
   ```

2. **Install dependencies**
   ```bash
   # Using poetry (recommended)
   poetry install
   
   # Or using pip
   pip install -e ".[dev]"
   ```

3. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pre-commit install
   ```

## Development Workflow

### Running Tests and Checks

Instead of running individual tools like `ruff`, `mypy`, and `pytest` manually, use the provided `ci.bash` script that runs all quality checks:

```bash
# Run all checks (formatting, linting, type checking, tests, coverage)
./ci.bash
```

This script:
- Formats code with `ruff format`
- Checks and auto-fixes linting issues with `ruff check --fix`
- Runs type checking with `mypy`
- Runs tests with `pytest` and generates coverage reports
- Shows coverage report for uncovered lines

### Individual Commands

If you need to run tools individually:

```bash
# Format code
ruff format src tests examples

# Check linting
ruff check src tests examples

# Fix auto-fixable linting issues
ruff check --fix src tests examples

# Type checking
mypy src

# Run tests
pytest

# Run tests with coverage
pytest --cov=pocketbase

# Generate coverage report
coverage report -m --skip-covered --skip-empty
```

### Testing with PocketBase

Many tests require a running PocketBase instance. Set up a test instance:

```bash
# Download and run PocketBase (adjust URL for your OS)
wget https://github.com/pocketbase/pocketbase/releases/download/v0.20.0/pocketbase_0.20.0_linux_amd64.zip
unzip pocketbase_0.20.0_linux_amd64.zip
./pocketbase serve --http=127.0.0.1:8123

# In another terminal, create a superuser
./pocketbase superuser create test@example.com test
```

## Contribution Guidelines

### Reporting Bugs

Before creating a bug report:
- Check existing issues to avoid duplicates
- Ensure you're using the latest version
- Include steps to reproduce, expected behavior, and environment details

### Requesting Features

Before requesting a feature:
- Check if it already exists in the latest release
- Search closed issues and discussions
- Consider starting a discussion before opening an issue
- Provide clear use cases and examples

### Contributing Code

Code contributions are welcome! Please ensure:

- There's an existing issue or discussion about the change
- All tests pass (`./ci.bash` runs successfully)
- New features include tests and documentation
- Commit messages are clear and descriptive

#### Code Style

- Follow PEP 8 (enforced by `ruff`)
- Use type hints for all public APIs
- Write docstrings for all public functions and classes
- Keep line length at 120 characters

#### Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Run `./ci.bash` to ensure all checks pass
4. Update documentation if needed
5. Create a pull request with a clear description

## Documentation

Documentation improvements are especially welcome! To work on docs:

```bash
# Install docs dependencies
pip install mkdocs mkdocs-material mkdocstrings[python] mkdocs-autorefs

# Serve docs locally
mkdocs serve

# Build docs
mkdocs build
```

The documentation uses:
- **MkDocs** with Material theme
- **mkdocstrings** for API reference from docstrings
- **Markdown** with extensions for enhanced formatting

## Security Policy

--8<-- "SECURITY.md"

## Legal

By contributing to this project, you agree that:
- You have authored 100% of the contributed content
- You have the necessary rights to the content
- Your contributions may be provided under the project's MIT license

## Getting Help

- **General Questions**: [GitHub Discussions](https://github.com/thijsmie/pocketbase-async/discussions)
- **Bug Reports**: [GitHub Issues](https://github.com/thijsmie/pocketbase-async/issues)
- **Direct Contact**: For sensitive issues, email opensource [at] tmiedema.com
   ```

2. **Install dependencies**:
   ```bash
   # Using Poetry (recommended)
   poetry install
   
   # Or using pip
   pip install -e ".[dev]"
   ```

3. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   poetry run pre-commit install
   ```

## Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=pocketbase

# Run specific test file
poetry run pytest tests/test_record.py

# Run tests with verbose output
poetry run pytest -v
```

## Code Style

We use several tools to maintain code quality:

- **Ruff** for linting and formatting
- **MyPy** for type checking

```bash
# Run linting
poetry run ruff check .

# Auto-fix issues
poetry run ruff check --fix .

# Type checking
poetry run mypy src/pocketbase
```

## Documentation

We use MkDocs with Material theme for documentation:

```bash
# Install docs dependencies
pip install mkdocs mkdocs-material mkdocstrings[python] mkdocs-autorefs

# Serve docs locally
mkdocs serve

# Build docs
mkdocs build
```

## Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Add tests** for any new functionality

4. **Update documentation** if needed

5. **Run the test suite**:
   ```bash
   poetry run pytest
   poetry run ruff check .
   poetry run mypy src/pocketbase
   ```

## Submitting Changes

1. **Commit your changes**:
   ```bash
   git commit -m "feat: add awesome new feature"
   ```

   We follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test additions/changes
   - `refactor:` for code refactoring

2. **Push to your fork**:
   ```bash
   git push origin feat/your-feature-name
   ```

3. **Create a Pull Request** on GitHub

## What to Contribute

### Bug Reports
- Check existing issues first
- Provide clear reproduction steps
- Include Python version and PocketBase version
- Include error messages and stack traces

### Feature Requests
- Check if it's already requested
- Describe the use case clearly
- Consider starting with a discussion

### Code Contributions
- Bug fixes are always welcome
- New features should be discussed first
- Documentation improvements
- Test coverage improvements
- Performance optimizations

## Code Guidelines

### Python Code Style
- Follow PEP 8
- Use type hints for all public APIs
- Write docstrings for all public functions/classes
- Keep functions focused and small
- Use descriptive variable names

### Testing
- Write tests for all new functionality
- Aim for high test coverage
- Use descriptive test names
- Test both success and error cases

### Documentation
- Update docstrings for any API changes
- Add examples for new features
- Update the changelog for significant changes

## Project Structure

```
pocketbase-async/
├── src/pocketbase/          # Main package
│   ├── client.py           # Main PocketBase client
│   ├── models/             # Data models and DTOs
│   ├── services/           # Service classes
│   └── utils/              # Utility functions
├── tests/                  # Test suite
├── docs/                   # Documentation
├── examples/               # Usage examples
└── pyproject.toml          # Project configuration
```

## Release Process

Releases are handled by maintainers:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a git tag
4. GitHub Actions automatically publishes to PyPI

## Getting Help

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discord**: Join our community Discord (link in README)

## Code of Conduct

Please read and follow our [Code of Conduct](https://github.com/thijsmie/pocketbase-async/blob/main/CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
