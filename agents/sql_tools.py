"""
Tool declarations and execution adapters for ClickHouse within the Agentic Workflow.
"""

from database.clickhouse_manager import db_manager

def get_database_schema() -> str:
    """Returns the full schema description of the cinematic analytics database."""
    return db_manager.get_schema_summary()

def execute_clickhouse_query(sql_query: str) -> dict:
    """
    Executes a SQL analytical query against the ClickHouse streaming & box-office database.
    
    Args:
        sql_query: The SQL query to run.
        
    Returns:
        dict containing 'success', 'data' (records as JSON), 'execution_time_ms', 'row_count', and 'error'.
    """
    res = db_manager.execute_query(sql_query)
    
    if res["success"]:
        # Convert DataFrame to records for JSON serialization to agent
        data_records = res["data"].head(100).to_dict(orient="records")
        return {
            "success": True,
            "execution_time_ms": res["execution_time_ms"],
            "row_count": res["row_count"],
            "engine": res["engine"],
            "records": data_records,
            "columns": list(res["data"].columns) if not res["data"].empty else []
        }
    else:
        return {
            "success": False,
            "execution_time_ms": res["execution_time_ms"],
            "error": res["error"]
        }

def get_popular_titles() -> list:
    """Returns the list of active movie and streaming titles in the database."""
    res = db_manager.execute_query("SELECT DISTINCT title FROM streaming_telemetry UNION SELECT DISTINCT title FROM box_office_daily")
    if res["success"] and not res["data"].empty:
        return res["data"]["title"].tolist()
    return ["CyberBlade 2099", "The Shadow Protocol", "Neon Horizons: Season 2", "Kingdom of Sand", "Starlight Odyssey"]
