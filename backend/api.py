"""
CinePulse OS: Enterprise FastAPI Backend & LangGraph Agent Swarm.
Bridges Google Gemini 2.5 Multi-Agent Orchestration with Sub-10ms ClickHouse Cloud Streaming.
"""

from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database.clickhouse_manager import db_manager
from agents.director_agent import cinepulse_agent

app = FastAPI(
    title="CinePulse OS Enterprise API",
    description="Autonomous Hollywood Studio Multi-Agent Intelligence Engine (Google Gemini 2.5 + ClickHouse Cloud)",
    version="2.0.0"
)

class StudioQueryRequest(BaseModel):
    query: str
    catalog_title: str = "All Studio Releases (Global)"

class PacingSimulationRequest(BaseModel):
    target_scene: str
    trim_minutes: float
    pacing_boost: float
    action_reallocation: bool = True

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database_engine": db_manager.mode,
        "clickhouse_host": db_manager.host,
        "swarm_status": "ONLINE"
    }

@app.post("/api/v1/swarm/direct")
def direct_swarm(req: StudioQueryRequest) -> Dict[str, Any]:
    """
    Executes the 3-Agent Swarm (The Director -> Technical Producer -> Studio Head).
    """
    try:
        trace = cinepulse_agent.run_workflow(req.query)
        return {
            "success": True,
            "director_thought": trace["director_thought"],
            "sql_queries": trace["sql_queries"],
            "total_sql_latency_ms": trace["total_sql_time_ms"],
            "executive_brief": trace["executive_brief"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/simulator/directors-cut")
def simulate_directors_cut(req: PacingSimulationRequest) -> Dict[str, Any]:
    """
    Simulates audience retention curve lift and retained subscriber revenue.
    """
    retention_gain_pct = round((req.trim_minutes * 3.8) + (req.pacing_boost * 2.1) + (4.0 if req.action_reallocation else 0), 1)
    retained_subscribers = int(retention_gain_pct * 1250)
    revenue_saved_m = round(retained_subscribers * 14.99 * 12 / 1000000, 2)
    
    return {
        "retention_gain_pct": retention_gain_pct,
        "projected_retained_subscribers": retained_subscribers,
        "projected_annual_revenue_saved_usd_m": revenue_saved_m,
        "target_scene": req.target_scene,
        "verdict": f"Trimming {req.trim_minutes} min eliminates churn dip and lifts episode completion by +{retention_gain_pct}%"
    }

@app.get("/api/v1/telemetry/visual-cognition")
def get_visual_cognition_stream():
    """
    Returns screen-space luminance (nits) and mobile churn risk data from ClickHouse.
    """
    res = db_manager.execute_query("SELECT timeline_sec, luminance_nits, contrast_ratio, color_entropy, active_face_count, mobile_churn_risk FROM visual_cognition_stream LIMIT 30")
    if res["success"]:
        return {"data": res["data"].to_dict(orient="records"), "latency_ms": res["execution_time_ms"]}
    return {"error": res["error"]}
