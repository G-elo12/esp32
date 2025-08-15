import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('greenhouse.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sensor_data (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 humidity1 REAL,
                 humidity2 REAL,
                 humidity3 REAL,
                 humidity4 REAL,
                 temperature REAL,
                 timestamp TEXT
                 )''')
    conn.commit()
    conn.close()

def save_sensor_data(humidity1, humidity2, humidity3, humidity4, temperature):
    conn = sqlite3.connect('greenhouse.db')
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute('''INSERT INTO sensor_data (humidity1, humidity2, humidity3, humidity4, temperature, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (humidity1, humidity2, humidity3, humidity4, temperature, timestamp))
    conn.commit()
    conn.close()

def get_recent_data(limit=10):
    conn = sqlite3.connect('greenhouse.db')
    c = conn.cursor()
    c.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return [{
        'id': row[0],
        'humidity1': row[1],
        'humidity2': row[2],
        'humidity3': row[3],
        'humidity4': row[4],
        'temperature': row[5],
        'timestamp': row[6]
    } for row in rows]