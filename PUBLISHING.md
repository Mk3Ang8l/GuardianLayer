# GuardianLayer PyPI Publishing Guide

## Prerequisites

1. **Install build tools**:
   ```bash
   pip install --upgrade build twine
   ```

2. **Configure PyPI credentials**:
   - Create account on [PyPI](https://pypi.org)
   - Create account on [TestPyPI](https://test.pypi.org) for testing
   - Generate API tokens for both

3. **Configure `.pypirc`** in your home directory:
   ```ini
   [distutils]
   index-servers =
       pypi
       testpypi

   [pypi]
   username = __token__
   password = pypi-YOUR-API-TOKEN-HERE

   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = pypi-YOUR-TESTPYPI-API-TOKEN-HERE
   ```

## Pre-Publishing Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` with release notes
- [ ] Run all tests: `pytest tests/ -v --cov=src`
- [ ] Run linters: `ruff check src/`
- [ ] Check types: `mypy src/`
- [ ] Build documentation: `cd docs && sphinx-build -b html . _build/html`
- [ ] Review README.md renders correctly
- [ ] Ensure all URLs in `pyproject.toml` are correct
- [ ] Tag the release in Git

## Build the Package

1. **Clean previous builds**:
   ```bash
   rm -rf dist/ build/ src/*.egg-info
   ```

2. **Build source and wheel distributions**:
   ```bash
   python -m build
   ```

   This creates:
   - `dist/GuardianLayer-X.X.X.tar.gz` (source distribution)
   - `dist/GuardianLayer-X.X.X-py3-none-any.whl` (wheel distribution)

3. **Check the built distributions**:
   ```bash
   twine check dist/*
   ```

## Test on TestPyPI First

1. **Upload to TestPyPI**:
   ```bash
   twine upload --repository testpypi dist/*
   ```

2. **Test installation from TestPyPI**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ GuardianLayer
   ```

3. **Verify the package**:
   ```bash
   python -c "from GuardianLayer import GuardianLayer; print(GuardianLayer.__version__)"
   ```

4. **Check TestPyPI page**: https://test.pypi.org/project/GuardianLayer/

## Publish to PyPI

Once everything looks good on TestPyPI:

1. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

2. **Verify on PyPI**: https://pypi.org/project/GuardianLayer/

3. **Test installation**:
   ```bash
   pip install GuardianLayer
   ```

## Post-Publishing

1. **Create GitHub Release**:
   - Go to GitHub → Releases → Create new release
   - Tag: `v2.0.0`
   - Title: `GuardianLayer v2.0.0`
   - Description: Copy from CHANGELOG.md
   - Attach built distributions

2. **Announce the release**:
   - GitHub Discussions
   - Twitter/X
   - Reddit (r/Python, r/MachineLearning)
   - Relevant AI/LLM communities

3. **Update documentation**:
   - Ensure ReadTheDocs builds successfully
   - Update any external documentation links

## Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Check distributions
        run: twine check dist/*
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

Then add `PYPI_API_TOKEN` to GitHub repository secrets.

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (2.x.x): Breaking changes
- **MINOR** (x.1.x): New features, backward compatible
- **PATCH** (x.x.1): Bug fixes, backward compatible

## Troubleshooting

**"Invalid distribution" error**:
- Ensure `pyproject.toml` is properly formatted
- Check that all required fields are present
- Verify README.md is valid Markdown

**"File already exists" error**:
- Can't re-upload same version
- Increment version number in `pyproject.toml`
- Rebuild and upload

**Import errors after installation**:
- Check package structure
- Verify `__init__.py` files exist
- Test in clean virtual environment

## Support

For issues with publishing, see:
- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
