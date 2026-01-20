"""AI Loop Guardian v2.0 - Meta-Cognition Layer for AI Agents"""

__version__ = "2.0.0"

from .LoopDetector import LoopDetector, LoopMetrics

from .mcp_facade import MCPFacade, ToolSchema
from .experience_layer import ExperienceLayer
from .advice_generator import AdviceGenerator, AdviceStyle, AdviceContext
from .health_monitor import HealthMonitor, CircuitState, ErrorType, ErrorClassifier
from .cache import LRUCache, AdviceCache, ValidationCache, HashCache, CacheStats
from .metrics import MetricsCollector
from .interfaces import StorageProvider, CacheProvider
from .providers import SQLiteStorageProvider, InMemoryCacheProvider
from .guardian import GuardianLayer

__all__ = [
    # Core
    "GuardianLayer",
    "LoopDetector",
    "LoopMetrics",
    # Validation
    "MCPFacade",
    "ToolSchema",
    # Health
    "HealthMonitor",
    "CircuitState",
    "ErrorType",
    "ErrorClassifier",
    # Experience & Storage
    "ExperienceLayer",
    "StorageProvider",
    "SQLiteStorageProvider",
    # Advice
    "AdviceGenerator",
    "AdviceStyle",
    "AdviceContext",
    # Caching
    "CacheProvider",
    "InMemoryCacheProvider",
    "LRUCache",
    "AdviceCache",
    "ValidationCache",
    "HashCache",
    "CacheStats",
    # Metrics
    "MetricsCollector",
]
