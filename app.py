from flask import Flask, render_template, request, redirect, session
from kafka import KafkaProducer
import sqlite3 as sql
import datetime

app = Flask(__name__)
app.secret_key = 'nccugogo'

@app.route('/')
def home():
    return render_template('home.html')

def write_event(topic, msg):
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    producer.send(topic, msg.encode())
    producer.close()

# 建立kafka主題：登入事件
def send_login_event(ssn, name):
    topic = 'login_events'
    message = f'{{"user_ssn": "{ssn}", "user_name": "{name}", "behavior": "log in"}}'
    write_event(topic, message)

def send_logout_event(ssn, name):
    topic = 'logout_events'
    message = f'{{"user_ssn": "{ssn}", "user_name": "{name}", "behavior": "log out"}}'
    write_event(topic, message)

# 建立kafka主題："搜尋書本"事件
def send_search_history(book_name):
    topic = 'search_history'
    message = f'search：{book_name}'
    write_event(topic, message) 

# 讀者登入，每次登入就記錄到topic(kafka log)   
@app.route('/r_signin',methods = ['POST'])
def r_signin():
  con = sql.connect("readers.db")
  con.row_factory = sql.Row
  cur = con.cursor()
  rname=request.form["rname"]
  rpassword=request.form["password"]
  cur.execute("SELECT * FROM readers WHERE rname=? and password=?", (rname, rpassword))
  people = cur.fetchall()
  if len(people) == 0:
      return redirect("/result?msg=帳號或密碼錯誤")
  cur.execute("SELECT ssn FROM readers WHERE rname=? and password=?", (rname, rpassword,))
  ssn = cur.fetchone()[0]
  session["reader"] = rname
  session["ssn"] = ssn
  send_login_event(ssn, rname)
  return redirect("/r_member")

# 讀者註冊
@app.route('/new_reader')
def new_reader():
    return render_template('new_reader.html')

@app.route('/r_signup',methods = ['POST'])
def r_signup():
      try:
         rname = request.form["rname"]
         ssn = request.form["ssn"]
         address = request.form["address"]
         mail = request.form["mail"]
         phone = request.form["phone"]
         password = request.form["password"]
         with sql.connect("readers.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO readers (rname, ssn, address, mail, phone, password) VALUES (?,?,?,?,?,?)",(rname,ssn,address,mail,phone,password) )
            con.commit()
            msg = "讀者帳號已成功建立！"
      except:
         con.rollback()
         msg = "讀者註冊失敗，請聯絡管理員！"
      finally:
         con.close()
         return render_template("result.html",msg = msg)
      
# 讀者登出
@app.route('/r_signout')
def r_signout():
  ssn = session["ssn"]
  rname = session["reader"]
  send_logout_event(ssn, rname)
  return redirect("/")

# 任何訪客搜尋書本，都會被記錄到log
@app.route('/book_search')
def books():
    book_name = request.args.get("book_search")
    con = sql.connect("books.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from books where title LIKE '%{}%'".format(book_name))
    books = cur.fetchall()
    send_search_history(book_name)
    return render_template("book_search.html", book_search = books)

# 讀者查看個人資料
@app.route('/r_profile')
def r_profile():
  if "reader" in session:
    ssn = session["ssn"]
    con = sql.connect("readers.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM readers WHERE ssn = ?", (ssn,))
    reader = cur.fetchone()
    con.close
    return render_template("/r_profile.html", reader = reader)
  else:
    return redirect("/")

# 讀者修改資料，也要被記錄到log
@app.route('/r_modify')
def r_modify():
    if "reader" in session:
      con = sql.connect("readers.db")
      con.row_factory = sql.Row
      cur = con.cursor()
      reader = session["reader"]
      cur.execute("SELECT ssn FROM readers WHERE rname = ?", (reader,))
      people = cur.fetchone()[0]
      return render_template("r_modify.html", rname = reader, ssn = people)
    else:
       return redirect("/")

@app.route('/r_modify0',methods = ['POST', 'GET'])
def r_modify0():
   if "reader" in session:
    if request.method == 'POST':
        try:
          address = request.form["address"]
          mail = request.form["mail"]
          phone = request.form["phone"]
          password = request.form["password"]
          
          with sql.connect("readers.db") as con:
              cur = con.cursor()
              if address:
                  cur.execute("update readers set address=? WHERE rname=?", (address, session["reader"]))
              if mail:
                  cur.execute("update readers set mail=? WHERE rname=?", (mail, session["reader"]))
              if phone:
                  cur.execute("update readers set phone=? WHERE rname=?", (phone, session["reader"]))
              if password:
                  cur.execute("update readers set password=? WHERE rname=?", (password, session["reader"]))
              con.commit()
              msg = "讀者資料修改成功！"
        except:
          con.rollback()
          msg = "讀者修改資料失敗，請聯絡管理員！"
        finally:
          con.close()
          return render_template("r_result.html",msg = msg)
   else:
    return redirect("/")

# 讀者登入後，可以查看所有書本，並且借書      
@app.route('/book_available')
def book_available():
  if "reader" in session:
    con = sql.connect("books.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from books")
    books = cur.fetchall()
    con.close
    return render_template("book_available.html", books = books)
  else:
    return redirect("/")

# 讀者借書
@app.route('/r_borrowed')
def r_borrowed():
  if "reader" in session:
    ssn = session["ssn"]
    con = sql.connect("reports.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from reports where User_id=?", (ssn,))
    borrowed = cur.fetchall()
    con.close()
    return render_template("r_borrow.html", borrowed = borrowed)
  else:
    return redirect("/")
  
@app.route('/borrow')
def borrow():
    if "reader" in session:
        ISBN = request.args.get("book")
        try:
            with sql.connect("books.db") as con:
                cur = con.cursor()
                cur.execute("SELECT title FROM books WHERE ISBN=?", (ISBN,))
                title = cur.fetchone()[0]

            with sql.connect("readers.db") as con1:
                con1.row_factory = sql.Row
                cur1 = con1.cursor()
                reader = session["reader"]
                cur1.execute("SELECT ssn FROM readers WHERE rname = ?", (reader,))
                people = cur1.fetchone()[0]

            with sql.connect("reports.db") as con2:
                con2.row_factory = sql.Row
                cur2 = con2.cursor()
                cur2.execute("SELECT book_no FROM reports WHERE book_no = ?", (ISBN,))
                tmp = cur2.fetchone()
                if tmp is None:
                    return_date = datetime.date.today() + datetime.timedelta(days=30)
                    cur2.execute("INSERT INTO reports(User_id, book_no, title) VALUES (?, ?, ?)", (people, ISBN, title))
                    msg1 = "借閱成功！請在"+return_date.strftime('%Y-%m-%d')+"之前歸還，謝謝！"
                    with sql.connect("books.db") as con:
                        cur = con.cursor()
                        cur.execute("SELECT title FROM books WHERE ISBN = ?", (ISBN,))
                        msg2 = cur.fetchone()[0]
                else:
                    msg1 = "這本書已經被借走囉！"
                    msg2 = ""
        except Exception as e:
            con.rollback()
            msg1 = "發生錯誤！請稍後再試！"
            msg2 = "未知"
            print(e)
        return render_template("borrow_result.html", msg1=msg1, msg2=msg2)
    else:
        return redirect("/")

# 讀者還書  
@app.route('/return_book')
def return_book():
   if "reader" in session:
     book = request.args.get('book')
     con = sql.connect("reports.db")
     de = "DELETE FROM reports WHERE book_no="+book
     cur = con.cursor()
     cur.execute(de)
     con.commit()
     con.close()
     return render_template("r_result.html", msg = "成功歸還！祝您有美好的一天！")
   else:
      return redirect("/")

# 讀者推薦書籍  
@app.route('/recommend')
def recommend():
    return render_template("recommend.html")

@app.route('/new_recommend',methods = ['POST', 'GET'])
def new_recommend():
    if request.method == 'POST':
      try:
         ISBN = request.form["ISBN"]
         title = request.form["title"]
         author = request.form["author"]
         category = request.form["category"]
         version = request.form["version"]
         
         with sql.connect("recommends.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO recommends (ISBN, title, author, category, version) VALUES (?,?,?,?,?)",(ISBN, title, author, category, version) )
            con.commit()
            msg = "感謝您的推薦！我們會盡快購買！"
      except:
         con.rollback()
         msg = "發生錯誤，請聯絡管理員！"
      finally:
         con.close()
         return render_template("r_result.html",msg = msg)
      
# 訪客 查看書籍
@app.route('/booklist')
def booklist():
    con = sql.connect("books.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from books")
    
    books = cur.fetchall()
    return render_template("booklist.html", books = books)












# 以下為管理員的程式碼，不用看！！！
@app.route('/report_manage')
def reports():
    con = sql.connect("reports.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from reports")
    
    reports = cur.fetchall()
    return render_template("report_manage.html", reports = reports)

@app.route('/book_manage')
def book_manage():
    con = sql.connect("books.db")
    con.row_factory = sql.Row
    
    cur = con.cursor()
    cur.execute("select * from books")
    
    books = cur.fetchall()
    return render_template("book_manage.html", books = books)

# 新增書籍
@app.route('/new_book',methods = ['POST', 'GET'])
def new_book():
   if request.method == 'POST':
      try:
         ISBN = request.form["ISBN"]
         title = request.form["title"]
         author = request.form["author"]
         category = request.form["category"]
         version = request.form["version"]
         publisher = request.form["publisher"]
         with sql.connect("books.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO books (ISBN, title, author, category, version, publisher) VALUES (?,?,?,?,?)",(ISBN, title, author, category, version, publisher) )
            con.commit()
            msg = "書籍上架成功！"
      except:
         con.rollback()
         msg = "書籍上架失敗，請聯絡電算中心！"
      finally:
         con.close()
         return render_template("s_result.html",msg = msg)

@app.route('/d_report')
def d_report():
    con = sql.connect("reports.db")
    ID = request.args.get("book")
    de = "DELETE FROM reports WHERE book_no="+ID
    cur = con.cursor()
    cur.execute(de)
    con.commit()
    return render_template("s_result.html", msg="借閱紀錄刪除成功！")

@app.route('/d_book')
def d_book():
    con = sql.connect("books.db")
    ID = request.args.get("book")
    de = "DELETE FROM books WHERE ISBN="+ID
    cur = con.cursor()
    cur.execute(de)
    con.commit()
    return render_template("s_result.html", msg="書籍下架成功！")

@app.route('/s_signin', methods=['POST'])
def s_signin():
  with sql.connect("staffs.db") as con:
      con.row_factory = sql.Row
      cur = con.cursor()
      empid = request.form["empid"]
      spassword = request.form["password"]
      cur.execute("SELECT * FROM staffs WHERE empid=? and password=?", (empid, spassword))
      people = cur.fetchall()
      if len(people) == 0:
        return redirect("/result?msg=帳號或密碼錯誤")
      cur.execute("SELECT sname FROM staffs WHERE empid=? and password=?", (empid, spassword,))
      sname = cur.fetchone()[0]
  session["staff"] = empid
  return render_template("/s_member.html", sname=sname)

@app.route('/s_member')
def s_member():
  if "staff" in session:
    con = sql.connect("staffs.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT sname FROM staffs WHERE empid=?", (session["staff"],))
    sname = cur.fetchone()[0]
    con.close()
    return render_template("/s_member.html", sname=sname)
  else:
    return redirect("/")

@app.route('/s_signout')
def s_signout():
  del session["staff"]
  return redirect("/")
       
@app.route('/r_member')
def r_member():
  if "reader" in session:
    return render_template("r_member.html", rname = session["reader"])
  else:
    return render_template("/")

@app.route('/recommend_list')
def recommend_list():
    con = sql.connect("recommends.db")
    con.row_factory = sql.Row
    
    cur = con.cursor()
    cur.execute("select * from recommends")
    
    recommends = cur.fetchall()
    return render_template("recommend_list.html", recommends = recommends)

@app.route('/reader_list')
def reader_list():
  if "staff" in session:
    con = sql.connect("readers.db")
    con.row_factory = sql.Row
    
    cur = con.cursor()
    cur.execute("select * from readers")
    
    readers = cur.fetchall()
    return render_template("reader_list.html", readers = readers)
  else:
    return redirect("/")

@app.route('/new_staff')
def new_staff():
    return render_template('new_staff.html')

         
@app.route("/r_result")
def r_result():
    message = request.args.get("msg", "發生錯誤，請聯繫圖書館")
    return render_template("r_result.html", msg=message)

@app.route("/s_result")
def s_result():
    message = request.args.get("msg", "發生錯誤，請聯繫電算中心")
    return render_template("s_result.html", msg=message)

@app.route("/result")
def result():
    message = request.args.get("msg", "發生錯誤，請聯繫圖書館")
    return render_template("result.html", msg=message)

@app.route('/borrow_result')
def borrow_result():
    message1 = request.args.get("msg1", "發生錯誤，請聯繫圖書館")
    message2 = request.args.get("msg2", "發生錯誤，請聯繫圖書館")
    return render_template("result.html", msg1=message1, msg2=message2)

if __name__ == '__main__':
    app.run(debug=True)