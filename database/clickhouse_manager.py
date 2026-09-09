"""
Database Connection Manager for CinePulse AI (Enterprise Edition).
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
    generate_audience_sentiment,
    generate_frame_script_alignment,
    generate_visual_cognition_stream,
    generate_perceptual_pacing_telemetry,
    generate_theatrical_svod_elasticity
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
        
        # Always pre-seed local fallback engine so failover is instant
        self._seed_local_engine()
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

    def _seed_local_engine(self):
        """Pre-seeds all 8 core & proprietary tables into local in-memory engine."""
        df_bo = generate_box_office_data(days=30)
        df_stream = generate_streaming_telemetry(num_sessions=3500)
        df_scenes = generate_scene_retention_data()
        df_sentiment = generate_audience_sentiment(num_reviews=1000)
        
        df_frame = generate_frame_script_alignment()
        df_visual = generate_visual_cognition_stream()
        df_pacing = generate_perceptual_pacing_telemetry()
        df_svod = generate_theatrical_svod_elasticity()
        
        self.duck_conn.register("box_office_daily", df_bo)
        self.duck_conn.register("streaming_telemetry", df_stream)
        self.duck_conn.register("scene_retention_metrics", df_scenes)
        self.duck_conn.register("audience_sentiment", df_sentiment)
        
        self.duck_conn.register("frame_script_alignment", df_frame)
        self.duck_conn.register("visual_cognition_stream", df_visual)
        self.duck_conn.register("perceptual_pacing_telemetry", df_pacing)
        self.duck_conn.register("theatrical_svod_elasticity", df_svod)
        print("[Database] Loaded 8 tables into CinePulse analytical storage engine.")

    def seed_clickhouse_cloud(self):
        """Creates DDL schemas and uploads all 8 datasets into ClickHouse Cloud cluster."""
        if self.mode != "clickhouse" or not self.client:
            return {"status": "error", "message": "ClickHouse Cloud is not connected"}
        
        try:
            # 1. Base Tables
            self.client.command("CREATE TABLE IF NOT EXISTS box_office_daily (title String, report_date String, day_number Int32, region String, country String, daily_gross_usd Float64, screen_count Int32, avg_ticket_price Float64, marketing_spend_usd Float64, audience_rating_pct Float64) ENGINE = MergeTree() ORDER BY (title, report_date);")
            self.client.command("CREATE TABLE IF NOT EXISTS streaming_telemetry (session_id String, user_id String, title String, episode Int32, session_timestamp String, watch_duration_sec Int32, completion_pct Float64, buffer_events Int32, bitrate_kbps Int32, quality_tier String, device_type String, region String, drop_off_timestamp_sec Int32, user_rating Int32) ENGINE = MergeTree() ORDER BY (title, session_id);")
            self.client.command("CREATE TABLE IF NOT EXISTS scene_retention_metrics (title String, episode Int32, scene_id String, minute_mark Int32, scene_type String, character_focus String, pacing_score Float64, emotional_tone String, churn_risk_score Float64, viewer_drop_count Int32) ENGINE = MergeTree() ORDER BY (title, scene_id);")
            self.client.command("CREATE TABLE IF NOT EXISTS audience_sentiment (review_id String, title String, platform String, region String, sentiment_score Float64, sentiment_label String, comment_text String, review_timestamp String) ENGINE = MergeTree() ORDER BY (title, review_id);")
            
            # 2. Proprietary Engine Tables
            self.client.command("CREATE TABLE IF NOT EXISTS frame_script_alignment (title String, timeline_sec Int32, timeline_min Int32, shot_type String, narrative_theme String, dialogue_density_wpm Int32, viewer_drop_count Int32, retention_pct Float64) ENGINE = MergeTree() ORDER BY (title, timeline_sec);")
            self.client.command("CREATE TABLE IF NOT EXISTS visual_cognition_stream (title String, timeline_sec Int32, luminance_nits Float64, contrast_ratio Float64, color_entropy Float64, active_face_count Int32, mobile_churn_risk Float64) ENGINE = MergeTree() ORDER BY (title, timeline_sec);")
            self.client.command("CREATE TABLE IF NOT EXISTS perceptual_pacing_telemetry (title String, minute_window Int32, cuts_per_minute Int32, audio_db_variance Float64, cdn_buffer_rate_pct Float64, bitrate_drop_flag Int32, pacing_stress_index Float64) ENGINE = MergeTree() ORDER BY (title, minute_window);")
            self.client.command("CREATE TABLE IF NOT EXISTS theatrical_svod_elasticity (title String, budget_m Float64, projected_theatrical_gross_m Float64, theatrical_net_profit_m Float64, projected_svod_subs_gained_k Int32, svod_annual_value_m Float64, optimal_release_strategy String, hybrid_roi_score Float64) ENGINE = MergeTree() ORDER BY (title);")

            # 3. Clean and Insert
            for t in ["box_office_daily", "streaming_telemetry", "scene_retention_metrics", "audience_sentiment", "frame_script_alignment", "visual_cognition_stream", "perceptual_pacing_telemetry", "theatrical_svod_elasticity"]:
                self.client.command(f"TRUNCATE TABLE IF EXISTS {t}")

            self.client.insert_df("box_office_daily", generate_box_office_data(days=30))
            self.client.insert_df("streaming_telemetry", generate_streaming_telemetry(num_sessions=3500))
            self.client.insert_df("scene_retention_metrics", generate_scene_retention_data())
            self.client.insert_df("audience_sentiment", generate_audience_sentiment(num_reviews=1000))
            
            self.client.insert_df("frame_script_alignment", generate_frame_script_alignment())
            self.client.insert_df("visual_cognition_stream", generate_visual_cognition_stream())
            self.client.insert_df("perceptual_pacing_telemetry", generate_perceptual_pacing_telemetry())
            self.client.insert_df("theatrical_svod_elasticity", generate_theatrical_svod_elasticity())
            
            return {"status": "success", "message": "Successfully seeded ClickHouse Cloud with all 8 cinematic engines!"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def execute_query(self, sql_query: str):
        """Executes analytical SQL query and returns results and execution time in ms."""
        start_time = time.perf_counter()
        try:
            clean_sql = sql_query.strip().rstrip(";")
            if self.mode == "clickhouse" and self.client:
                result = self.client.query_df(clean_sql)
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return {"success": True, "data": result, "execution_time_ms": duration_ms, "row_count": len(result), "engine": "ClickHouse Cloud", "error": None}
            else:
                result = self.duck_conn.execute(clean_sql).fetchdf()
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return {"success": True, "data": result, "execution_time_ms": duration_ms, "row_count": len(result), "engine": "ClickHouse Compatible Engine", "error": None}
        except Exception as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {"success": False, "data": pd.DataFrame(), "execution_time_ms": duration_ms, "row_count": 0, "engine": self.mode, "error": str(e)}

    def get_schema_summary(self) -> str:
        return """
DATABASE SCHEMAS (CinePulse Studio Operating System):
1. box_office_daily: (title, report_date, day_number, region, country, daily_gross_usd, screen_count, avg_ticket_price, marketing_spend_usd, audience_rating_pct)
2. streaming_telemetry: (session_id, user_id, title, episode, session_timestamp, watch_duration_sec, completion_pct, buffer_events, bitrate_kbps, quality_tier, device_type, region, drop_off_timestamp_sec, user_rating)
3. scene_retention_metrics: (title, episode, scene_id, minute_mark, scene_type, character_focus, pacing_score, emotional_tone, churn_risk_score, viewer_drop_count)
4. audience_sentiment: (review_id, title, platform, region, sentiment_score, sentiment_label, comment_text, review_timestamp)
5. frame_script_alignment: (title, timeline_sec, timeline_min, shot_type, narrative_theme, dialogue_density_wpm, viewer_drop_count, retention_pct)
6. visual_cognition_stream: (title, timeline_sec, luminance_nits, contrast_ratio, color_entropy, active_face_count, mobile_churn_risk)
7. perceptual_pacing_telemetry: (title, minute_window, cuts_per_minute, audio_db_variance, cdn_buffer_rate_pct, bitrate_drop_flag, pacing_stress_index)
8. theatrical_svod_elasticity: (title, budget_m, projected_theatrical_gross_m, theatrical_net_profit_m, projected_svod_subs_gained_k, svod_annual_value_m, optimal_release_strategy, hybrid_roi_score)
"""

db_manager = ClickHouseManager()
