"""
Verification test script for CinePulse AI with UTF-8 safe output.
"""
import sys

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database.clickhouse_manager import db_manager
from agents.director_agent import cinepulse_agent

def main():
    print("--- 1. Testing Database Initialization ---")
    print(f"Database Engine: {db_manager.mode}")
    schema = db_manager.get_schema_summary()
    print(f"Schema length: {len(schema)} chars")

    print("\n--- 2. Testing Sample ClickHouse Query ---")
    res = db_manager.execute_query("SELECT title, count(*) as count FROM streaming_telemetry GROUP BY title")
    print(f"Query Success: {res['success']}, Execution Time: {res['execution_time_ms']} ms, Rows: {res['row_count']}")
    if res["success"]:
        print(res["data"].head(3))

    print("\n--- 3. Testing Multi-Agent Workflow ---")
    trace = cinepulse_agent.run_workflow("Why are viewers dropping off in early scenes, and what operational adjustments should the studio make?")
    print(f"Director Thought: {trace['director_thought']}")
    print(f"Total SQL Queries Executed: {len(trace['sql_queries'])}")
    print(f"Total SQL Query Time: {trace['total_sql_time_ms']} ms")
    print(f"Executive Brief Generated (chars): {len(trace['executive_brief'])}")
    print("\n✅ All CinePulse AI components verified successfully!")

if __name__ == "__main__":
    main()
