from flask import Flask, session, redirect, url_for, escape, request, render_template, flash
from bcrypt import hashpw, gensalt
import mysql.connector
import os, encodings

cnx = mysql.connector.connect(  # Here I connect to the database that is setup in xampp running apache.
  host="localhost",
  user="root",
  passwd="",
  database="names"
)

app = Flask(__name__)
app.secret_key = 'INSERT A SECRET KEY HERE'  # Secret key used for sessions!


'''
In the signup route I use a form from html using the post method to grab the data. I then generate my salt wich I use
to hash the password I just recieved. I then save the hashed password, salt, email and username to the database
After that I then redirect them to login!
'''
@app.route('/signup', methods=['POST'])
def signup():
    try:
        name = request.form['name']
        email = request.form['e-mail']      # Grabbing the users inputs from the html form!
        password = request.form['password']
        salt = gensalt(12)
        hashed = hashpw(password.encode('utf8'), salt)  # Hashing the Password
        cursor = cnx.cursor(buffered=True)
        sql = "INSERT INTO `database`(`email`, `display_name`, `password`, `salt`) VALUES (%s, %s, %s, %s)"     # Saving their credentials to the database!
        val = (email, name, hashed, salt)
        cursor.execute(sql, val)
        cnx.commit()
        return redirect('/LoginLoad', code=302)     # Redirecting them to the login screen.
    except ValueError:
        return "A user with those credentials already exists"


'''
In the login route I first check if there in a session if not I then hash the password they gave me and compare that
password to the hashed password I have saved in my database. After that is done I create a session and then render the
dashboard template that fills up with all the posts I grabbed from my database.
'''
@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'username' in session:   # Checking if they are in a session and if so loading up the homepage!
        cursor = cnx.cursor(buffered=True)
        sql_select_query = "select `content`, `display_name`, `post_date`, `sub-name` from `posts` ORDER BY `post_date` DESC LIMIT 8"
        cursor.execute(sql_select_query)
        post = cursor.fetchall()
        print(post)
        return render_template('dashboard.html', username=session['username'], posts=post)
    else:
        try:
            name_entered = request.form['name']             #Grabbing there details off of login form.
            password_entered = request.form['password']
            cursor = cnx.cursor(buffered=True)
            sql_select_query = "select `password` from `database` where `display_name` = %s"
            cursor.execute(sql_select_query, (name_entered,))
            record, = cursor.fetchone()                                                 #Grabbing Salt and Hash from database
            salt_query = "select `salt` from `database` where `display_name` = %s"
            cursor.execute(salt_query, (name_entered,))
            salt = cursor.fetchone()[0]
            if hashpw(password_entered.encode('utf8'), salt) == record:     # Then comparing both hashed passwords.
                cursor = cnx.cursor(buffered=True)
                sql_select_query = "select `content`, `display_name`, `post_date`, `sub-name` from `posts` DESC LIMIT 8"    # Grabs all the posts!
                cursor.execute(sql_select_query)
                post = cursor.fetchall()
                session['username'] = name_entered
                return render_template('dashboard.html', username=name_entered, posts=post)     # Renders the homepage
            else:
                return 'Incorrect Username or Password'
        except:
            return 'There was an error! please try logging in again. Or message Nolsters#1038 on discord!'



'''
This loads up the login html file.
'''
@app.route('/LoginLoad')
def LoginLoad():
    return render_template('login.html')


'''
This module logs the users out by canceling there session and redirecting them back to the login screen.
'''
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/LoginLoad')


'''
Loads up the html file to make posts!
'''
@app.route('/MakePost')
def MakePost():
    return render_template('post.html')


'''
Loads up the html signup file.
'''
@app.route('/')
def hello_world():
    return render_template('signup.html')


'''
Loads up the create a sub social html file
'''
@app.route('/sub_load')
def subsocial_create():
    return render_template('create_sub_social.html', username=session['username'])



'''
Takes the user input from login and inputs into the database!
'''
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


'''
Displaying your profile!
'''
@app.route('/profile_load')
def profile():
    cursor = cnx.cursor(buffered=True)
    sql_select_query = "select `content`, `display_name` from `posts` where `display_name` = %s"    # Grabs all your posts
    cursor.execute(sql_select_query, (session['username'],))
    post = cursor.fetchall()
    return render_template('profile.html', username=session['username'], posts=post)    # Returns a dashboard like html file custom to your posts


'''
Profile Search. Displays the profile of the one you searched. Very similar to the /profile_load module
except instead of your details getting looked up its the imputed ones.
'''
@app.route('/profile_search', methods=['POST', 'GET'])
def profile_search():
    name = request.form['search']
    cursor = cnx.cursor(buffered=True)
    sql_select_query = "select `content`, `display_name` from `posts` where `display_name` = %s"
    cursor.execute(sql_select_query, (name,))
    post = cursor.fetchall()
    return render_template('profile.html', username=name, posts=post)


'''
This coad takes the create a sub social html file input's and creates one now allowing people to post to that specific
sub social.
'''
@app.route('/sub_create', methods=['POST', 'GET'])
def sub_call():
    name = request.form['sub-name']     # Grabs input from html doc.
    cursor = cnx.cursor(buffered=True)
    sql = "INSERT INTO `sub`(`sub-name`) VALUES (%s)"   # Puts input in the database
    cursor.execute(sql, (name,))
    cnx.commit()
    return redirect('/login')     # Returns you back to the dashboard


@app.route('/sub_search', methods=['POST', 'GET'])




'''
This starts the application
'''
if __name__ == '__main__':
    app.run(debug=True)
