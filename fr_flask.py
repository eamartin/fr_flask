from flask import Flask, render_template, request, session
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

UNKNOWN = 'Unknown'

HOUSES = ['Avery', 'Blacker', 'Dabney', 'Fleming', 'Lloyd', 'Page', 'Ricketts',
          'Ruddock']

HOUSES_ENUM = db.Enum(*(HOUSES + ['Unknown']))

IMG_FORMAT = 'prefrosh_images/%s.jpg'

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
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    prefrosh_id = db.Column(db.Integer, db.ForeignKey(Prefrosh.id))
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
            return redirect(url_for(prefrosh_predict, prefrosh_id=user.progress))
        else:
            return render_template("home.html")

    user = User.query.filter_by(username=request.form["username"])
    if user is None:
        user = User(request.form["username"], request.form["house"])
        db.session.add(user)
        db.session.commit()
    session['user_id'] = user.id
    return redirect(url_for(prefrosh_predict, prefrosh_id=user.progress))

@app.route("/prefrosh/<int:prefrosh_id>", methods=["GET", "POST"])
def prefrosh_predict(prefrosh_id):
    if request.method == "GET" or "user_id" not in session:
        return render_template("predict.html",
                               photo_url=url_for('static',
                                                 filename=IMG_DIR % prefrosh_id))
    else:
        prior_prediction = Prediction.filter.query_by(user_id=session["user_id"],
                                                      prefrosh_id=prefrosh_id).first()
        if prior_prediction is not None:
            abort(500)
        pred = Prediction(session["user_id"], prefrosh_id, request["prediction"])
        user = User.query.filter_by(id=session["user_id"]).first()
        user.progress += 1
        db.session.add(pred)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for(prefrosh_predict, prefrosh_id=user.progress))

if __name__ == '__main__':
    app.debug = True
    app.run()
