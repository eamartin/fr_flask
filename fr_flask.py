from flask import Flask, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://test.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    progress = db.Column(db.Integer)


@app.route("/", methods=["GET"])
def homepage():
    return render_template("home.html")

@app.route("/signup_or_login", methods=["POST"])
def signup_or_login():
    print request.form['username']
    print request.form['house']

if __name__ == '__main__':
    app.debug = True
    app.run()
