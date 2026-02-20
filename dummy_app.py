import sqlite3

def get_user_data(user_id):
    # EXTREM UNSICHER: Direkte String-Verkettung in SQL!
    query = "SELECT * FROM users WHERE id = " + user_id
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    
    return cursor.fetchall()