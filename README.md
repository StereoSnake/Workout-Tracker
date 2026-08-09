# 🏋️ Workout Tracker (v.1.4.0)

A secured, full-stack Flask application designed for high-precision training logs. Evolving from a "30 Days of Python" challenge, this project now features a 4-tier relational database, secure user authentication, and a modern dashboard UI. IronSheet has evolved into a complete, modern web application featuring a Figma-aligned dark UI, static asset integration, custom dropdown controls, and robust CSRF-protected backend mapping.

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

## 🚀 Version 1.4.0 New Features & Design Overhaul

* **Figma-Aligned UI Redesign:** Rebuilt all HTML views (``add.html``, ``index.html``) and overhauled ``style.css`` with a custom dark theme design system, elevated card layouts, and refined typography.
* **SVG Asset Pipeline:** Integrated dedicated SVG icons (``static/icons/``) for navigation, workout actions, and responsive UI elements.


## 🛠️ Technical Challenges & Solutions

During development, I encountered and solved several technical hurdles:
1. **Translating Figma Designs to a Responsive CSS Component Architecture**

   * **The Challenge:** Transferring exact pixel dimensions, fixed card heights, and precise spacing from static Figma frames into standard HTML often leads to rigid layouts. Rigid pixel layouts break on smaller viewports, cause element overlap when long exercise names are selected, or misalign input fields across rows.
   * **The Solution:** Implemented a fluid flexbox layout with custom CSS custom properties (variables) derived directly from the Figma color palette and grid. By replacing fixed pixel dimensions with dynamic sizing (``width: 100%``, flex containers, and relative ``rem/em`` spacing), components retain the clean visual hierarchy of the Figma file while remaining responsive across desktop and mobile screens.


## 🛤️ Future Roadmap

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
6. **Initialize Database:** (Crucial: Delete any ``workout.db`` from v1.2.0 to allow the new schema to generate).
7. **Run the app:** ``python app.py``