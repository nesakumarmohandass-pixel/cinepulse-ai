"""
Seed dataset generator for CinePulse AI.
Generates realistic cinematic box office, streaming telemetry, scene retention, and audience sentiment data.
"""

import random
from datetime import datetime, timedelta
import pandas as pd

TITLES = [
    {"title": "CyberBlade 2099", "genre": "Sci-Fi / Action", "runtime_min": 138, "budget_m": 165, "episodes": 1},
    {"title": "The Shadow Protocol", "genre": "Spy Thriller", "runtime_min": 55, "budget_m": 80, "episodes": 8},
    {"title": "Neon Horizons: Season 2", "genre": "Cyberpunk Drama", "runtime_min": 48, "budget_m": 95, "episodes": 10},
    {"title": "Kingdom of Sand", "genre": "Historical Epic", "runtime_min": 162, "budget_m": 210, "episodes": 1},
    {"title": "Starlight Odyssey", "genre": "Space Opera", "runtime_min": 60, "budget_m": 120, "episodes": 6}
]

REGIONS = {
    "North America": ["USA", "Canada"],
    "Europe": ["UK", "Germany", "France", "Spain", "Italy"],
    "Asia-Pacific": ["Japan", "South Korea", "Australia", "India"],
    "Latin America": ["Brazil", "Mexico", "Argentina"]
}

DEVICES = ["Smart TV (4K)", "Mobile (iOS)", "Mobile (Android)", "Web Browser", "Tablet", "Gaming Console"]
PLATFORMS = ["X (Twitter)", "Reddit", "Letterboxd", "Rotten Tomatoes", "IMDb", "TikTok"]

def generate_box_office_data(days=30):
    records = []
    base_date = datetime.now() - timedelta(days=days)
    
    for movie in [t for t in TITLES if t["episodes"] == 1]:
        title = movie["title"]
        base_gross = movie["budget_m"] * 1_000_000 * 0.28  # Opening day gross target
        
        for d in range(1, days + 1):
            date_val = base_date + timedelta(days=d)
            # Weekend boost multiplier
            day_of_week = date_val.weekday()
            weekend_boost = 2.4 if day_of_week in [4, 5, 6] else 0.85
            # Decay curve over weeks
            decay = max(0.08, (1.0 / (1.0 + (d * 0.09))))
            
            for region, countries in REGIONS.items():
                reg_weight = 0.45 if region == "North America" else (0.28 if region == "Europe" else 0.20)
                for country in countries:
                    daily_gross = round(base_gross * decay * weekend_boost * reg_weight * random.uniform(0.85, 1.18), 2)
                    screens = random.randint(800, 4200) if region == "North America" else random.randint(250, 1800)
                    ticket_price = round(random.uniform(11.50, 17.50), 2) if region == "North America" else round(random.uniform(8.0, 14.0), 2)
                    marketing = round(daily_gross * random.uniform(0.08, 0.22), 2)
                    rating = round(random.uniform(74.0, 92.0) - (d * 0.15), 1)
                    
                    records.append({
                        "title": title,
                        "report_date": date_val.strftime("%Y-%m-%d"),
                        "day_number": d,
                        "region": region,
                        "country": country,
                        "daily_gross_usd": daily_gross,
                        "screen_count": screens,
                        "avg_ticket_price": ticket_price,
                        "marketing_spend_usd": marketing,
                        "audience_rating_pct": max(50.0, rating)
                    })
    return pd.DataFrame(records)

def generate_streaming_telemetry(num_sessions=2500):
    records = []
    now = datetime.now()
    
    for i in range(1, num_sessions + 1):
        show = random.choice(TITLES)
        title = show["title"]
        episode = random.randint(1, show["episodes"])
        runtime_sec = show["runtime_min"] * 60
        
        region = random.choice(list(REGIONS.keys()))
        device = random.choice(DEVICES)
        
        # Simulate realistic drop-off behavior (higher drop-offs in early minutes if slow, or middle climax)
        completion_type = random.choices(["full", "drop_early", "drop_mid", "drop_late"], weights=[0.62, 0.14, 0.16, 0.08])[0]
        
        if completion_type == "full":
            completion_pct = round(random.uniform(94.0, 100.0), 1)
            watch_duration = runtime_sec
            drop_off_sec = 0
            rating = random.randint(4, 5)
        elif completion_type == "drop_early":
            completion_pct = round(random.uniform(8.0, 22.0), 1)
            drop_off_sec = int(runtime_sec * (completion_pct / 100.0))
            watch_duration = drop_off_sec
            rating = random.randint(1, 3)
        elif completion_type == "drop_mid":
            completion_pct = round(random.uniform(35.0, 60.0), 1)
            drop_off_sec = int(runtime_sec * (completion_pct / 100.0))
            watch_duration = drop_off_sec
            rating = random.randint(2, 4)
        else:
            completion_pct = round(random.uniform(70.0, 88.0), 1)
            drop_off_sec = int(runtime_sec * (completion_pct / 100.0))
            watch_duration = drop_off_sec
            rating = random.randint(3, 5)
            
        buffer_events = random.choices([0, 1, 2, 3, 5], weights=[0.82, 0.11, 0.04, 0.02, 0.01])[0]
        bitrate = random.choice([3500, 6000, 11000, 18000, 24000]) if "4K" in device else random.choice([2500, 4500, 8000])
        quality = "4K HDR" if bitrate >= 18000 else ("1080p HD" if bitrate >= 6000 else "720p")
        
        time_offset = random.randint(0, 14 * 24 * 3600)
        sess_time = now - timedelta(seconds=time_offset)
        
        records.append({
            "session_id": f"sess_{100000 + i}",
            "user_id": f"usr_{random.randint(1000, 9999)}",
            "title": title,
            "episode": episode,
            "session_timestamp": sess_time.strftime("%Y-%m-%d %H:%M:%S"),
            "watch_duration_sec": watch_duration,
            "completion_pct": completion_pct,
            "buffer_events": buffer_events,
            "bitrate_kbps": bitrate,
            "quality_tier": quality,
            "device_type": device,
            "region": region,
            "drop_off_timestamp_sec": drop_off_sec,
            "user_rating": rating
        })
    return pd.DataFrame(records)

def generate_scene_retention_data():
    records = []
    
    for show in TITLES:
        title = show["title"]
        runtime_min = show["runtime_min"]
        scenes_count = max(5, runtime_min // 8)
        
        scene_types = ["Action Sequence", "Dialogue / Character Drama", "Plot Exposition", "Climax / Twist", "Montage / Transition", "Slow Pacing Background"]
        characters = ["Protagonist (Alex)", "Antagonist (Vane)", "Ensemble Crew", "Supporting Mentor", "Solo Monologue"]
        
        for sc in range(1, scenes_count + 1):
            minute_start = (sc - 1) * 8
            scene_type = random.choice(scene_types)
            pacing = round(random.uniform(4.5, 9.8), 1)
            
            # Slow exposition has higher churn risk
            if "Exposition" in scene_type or "Slow" in scene_type:
                churn_score = round(random.uniform(0.45, 0.88), 2)
                drops = random.randint(120, 680)
            elif "Action" in scene_type or "Climax" in scene_type:
                churn_score = round(random.uniform(0.04, 0.22), 2)
                drops = random.randint(15, 90)
            else:
                churn_score = round(random.uniform(0.18, 0.42), 2)
                drops = random.randint(45, 210)
                
            records.append({
                "title": title,
                "episode": 1,
                "scene_id": f"SC_{sc:02d}",
                "minute_mark": minute_start,
                "scene_type": scene_type,
                "character_focus": random.choice(characters),
                "pacing_score": pacing,
                "emotional_tone": random.choice(["Tense", "Excited", "Melancholy", "Inspiring", "Intriguing", "Monotonous"]),
                "churn_risk_score": churn_score,
                "viewer_drop_count": drops
            })
    return pd.DataFrame(records)

def generate_audience_sentiment(num_reviews=800):
    records = []
    now = datetime.now()
    
    positive_snippets = [
        "Incredible visual effects and pacing! Best release of the year.",
        "The sound design and musical score blew me away in IMAX.",
        "Loved the character arc in the second half. Top tier writing.",
        "Stunning cinematography, will definitely rewatch this weekend."
    ]
    
    negative_snippets = [
        "First 30 minutes dragged way too slow, almost turned it off.",
        "CGI felt unfinished in the third act battle scene.",
        "Pacing issues in episode 3 ruined the momentum.",
        "Audio mixing was terrible—dialogue was muffled under the loud soundtrack."
    ]
    
    for i in range(1, num_reviews + 1):
        show = random.choice(TITLES)
        sentiment_type = random.choices(["positive", "negative", "neutral"], weights=[0.60, 0.28, 0.12])[0]
        
        if sentiment_type == "positive":
            score = round(random.uniform(0.65, 0.98), 2)
            label = "Positive"
            comment = random.choice(positive_snippets)
        elif sentiment_type == "negative":
            score = round(random.uniform(-0.95, -0.40), 2)
            label = "Negative"
            comment = random.choice(negative_snippets)
        else:
            score = round(random.uniform(-0.20, 0.35), 2)
            label = "Neutral"
            comment = "Solid entertainment, decent performances but somewhat predictable."
            
        region = random.choice(list(REGIONS.keys()))
        platform = random.choice(PLATFORMS)
        review_time = now - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23))
        
        records.append({
            "review_id": f"rev_{50000 + i}",
            "title": show["title"],
            "platform": platform,
            "region": region,
            "sentiment_score": score,
            "sentiment_label": label,
            "comment_text": comment,
            "review_timestamp": review_time.strftime("%Y-%m-%d %H:%M:%S")
        })
    return pd.DataFrame(records)
