from flask import Flask, render_template, request, redirect, session
from flask_bcrypt import Bcrypt
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

bcrypt = Bcrypt(app)

def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username,hashed_password)
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cur.fetchone()

        conn.close()

        if user and bcrypt.check_password_hash(user[2], password):
            session['user'] = username
            return redirect('/dashboard')

        return "Invalid Login"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():

    if 'user' in session:
        return render_template('dashboard.html',
                               username=session['user'])

    return redirect('/login')

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
    