"""
Seed ClickHouse Cloud directly with cinema datasets.
"""
import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database.clickhouse_manager import db_manager

def main():
    print(f"Connecting to ClickHouse Cloud: {db_manager.host} ...")
    db_manager._init_connection()
    print(f"Active DB Engine: {db_manager.mode}")
    
    if db_manager.mode == "clickhouse":
        print("Uploading cinematic tables to ClickHouse Cloud...")
        res = db_manager.seed_clickhouse_cloud()
        print("Seed Result:", res)
        
        # Test Query
        test_q = "SELECT title, count(*) as count FROM streaming_telemetry GROUP BY title"
        q_res = db_manager.execute_query(test_q)
        print("Cloud Query Test:", q_res)
        print("\n✅ Successfully connected and verified with ClickHouse Cloud!")
    else:
        print("Notice: Still in local mode, check credentials.")

if __name__ == "__main__":
    main()
