from flask import Flask, session, redirect, url_for, escape, request, render_template, flash
from bcrypt import hashpw, gensalt
import mysql.connector
import os, encodings

cnx = mysql.connector.connect(
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
        cursor = cnx.cursor(buffered=True)
        sql = "INSERT INTO `database`(`email`, `display_name`, `password`, `salt`) VALUES (%s, %s, %s, %s)"
        val = (email, name, hashed, salt)
        cursor.execute(sql, val)
        cnx.commit()
        return redirect('/LoginLoad', code=302)
    except:
        return "A user with those credentials already exists"


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'username' in session:
        cursor = cnx.cursor(buffered=True)
        sql_select_query = "select `content`, `display_name`, `post_date`, `sub-name` from `posts` ORDER BY `post_date` DESC"
        cursor.execute(sql_select_query)
        post = cursor.fetchall()
        print(post)
        return render_template('dashboard.html', username=session['username'], posts=post)
    else:
        try:
            name_entered = request.form['name']
            password_entered = request.form['password']
            cursor = cnx.cursor(buffered=True)
            sql_select_query = "select `password` from `database` where `display_name` = %s"
            cursor.execute(sql_select_query, (name_entered,))
            record, = cursor.fetchone()
            salt_query = "select `salt` from `database` where `display_name` = %s"
            cursor.execute(salt_query, (name_entered,))
            salt = cursor.fetchone()[0]
            if hashpw(password_entered.encode('utf8'), salt) == record:
                cursor = cnx.cursor(buffered=True)
                sql_select_query = "select `content`, `display_name` from `posts`"
                cursor.execute(sql_select_query)
                post = cursor.fetchall()
                session['username'] = name_entered
                return render_template('dashboard.html', username=name_entered, posts=post)
            else:
                return 'Incorrect Username or Password'
        except TypeError:
            return 'That user does not exist'


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/LoginLoad')


@app.route('/MakePost')
def MakePost():
    return render_template('post.html')


@app.route('/post', methods=['POST', 'GET'])
def post():
    if 'username' in session:
        try:
            username_session = session['username']
            sub = request.form['sub-choice']
            cursor = cnx.cursor(buffered=True)
            sql_select_query = "select `sub-name` from `sub` where `sub-name` = %s"
            cursor.execute(sql_select_query, (sub,))
            sub_check = cursor.fetchone()[0]
            print(sub_check)
            cursor = cnx.cursor(buffered=True)
            content = request.form['Post']
            sql = "INSERT INTO `posts`(`display_name`, `content`, `sub-name`) VALUES (%s, %s, %s)"
            val = (username_session, content, sub)
            cursor.execute(sql, val)
            cnx.commit()
            return redirect('/login')
        except TypeError:
            return redirect('/login')

@app.route('/')
def hello_world():
    return render_template('signup.html')


@app.route('/profile_load')
def profile():
    cursor = cnx.cursor(buffered=True)
    sql_select_query = "select `content`, `display_name` from `posts` where `display_name` = %s"
    cursor.execute(sql_select_query, (session['username'],))
    post = cursor.fetchall()
    return render_template('profile.html', username=session['username'], posts=post)


@app.route('/profile_search', methods=['POST', 'GET'])
def profile_search():
    name = request.form['search']
    cursor = cnx.cursor(buffered=True)
    sql_select_query = "select `content`, `display_name` from `posts` where `display_name` = %s"
    cursor.execute(sql_select_query, (name,))
    post = cursor.fetchall()
    return render_template('profile.html', username=name, posts=post)


@app.route('/sub_load')
def subsocial_create():
    return render_template('create_sub_social.html', username=session['username'])


@app.route('/sub_create', methods=['POST', 'GET'])
def sub_call():
    name = request.form['sub-name']
    cursor = cnx.cursor(buffered=True)
    sql = "INSERT INTO `sub`(`sub-name`) VALUES (%s)"
    cursor.execute(sql, (name,))
    cnx.commit()
    return redirect('/login')


@app.route('/LoginLoad')
def LoginLoad():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
