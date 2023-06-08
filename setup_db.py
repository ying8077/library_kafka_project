import sqlite3
import csv

with open('./books.csv', newline='', encoding="utf-8") as f:
    csv_reader = csv.DictReader(f) 
    books = [
        (row['ISBN'], row['書名'], row['作者'], row['分類'], row['版次'], row['出版社'], row['圖片'], row['簡介'])
        for row in csv_reader
        ]

with open('create_db.sql', encoding="utf-8") as f:  
    create_db_sql = f.read()

db = sqlite3.connect('books.db')
with db:
    db.executescript(create_db_sql)
    db.executemany(
        'INSERT INTO books(ISBN, title, author, category, version, publisher, img, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        books
    )
print ("\n")
print ("books table created successfully")

db = sqlite3.connect('readers.db')
with db:
    db.executescript(create_db_sql)
    data = ()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO readers(rname, ssn, address, mail, phone, password) VALUES ("kevin","b122456731","台北市文山區指南路二段64號","nccu2022@gmail.com","0935641297","1234")'
    )
print ("readers table created successfully")

db = sqlite3.connect('staffs.db')
with db:
    db.executescript(create_db_sql)
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO staffs(sname, empid, password) VALUES ("Lisa","123", "123")'
    )
print ("staffs table created successfully")

db = sqlite3.connect('reports.db')
with db:
    db.executescript(create_db_sql)
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO reports(User_id, book_no, title, issue, return_date) VALUES ("b122456731","9786267252246","沈錳坤 資料庫聖經","2023-06-01 10:00:00","2023-07-01 10:00:00")'
    )
print ("reports table created successfully")

db = sqlite3.connect('recommends.db')
with db:
    db.executescript(create_db_sql)
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO recommends(ISBN, title, author, category, version) VALUES ("9786878752246","資料庫聖經","沈錳坤","教科書","初版")'
    )
print ("recommends table created successfully")

db = sqlite3.connect('publishers.db')
with db:
    db.executescript(create_db_sql)
    cursor = db.cursor()
    con = sqlite3.connect("books.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT DISTINCT publisher FROM books")
    publishers = cur.fetchall()
    con.close()

    publisher_names = [publisher['publisher'] for publisher in publishers]
    cursor.executemany(
    'INSERT INTO  publishers(pname) VALUES (?)',
    [(name,) for name in publisher_names]
)
print ("publishers table created successfully")