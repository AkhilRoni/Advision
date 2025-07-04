# ad_manager.py
import sqlite3
from constants import DEFAULT_AD_PATH
from datetime import datetime
import random
from PyQt5.QtCore import Qt, QTimer
import os

DATABASE = "C:/Users/akhil/Desktop/#ADVISION_Integration_1/ads_database2.db"

def get_ad_path(age_group, gender, priority):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''SELECT ad_id,file_path FROM ads 
                      WHERE gender = ? AND age_group = ? AND priority = ? 
                      LIMIT 1''', 
                   (gender, age_group, priority))
    
    
    
    result = cursor.fetchone()
    conn.close()

    print("These are ads found:  "+ str(result))
    print("Exists:", os.path.exists(result[1]))

    
    if result:
        return result  # Return the ad file path
        
    else:
        print(f"No matching ad found for priority {priority}, using default.")
        
        file_path = get_general_ad()  # Fallback default ad path
        return [0,file_path]


def get_general_ad():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''SELECT ad_id,file_path FROM ads 
                      WHERE gender = "General" AND age_group = "General"
                      ''', 
                   )
    
    rows = cursor.fetchall()
    conn.close()

    result = random.choice(rows)
    file_path = result[1]
    print("Ad selected is Ad number: ",result[0])
    return file_path

    
def get_next_ad_path(age_group, gender, current_priority):
    # Cycle through priorities 1 → 2 → 3, then reset to default
    if current_priority < 3:
        next_priority = current_priority + 1
        return get_ad_path(age_group, gender, next_priority)

    else:
        return get_general_ad
    
def log_played_ad(mainwindow_instance,ad_id,age_group,gender,initial_mood,ad_priority):

    if ad_priority == 1:
        initial_mood = None
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    timestamp =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO ad_log(timestamp,ad_id,age_group,gender,initial_mood,final_mood,switched_ad) VALUES (?,?,?,?,?,?,?) 
        ''', (timestamp,ad_id,age_group,gender,initial_mood,None,False))
    
    
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    mainwindow_instance.current_log_id = log_id
    print("Log ID:",mainwindow_instance.current_log_id)

def update_log_fin(ad_priority,mainwindow_instance,final_mood = None,switched_ad = False):

    if mainwindow_instance.current_log_id is None:
        print("⚠️ No active log ID to update!")
        return 
    
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        timestamp =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            UPDATE ad_log SET final_mood = ? , switched_ad = ? WHERE log_id = ?
            ''', (final_mood,switched_ad,mainwindow_instance.current_log_id))
        conn.commit()
        conn.close()
        print("✅ Log updated successfully!")

    except Exception as e:
        print(f"🚨 Error updating log: {e}")

    mainwindow_instance.current_log_id = None


def get_all_general_ads():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''SELECT file_path FROM ads WHERE gender = "General" AND age_group = "General"''')
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]  # Return a list of all general ad paths


def bin_age_to_group(age):
    if age < 18:
        return "0-17"
    elif age < 31:  # Increased the upper limit to avoid misclassification
        return "18-30"
    elif age < 51:
        return "31-50"
    elif age < 71:
        return "51-70"
    else:
        return "70+"