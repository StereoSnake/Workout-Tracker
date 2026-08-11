# 🏋️ Workout Tracker (v.1.4.1)

A secured, full-stack Flask application designed for high-precision training logs. Evolving from a "30 Days of Python" challenge, this project features a 4-tier relational database, secure user authentication, and a modern dashboard UI. IronSheet has evolved into a complete web application featuring a Figma-aligned dark UI, native date tracking with retrofitting support, static asset integration, custom dropdown controls, and robust CSRF-protected backend mapping.

## 📁 Project Structure

The application follows standard Flask conventions, now featuring environment security and a dashboard-centric layout:

```text
.
├── app.py               # Main application logic, 4-tier Models, and Routes
├── .env                 # Secured Environment Variables (Secret Keys, DB URL)
├── .gitignore           # Shields .env, venv, and database binaries from VCS
├── requirements.txt     # Project dependencies (Flask, SQLAlchemy, WTForms, etc.)
├── instance/            # Local SQLite storage
├── static/
│   ├── style.css        # Custom dark-theme CSS architecture & custom inputs
│   └── icons/           # SVG asset library for navigation & action items
└── templates/           # Jinja2 HTML views
    ├── index.html       # History dashboard & login interface
    ├── add.html         # Grouped exercise selection & set logging form
    └── register.html    # User registration view
```

## 🚀 Version 1.4.1 New Features & Layout Refactor

* **Backtrack & Past Workout Logging:** Updated database schema and form handlers to decoupling creation timestamps from performance dates. Users can now record historical workouts by specifying the date performed.
* **Figma Layer-Tree Alignment:** Rebuilt ``add.html`` and overhauled ``style.css`` to match exact Figma layer trees (``add-workout-header``, ``add-workout-title``, and ``add-workout-date``), creating a clean, side-by-side header control.
* **Interactive Native Date Picker:** Configured native ``<input type="date">`` controls with dark-mode overrides and full-container click targets for intuitive calendar picking across desktop and mobile browsers.


## 🛠️ Technical Challenges & Solutions

During development, I encountered and solved several technical hurdles:
1. **Translating Figma Designs to a Responsive CSS Component Architecture**

   * **The Challenge:** Transferring exact pixel dimensions, fixed card heights, and precise spacing from static Figma frames into standard HTML often leads to rigid layouts. Rigid pixel layouts break on smaller viewports, cause element overlap when long exercise names are selected, or misalign input fields across rows.
   * **The Solution:** Implemented a fluid flexbox layout with custom CSS custom properties (variables) derived directly from the Figma color palette and grid. By replacing fixed pixel dimensions with dynamic sizing (``width: 100%``, flex containers, and relative ``rem/em`` spacing), components retain the clean visual hierarchy of the Figma file while remaining responsive across desktop and mobile screens.

2. **Decoupling Creation Timestamps for Historical Logging**

   * **The Challenge:** Relying solely on ``datetime.now()`` for ``date_posted`` meant all workouts were logged under the exact moment they were saved, preventing users from entering training logs from previous days.
   * **The Solution:** Introduced a dedicated ``db.Date`` column (``date``) on the ``Workout`` model, defaulting to today's date if left blank while preserving ``date_posted`` for audit metadata. Sorting on ``index.html`` was updated to order logs by ``Workout.date.desc()`` so historical entries seamlessly slot into chronological order in the user's timeline.


## 🛤️ Future Roadmap

* **Database Migrations:** Integrating ``Flask-Migrate`` (Alembic) to handle schema updates automatically without resetting database files.
* **N+1 Optimization:** Implementing ``joinedload`` to improve database performance by reducing the number of queries needed to display the history log.
* **Dynamic Set Injection:** Using Vanilla JS to allow users to add/remove sets and exercises on the fly without page refreshes.

## 🔧 Setup Instructions

1. **Clone the repository.**
2. **Create a virtual environment:** ``python -m venv venv``
3. **Activate the environment:**
   * Windows: ``venv\Scripts\activate``
   * macOS/Linux: ``source venv/bin/activate``
4. **Install dependencies:** ``pip install -r requirements.txt``
5. **Configure Environment:**
    * Create a ``.env`` file in the root directory.
    * Add: ``SECRET_KEY=your_random_string``
6. **Initialize Database:** (Crucial: Delete any existing ``workout.db`` or ``instance/workout.db`` file to allow ``db.create_all()`` to generate the updated schema with the new ``date`` column).
7. **Run the app:** ``python app.py``