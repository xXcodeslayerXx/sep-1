from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import jsonify
import requests
from flask_wtf import CSRFProtect
from flask_csp.csp import csp_header
import logging
import datetime
import userManagement as dbHandler
from datetime import datetime, timedelta

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
    if request.method == "POST":
        print("POST")
    return render_template("/index.html")


@app.route("/privacy.html", methods=["GET"])
def privacy():
    return render_template("/privacy.html")


# example CSRF protected form
@app.route("/form.html", methods=["POST", "GET"])
def form():
    if request.method == "POST":
        email = request.form["email"]
        text = request.form["text"]
        return render_template("/form.html")
    else:
        return render_template("/form.html")


# Endpoint for logging CSP violations
@app.route("/csp_report", methods=["POST"])
@csrf.exempt
def csp_report():
    app.logger.critical(request.data.decode())
    return "done"


saved_times = []

# def format_time(ms):
#     return str(datetime.timedelta(milliseconds=ms)).split('.')[0]

@app.route('/study.html',methods=['GET','POST'])
def study():
    if request.method =='POST':
        action= request.form.get('action') # Getting which button was clicked
        print(action)
        if action == "start": 
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            starttime= str(current_time)
            return render_template('study.html',starttime=starttime)
        elif action == "stop":
            starttime = request.form["start_time"]
            print(starttime)
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            endtime = str(current_time)

            timespent = calculatetimespent(starttime, endtime)
            dbHandler.savelog('','',timespent,now)
            return render_template('study.html',starttime=starttime, end_time=endtime)
        else: #reset was clicked
            return render_template('study.html',starttime = '00:00:00')
    else:
        return render_template('study.html',starttime = '00:00:00')
    
def calculatetimespent(starttime, endtime):
    start = datetime.strptime(starttime, "%H:%M:%S")
    end = datetime.strptime(endtime, "%H:%M:%S")
    time_difference = end - start
    seconds = time_difference.total_seconds()
    return (seconds)


@app.route('/save', methods=['POST'])
def save_time():
    data = request.get_json()
    ms = data['time']
    formatted = format_time(ms)
    saved_times.append(ms)
    print(f"Time saved: {formatted} ({ms} ms)")  # You can store this in a DB
    return jsonify({"status": "success", "formatted": formatted})

if __name__ == '__main__':
    app.run(debug=True)



# @app.route("/study.html", methods=["POST", "GET"])
# def study():
#     if request.method == "POST":
#         value = "Here I am"
#         return render_template("/study.html",message=value )
#     return render_template("/study.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

