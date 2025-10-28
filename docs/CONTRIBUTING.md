# Contributing to GovChat-NL

Thank you for contributing to GovChat-NL! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Development Setup](#development-setup)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [CI/CD Pipeline](#cicd-pipeline)

## Development Setup

### Prerequisites

- Python 3.11 or 3.12
- Node.js 22
- Docker and Docker Compose
- Git

### Local Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/Schravenralph/GovChat-NL.git
cd GovChat-NL
```

2. Install Python dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Install Node.js dependencies:
```bash
npm install
```

4. Copy environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start development services:
```bash
docker-compose up -d
npm run dev
```

## Pre-commit Hooks

We use pre-commit hooks to ensure code quality and consistency before commits are made.

### Installation

1. Install pre-commit:
```bash
pip install pre-commit
```

2. Install the git hook scripts:
```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

3. (Optional) Run against all files:
```bash
pre-commit run --all-files
```

### What Pre-commit Checks

The pre-commit hooks will automatically:

- **Format Python code** with Black
- **Lint Python code** with Ruff
- **Sort imports** with isort
- **Format frontend code** (JS/TS/Svelte) with Prettier
- **Lint frontend code** with ESLint
- **Check for security issues** with Bandit
- **Validate YAML/JSON** files
- **Check for large files** (>1MB)
- **Detect private keys** and secrets
- **Validate commit messages** (Conventional Commits format)

### Skipping Hooks (Not Recommended)

If you need to skip hooks temporarily:
```bash
git commit --no-verify -m "your message"
```

**Warning**: This should only be used in exceptional circumstances. CI will still run all checks.

## Coding Standards

### Python Code

- **Style**: Follow [PEP 8](https://pep8.org/)
- **Formatter**: Black with default settings
- **Linter**: Ruff with our configuration
- **Import sorting**: isort with Black profile
- **Docstrings**: Google style docstrings for all public functions/classes
- **Type hints**: Use type hints for function signatures

Example:
```python
def process_document(document_id: str, options: dict[str, Any]) -> ProcessedDocument:
    """Process a policy document with the given options.

    Args:
        document_id: The unique identifier of the document
        options: Processing options including language, format, etc.

    Returns:
        A ProcessedDocument object with extracted metadata and content.

    Raises:
        DocumentNotFoundError: If the document doesn't exist
        ProcessingError: If document processing fails
    """
    pass
```

### TypeScript/JavaScript Code

- **Style**: Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- **Formatter**: Prettier with project configuration
- **Linter**: ESLint with TypeScript and Svelte plugins
- **Type safety**: Use TypeScript strict mode

### Svelte Components

- **Props**: Define explicit prop types
- **Reactivity**: Use `$:` for reactive statements
- **Accessibility**: Include ARIA labels and keyboard navigation
- **i18n**: Use translation keys for all user-facing text

Example:
```svelte
<script lang="ts">
  import { _ } from 'svelte-i18n';

  export let documentId: string;
  export let onClose: () => void;

  $: isValid = documentId && documentId.length > 0;
</script>

<div role="dialog" aria-label={$_('document.viewer.title')}>
  <!-- Component content -->
</div>
```

## Testing

### Running Tests

**Backend unit tests**:
```bash
pytest backend/tests/unit/ -v
```

**Backend integration tests**:
```bash
pytest backend/tests/integration/ -v
```

**Frontend unit tests**:
```bash
npm run test:frontend
```

**E2E tests**:
```bash
npm run cy:open  # Interactive mode
npm run cy:run   # Headless mode
```

### Test Coverage

- **Minimum coverage**: 80% for new code
- **Critical paths**: 100% coverage required
- **Generate coverage report**:
```bash
pytest --cov=backend --cov-report=html
```

### Writing Tests

**Unit test example** (Python):
```python
import pytest
from backend.services.search_service import SearchService

@pytest.mark.asyncio
async def test_search_documents_returns_results():
    """Test that search returns expected results."""
    service = SearchService()
    results = await service.search("policy", filters={"municipality": "Amsterdam"})

    assert len(results) > 0
    assert all(r.municipality == "Amsterdam" for r in results)
```

**Integration test example** (Python):
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_search_api_endpoint(client: AsyncClient):
    """Test search API endpoint with authentication."""
    response = await client.get(
        "/api/v1/policy/search",
        params={"q": "subsidie", "municipality": "Utrecht"},
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == 200
    assert "results" in response.json()
```

## Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependency updates
- **perf**: Performance improvements

### Examples

```
feat(policy-scanner): add Gemeenteblad scraper plugin

Implement scraper for Gemeentebladen.nl with:
- Rate limiting (10 requests/minute)
- Retry logic with exponential backoff
- Duplicate detection using SHA-256 hashes

Closes #123
```

```
fix(search): resolve pagination bug on last page

The search API was returning empty results on the last page
when the total count was exactly divisible by page size.

Fixes #456
```

```
docs(contributing): add pre-commit hook setup instructions

Add detailed instructions for:
- Installing pre-commit
- Configuring hooks
- Running manual checks
```

### Commit Message Rules

- Use imperative mood ("add" not "added")
- First line ≤ 72 characters
- Body wraps at 72 characters
- Reference issues/PRs in footer
- Breaking changes must include `BREAKING CHANGE:` in footer

## Pull Request Process

### Before Creating a PR

1. **Create a feature branch**:
```bash
git checkout -b feature/policy-scanner-gemeenteblad
```

2. **Make your changes** following coding standards

3. **Write tests** for new functionality

4. **Run all checks locally**:
```bash
# Format code
npm run format
npm run format:backend

# Run linters
npm run lint

# Run tests
pytest backend/tests/
npm run test:frontend

# Run pre-commit
pre-commit run --all-files
```

5. **Commit with conventional commits**

6. **Push to your branch**:
```bash
git push origin feature/policy-scanner-gemeenteblad
```

### Creating the PR

1. Go to GitHub and create a Pull Request
2. Fill out the PR template completely
3. Link related issues using keywords (Closes #123, Fixes #456)
4. Request reviews from relevant team members
5. Ensure all CI checks pass

### PR Title Format

PR titles must follow conventional commits format:

```
feat(policy-scanner): add Gemeenteblad scraper plugin
fix(search): resolve pagination bug
docs(api): update search endpoint documentation
```

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran and their results.

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Related Issues
Closes #123
Relates to #456
```

### Code Review Process

1. **Automated checks** must pass:
   - Linting and formatting
   - Unit tests (>80% coverage)
   - Integration tests
   - Security scans
   - Docker build

2. **Human review** requirements:
   - At least 1 approval from a team member
   - No unresolved conversations
   - All feedback addressed

3. **Merge strategy**:
   - Use "Squash and merge" for feature branches
   - Use "Rebase and merge" for hotfixes
   - Delete branch after merge

## CI/CD Pipeline

### Automated Checks

Our CI/CD pipeline runs on every push and PR:

1. **Lint and Format Check**
   - Black formatting (Python)
   - Ruff linting (Python)
   - Prettier formatting (Frontend)
   - ESLint (Frontend)

2. **Unit Tests**
   - Python 3.11 and 3.12
   - Coverage >80% required
   - Reports uploaded to Codecov

3. **Integration Tests**
   - PostgreSQL service
   - Meilisearch service
   - Full API testing

4. **Contract Tests**
   - OpenAPI spec validation
   - API contract verification

5. **Security Scans**
   - Trivy vulnerability scanner
   - TruffleHog secret detection
   - Bandit security checks

6. **Docker Build**
   - Multi-stage build validation
   - Layer caching optimization

### Pipeline Configuration

See `.github/workflows/policy-scanner-ci.yaml` for full configuration.

### Branch Protection Rules

The `main` branch is protected with:
- Require PR before merging
- Require 1+ approvals
- Require status checks to pass
- Require branches to be up to date
- Require conversation resolution

## Getting Help

- **Documentation**: Check `docs/` directory
- **Architecture**: See `policy-scanner-architecture.md`
- **API Docs**: See `docs/api/`
- **Issues**: Search existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

Thank you for contributing to GovChat-NL! 🎉
