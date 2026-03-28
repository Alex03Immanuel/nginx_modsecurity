from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


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
    else:
        return render_template("sign_in.html", error="Invalid credentials")


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        return render_template("sign_up.html")

    username = request.form['username']
    password = request.form['password']

    if User.query.filter_by(username=username).first():
        return render_template("sign_up.html", error="Username already exists")

    
    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    session['username'] = new_user.username
    return redirect(url_for("sign_in"))

@app.route('/landing_page')
def dashboard():
    if "username" in session:
        return render_template("dashboard.html", username=session['username'])
    else:
        return redirect(url_for("welcome"))


if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)
