from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///workout.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    sets = db.relationship("ExerciseSet", backref="parent_workout", cascade="all, delete-orphan", lazy=True)

class ExerciseSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)

    workout_id = db.Column(db.Integer, db.ForeignKey("workout.id"), nullable=False)

@app.route("/")
def index():
    workouts = Workout.query.order_by(Workout.date_posted.desc()).all()
    return render_template("index.html", workouts=workouts)

@app.route("/add", methods=["GET", "POST"])
def add_workout():
    if request.method == "POST":
        title = request.form.get("title")

        new_workout = Workout(title=title)
        db.session.add(new_workout)
        db.session.flush()

        exercise_names = request.form.getlist("ex_name")
        weights = request.form.getlist("weight")
        reps_list = request.form.getlist("reps")

        for name, w, r in zip(exercise_names, weights, reps_list):
            if name and w and r:
                new_set = ExerciseSet(
                    exercise_name = name,
                    weight = int(w),
                    reps = int(r),
                    workout_id = new_workout.id
                )
                db.session.add(new_set)
        
        db.session.commit()
        return redirect(url_for("index"))
    
    return render_template("add.html")

@app.route("/delete/<int:workout_id>", methods=["POST"])
def delete_workout(workout_id):
    workout_to_delete = Workout.query.get_or_404(workout_id)

    try:
        db.session.delete(workout_to_delete)
        db.session.commit()
        return redirect(url_for("index"))
    except:
        return "There was a problem deleting that workout."

if __name__ == "__main__":
    app.run(debug=True)