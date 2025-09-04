#### INTENTIONALLY VULNERABLE DEMO APP — FOR SCANNER TESTING ONLY
# DO NOT USE IN PRODUCTION
from flask import Flask, request, render_template_string, redirect, send_from_directory
import sqlite3, os, hashlib, random, pickle, requests

app = Flask(__name__)
app.config["SECRET_KEY"] = "hardcoded-secret-key"  # Hardcoded secret
API_KEY = "sk_test_demo_123"                       # Hardcoded API key
UPLOAD_DIR = "uploads"                             # Insecure upload dir
os.makedirs(UPLOAD_DIR, exist_ok=True)

# initialize DB (stores passwords with MD5 and prints secrets)
def init_db():
    conn = sqlite3.connect("demo.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    # weak hash (MD5) & default admin creds
    c.execute("INSERT OR IGNORE INTO users(id,username,password) VALUES(1,'admin',?)",
              (hashlib.md5(b"admin123").hexdigest(),))
    conn.commit()
    conn.close()
    print(f"[BOOT] SECRET_KEY={app.config['SECRET_KEY']} API_KEY={API_KEY}")  # Leaks secrets to logs
init_db()

@app.route("/")
def index():
    # Reflected XSS via 'q'
    q = request.args.get("q", "")
    html = f"""
    <h1>Vuln Demo</h1>
    <p>Search term: <b>{q}</b></p>  <!-- unescaped -->
    <ul>
      <li><a href="/login?user=admin&pass=admin123">Auto Login (GET with creds)</a></li>
      <li><a href="/profile?user=admin">View Profile</a></li>
      <li><a href="/upload">Upload File</a></li>
      <li><a href="/proxy?url=http://example.com">Naive Proxy</a></li>
      <li><a href="/next?next=http://evil.example/steal">Open Redirect</a></li>
      <li><a href="/unpickle?data={pickle.dumps({'role':'admin'}).hex()}">Unpickle</a></li>
    </ul>
    """
    return render_template_string(html)  # No CSP, no escaping

@app.route("/login")
def login():
    # Credentials via GET; SQLi via string concatenation
    user = request.args.get("user", "")
    pwd = request.args.get("pass", "")
    hashed = hashlib.md5(pwd.encode()).hexdigest()  # Weak hash
    conn = sqlite3.connect("demo.db")
    c = conn.cursor()
    # SQL injection:
    sql = f"SELECT id,username FROM users WHERE username='{user}' AND password='{hashed}'"
    print("[SQL]", sql)
    row = c.execute(sql).fetchone()
    conn.close()
    if row:
        # Weak session token using random.random
        token = str(random.random())
        return f"Welcome {row[1]}! session={token}"
    return "Invalid credentials", 401

@app.route("/profile")
def profile():
    # No auth check; info disclosure
    username = request.args.get("user", "")
    conn = sqlite3.connect("demo.db")
    c = conn.cursor()
    # Another SQLi vector
    sql = f"SELECT id,username,password FROM users WHERE username='{username}'"
    row = c.execute(sql).fetchone()
    conn.close()
    if row:
        return f"User: {row[1]} | Hash:{row[2]}"  # leaks password hash
    return "Not found", 404

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return """
        <form method="POST" enctype="multipart/form-data">
          <input name="file" type="file"><button>Upload</button>
        </form>
        """
    f = request.files.get("file")
    # Path traversal: trust filename
    path = os.path.join(UPLOAD_DIR, f.filename)
    f.save(path)
    return f"Saved to {path}"

@app.route("/files/<path:name>")
def files(name):
    # Directory listing + traversal exposure
    return send_from_directory(UPLOAD_DIR, name)  # no filename sanitization

@app.route("/proxy")
def proxy():
    # SSRF-ish naive proxy with TLS verify disabled
    url = request.args.get("url", "http://example.com")
    try:
        r = requests.get(url, timeout=2, verify=False)  # verify=False
        return r.text  # streams arbitrary response
    except Exception as e:
        return f"Error fetching: {e}", 502

@app.route("/next")
def open_redirect():
    # Open redirect with no allowlist
    nxt = request.args.get("next", "/")
    return redirect(nxt)

@app.route("/unpickle")
def unpickle_route():
    # Unsafe deserialization (user-controlled pickle)
    data_hex = request.args.get("data", "")
    try:
        blob = bytes.fromhex(data_hex)
        obj = pickle.loads(blob)  # RCE risk
        return f"Unpickled: {obj}"
    except Exception as e:
        return f"Bad pickle: {e}", 400

@app.route("/config")
def config_leak():
    # Information disclosure of secrets and environment
    return {
        "debug": True,
        "secret": app.config["SECRET_KEY"],
        "api_key": API_KEY,
        "env": dict(os.environ)  # leaks environment
    }

if __name__ == "__main__":
    # Debug mode on, reloader on, binds all interfaces
    app.run(host="0.0.0.0", port=5000, debug=True)
