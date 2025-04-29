from flask import Flask, request, redirect, make_response
import sqlite3, os, time

app = Flask(__name__)
DB_PATH = 'blind_users.db'

# Initialize the SQLite database
def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("CREATE TABLE users (username TEXT, password TEXT)")
        # Admin account with secret password
        c.execute("INSERT INTO users VALUES ('admin', 'bl1nd_s3cr3t')")
        conn.commit()
        conn.close()
        print("[+] Database initialized.")

init_db()

@app.route('/')
def index():
    user = request.cookies.get('user')
    if user:
        return f"Welcome, {user}!<br><a href='/admin'>Admin page</a>"
    return "Welcome!<br><a href='/login'>Login</a>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        # VULNERABLE TO TIME-BASED BLIND SQL INJECTION
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{u}' AND password = '{p}'"
        print(f"[DEBUG] Executing: {query}")

        try:
            start = time.time()
            c.execute(query)
            result = c.fetchone()
            elapsed = time.time() - start
        except:
            result = None
            elapsed = 0

        conn.close()

        if result:
            resp = make_response("Welcome back!<br><a href='/admin'>Go to admin page</a>")
            resp.set_cookie('user', result[0])  # Set username as session
            return resp
        return "Invalid credentials."
    
    return '''
    <h2>Login</h2>
    <form method="post">
        Username: <input name="username"><br>
        Password: <input name="password" type="password"><br>
        <input type="submit" value="Login">
    </form>
    '''

@app.route('/admin')
def admin():
    username = request.cookies.get('user')
    if username == 'admin':
        return "Welcome admin!<br>Flag: <code>flag{n0_0utput_n0_pr0bl3m_bl1nd_5qli}</code>"
    return "Admins only. Access denied."

if __name__ == '__main__':
    app.run(debug=True)
