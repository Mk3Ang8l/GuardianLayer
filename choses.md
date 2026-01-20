# 🚀 GuardianLayer - Ce qu'il FAUT changer

## ⚡ URGENT (Bloquants production)

### 1. **Ajouter support Async**
```python
# guardian.py - AVANT
def check(self, tool_call: Dict) -> Dict:
    is_loop = self.loop_detector.check(tool_call)

# APRÈS
async def check(self, tool_call: Dict) -> Dict:
    is_loop = await self.loop_detector.check_async(tool_call)
    validation = await self.mcp_facade.validate_async(tool_call)
```
**Impact**: Compatible FastAPI, aiohttp, agents modernes

---

### 2. **Thread-safe SQLite**
```python
# experience_layer.py - AVANT
self._conn = sqlite3.connect(db_path)

# APRÈS
import sqlalchemy
engine = create_engine(f"sqlite:///{db_path}", 
                       pool_pre_ping=True,
                       connect_args={"check_same_thread": False})
```
**Impact**: Évite corruption DB en production multi-thread

---

### 3. **Tests automatisés**
```bash
# Ajouter pytest
pip install pytest pytest-cov pytest-asyncio

# tests/test_guardian.py
import pytest

@pytest.fixture
def guardian():
    return GuardianLayer(db_path=":memory:")

def test_loop_detection(guardian):
    call = {"tool": "search", "query": "test"}
    assert guardian.check(call)["allowed"] == True
    assert guardian.check(call)["allowed"] == False  # Loop

# Run
pytest --cov=src tests/
```
**Impact**: 0 regression, CI/CD possible

---

## 🔥 IMPORTANT (Stabilité)

### 4. **Fixer le typo GuardianLayer → GuardianLayer**
```bash
# Renommer PARTOUT
find . -type f -name "*.py" -exec sed -i 's/Guardian/Guardian/g' {} \;
```

### 5. **Configuration via ENV**
```python
# config.py - NOUVEAU FICHIER
import os

class Config:
    MAX_REPEATS = int(os.getenv("GUARDIAN_MAX_REPEATS", "2"))
    CACHE_SIZE = int(os.getenv("GUARDIAN_CACHE_SIZE", "500"))
    DB_PATH = os.getenv("GUARDIAN_DB_PATH", "guardian.db")
    LOG_LEVEL = os.getenv("GUARDIAN_LOG_LEVEL", "INFO")

# guardian.py
from .config import Config
def __init__(self, max_repeats=Config.MAX_REPEATS):
```

### 6. **Logs structurés**
```python
# guardian.py - AVANT
logger.info("🛡️ GuardianLayer initialized")

# APRÈS
import structlog
logger = structlog.get_logger()
logger.info("guardian_initialized", version="2.0", db_path=db_path)
```

---

## 💡 RECOMMANDÉ (Qualité)

### 7. **Documentation API**
```bash
# Ajouter docstrings
pip install sphinx sphinx-rtd-theme

# src/guardian.py
class GuardianLayer:
    """
    Meta-cognition shield for AI agents.
    
    Args:
        db_path: SQLite database path (None for memory-only)
        max_repeats: Max allowed identical calls before blocking
        
    Example:
        >>> guardian = GuardianLayer(db_path="agent.db")
        >>> result = guardian.check({"tool": "search", "query": "test"})
        >>> print(result["allowed"])
        True
    """
```

### 8. **Prometheus metrics**
```python
# metrics.py - AJOUTER
from prometheus_client import Counter, Gauge

loops_prevented = Counter('guardian_loops_prevented', 'Total loops blocked')
health_score = Gauge('guardian_tool_health', 'Tool health', ['tool_name'])

class MetricsCollector:
    def track_loop_prevented(self):
        self._roi.loops_prevented += 1
        loops_prevented.inc()  # ← NOUVEAU
```

### 9. **Rate limiting interne**
```python
# guardian.py
from collections import deque
import time

class GuardianLayer:
    def __init__(self, max_checks_per_second=100):
        self._rate_limit = deque(maxlen=max_checks_per_second)
    
    def check(self, tool_call):
        now = time.time()
        # Remove old timestamps
        while self._rate_limit and self._rate_limit[0] < now - 1:
            self._rate_limit.popleft()
        
        if len(self._rate_limit) >= 100:
            return {"allowed": False, "reason": "Rate limit exceeded"}
        
        self._rate_limit.append(now)
```

---

## 🎯 BONUS (Nice-to-have)

### 10. **CLI pour debug**
```python
# cli.py - NOUVEAU FICHIER
import click
from .guardian import GuardianLayer

@click.group()
def cli():
    pass

@cli.command()
@click.option('--db-path', default='guardian.db')
def stats(db_path):
    """Show GuardianLayer statistics"""
    g = GuardianLayer(db_path=db_path)
    metrics = g.get_metrics()
    click.echo(f"Loops prevented: {metrics['roi']['loops_prevented']}")
    click.echo(f"Tokens saved: {metrics['roi']['tokens_saved']}")

@cli.command()
@click.option('--db-path', default='guardian.db')
def reset(db_path):
    """Reset all statistics"""
    g = GuardianLayer(db_path=db_path)
    g.reset()
    click.echo("✅ Reset complete")

# Usage: python -m guardian stats
```

### 11. **GitHub Actions CI**
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -e .[dev]
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v2
```

---

## 📋 Checklist prioritaire

```
CRITIQUE (Semaine 1):
[ ] Async support (guardian.py, loop_detector.py, mcp_facade.py)
[ ] SQLAlchemy au lieu de sqlite3 direct
[ ] pytest + 50% coverage minimum
[ ] Fixer typo Guardian → Guardian

IMPORTANT (Semaine 2-3):
[ ] Config via ENV variables
[ ] Logs structurés (structlog)
[ ] Documentation Sphinx
[ ] Rate limiting interne

BONUS (Semaine 4+):
[ ] Prometheus exporters
[ ] CLI debug
[ ] GitHub Actions CI/CD
[ ] Migration Alembic pour DB schema
```

---

## 🔥 Quick wins (1 heure)

```python
# 1. Type hints stricts
pip install mypy
mypy src/  # Corriger les erreurs

# 2. Formatter
pip install black
black src/ tests/

# 3. Linter
pip install ruff
ruff check src/ --fix

# 4. Pre-commit hooks
pip install pre-commit
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff

pre-commit install
```

---

## ⚠️ À NE PAS faire

❌ **Réécrire tout en TypeScript** (perte de temps)
❌ **Ajouter des features avant de fixer async** (dette technique)
❌ **Optimiser prématurément** (le cache fonctionne déjà bien)
❌ **Changer l'API publique** (breaking changes)

✅ **Focus**: Stabilité > Features

---

## 📊 Résultat attendu

**Avant**: 6.5/10 (MVP)
**Après ces changes**: 8.5/10 (Production-ready)

**Temps estimé**: 3-4 semaines à 1 dev
**ROI**: Utilisable par des entreprises (pas juste hobby)