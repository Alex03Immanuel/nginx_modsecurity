import os
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-key')
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


patients = [
    {"id": 1, "name": "Aisha Khan", "age": 40, "condition": "Hypertension", "doctor": "Dr. Mehta", "report": "report_001.txt"},
    {"id": 2, "name": "Ravi Verma", "age": 53, "condition": "Type 2 Diabetes", "doctor": "Dr. Patel", "report": "report_002.txt"},
    {"id": 3, "name": "Sarah Lin", "age": 35, "condition": "Asthma", "doctor": "Dr. Chen", "report": "report_003.txt"},
    {"id": 4, "name": "James Okafor", "age": 61, "condition": "Coronary Artery Disease", "doctor": "Dr. Mehta", "report": "report_004.txt"},
    {"id": 5, "name": "Priya Nair", "age": 28, "condition": "Migraine", "doctor": "Dr. Patel", "report": "report_005.txt"},
]

ALLOWED_REPORTS = {"report_001.txt", "report_002.txt", "report_003.txt", "report_004.txt", "report_005.txt"}    
REPORTS_FOLDER = os.path.join(os.path.dirname(__file__), "reports")


# routes
@app.route('/')
def welcome():
    if "username" in session:
        return redirect(url_for("dashboard"))
    else:
        return render_template("welcome.html")


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'GET':
        return render_template("sign_in.html")

    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        session['username'] = user.username
        return redirect(url_for("dashboard"))
    
    return render_template("sign_in.html", error="Invalid credentials")



@app.route('/landing_page')
def dashboard():
    if "username" not in session:
        return redirect(url_for("welcome"))
    
    query = request.args.get('q', '')
    if query:
        filtered_patients = [p for p in patients if query.lower() in p["name"].lower()]
    else:
        filtered_patients = patients

    return render_template("dashboard.html", patients=filtered_patients, query=query, username=session["username"])


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for("welcome"))


@app.route('/patient/<int:patient_id>')
def patient_profile(patient_id):
    if "username" not in session:
        return redirect(url_for("welcome"))
    
    for p in patients:
        if p["id"] == patient_id:
            return render_template("patient.html", patient=p)
    
    return "<h1>Patient not found</h1>", 404

@app.route('/download')
def download():
    if "username" not in session:
        return redirect(url_for("welcome"))
    
    report_name = request.args.get('report')
    
    if not report_name:
        return "Report name is required", 400

    if report_name not in ALLOWED_REPORTS:
        return "Report not found", 404
    
    return send_from_directory(REPORTS_FOLDER, report_name, as_attachment=True)
    
    

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)
