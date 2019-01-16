from flask import Flask, session, redirect, url_for, escape, request, render_template
from bcrypt import hashpw, gensalt
import mysql.connector
import os, encodings

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="names"
)

app = Flask(__name__)
app.secret_key = '\xf1q=\xac\x98b\x1f\\\xf2\x95MGj\xe4g:\x0b\x0fP\xdb\xe4\x93\xae\xa1'



@app.route('/signup', methods=['POST'])
def signup():
    try:
        name = request.form['name']
        email = request.form['e-mail']
        password = request.form['password']
        salt = gensalt(12)
        hashed = hashpw(password.encode('utf8'), salt)
        mycursor = mydb.cursor()
        sql = "INSERT INTO `database`(`email`, `display_name`, `password`, `salt`) VALUES (%s, %s, %s, %s)"
        val = (email, name, hashed, salt)
        mycursor.execute(sql, val)
        mydb.commit()
        redirect('/login')
    except:
        return "A user with those credentials already exists"


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'username' in session:
        mycursor = mydb.cursor()
        sql_select_query = "select `content`, `display_name` from `posts`"
        mycursor.execute(sql_select_query)
        post = mycursor.fetchall()
        return render_template('dashboard.html', username=session['username'], posts=post)
    else:
        try:
            name_entered = request.form['name']
            password_entered = request.form['password']
            mycursor = mydb.cursor()
            sql_select_query = "select `password` from `database` where `display_name` = %s"
            mycursor.execute(sql_select_query, (name_entered,))
            record, = mycursor.fetchone()
            salt_query = "select `salt` from `database` where `display_name` = %s"
            mycursor.execute(salt_query, (name_entered,))
            salt = mycursor.fetchone()[0]
            if hashpw(password_entered.encode('utf8'), salt) == record:
                mycursor = mydb.cursor()
                sql_select_query = "select `content`, `display_name` from `posts`"
                mycursor.execute(sql_select_query)
                post = mycursor.fetchall()
                session['username'] = name_entered
                return render_template('dashboard.html', username=name_entered, posts=post)
            else:
                return 'Incorrect Username or Password'
        except TypeError:
            return 'That user does not exist'

@app.route('/MakePost')
def MakePost():
    return render_template('post.html')

@app.route('/post', methods=['POST', 'GET'])
def post():
    if 'username' in session:
        username_session = session['username']
        mycursor = mydb.cursor()
        content = request.form['Post']
        sql = "INSERT INTO `posts`(`display_name`, `content`) VALUES (%s, %s)"
        val = (username_session, content)
        mycursor.execute(sql, val)
        mydb.commit()
        return redirect('/login')

@app.route('/')
def hello_world():
    return render_template('signup.html')


@app.route('/LoginLoad')
def LoginLoad():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
