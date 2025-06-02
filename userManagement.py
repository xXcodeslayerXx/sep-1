import sqlite3 as sql
import bcrypt


### example
def getUsers():
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM id7-tusers")
    con.close()
    return cur

def savelog(subject, topic, TimeSpent, Today):
    con = sql.connect("databaseFiles/database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO study (Subject, Topic, TimeSpent, TimeAndDate) VALUES (?, ?, ?, ?)", 
                ('English', 'Reading', TimeSpent, Today),
                )
    con.commit()
    con.close()