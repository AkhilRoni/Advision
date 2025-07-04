from fastapi import FastAPI, File, UploadFile, Form, Query, HTTPException
from collections import defaultdict

from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import shutil
import sqlite3
import urllib.parse


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "C:/Users/akhil/Desktop/#ADVISION_Integration_1/Advision_App/ads"
DATABASE = "C:/Users/akhil/Desktop/#ADVISION_Integration_1/ads_database2.db"
 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  

# Upload an ad
@app.post("/upload-ad")
async def upload_ad(
    ad_name: str = Form(...),
    ad_video: UploadFile = File(...),
    ad_gender: str = Form(...),
    ad_age: str = Form(...),
):
    video_path = os.path.join(UPLOAD_FOLDER, f"{ad_name}.mp4")

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(ad_video.file, buffer)

    conn = sqlite3.connect(DATABASE)  
    cursor = conn.cursor()

    # Get the next available priority for this age_group and gender
    cursor.execute(
        "SELECT COALESCE(MAX(priority), 0) + 1 FROM ads WHERE age_group = ? AND gender = ?",
        (ad_age, ad_gender),
    )
    next_priority = cursor.fetchone()[0]

    # Insert new ad with correct priority
    file_path = "ads/"+f"{ad_name}.mp4"
    cursor.execute(
        """
        INSERT INTO ads (ad_name, age_group, gender, priority, file_path) 
        VALUES (?, ?, ?, ?, ?)
        """,
        (ad_name, ad_age, ad_gender, next_priority, file_path),
    )
    conn.commit()
    conn.close()

    return {
        "message": "Ad Uploaded Successfully!",
        "file_path": video_path,
        "priority": next_priority,
    }


# 🚀 Get ads from the database
@app.get("/get-ads")
async def get_ads(age_group: str = Query(None), gender: str = Query(None)):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if age_group:
        age_group = urllib.parse.unquote(age_group).strip()  # Decode & remove extra spaces
        print(f"✅ Received Age Group: '{age_group}'")  # Debugging

    query = "SELECT ad_id, ad_name, age_group, gender, file_path FROM ads WHERE 1=1"
    params = []

    if age_group:
        query += " AND age_group LIKE ?"
        params.append(age_group)

    if gender:
        query += " AND gender = ?"
        params.append(gender)

    print(f"🔍 Executing Query: {query} with Params: {params}")
    cursor.execute(query, params)
    ads = cursor.fetchall()
    conn.close()

    ads_json = [
        {
            "ad_id": ad[0],
            "ad_name": ad[1],
            "age_group": ad[2],
            "gender": ad[3],
            "file_path": ad[4],
        }
        for ad in ads
    ]

    return {"ads": ads_json}


"""# 🚀 Delete an ad
@app.delete("/delete-ad/{ad_id}")
async def delete_ad(ad_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT video_path FROM ads WHERE ad_id = ?", (ad_id,))
    ad = cursor.fetchone()

    if not ad:
        conn.close()
        raise HTTPException(status_code=404, detail="Ad not found")

    video_path = ad[0]
    if os.path.exists(video_path):
        os.remove(video_path)

    cursor.execute("DELETE FROM ads WHERE ad_id = ?", (ad_id,))
    conn.commit()
    conn.close()

    return {"message": f"Ad {ad_id} deleted successfully"}
"""
@app.delete("/delete-ad/{ad_id}")
async def delete_ad(ad_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch video path, priority, age group, and gender of the ad to be deleted
    cursor.execute("SELECT file_path, priority, age_group, gender FROM ads WHERE ad_id = ?", (ad_id,))
    ad = cursor.fetchone()

    if not ad:
        conn.close()
        raise HTTPException(status_code=404, detail="Ad not found")

    video_path, deleted_priority, age_group, gender = ad  

    # Delete the video file
    if os.path.exists(video_path):
        os.remove(video_path)

    # Delete the ad from the database
    cursor.execute("DELETE FROM ads WHERE ad_id = ?", (ad_id,))

    # Update priorities only for the same age group & gender
    cursor.execute(
        "UPDATE ads SET priority = priority - 1 WHERE priority > ? AND age_group = ? AND gender = ?",
        (deleted_priority, age_group, gender)
    )

    conn.commit()
    conn.close()

    return {"message": f"Ad {ad_id} deleted successfully, and priorities adjusted"}

# 🚀 Get ad logs from the database
@app.get("/get-logs")
async def get_logs():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT log_id, timestamp, ad_id, age_group, gender, initial_mood, final_mood, switched_ad FROM ad_log")
    logs = cursor.fetchall()
    conn.close()

    logs_json = [
        {
            "log_id": log[0],
            "timestamp": log[1],
            "ad_id": log[2],
            "age_group": log[3],
            "gender": log[4],
            
            "final_mood": log[6] if log[6] is not None else "N/A",
            "switched_ad": "Yes" if log[7] == 1 else "No",
        }
        for log in logs
    ]

    return {"logs": logs_json}


# 🚀 Get interactions by age group
@app.get("/analytics/age-group")
async def get_age_group_interactions():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT age_group, COUNT(*) 
        FROM ad_log 
        GROUP BY age_group
    """)
    
    data = cursor.fetchall()
    conn.close()

    return {"age_group_interactions": {row[0]: row[1] for row in data}}


# 🚀 Get interactions by gender
@app.get("/analytics/gender")
async def get_gender_interactions():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT gender, COUNT(*) 
        FROM ad_log
        GROUP BY gender
    """)
    
    data = cursor.fetchall()
    conn.close()

    return {"gender_interactions": {row[0]: row[1] for row in data}}


# 🚀 Get most rejected ads
@app.get("/analytics/rejected-ads")
async def get_rejected_ads():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch rejected ads
    cursor.execute("""
        SELECT ads.ad_name, ads.age_group, COUNT(*) 
        FROM ad_log 
        JOIN ads ON ad_log.ad_id = ads.ad_id
        WHERE ad_log.final_mood IN ('angry', 'sad')
        GROUP BY ad_log.ad_id
    """)
    
    rejected_ads = cursor.fetchall()

    conn.close()

    print("✅ REJECTED ADS DATA:", rejected_ads)  # ✅ PRINTING FOR DEBUGGING

    return {"rejected_ads": [{"ad_name": row[0], "age_group": row[1], "rejections": row[2]} for row in rejected_ads]}


# 🚀 Get most liked ads (ads that changed mood from angry/sad → happy)
@app.get("/analytics/liked-ads")
async def get_liked_ads():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch all ads where final mood was "happy"
    cursor.execute("""
        SELECT ads.ad_name, ads.age_group, COUNT(ad_log.log_id) 
        FROM ad_log
        JOIN ads ON ad_log.ad_id = ads.ad_id
        WHERE ad_log.final_mood = 'happy'
        GROUP BY ads.ad_name, ads.age_group
        ORDER BY COUNT(ad_log.log_id) DESC;
    """)

    liked_ads = cursor.fetchall()
    conn.close()

    # Convert data into JSON format
    liked_ads_json = [
        {"ad_name": ad[0], "age_group": ad[1], "likes": ad[2]} for ad in liked_ads
    ]

    return {"liked_ads": liked_ads_json}



@app.get("/analytics/time-distribution")
async def get_time_distribution():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Query to count interactions per hour
    cursor.execute("""
        SELECT strftime('%H', timestamp) AS hour, COUNT(*) 
        FROM ad_log 
        GROUP BY hour 
        ORDER BY hour
    """)
    results = cursor.fetchall()
    conn.close()

    # Convert to dictionary { "00": count, "01": count, ... }
    time_distribution = defaultdict(int)
    for hour, count in results:
        time_distribution[int(hour)] = count  # Convert '00' -> 0, '01' -> 1, etc.

    return {"time_distribution": time_distribution}

# 🚀 Get most frequent age groups
@app.get("/analytics/frequent-age-groups")
async def get_frequent_age_groups():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT age_group, COUNT(*) FROM ad_log GROUP BY age_group ")
    age_groups = cursor.fetchall()
    conn.close()

    age_group_data = {age_group: count for age_group, count in age_groups}

    return {"frequent_age_groups": age_group_data}

@app.get("/analytics/ad-switch-ratio")
async def get_ad_switch_ratio():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            SUM(CASE WHEN switched_ad = 1 THEN 1 ELSE 0 END) AS switched,
            SUM(CASE WHEN switched_ad = 0 THEN 1 ELSE 0 END) AS not_switched
        FROM ad_log
    """)
    
    result = cursor.fetchone()
    conn.close()

    return {"switched": result[0] or 0, "not_switched": result[1] or 0}

@app.get("/analytics/mood-trend")
async def get_mood_trend():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Get mood counts for each hour
    cursor.execute("""
        SELECT CAST(strftime('%H', timestamp) AS INTEGER) as hour, 
               SUM(CASE WHEN final_mood = 'happy' THEN 1 ELSE 0 END) AS happy,
               SUM(CASE WHEN final_mood = 'angry' THEN 1 ELSE 0 END) AS angry,
               SUM(CASE WHEN final_mood = 'sad' THEN 1 ELSE 0 END) AS sad
        FROM ad_log
        GROUP BY hour
        ORDER BY hour ASC
    """)

    results = cursor.fetchall()
    conn.close()

    # Ensure all 24 hours exist, even if they're 0
    full_hours = {hour: {"happy": 0, "angry": 0, "sad": 0} for hour in range(24)}

    # Fill in actual data
    for row in results:
        full_hours[row[0]] = {"happy": row[1], "angry": row[2], "sad": row[3]}

    return {
        "hours": list(full_hours.keys()),  
        "happy": [full_hours[h]["happy"] for h in full_hours],  
        "angry": [full_hours[h]["angry"] for h in full_hours],  
        "sad": [full_hours[h]["sad"] for h in full_hours]  
    }


@app.get("/dashboard-stats")
async def get_dashboard_stats():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Total ads count
    cursor.execute("SELECT COUNT(*) FROM ads")
    total_ads = cursor.fetchone()[0]

    # Total impressions (log entries count)
    cursor.execute("SELECT COUNT(*) FROM ad_log")
    total_impressions = cursor.fetchone()[0]

    # Switched ads count
    cursor.execute("SELECT COUNT(*) FROM ad_log WHERE switched_ad = 1")
    switched_ads = cursor.fetchone()[0]

    # Most played ad (ad with highest occurrences in logs)
    cursor.execute("""
        SELECT ads.ad_name, ads.age_group, COUNT(ad_log.ad_id) as play_count
        FROM ad_log 
        JOIN ads ON ad_log.ad_id = ads.ad_id
        GROUP BY ad_log.ad_id
        ORDER BY play_count DESC
        LIMIT 1
    """)
    most_played_ad = cursor.fetchone()

    conn.close()

    return {
        "total_ads": total_ads,
        "total_impressions": total_impressions,
        "switched_ads": switched_ads,
        "most_played_ad": f"{most_played_ad[0]} ({most_played_ad[1]})" if most_played_ad else "N/A"
    }



# 🚀 Get all ads from the database (for ads table)
@app.get("/get-all-ads")
async def get_all_ads():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT ad_id, ad_name, age_group, gender, priority, file_path FROM ads")
    ads = cursor.fetchall()
    conn.close()

    ads_json = [
        {
            "ad_id": ad[0],
            "ad_name": ad[1],
            "age_group": ad[2],
            "gender": ad[3],
            "priority": ad[4],
            "file_path": ad[5],
        }
        for ad in ads
    ]

    return {"ads": ads_json}
