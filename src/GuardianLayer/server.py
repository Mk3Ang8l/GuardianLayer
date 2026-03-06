"""
GuardianLayer FastAPI Server — Complete Edition
Endpoints: check, report, tools, awareness, metrics, reset,
           config (db/redis), health, sessions, hooks, logs
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ── Optional Redis import ─────────────────────────────────────
try:
    import redis as redis_lib

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from GuardianLayer import GuardianLayer, AdviceStyle
from GuardianLayer.providers import (
    SQLiteStorageProvider,
    AsyncSQLiteStorageProvider,
    InMemoryCacheProvider,
)

logger = logging.getLogger(__name__)

# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title="GuardianLayer API",
    description=(
        "REST API for GuardianLayer — the meta-cognition shield for AI agents.\n\n"
        "Use this API to:\n"
        "- Validate tool calls before execution (`/check`)\n"
        "- Report execution results for learning (`/report`)\n"
        "- Register MCP tools (`/tools/register`)\n"
        "- Reconfigure the database or Redis at runtime (`/config/database`, `/config/redis`)\n"
        "- Inspect health, metrics, sessions, logs, hooks\n"
    ),
    version="2.0.6",
    contact={"name": "Michael", "email": "xvorpxvobby@gmail.com"},
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global state ──────────────────────────────────────────────
_guardian: Optional[GuardianLayer] = None
_current_db_path: str = os.getenv("GUARDIAN_DB_PATH", "guardian_server.db")
_current_redis_url: Optional[str] = None
_redis_client = None
_incident_log: List[Dict] = []  # In-memory rolling log (last 500)
_registered_hooks: Dict[str, str] = {}  # tool_name -> hook description


def _build_guardian(
    db_path: str = _current_db_path,
    redis_url: Optional[str] = None,
) -> GuardianLayer:
    """Construct a fresh GuardianLayer with the given backends."""
    cache_provider = None

    if redis_url and REDIS_AVAILABLE:
        try:
            r = redis_lib.from_url(redis_url)
            r.ping()  # Validate connection

            # Lazy import to avoid circular deps
            from GuardianLayer.interfaces import CacheProvider

            class RedisCacheProvider(CacheProvider):
                def __init__(self, client):
                    self._r = client
                    import pickle

                    self._pickle = pickle

                def get(self, key: str):
                    v = self._r.get(f"gl:{key}")
                    return self._pickle.loads(v) if v else None

                def set(self, key: str, value, ttl=None):
                    self._r.set(f"gl:{key}", self._pickle.dumps(value), ex=ttl or 3600)

                def delete(self, key: str):
                    self._r.delete(f"gl:{key}")

                def get_stats(self):
                    info = self._r.info("stats")
                    return {
                        "hits": info.get("keyspace_hits", 0),
                        "misses": info.get("keyspace_misses", 0),
                        "backend": "redis",
                        "url": redis_url,
                    }

            global _redis_client
            _redis_client = r
            cache_provider = RedisCacheProvider(r)
            logger.info(f"Redis cache connected: {redis_url}")
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory cache: {e}")
            cache_provider = InMemoryCacheProvider()
    else:
        cache_provider = InMemoryCacheProvider()

    storage = SQLiteStorageProvider(db_path)
    storage.init()

    return GuardianLayer(
        storage_provider=storage,
        cache_provider=cache_provider,
    )


def get_guardian() -> GuardianLayer:
    global _guardian
    if _guardian is None:
        _guardian = _build_guardian(_current_db_path, _current_redis_url)
    return _guardian


# ── Schemas ───────────────────────────────────────────────────


class ToolCallRequest(BaseModel):
    tool: str = Field(..., example="web_search")
    arguments: Dict[str, Any] = Field(default={}, example={"query": "Python tutorials"})


class ReportRequest(BaseModel):
    tool: str = Field(..., example="web_search")
    arguments: Dict[str, Any] = Field(default={})
    success: bool = Field(..., example=True)
    error: Optional[str] = Field(None, example="Connection timeout")
    context_hint: Optional[str] = Field(None, example="User was searching for docs")


class MCPTool(BaseModel):
    name: str
    description: Optional[str] = ""
    inputSchema: Dict[str, Any] = {}


class RegisterToolsRequest(BaseModel):
    tools: List[MCPTool]


class DatabaseConfigRequest(BaseModel):
    db_path: str = Field(
        ...,
        example="./new_experience.db",
        description="Path to the SQLite file. Use ':memory:' for ephemeral storage.",
    )


class RedisConfigRequest(BaseModel):
    redis_url: Optional[str] = Field(
        None,
        example="redis://localhost:6379/0",
        description="Redis URL. Set to null to disable Redis and switch to in-memory cache.",
    )


class HookRequest(BaseModel):
    tool_name: str = Field(..., example="database_query")
    description: str = Field(
        ...,
        example="Blocks SQL queries containing DROP or DELETE",
        description="Human-readable description of what this hook validates.",
    )
    blocked_keywords: Optional[List[str]] = Field(
        None,
        example=["DROP", "DELETE", "TRUNCATE"],
        description="Keywords that cause the hook to reject a call (case-insensitive).",
    )


class AdviceStyleRequest(BaseModel):
    style: str = Field(..., example="expert", description="One of: concise, expert, friendly")


# ── Startup / Shutdown ────────────────────────────────────────


@app.on_event("startup")
def on_startup():
    get_guardian()
    logger.info("GuardianLayer server started")


@app.on_event("shutdown")
def on_shutdown():
    global _guardian
    if _guardian:
        _guardian.close()


# ─────────────────────────────────────────────────────────────
# Core endpoints
# ─────────────────────────────────────────────────────────────


@app.get("/healthcheck", tags=["System"], summary="Server health check")
def healthcheck():
    """Returns OK if the server is running and GuardianLayer is initialized."""
    g = get_guardian()
    return {
        "status": "ok",
        "db_path": _current_db_path,
        "redis_enabled": _redis_client is not None,
        "tools_registered": len(g.mcp_facade.list_tools()),
    }


@app.post("/check", tags=["Core"], summary="Validate a tool call")
def check(body: ToolCallRequest):
    """
    Run a tool call through all GuardianLayer protection layers.

    Returns `allowed: true/false` plus advice, health score, and block reason.
    """
    g = get_guardian()
    call = {"tool": body.tool, "arguments": body.arguments}
    result = g.check(call)

    # Log for /logs endpoint
    _incident_log.append(
        {
            "ts": time.time(),
            "type": "check",
            "tool": body.tool,
            "allowed": result["allowed"],
            "reason": result.get("reason"),
        }
    )
    if len(_incident_log) > 500:
        _incident_log.pop(0)

    return result


@app.post("/report", tags=["Core"], summary="Report execution result")
def report(body: ReportRequest):
    """
    Tell GuardianLayer whether the last tool call succeeded or failed.

    This feeds the experience layer and health monitor so the system learns over time.
    """
    g = get_guardian()
    g.report_result(
        {"tool": body.tool, "arguments": body.arguments},
        success=body.success,
        error=body.error,
        context_hint=body.context_hint,
    )

    _incident_log.append(
        {
            "ts": time.time(),
            "type": "report",
            "tool": body.tool,
            "success": body.success,
            "error": body.error,
        }
    )
    if len(_incident_log) > 500:
        _incident_log.pop(0)

    return {"status": "recorded"}


# ─────────────────────────────────────────────────────────────
# Tools
# ─────────────────────────────────────────────────────────────


@app.post("/tools/register", tags=["Tools"], summary="Register MCP tools")
def register_tools(body: RegisterToolsRequest):
    """Register one or more MCP-compatible tool definitions."""
    g = get_guardian()
    raw = [t.model_dump() for t in body.tools]
    count = g.ingest_tools(raw)
    return {"registered": count, "total": len(g.mcp_facade.list_tools())}


@app.get("/tools", tags=["Tools"], summary="List registered tools")
def list_tools():
    """Returns all tool names currently registered with the MCP facade."""
    g = get_guardian()
    return {"tools": g.mcp_facade.list_tools()}


@app.delete("/tools/{tool_name}", tags=["Tools"], summary="Reset a tool's health")
def reset_tool_health(tool_name: str):
    """
    Manually reset the circuit breaker and health score for a specific tool.
    Useful for admin overrides when a tool has recovered.
    """
    g = get_guardian()
    g.reset_tool(tool_name)
    return {"status": "reset", "tool": tool_name}


# ─────────────────────────────────────────────────────────────
# Configuration — Database
# ─────────────────────────────────────────────────────────────


@app.get("/config/database", tags=["Configuration"], summary="Get current database config")
def get_database_config():
    """Returns the current SQLite database path."""
    return {
        "db_path": _current_db_path,
        "is_memory": _current_db_path == ":memory:",
    }


@app.post("/config/database", tags=["Configuration"], summary="Switch database at runtime")
def set_database_config(body: DatabaseConfigRequest):
    """
    Switch GuardianLayer to a different SQLite database without restarting.

    ⚠️ This rebuilds the GuardianLayer instance. In-flight sessions will be reset.
    Registered tools **are not** automatically migrated — re-register them after switching.
    """
    global _guardian, _current_db_path

    old_path = _current_db_path

    try:
        if _guardian:
            _guardian.close()

        _current_db_path = body.db_path
        _guardian = _build_guardian(body.db_path, _current_redis_url)

        return {
            "status": "switched",
            "previous_db": old_path,
            "new_db": body.db_path,
            "warning": "Registered tools have been cleared. Please re-register via /tools/register.",
        }
    except Exception as e:
        # Rollback
        _current_db_path = old_path
        _guardian = _build_guardian(old_path, _current_redis_url)
        raise HTTPException(status_code=500, detail=f"Database switch failed: {e}")


# ─────────────────────────────────────────────────────────────
# Configuration — Redis
# ─────────────────────────────────────────────────────────────


@app.get("/config/redis", tags=["Configuration"], summary="Get Redis cache status")
def get_redis_config():
    """Returns whether Redis is currently connected and its URL."""
    connected = False
    if _redis_client:
        try:
            _redis_client.ping()
            connected = True
        except Exception:
            connected = False

    return {
        "redis_enabled": _redis_client is not None,
        "redis_url": _current_redis_url,
        "connected": connected,
        "redis_available": REDIS_AVAILABLE,
    }


@app.post("/config/redis", tags=["Configuration"], summary="Enable or disable Redis cache")
def set_redis_config(body: RedisConfigRequest):
    """
    Switch the cache backend to Redis (or back to in-memory).

    - Pass a valid `redis_url` to enable Redis.
    - Pass `null` to disable Redis and fall back to in-memory LRU cache.

    ⚠️ This rebuilds the GuardianLayer instance. Registered tools will be cleared.
    """
    global _guardian, _current_redis_url

    if not REDIS_AVAILABLE and body.redis_url:
        raise HTTPException(
            status_code=400,
            detail="redis package is not installed. Run: pip install redis",
        )

    old_url = _current_redis_url

    try:
        if _guardian:
            _guardian.close()

        _current_redis_url = body.redis_url
        _guardian = _build_guardian(_current_db_path, body.redis_url)

        return {
            "status": "switched",
            "previous_redis_url": old_url,
            "new_redis_url": body.redis_url,
            "redis_enabled": body.redis_url is not None,
            "warning": "Registered tools have been cleared. Please re-register via /tools/register.",
        }
    except Exception as e:
        _current_redis_url = old_url
        _guardian = _build_guardian(_current_db_path, old_url)
        raise HTTPException(status_code=500, detail=f"Redis switch failed: {e}")


# ─────────────────────────────────────────────────────────────
# Configuration — Advice style
# ─────────────────────────────────────────────────────────────


@app.post("/config/advice-style", tags=["Configuration"], summary="Change advice style")
def set_advice_style(body: AdviceStyleRequest):
    """
    Change how GuardianLayer formats its advice injections.

    - `concise` — short and direct (best for small models)
    - `expert` — detailed technical analysis (best for GPT-4 / Claude)
    - `friendly` — conversational (best for user-facing agents)
    """
    style_map = {
        "concise": AdviceStyle.CONCISE,
        "expert": AdviceStyle.EXPERT,
        "friendly": AdviceStyle.FRIENDLY,
    }
    style = style_map.get(body.style.lower())
    if not style:
        raise HTTPException(
            status_code=400, detail=f"Unknown style '{body.style}'. Use: concise, expert, friendly"
        )

    get_guardian().set_advice_style(style)
    return {"status": "updated", "advice_style": body.style.lower()}


# ─────────────────────────────────────────────────────────────
# Awareness & Metrics
# ─────────────────────────────────────────────────────────────


@app.get("/awareness", tags=["Observability"], summary="Get self-awareness context")
def awareness():
    """
    Returns the formatted self-awareness string to inject into your LLM prompt.

    Includes circuit-breaker status and low-reliability warnings for all tracked tools.
    """
    return {"context": get_guardian().get_awareness_context()}


@app.get("/metrics", tags=["Observability"], summary="Get all metrics")
def metrics():
    """
    Returns comprehensive metrics: ROI (tokens saved, loops prevented),
    loop detection stats, health per tool, session stats, and cache stats.
    """
    return get_guardian().get_metrics()


@app.get("/health", tags=["Observability"], summary="Get per-tool health scores")
def health():
    """
    Returns health score (0–100), circuit state, and success rate for every tracked tool.
    """
    return get_guardian().health_monitor.get_all_health()


# ─────────────────────────────────────────────────────────────
# Sessions
# ─────────────────────────────────────────────────────────────


@app.get("/session", tags=["Sessions"], summary="Get current session stats")
def get_session():
    """Returns stats for the current active session (calls, successes, failures, duration)."""
    return get_guardian().experience.get_session_stats()


@app.post("/session/new", tags=["Sessions"], summary="Start a new session")
def new_session(
    session_id: Optional[str] = Query(
        None, description="Custom session ID (auto-generated if omitted)"
    ),
):
    """
    Start a fresh session. Clears loop detection history and resets session counters.
    Use this between user conversations or agent runs.
    """
    g = get_guardian()
    g.reset()
    sid = g.experience.session_id
    return {"status": "new_session", "session_id": sid}


# ─────────────────────────────────────────────────────────────
# Hooks (validation rules)
# ─────────────────────────────────────────────────────────────


@app.get("/hooks", tags=["Hooks"], summary="List registered hooks")
def list_hooks():
    """Returns all custom validation hooks currently registered."""
    return {"hooks": _registered_hooks}


@app.post("/hooks", tags=["Hooks"], summary="Register a keyword-based validation hook")
def register_hook(body: HookRequest):
    """
    Register a simple keyword-based validation hook for a tool.

    When a call to `tool_name` contains any of `blocked_keywords` in its arguments,
    the call will be blocked with a clear error message.

    For advanced logic, implement a custom hook in code and inject it directly.
    """
    g = get_guardian()

    keywords = [kw.upper() for kw in (body.blocked_keywords or [])]

    def _hook(tool_call: Dict[str, Any]) -> Optional[str]:
        args_str = str(tool_call.get("arguments", {})).upper()
        for kw in keywords:
            if kw in args_str:
                return f"Blocked keyword detected: '{kw}'"
        return None

    g.register_hook(body.tool_name, _hook)
    _registered_hooks[body.tool_name] = body.description

    return {
        "status": "registered",
        "tool": body.tool_name,
        "blocked_keywords": body.blocked_keywords,
        "description": body.description,
    }


@app.delete("/hooks/{tool_name}", tags=["Hooks"], summary="Remove hook for a tool")
def delete_hook(tool_name: str):
    """
    Remove the registered hook description for a tool.

    Note: The underlying Python hook function cannot be removed at runtime without
    restarting. This endpoint removes the hook from the registry listing only.
    Use `/session/new` or `/reset` to fully clear hook state.
    """
    if tool_name not in _registered_hooks:
        raise HTTPException(status_code=404, detail=f"No hook found for tool '{tool_name}'")
    _registered_hooks.pop(tool_name)
    return {"status": "removed", "tool": tool_name}


# ─────────────────────────────────────────────────────────────
# Logs
# ─────────────────────────────────────────────────────────────


@app.get("/logs", tags=["Observability"], summary="Get recent incident log")
def get_logs(
    limit: int = Query(50, ge=1, le=500, description="Number of recent entries to return"),
    tool: Optional[str] = Query(None, description="Filter by tool name"),
    type: Optional[str] = Query(None, description="Filter by event type: check or report"),
    blocked_only: bool = Query(False, description="Only show blocked calls"),
):
    """
    Returns recent check and report events (last 500 kept in memory).

    Useful for debugging agent behavior without querying the database directly.
    """
    logs = list(reversed(_incident_log))  # Most recent first

    if tool:
        logs = [l for l in logs if l.get("tool") == tool]
    if type:
        logs = [l for l in logs if l.get("type") == type]
    if blocked_only:
        logs = [l for l in logs if l.get("allowed") is False]

    return {
        "total": len(logs),
        "limit": limit,
        "entries": logs[:limit],
    }


# ─────────────────────────────────────────────────────────────
# Reset
# ─────────────────────────────────────────────────────────────


@app.post("/reset", tags=["System"], summary="Full reset (loop history + metrics)")
def reset():
    """
    Resets loop detection history, session counters, and ROI metrics.
    Does NOT clear registered tools, hooks, or the database.
    """
    get_guardian().reset()
    _incident_log.clear()
    return {"status": "reset"}
