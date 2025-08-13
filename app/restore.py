import sqlite3

conn = sqlite3.connect('db.sqlite3')

with open('backup.sql', 'r', encoding='utf-8') as f:
    conn.executescript(f.read())

conn.close()
print("Дамп успешно загружен!")