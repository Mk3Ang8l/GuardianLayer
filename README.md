# GuardianLayer

[![PyPI](https://img.shields.io/pypi/v/GuardianLayer.svg)](https://pypi.org/project/GuardianLayer/)
[![Tests](https://github.com/your-org/GuardianLayer/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/GuardianLayer/actions)
[![Docs](https://img.shields.io/badge/docs-Sphinx-blue)](https://your-docs-url)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Library to prevent infinite loops in AI systems.

## Installation
Install the package from PyPI:

```bash
pip install GuardianLayer
```

(If you are installing a development copy from source:)
```bash
git clone https://github.com/your-org/GuardianLayer.git
cd GuardianLayer
pip install -e '.[dev]'
```

## Usage
```python
from GuardianLayer import LoopDetector

detector = LoopDetector()
result = detector.check({"tool": "search", "query": "test"})

if result[0]:  # If loop detected
    print(f"Loop: {result[1]}")
```

Notes:
- Package name on PyPI and the import name are both `GuardianLayer`.
- Example CLI/HTTP endpoints (if your project exposes any) and docs are available via the repository and the `docs/` folder — update the links above after you publish the docs or host them (ReadTheDocs / GitHub Pages).

## License

MIT