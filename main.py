from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import jsonify
import requests
from flask_wtf.csrf import CSRFProtect
from flask_csp.csp import csp_header
import logging
import datetime
import userManagement as dbHandler
from datetime import datetime, timedelta
from flask import session

# Code snippet for logging a message
# app.logger.critical("message")

app_log = logging.getLogger(__name__)
logging.basicConfig(
    filename="security_log.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
)

# Generate a unique basic 16 key: https://acte.ltd/utils/randomkeygen
app = Flask(__name__)
app.secret_key = b"_53oi3uriq9pifpff;apl"
csrf = CSRFProtect(app)


# Redirect index.html to domain root for consistent UX
@app.route("/index", methods=["GET","POST"])
@app.route("/index.htm", methods=["GET"])
@app.route("/index.asp", methods=["GET"])
@app.route("/index.php", methods=["GET"])
@app.route("/index.html", methods=["GET","POST"])
def root():
    return redirect("/", 302)

@app.route("/", methods=["POST", "GET"])
@csp_header(
    {
        # Server Side CSP is consistent with meta CSP in layout.html
        "base-uri": "'self'",
        "default-src": "'self'",
        "style-src": "'self'",
        "script-src": "'self'",
        "img-src": "'self' data:",
        "media-src": "'self'",
        "font-src": "'self'",
        "object-src": "'self'",
        "child-src": "'self'",
        "connect-src": "'self'",
        "worker-src": "'self'",
        "report-uri": "/csp_report",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "frame-src": "'none'",
    }
)
def index():
    error = None
    if request.method == "POST":
        print("POST")
        return render_template("index.html", error=error)
    # Always return a response for GET
    return render_template("index.html", error=error)

@app.route("/privacy.html", methods=["GET"])
def privacy():
    return render_template("/privacy.html")

@app.route("/login", methods=["GET", "POST"])

def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = dbHandler.get_user(username, password)
        if user:
            session["user_id"] = user[0]  # save user id
            session["username"] = user[1]
            return render_template("index.html")
        else:
            return "Invalid login!"
    print('test')
    return render_template("login.html")

## Removed automatic login() call to avoid using request outside context

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

 # Get study summary for the current user
    user_id = session["user_id"]
    user_study_summary = dbHandler.get_user_study_summary(user_id)
    
    # Get all users study summary for admin view (optional)
    all_users_summary = dbHandler.get_all_users_study_summary()
    
    return render_template("dashboard.html", 
                        username=session["username"], 
                        user_study_summary=user_study_summary,
                        all_users_summary=all_users_summary)

@app.route("/subjects", methods=["GET"])
def subjects():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("subjects.html")


# example CSRF protected form
@app.route("/form.html", methods=["POST", "GET"])
def form():
    if request.method == "POST":
        username = request.form["Username"]
        password = request.form["Password"]
        try:
            dbHandler.create_user(username, password)
            return render_template("/form.html")
        except Exception:
            return "Username already exists!"
    return render_template("/form.html")
        

# Endpoint for logging CSP violations
@app.route("/csp_report", methods=["POST"])
@csrf.exempt
def csp_report():
    app.logger.critical(request.data.decode())
    return "done"


# Removed stray decorator with no function
# def format_time(ms):
#     return str(datetime.timedelta(milliseconds=ms)).split('.')[0]

@app.route('/study.html', methods=['GET'])
def study():
    subject = request.args.get('subject', 'General')
    return render_template('study.html', subject=subject)

@app.route('/study-timer', methods=['GET'])
def study_timer():
    subject = request.args.get('subject', 'General')
    return render_template('study.html', subject=subject)

@app.route('/save-study-session', methods=['POST'])
@csrf.exempt
def save_study_session():
    try:
        data = request.get_json()
        subject = data.get('subject', 'General')
        time_spent_seconds = data.get('timeSpentSeconds', 0)
        start_time = data.get('startTime', '')
        end_time = data.get('endTime', '')
        
        # For now, use a default user_id (you can get this from session later)
        user_id = session.get('user_id', 1)  # Default to user 1 if not logged in
        
        dbHandler.save_study_session(user_id, subject, time_spent_seconds, start_time, end_time)
        
        return jsonify({"status": "success", "message": "Study session saved successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
