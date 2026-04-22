from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

#CONFIGURATION
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-very-unsafe")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///workout.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#EXTENSIONS
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "index"  #Redirects to index if @login_required fails

# ==========================================
# MODELS
# ==========================================

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    #Relationship: A User has many Workouts
    workouts = db.relationship("Workout", backref="author", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)               # Linked to User

    # Relationship: A Workout has many ExerciseEntries
    entries = db.relationship("ExerciseEntry", backref="parent_workout", cascade="all, delete-orphan", lazy=True)

class ExerciseEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String(100), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey("workout.id"), nullable=False)         # Linked to Workout

    # Relationship: An ExerciseEntry has many SetRecords
    sets = db.relationship("SetRecord", backref="parent_entry", cascade="all, delete-orphan", lazy=True)

class SetRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    entry_id = db.Column(db.Integer, db.ForeignKey("exercise_entry.id"), nullable=False)    # Linked to Exercise

class ExerciseType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    muscle_group = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<ExerciseType {self.name} ({self.muscle_group})>"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==========================================
# AUTH ROUTES
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            flash("That username is already taken. Try another!", "danger")
            return redirect(url_for("register"))
        
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! You can now login.", "success")
        return redirect(url_for("index"))
    return render_template("register.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        flash(f"Logged in as {username}. Get to work!", "success")
        return redirect(url_for("index"))
    
    flash("Invalid username or password.", "danger")
    return redirect(url_for("index"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# ==========================================
# WORKOUT ROUTES
# ==========================================

@app.route("/")
def index():
    if current_user.is_authenticated:
        # Fetch ONLY the current user´s workouts
        # Because of the relationships, we just fetch workouts.
        workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date_posted.desc()).all()
        return render_template("index.html", workouts=workouts)
    return render_template("index.html")    # Template will handle showing the login form

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_workout():
    if request.method == "POST":
        title = request.form.get("title")

        new_workout = Workout(title=title, user_id=current_user.id) # Assign to user
        db.session.add(new_workout)
        db.session.flush()  #Populates new_workout.id

        # Loop through the 5 possible exercise blocks from the form
        for i in range(1, 6):
            # Each block has its own unique name attribute: ex_name_1, ex_name_2, etc.
            name = request.form.get(f"ex_name_{i}")

            if name:    # If the user selected an exercise for this block
                new_entry = ExerciseEntry(exercise_name=name, workout_id=new_workout.id)
                db.session.add(new_entry)
                db.session.flush()  #Populates new_entry.id

                # Get all weights and reps for this specific exercise block
                weights = request.form.getlist(f"weight_{i}")
                reps_list = request.form.getlist(f"reps_{i}")

                for w, r in zip(weights, reps_list):
                    # Only save the set if BOTH weight and reps are filled out
                    if w.strip() and r.strip():     # Check for empty strings
                        new_set = SetRecord(
                            weight=float(w),
                            reps=int(r),
                            entry_id=new_entry.id
                        )
                        db.session.add(new_set)
        
        db.session.commit()
        return redirect(url_for("index"))
    
    # Logic for GET request (displaying the form)
    all_types = ExerciseType.query.order_by(ExerciseType.muscle_group, ExerciseType.name).all()
    grouped_exercises = {}
    for etype in all_types:
        if etype.muscle_group not in grouped_exercises:
            grouped_exercises[etype.muscle_group] = []
        grouped_exercises[etype.muscle_group].append(etype.name)
    
    return render_template("add.html", exercises=grouped_exercises)

@app.route("/delete/<int:workout_id>", methods=["POST"])
@login_required
def delete_workout(workout_id):
    # Ensure the workout belongs to the user before deleting
    workout_to_delete = Workout.query.filter_by(id=workout_id, user_id=current_user.id).first_or_404()

    try:
        db.session.delete(workout_to_delete)
        db.session.commit()
        return redirect(url_for("index"))
    except:
        return "There was a problem deleting that workout."

# ==========================================
# DATABASE INITIALIZATION
# ==========================================
    
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