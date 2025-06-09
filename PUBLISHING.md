# Publishing Guide for BAI2 to CSV

This document provides a comprehensive guide for publishing the `bai2-to-csv` package to PyPI.

## Pre-Publishing Checklist

Before publishing, ensure all of the following are completed:

### 1. Code Quality ✅
- [ ] All tests pass (`pytest tests/`)
- [ ] Code coverage is above 80%
- [ ] Code formatting is correct (`black --check src tests`)
- [ ] Import sorting is correct (`isort --check-only src tests`)
- [ ] Linting passes (`flake8 src tests`)
- [ ] Type checking passes (`mypy src tests`)

### 2. Documentation ✅
- [ ] README.md is up to date with usage examples
- [ ] CHANGELOG.md includes all changes for this version
- [ ] All docstrings are complete and accurate
- [ ] License file is present and correct

### 3. Package Metadata ✅
- [ ] Version number is correct in `pyproject.toml`
- [ ] Package description is accurate
- [ ] Author information is correct
- [ ] Repository URLs are correct
- [ ] Keywords and classifiers are appropriate
- [ ] Dependencies are correctly specified

### 4. GitHub Setup
- [ ] Repository is public (for open source)
- [ ] GitHub secrets are configured:
  - `PYPI_API_TOKEN`
  - `TEST_PYPI_API_TOKEN`
- [ ] GitHub Actions workflows are working
- [ ] All branches are up to date

## PyPI Account Setup

### 1. Create Accounts
1. Register at [PyPI](https://pypi.org/account/register/)
2. Register at [Test PyPI](https://test.pypi.org/account/register/)
3. Verify your email addresses

### 2. Generate API Tokens
1. Go to PyPI → Account Settings → API tokens
2. Create a new token with "Entire account" scope
3. Copy the token (starts with `pypi-`)
4. Repeat for Test PyPI

### 3. Configure GitHub Secrets
1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add new repository secrets:
   - Name: `PYPI_API_TOKEN`, Value: your PyPI token
   - Name: `TEST_PYPI_API_TOKEN`, Value: your Test PyPI token

## Publishing Process

### Option 1: Automated Publishing (Recommended)

#### For Testing (Test PyPI)
1. Go to GitHub → Actions
2. Select "Publish to PyPI" workflow
3. Click "Run workflow"
4. Optionally specify a version
5. The package will be published to Test PyPI

#### For Production (PyPI)
1. Update version: `poetry version patch` (or `minor`, `major`)
2. Update `CHANGELOG.md` with new version details
3. Commit changes: `git commit -am "Release vX.X.X"`
4. Push: `git push`
5. Create GitHub release:
   - Go to Releases → Create new release
   - Tag: `vX.X.X`
   - Title: `vX.X.X`
   - Description: Copy from CHANGELOG.md
   - Publish release
6. GitHub Actions will automatically publish to PyPI

### Option 2: Manual Publishing

#### Local Setup
```bash
# Install dependencies
poetry install --with dev

# Configure repositories
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi your-test-pypi-token
poetry config pypi-token.pypi your-pypi-token
```

#### Build and Test
```bash
# Run full test suite
./scripts/build_package.sh

# Or manually:
poetry build
poetry run twine check dist/*
```

#### Publish to Test PyPI
```bash
poetry publish --repository testpypi
```

#### Test Installation from Test PyPI
```bash
pip install --index-url https://test.pypi.org/simple/ bai2-to-csv
```

#### Publish to PyPI
```bash
poetry publish
```

## Post-Publishing

After successful publication:

1. **Test Installation**: `pip install bai2-to-csv`
2. **Update Documentation**: Ensure README reflects new features
3. **Create Announcement**: Consider blog post or social media
4. **Monitor Usage**: Check PyPI download statistics
5. **Handle Issues**: Monitor GitHub issues and PyPI project page

## Troubleshooting

### Common Issues

#### "The name 'bai2-to-csv' is already taken"
- Choose a different package name in `pyproject.toml`
- Update all references to the new name

#### "Invalid token"
- Regenerate API tokens
- Update GitHub secrets
- Ensure token has correct permissions

#### "Upload failed"
- Check if version already exists
- Ensure package builds correctly
- Verify all required files are included

#### "Tests fail in CI"
- Run tests locally first
- Check Python version compatibility
- Review dependency conflicts

### Getting Help

- PyPI Help: https://pypi.org/help/
- Poetry Documentation: https://python-poetry.org/docs/
- GitHub Actions: https://docs.github.com/actions

## Version History

- v0.1.0 - Initial release with basic BAI2 to CSV conversion functionality