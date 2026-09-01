"""
Database Connection Manager for CinePulse AI.
Supports ClickHouse Cloud (via clickhouse-connect) with zero-configuration in-memory fallback.
"""

import os
import time
import pandas as pd
import duckdb
from dotenv import load_dotenv

load_dotenv()

from database.seed_data import (
    generate_box_office_data,
    generate_streaming_telemetry,
    generate_scene_retention_data,
    generate_audience_sentiment
)

class ClickHouseManager:
    def __init__(self):
        self.host = os.getenv("CLICKHOUSE_HOST", "localhost")
        self.port = int(os.getenv("CLICKHOUSE_PORT", "8443"))
        self.user = os.getenv("CLICKHOUSE_USER", "default")
        self.password = os.getenv("CLICKHOUSE_PASSWORD", "")
        self.database = os.getenv("CLICKHOUSE_DATABASE", "default")
        self.secure = os.getenv("CLICKHOUSE_SECURE", "True").lower() in ["true", "1", "t"]
        
        self.client = None
        self.mode = "in-memory"
        self.duck_conn = duckdb.connect(database=":memory:")
        
        self._init_connection()

    def _init_connection(self):
        """Attempts connection to ClickHouse, falls back to local engine if unreachable."""
        if self.host and self.password and self.host != "localhost":
            try:
                import clickhouse_connect
                self.client = clickhouse_connect.get_client(
                    host=self.host,
                    port=self.port,
                    username=self.user,
                    password=self.password,
                    database=self.database,
                    secure=self.secure
                )
                self.mode = "clickhouse"
                print(f"[ClickHouse] Successfully connected to ClickHouse Cloud at {self.host}")
                return
            except Exception as e:
                print(f"[ClickHouse] Connection note: {e}. Defaulting to high-performance local analytical engine.")
        
        self.mode = "in-memory"
        self._seed_local_engine()

    def _seed_local_engine(self):
        """Pre-seeds tables into in-memory engine with realistic blockbuster cinema data."""
        df_bo = generate_box_office_data(days=30)
        df_stream = generate_streaming_telemetry(num_sessions=3500)
        df_scenes = generate_scene_retention_data()
        df_sentiment = generate_audience_sentiment(num_reviews=1000)
        
        self.duck_conn.register("box_office_daily", df_bo)
        self.duck_conn.register("streaming_telemetry", df_stream)
        self.duck_conn.register("scene_retention_metrics", df_scenes)
        self.duck_conn.register("audience_sentiment", df_sentiment)
        print("[Database] Loaded 4 cinematic tables (box_office_daily, streaming_telemetry, scene_retention_metrics, audience_sentiment).")

    def seed_clickhouse_cloud(self):
        """Creates DDL schemas and uploads seed data into ClickHouse Cloud cluster."""
        if self.mode != "clickhouse" or not self.client:
            return {"status": "error", "message": "ClickHouse Cloud is not connected"}
        
        try:
            # 1. Create Tables
            self.client.command("""
            CREATE TABLE IF NOT EXISTS box_office_daily (
                title String,
                report_date String,
                day_number Int32,
                region String,
                country String,
                daily_gross_usd Float64,
                screen_count Int32,
                avg_ticket_price Float64,
                marketing_spend_usd Float64,
                audience_rating_pct Float64
            ) ENGINE = MergeTree()
            ORDER BY (title, report_date);
            """)

            self.client.command("""
            CREATE TABLE IF NOT EXISTS streaming_telemetry (
                session_id String,
                user_id String,
                title String,
                episode Int32,
                session_timestamp String,
                watch_duration_sec Int32,
                completion_pct Float64,
                buffer_events Int32,
                bitrate_kbps Int32,
                quality_tier String,
                device_type String,
                region String,
                drop_off_timestamp_sec Int32,
                user_rating Int32
            ) ENGINE = MergeTree()
            ORDER BY (title, session_id);
            """)

            self.client.command("""
            CREATE TABLE IF NOT EXISTS scene_retention_metrics (
                title String,
                episode Int32,
                scene_id String,
                minute_mark Int32,
                scene_type String,
                character_focus String,
                pacing_score Float64,
                emotional_tone String,
                churn_risk_score Float64,
                viewer_drop_count Int32
            ) ENGINE = MergeTree()
            ORDER BY (title, scene_id);
            """)

            self.client.command("""
            CREATE TABLE IF NOT EXISTS audience_sentiment (
                review_id String,
                title String,
                platform String,
                region String,
                sentiment_score Float64,
                sentiment_label String,
                comment_text String,
                review_timestamp String
            ) ENGINE = MergeTree()
            ORDER BY (title, review_id);
            """)

            # 2. Generate Data
            df_bo = generate_box_office_data(days=30)
            df_stream = generate_streaming_telemetry(num_sessions=3500)
            df_scenes = generate_scene_retention_data()
            df_sentiment = generate_audience_sentiment(num_reviews=1000)
            
            # 3. Clean and Insert
            self.client.command("TRUNCATE TABLE IF EXISTS box_office_daily")
            self.client.command("TRUNCATE TABLE IF EXISTS streaming_telemetry")
            self.client.command("TRUNCATE TABLE IF EXISTS scene_retention_metrics")
            self.client.command("TRUNCATE TABLE IF EXISTS audience_sentiment")

            self.client.insert_df("box_office_daily", df_bo)
            self.client.insert_df("streaming_telemetry", df_stream)
            self.client.insert_df("scene_retention_metrics", df_scenes)
            self.client.insert_df("audience_sentiment", df_sentiment)
            
            return {"status": "success", "message": "Successfully seeded ClickHouse Cloud with 4 cinema datasets!"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def execute_query(self, sql_query: str):
        """
        Executes an analytical SQL query and returns results, execution time in ms, and row count.
        """
        start_time = time.perf_counter()
        
        try:
            clean_sql = sql_query.strip().rstrip(";")
            
            if self.mode == "clickhouse" and self.client:
                result = self.client.query_df(clean_sql)
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return {
                    "success": True,
                    "data": result,
                    "execution_time_ms": duration_ms,
                    "row_count": len(result),
                    "engine": "ClickHouse Cloud",
                    "error": None
                }
            else:
                result = self.duck_conn.execute(clean_sql).fetchdf()
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return {
                    "success": True,
                    "data": result,
                    "execution_time_ms": duration_ms,
                    "row_count": len(result),
                    "engine": "ClickHouse Compatible Engine",
                    "error": None
                }
        except Exception as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "success": False,
                "data": pd.DataFrame(),
                "execution_time_ms": duration_ms,
                "row_count": 0,
                "engine": self.mode,
                "error": str(e)
            }

    def get_schema_summary(self) -> str:
        """Returns the schema description for the AI Agent to write accurate SQL."""
        return """
DATABASE SCHEMAS (CinePulse Analytics):

1. box_office_daily:
   - title (String): Movie title (e.g. 'CyberBlade 2099', 'Kingdom of Sand')
   - report_date (String): YYYY-MM-DD
   - day_number (Int32): Days since release (1 to 30)
   - region (String): 'North America', 'Europe', 'Asia-Pacific', 'Latin America'
   - country (String): Country name
   - daily_gross_usd (Float64): Gross revenue in USD
   - screen_count (Int32): Number of active movie screens
   - avg_ticket_price (Float64): Average ticket price in USD
   - marketing_spend_usd (Float64): Daily marketing expenditure in USD
   - audience_rating_pct (Float64): Audience score % (0-100)

2. streaming_telemetry:
   - session_id (String): Unique stream session ID
   - user_id (String): User identifier
   - title (String): Title of film or series (e.g. 'Neon Horizons: Season 2', 'The Shadow Protocol')
   - episode (Int32): Episode number
   - session_timestamp (String): Stream start time
   - watch_duration_sec (Int32): Total seconds watched
   - completion_pct (Float64): % of episode watched (0-100)
   - buffer_events (Int32): Number of buffering/lag events during session
   - bitrate_kbps (Int32): Video bitrate in kbps
   - quality_tier (String): '4K HDR', '1080p HD', '720p'
   - device_type (String): 'Smart TV (4K)', 'Mobile (iOS)', 'Mobile (Android)', etc.
   - region (String): Geographic territory
   - drop_off_timestamp_sec (Int32): Second mark where viewer abandoned (0 if finished)
   - user_rating (Int32): Star rating 1 to 5

3. scene_retention_metrics:
   - title (String): Title
   - episode (Int32): Episode number
   - scene_id (String): e.g. 'SC_01', 'SC_02'
   - minute_mark (Int32): Minute start of the scene
   - scene_type (String): 'Action Sequence', 'Dialogue / Character Drama', 'Plot Exposition', 'Climax / Twist', etc.
   - character_focus (String): Lead character in scene
   - pacing_score (Float64): Pacing intensity 1.0 - 10.0
   - emotional_tone (String): 'Tense', 'Excited', 'Melancholy', 'Monotonous', etc.
   - churn_risk_score (Float64): Churn probability 0.0 - 1.0
   - viewer_drop_count (Int32): Number of viewers who stopped watching during this scene

4. audience_sentiment:
   - review_id (String): Review ID
   - title (String): Title
   - platform (String): 'X (Twitter)', 'Reddit', 'Letterboxd', 'Rotten Tomatoes', 'IMDb', 'TikTok'
   - region (String): Geographic region
   - sentiment_score (Float64): -1.0 (very negative) to +1.0 (very positive)
   - sentiment_label (String): 'Positive', 'Neutral', 'Negative'
   - comment_text (String): Review body
   - review_timestamp (String): Review post time
"""

# Global Singleton instance
db_manager = ClickHouseManager()
