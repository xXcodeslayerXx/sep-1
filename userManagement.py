import sqlite3 as sql
import bcrypt


def get_connection():
    conn = sql.connect("databaseFiles/database.db")
    return conn
# --- User functions ---
def create_user(username, password):
    # Insert a new user into the database
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def get_user(username, password):
    # Look up a user by username + password (login check)
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()   # fetch one matching row
    conn.close()
    return user  # returns tuple like (id, username, password) or None

def get_username_by_id(user_id):
    # Get username by user ID
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else f"User {user_id}"


# --- Subject functions ---

# Fetch all study records (for dashboard)
def get_study_records():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM study")
    rows = c.fetchall()
    result = [dict(zip([column[0] for column in c.description], row)) for row in rows]
    conn.close()
    return result

def add_subject(user_id, subject, weekly_goal=0):
    # Add a new subject for the logged-in user
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO subjects (user_id, subject, weekly_goal)
        VALUES (?, ?, ?)
    ''', (user_id, subject, weekly_goal))
    conn.commit()
    conn.close()

def update_study_time(subject_id, minutes):
    # Add study minutes to the total for a subject
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE subjects SET total_study_time = total_study_time + ? WHERE id=?", (minutes, subject_id))
    conn.commit()
    conn.close()


def save_study_session(user_id, subject, time_spent_seconds, start_time, end_time):
    # Save a study session to the study table
    conn = get_connection()
    c = conn.cursor()
    
    # Convert seconds to minutes for storage (round to 2 decimal places)
    time_spent_minutes = round(time_spent_seconds / 60, 2)
    
    print(f"Saving study session: {subject}, {time_spent_seconds}s = {time_spent_minutes}m")
    
    c.execute('''
        INSERT INTO study (user_id, Subject, TimeAndDate, OvrTime)
        VALUES (?, ?, ?, ?)
    ''', (user_id, subject, start_time, time_spent_minutes))
    
    conn.commit()
    conn.close()
    return True

def get_user_study_summary(user_id):
    # Get study summary for a specific user, grouped by subject
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            Subject,
            COUNT(*) as session_count,
            SUM(OvrTime) as total_time_minutes,
            AVG(OvrTime) as avg_time_minutes,
            MAX(TimeAndDate) as last_study_date
        FROM study 
        WHERE user_id = ?
        GROUP BY Subject
        ORDER BY total_time_minutes DESC
    ''', (user_id,))
    
    rows = c.fetchall()
    result = []
    for row in rows:
        result.append({
            'subject': row[0],
            'session_count': row[1],
            'total_time_minutes': round(row[2], 2) if row[2] else 0,
            'avg_time_minutes': round(row[3], 2) if row[3] else 0,
            'last_study_date': row[4]
        })
    
    conn.close()
    return result

def get_all_users_study_summary():
    # Get study summary for all users, grouped by user and subject
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            user_id,
            Subject,
            COUNT(*) as session_count,
            SUM(OvrTime) as total_time_minutes,
            AVG(OvrTime) as avg_time_minutes,
            MAX(TimeAndDate) as last_study_date
        FROM study 
        GROUP BY user_id, Subject
        ORDER BY user_id, total_time_minutes DESC
    ''')
    
    rows = c.fetchall()
    result = {}
    for row in rows:
        user_id = row[0]
        if user_id not in result:
            result[user_id] = []
        
        result[user_id].append({
            'subject': row[1],
            'session_count': row[2],
            'total_time_minutes': round(row[3], 2) if row[3] else 0,
            'avg_time_minutes': round(row[4], 2) if row[4] else 0,
            'last_study_date': row[5]
        })
    
    conn.close()
    return result