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

class ExerciseType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    muscle_group = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<ExerciseType {self.name} ({self.muscle_group})>"

@app.route("/")
def index():
    workouts = Workout.query.order_by(Workout.date_posted.desc()).all()

    for workout in workouts:
        grouped = {}
        for s in workout.sets:
            if s.exercise_name not in grouped:
                grouped[s.exercise_name] = []
            grouped[s.exercise_name].append(s)
        workout.grouped_sets = grouped

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
    
    all_types = ExerciseType.query.order_by(ExerciseType.muscle_group, ExerciseType.name).all()

    grouped_exercises = {}
    for etype in all_types:
        if etype.muscle_group not in grouped_exercises:
            grouped_exercises[etype.muscle_group] = []
        grouped_exercises[etype.muscle_group].append(etype.name)
    
    return render_template("add.html", exercises=grouped_exercises)

@app.route("/delete/<int:workout_id>", methods=["POST"])
def delete_workout(workout_id):
    workout_to_delete = Workout.query.get_or_404(workout_id)

    try:
        db.session.delete(workout_to_delete)
        db.session.commit()
        return redirect(url_for("index"))
    except:
        return "There was a problem deleting that workout."
    
def seed_exercise_library():
    #Populates the database with the initial exercises if they don´t exist.
    exercise_library = {
        "Chest": ["Incline Barbell Bench Press", "Incline DB Press", "Incline DB Flyes", "Flat Barbell Bench Press",
                  "Flat DB Press", "Flat DB Flyes", "Cable Fyles", "Push-ups", "Dips"],
        "Back": ["Lat Pulldown (Wide Grip)", "Lat Pulldown (V-Handle)", "Chest Supported DB Row", "Yates Row", "Pullovers",
                 "Pull-ups"],   
        "Legs": ["Barbell Squat", "Leg Extensions", "Leg Curls", "Romanian Deadlift"],
        "Shoulders": ["Lateral Raises (DB)", "Lateral Raises (Cable)", "Overhead DB Press", "Face Pulls", "Reverse Flyes"],
        "Bicep": ["Barbell Curls", "Cable Curls", "Alternating DB Curls", "Preacher Curls", "Hammer Curls", "Spider Curls"],
        "Tricep": ["Tricep Extensions", "Tricep Extentions (Underhand Grip)"],
        "Core": ["Plank", "Leg Raises", "Cable Crunches"]    
    }

    for group, exercises in exercise_library.items():
        for name in exercises:
            existing = ExerciseType.query.filter_by(name=name).first()
            if not existing:
                new_exercise = ExerciseType(name=name, muscle_group=group)
                db.session.add(new_exercise)
    
    db.session.commit()
    print("Database seeded with exercise_library!")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_exercise_library()
    app.run(debug=True)