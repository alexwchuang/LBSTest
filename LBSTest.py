# Alexander Chuang
# Live Building Systems Coding Challenge 1

from flask import Flask, render_template, url_for
import sqlite3
import json
from datetime import datetime


# Helper function due to threading restrictions on sqlite
def get_db_conn():
    conn = sqlite3.connect("LBSTestDB")
    cur = conn.cursor()
    return conn, cur

# Consumes an iterable of iterables and flattens the interior structure.
def flatten(iterable):
    if len(iterable) == 0:
        return []
    if len(iterable) == 1:
        return iterable[0]
    return iterable[0] + flatten(iterable[1:])


# Flask / SQLite setup
app = Flask("LBSTest")
conn, cur = get_db_conn()

# Basic data
meters = [
    (0, 'Meter Alpha'),
    (1, 'Meter Beta'),
    (2, 'Meter Gamma'),
    (3, 'Meter Delta'),  # no information about Meter Delta will be in the data
]

meter_data = [
    (0, 1, datetime.fromisoformat("2023-06-23 12:10:00-04:00"), 90),
    (1, 2, datetime.fromisoformat("2023-06-23 12:10:00-04:00"), 105),
    (2, 0, datetime.fromisoformat("2023-06-23 12:10:00-04:00"), 100),
    (3, 2, datetime.fromisoformat("2023-06-23 12:20:00-04:00"), 150),
    (4, 0, datetime.fromisoformat("2023-06-23 12:20:00-04:00"), 140),
    (5, 1, datetime.fromisoformat("2023-06-23 12:20:00-04:00"), 125),
    (6, 2, datetime.fromisoformat("2023-06-23 12:30:00-04:00"), 170),
    (7, 0, datetime.fromisoformat("2023-06-23 12:30:00-04:00"), 135),
]

# Create the tables. For the purposes of this test, we will only create/insert the test data if the tables don't already exist.
result = cur.execute("SELECT name FROM sqlite_master")
all_tables = flatten(result.fetchall())
if "meters" not in all_tables:
    cur.execute("CREATE TABLE meters(id, label)")
    cur.executemany("INSERT INTO meters VALUES(?, ?)", meters)
    conn.commit()
if "meter_data" not in all_tables:
    cur.execute("CREATE TABLE meter_data(id, meter_id, timestamp, value)")
    cur.executemany("INSERT INTO meter_data VALUES(?, ?, ?, ?)", meter_data)
    conn.commit()
cur.close()

# Set up routes
@app.route("/meters/")
def meters():
    conn, cur = get_db_conn()
    res = cur.execute("SELECT id, label FROM meters")
    data = res.fetchall()
    return render_template("meters.html", meter_data=data)

@app.route("/meters/<int:meter_id>")
def meter_data(meter_id: int):
    conn, cur = get_db_conn()
    res = cur.execute(f"SELECT * FROM meter_data WHERE meter_id={meter_id}")
    data = res.fetchall()
    data.sort(key=lambda x: x[2])
    return json.dumps(data)

# eof
