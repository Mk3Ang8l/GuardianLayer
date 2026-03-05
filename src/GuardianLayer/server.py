from fastapi import FastAPI
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from GuardianLayer import GuardianLayer

app = FastAPI(title="GuardianLayer API")
guardian = GuardianLayer(db_path="guardian_server.db")

# ── Schemas ──────────────────────────────────────────
class ToolCallRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any] = {}

class ReportRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any] = {}
    success: bool
    error: Optional[str] = None

class MCPTool(BaseModel):
    name: str
    description: Optional[str] = ""
    inputSchema: Dict[str, Any] = {}

class RegisterToolsRequest(BaseModel):
    tools: List[MCPTool]

# ── Endpoints ────────────────────────────────────────
@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

@app.post("/check")
def check(body: ToolCallRequest):
    result = guardian.check({"tool": body.tool, "arguments": body.arguments})
    return result

@app.post("/report")
def report(body: ReportRequest):
    guardian.report_result(
        {"tool": body.tool, "arguments": body.arguments},
        success=body.success,
        error=body.error
    )
    return {"status": "recorded"}

@app.post("/tools/register")
def register_tools(body: RegisterToolsRequest):
    raw = [t.model_dump() for t in body.tools]
    count = guardian.ingest_tools(raw)
    return {"registered": count}

@app.get("/tools")
def list_tools():
    return {"tools": guardian.mcp_facade.list_tools()}

@app.get("/awareness")
def awareness():
    return {"context": guardian.get_awareness_context()}

@app.get("/metrics")
def metrics():
    return guardian.get_metrics()

@app.post("/reset")
def reset():
    guardian.reset()
    return {"status": "reset"}