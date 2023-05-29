from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql
import datetime

app = Flask(__name__)
app.secret_key = 'nccugogo'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/book_search')
def books():
    con = sql.connect("books.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from books where title LIKE '%{}%'".format(request.args.get("book_search", "")))
    books = cur.fetchall()
    return render_template("book_search.html", book_search = books)

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
# 修改員工資料
@app.route('/s_modify')
def s_modify():
    if "staff" in session:
      return render_template("s_modify.html", empid = session["staff"])
    else:
       return redirect("/")

@app.route('/s_modify0',methods = ['POST', 'GET'])
def s_modify0():
   if "staff" in session:
    if request.method == 'POST':
        try:
          sname = request.form["sname"]
          password = request.form["password"]
          
          with sql.connect("staffs.db") as con:
              cur = con.cursor()
              if sname:
                  cur.execute("update staffs set sname=? WHERE empid=?", (sname, session["staff"]))
              if password:
                  cur.execute("update staffs set password=? WHERE empid=?", (password, session["staff"]))
              con.commit()
              msg = "員工資料修改成功！"
        except:
          con.rollback()
          msg = "讀者修改資料失敗，請聯絡管理員！"
        finally:
          con.close()
          return render_template("s_result.html",msg = msg)
   else:
    return redirect("/")
# 修改員工資料
      
    
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

# 讀者還書
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
  
# 讀者還書
  
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
      
@app.route('/recommend')
def recommend():
    return render_template("recommend.html")

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
# 新增書籍

# 新增一筆借閱紀錄
@app.route('/new_report',methods = ['POST', 'GET'])
def new_report():
  if request.method == 'POST':
   try:
    SSN = request.form["SSN"]
    ISBN = request.form["ISBN"]
    issue = request.form["issue"]
    return_date = request.form["return_date"]
    title = request.form["title"]
    with sql.connect("reports.db") as con:
     cur = con.cursor()
     cur.execute("INSERT INTO reports(User_id, book_no, title, issue, return_date) VALUES (?,?,?,?,?)",(SSN, ISBN, title, issue, return_date) )
     con.commit()
     msg = "借閱紀錄新增成功！"
   except:
    con.rollback()
    msg = "借閱紀錄新增失敗，請聯絡電算中心！"
   finally:
    con.close()
    return render_template("s_result.html",msg = msg)
# 新增一筆借閱紀錄

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

@app.route('/del_reader_operation', methods=['POST'])
def del_reader_operation():
    if "staff" in session:
        rname = request.form.get("rname")
        ssn = request.form.get("ssn")
        con = sql.connect("readers.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM readers WHERE rname=? AND ssn=?", (rname, ssn))
        people = cur.fetchall()
        if len(people) == 0:
            return redirect("/result?msg=查無此人，請檢查資料是否輸入正確！")
        de = "DELETE FROM readers WHERE ssn=?"
        cur.execute(de, (ssn,))
        con.commit()
        con.close()
        return render_template("s_result.html", msg="讀者帳戶移除成功！")
    else:
        return redirect("/")

@app.route('/del_reader')
def del_reader():
   if "staff" in session:
    return render_template("/del_reader.html")
   else:
    return redirect("/")
   
@app.route('/del_staff')
def del_staff():
   if "staff" in session:
    empid = session['staff']
    con = sql.connect("staffs.db")
    cur = con.cursor()
    cur.execute("SELECT sname FROM staffs WHERE empid=?", (empid,))
    sname = cur.fetchone()[0]
    return render_template("/del_staff.html", sname = sname)
   else:
    return redirect("/")
   
@app.route('/del_staff_self')
def del_staff_self():
    if "staff" in session:
        con = sql.connect("staffs.db")
        cur = con.cursor()
        staff = session["staff"]

        de = "DELETE FROM staffs WHERE empid=?"
        cur.execute(de, (staff,))
        con.commit()
        con.close()
        return render_template("result.html", msg="管理員帳戶移除成功！")
    else:
        return redirect("/")
    
# 讀者自己刪除帳戶
@app.route('/del_account')
def del_account():
   if "reader" in session:
    return render_template("/del_account.html", rname = session['reader'])
   else:
    return redirect("/")
   
@app.route('/del_account_self')
def del_account_self():
    if "reader" in session:
        con = sql.connect("readers.db")
        cur = con.cursor()
        ssn = session["ssn"]
        de = "DELETE FROM readers WHERE ssn=?"
        cur.execute(de, (ssn,))
        con.commit()
        con.close()
        return render_template("result.html", msg="讀者帳戶移除成功！")
    else:
        return redirect("/")
# 讀者自己刪除帳戶

    
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
  return redirect("/r_member")

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

# 管理員個人資料
@app.route('/s_profile')
def s_profile():
  if "staff" in session:
    empid = session["staff"]
    con = sql.connect("staffs.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM staffs WHERE empid = ?", (empid,))
    staff = cur.fetchone()
    con.close
    return render_template("/s_profile.html", staff = staff)
  else:
    return redirect("/")

@app.route('/r_signout')
def r_signout():
  del session["reader"]
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
    
@app.route('/booklist')
def booklist():
    con = sql.connect("books.db")
    con.row_factory = sql.Row
    
    cur = con.cursor()
    cur.execute("select * from books")
    
    books = cur.fetchall()
    return render_template("booklist.html", books = books)

@app.route('/r_booklist')
def r_booklist():
    con = sql.connect("books.db")
    con.row_factory = sql.Row
    
    cur = con.cursor()
    cur.execute("select * from books")
    
    books = cur.fetchall()
    return render_template("r_booklist.html", books = books)

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

@app.route('/new_reader')
def new_reader():
    return render_template('new_reader.html')

@app.route('/new_staff')
def new_staff():
    return render_template('new_staff.html')

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
         
@app.route('/s_signup',methods = ['POST', 'GET'])
def s_signup():
   if request.method == 'POST':
      try:
         sname = request.form["sname"]
         empid = request.form["empid"]
         password = request.form["password"]
         
         with sql.connect("staffs.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO staffs (sname, empid, password) VALUES (?,?,?)",(sname, empid, password) )
            con.commit()
            msg = "管理員帳號已成功建立！"
      except:
         con.rollback()
         msg = "管理員註冊失敗，請聯絡管理員！"
         
      finally:
         con.close()
         return render_template("s_result.html",msg = msg)
      
@app.route('/publishers')
def publishers():
    con = sql.connect("publishers.db")
    con.row_factory = sql.Row
    
    cur = con.cursor()
    cur.execute("select * from publishers")
    
    publishers = cur.fetchall()
    return render_template("publishers.html", publishers = publishers)

@app.route('/r_publishers')
def r_publishers():
    con = sql.connect("publishers.db")
    con.row_factory = sql.Row
    
    cur = con.cursor()
    cur.execute("select * from publishers")
    
    publishers = cur.fetchall()
    return render_template("r_publishers.html", publishers = publishers)
         
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