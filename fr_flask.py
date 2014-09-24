import os, os.path

from flask import Flask, render_template, redirect, request, session, url_for
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

app.secret_key = "whatsecretwhat"

UNKNOWN = 'Unknown'

HOUSES = ['Avery', 'Blacker', 'Dabney', 'Fleming', 'Lloyd', 'Page', 'Ricketts',
          'Ruddock']

HOUSES_ENUM = db.Enum(*(HOUSES + ['Unknown']))

IMG_DIR = 'prefrosh_images'

IMG_FORMAT = IMG_DIR + '/%s.jpg'

NUM_PREFROSH = len([name for name in os.listdir(os.path.join('static', IMG_DIR)) if os.path.isfile(name)])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    progress = db.Column(db.Integer)
    house = db.Column(HOUSES_ENUM, default=UNKNOWN)

    def __init__(self, username, house=UNKNOWN):
        self.username = username
        self.house = house
        self.progress = 0

class Prefrosh(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    house = db.Column(HOUSES_ENUM, default=UNKNOWN)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    prefrosh_id = db.Column(db.Integer)
    prediction = db.Column(HOUSES_ENUM, default=UNKNOWN)

    def __init__(self, user_id, prefrosh_id, prediction):
        self.user_id = user_id
        self.prefrosh_id = prefrosh_id
        self.prediction = prediction


@app.route("/", methods=["GET", "POST"])
def homepage():
    if request.method == "GET":
        if "user_id" in session:
            user = User.query.filter_by(id=session["user_id"]).first()
            return redirect(url_for("prefrosh_predict", prefrosh_id=user.progress))
        else:
            return render_template("home.html")

    user = User.query.filter_by(username=request.form["username"]).first()
    if user is None:
        user = User(request.form["username"], request.form["house"])
        db.session.add(user)
        db.session.commit()
    session['user_id'] = user.id
    return redirect(url_for("prefrosh_predict", prefrosh_id=user.progress))

@app.route("/prefrosh/<int:prefrosh_id>", methods=["GET", "POST"])
def prefrosh_predict(prefrosh_id):
    if request.method == "GET" or "user_id" not in session:
        return render_template("predict.html",
                               photo_url=url_for('static',
                                                 filename=IMG_FORMAT % prefrosh_id))
    else:
        prior_prediction = Prediction.query.filter_by(user_id=session["user_id"],
                                                      prefrosh_id=prefrosh_id).first()
        user = User.query.filter_by(id=session["user_id"]).first()
        if prior_prediction is not None or prefrosh_id != user.progress:
            return redirect(url_for("prefrosh_predict", prefrosh_id=user.progress))

        pred = Prediction(session["user_id"], prefrosh_id, request.form["prediction"])
        user.progress += 1
        db.session.add(pred)
        db.session.add(user)
        db.session.commit()
        if user.progress >= NUM_PREFROSH:
            return "You're done"
        return redirect(url_for("prefrosh_predict", prefrosh_id=user.progress))

if __name__ == '__main__':
    app.debug = True
    app.run()
