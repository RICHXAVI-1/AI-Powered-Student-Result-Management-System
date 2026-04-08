"""
AI-Powered Student Result Management System — Adeleke University
Single-file application: models, grading utilities, ML analyzer, and all routes.
Run:  python app.py
"""

# ══════════════════════════════════════════════════════════════════════════════
# IMPORTS
# ══════════════════════════════════════════════════════════════════════════════
import os
import sys
import pickle
import random
import logging
import datetime

import numpy as np
import pandas as pd

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# PYINSTALLER-COMPATIBLE PATH RESOLUTION
#
#   BUNDLE_DIR  — where bundled assets (templates, static, ml_data) live.
#                 Inside a PyInstaller onefile EXE this is sys._MEIPASS
#                 (a temp folder); during normal dev it is the script folder.
#
#   BASE_DIR    — the folder that contains the running EXE (or script).
#                 Used for the SQLite database, which must be writable at
#                 runtime and should survive across launches.
# ══════════════════════════════════════════════════════════════════════════════
if getattr(sys, 'frozen', False):
    # Running inside a PyInstaller bundle
    BUNDLE_DIR = sys._MEIPASS
    BASE_DIR   = os.path.dirname(sys.executable)
else:
    # Normal development run
    BUNDLE_DIR = os.path.abspath(os.path.dirname(__file__))
    BASE_DIR   = BUNDLE_DIR

# ══════════════════════════════════════════════════════════════════════════════
# DATABASE MODELS
# ══════════════════════════════════════════════════════════════════════════════
db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer,     primary_key=True)
    username      = db.Column(db.String(50),  unique=True, nullable=False)
    email         = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(20),  nullable=False)   # admin | lecturer | student
    full_name     = db.Column(db.String(100), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Department(db.Model):
    __tablename__ = 'departments'
    id         = db.Column(db.Integer,    primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    code       = db.Column(db.String(10),  unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Student(db.Model):
    __tablename__ = 'students'
    id            = db.Column(db.Integer,    primary_key=True)
    matric_number = db.Column(db.String(20), unique=True, nullable=False)
    first_name    = db.Column(db.String(50), nullable=False)
    last_name     = db.Column(db.String(50), nullable=False)
    email         = db.Column(db.String(100), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    level         = db.Column(db.Integer, nullable=False)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at    = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    department = db.relationship('Department', backref='students')
    results    = db.relationship('Result', backref='student', lazy=True)


class Course(db.Model):
    __tablename__  = 'courses'
    id             = db.Column(db.Integer,    primary_key=True)
    course_code    = db.Column(db.String(20),  unique=True, nullable=False)
    course_title   = db.Column(db.String(100), nullable=False)
    credit_unit    = db.Column(db.Integer,     nullable=False)
    semester       = db.Column(db.String(10),  nullable=False)   # First | Second
    level          = db.Column(db.Integer,     nullable=False)
    department_id  = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    created_at     = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    department = db.relationship('Department', backref='courses')
    results    = db.relationship('Result', backref='course', lazy=True)


class Result(db.Model):
    __tablename__ = 'results'
    id          = db.Column(db.Integer, primary_key=True)
    student_id  = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id   = db.Column(db.Integer, db.ForeignKey('courses.id'),  nullable=False)
    session     = db.Column(db.String(20), nullable=False)
    score       = db.Column(db.Float,  nullable=False)
    grade       = db.Column(db.String(2))
    grade_point = db.Column(db.Float)
    remarks     = db.Column(db.String(50))
    # Ownership: tracks which lecturer entered this result
    entered_by  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.datetime.utcnow,
                            onupdate=datetime.datetime.utcnow)

    lecturer    = db.relationship('User', foreign_keys=[entered_by], backref='entered_results')


class DeleteNotification(db.Model):
    """Tracks deletion requests sent by admin to the owning lecturer."""
    __tablename__ = 'delete_notifications'
    id             = db.Column(db.Integer, primary_key=True)
    result_id      = db.Column(db.Integer, db.ForeignKey('results.id'), nullable=False)
    requested_by   = db.Column(db.Integer, db.ForeignKey('users.id'),   nullable=False)   # admin
    lecturer_id    = db.Column(db.Integer, db.ForeignKey('users.id'),   nullable=False)   # owner
    status         = db.Column(db.String(20), default='pending')  # pending | approved | rejected
    admin_message  = db.Column(db.String(255), nullable=True)
    lecturer_note  = db.Column(db.String(255), nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    responded_at   = db.Column(db.DateTime, nullable=True)

    result   = db.relationship('Result',  foreign_keys=[result_id])
    admin    = db.relationship('User',    foreign_keys=[requested_by])
    lecturer = db.relationship('User',    foreign_keys=[lecturer_id])


class SessionSummary(db.Model):
    __tablename__  = 'session_summaries'
    id             = db.Column(db.Integer,  primary_key=True)
    student_id     = db.Column(db.Integer,  db.ForeignKey('students.id'), nullable=False)
    session        = db.Column(db.String(20), nullable=False)
    semester       = db.Column(db.String(10), nullable=False)
    total_units    = db.Column(db.Integer)
    total_points   = db.Column(db.Float)
    gpa            = db.Column(db.Float)
    cgpa           = db.Column(db.Float)
    created_at     = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    student = db.relationship('Student', backref='summaries')


# ══════════════════════════════════════════════════════════════════════════════
# GRADING UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

def get_grade(score):
    if   score >= 70: return 'A'
    elif score >= 60: return 'B'
    elif score >= 50: return 'C'
    elif score >= 45: return 'D'
    elif score >= 40: return 'E'
    else:             return 'F'


def get_grade_point(grade):
    return {'A': 5.0, 'B': 4.0, 'C': 3.0, 'D': 2.0, 'E': 1.0, 'F': 0.0}.get(grade, 0.0)


def get_remarks(grade):
    return {'A': 'Excellent', 'B': 'Very Good', 'C': 'Good',
            'D': 'Fair',      'E': 'Pass',       'F': 'Fail'}.get(grade, 'N/A')


def calculate_gpa(results):
    """results: list of (credit_unit, grade_point) tuples."""
    if not results:
        return 0.0
    total_points = sum(cu * gp for cu, gp in results)
    total_units  = sum(cu for cu, _ in results)
    return round(total_points / total_units, 2) if total_units else 0.0


def calculate_cgpa(all_results):
    return calculate_gpa(all_results)


def process_result(score, credit_unit):
    grade    = get_grade(score)
    gp       = get_grade_point(grade)
    return {
        'grade':          grade,
        'grade_point':    gp,
        'remarks':        get_remarks(grade),
        'weighted_point': gp * credit_unit,
    }


def validate_score(score):
    try:
        return 0 <= float(score) <= 100
    except (ValueError, TypeError):
        return False


def get_class_of_degree(cgpa):
    if   cgpa >= 4.50: return 'First Class Honours'
    elif cgpa >= 3.50: return 'Second Class Honours (Upper Division)'
    elif cgpa >= 2.50: return 'Second Class Honours (Lower Division)'
    elif cgpa >= 1.50: return 'Third Class Honours'
    elif cgpa >= 1.00: return 'Pass'
    else:              return 'Fail'


# ══════════════════════════════════════════════════════════════════════════════
# ML / AI PERFORMANCE ANALYZER
# ML assets are read from BUNDLE_DIR (packed inside the EXE).
# Training data CSV is written to BASE_DIR (next to the EXE, writable).
# ══════════════════════════════════════════════════════════════════════════════
ML_DIR       = os.path.join(BUNDLE_DIR, 'ml_data')
MODEL_PATH   = os.path.join(ML_DIR, 'performance_model.pkl')
SCALER_PATH  = os.path.join(ML_DIR, 'scaler.pkl')
ENCODER_PATH = os.path.join(ML_DIR, 'label_encoder.pkl')
FEATURE_PATH = os.path.join(ML_DIR, 'feature_names.pkl')

# Writable ML dir (used when re-training or generating new data at runtime)
ML_DIR_WRITABLE = os.path.join(BASE_DIR, 'ml_data')

FEATURE_COLS = [
    'avg_score', 'prev_avg_score', 'score_trend', 'score_std',
    'failed_courses', 'gpa', 'pass_rate',
    'attendance_rate', 'study_hours_per_week', 'num_courses',
]


def _load_ml_artifacts():
    try:
        with open(MODEL_PATH,   'rb') as f: model   = pickle.load(f)
        with open(SCALER_PATH,  'rb') as f: scaler  = pickle.load(f)
        with open(ENCODER_PATH, 'rb') as f: encoder = pickle.load(f)
        return model, scaler, encoder
    except FileNotFoundError:
        return None, None, None


class PerformanceAnalyzer:
    """ML-powered performance analysis using a trained Random Forest classifier."""

    def __init__(self):
        self.model, self.scaler, self.encoder = _load_ml_artifacts()
        self._ml_ready = all(x is not None for x in [self.model, self.scaler, self.encoder])

    def _build_feature_vector(self, student_results, attendance_rate=75.0, study_hours=5.0):
        if not student_results:
            return None
        scores = [float(r['score']) for r in student_results]
        gpas   = [float(r.get('gpa', 0)) for r in student_results]
        grades = [r.get('grade', 'F') for r in student_results]

        avg_score      = np.mean(scores)
        score_std      = np.std(scores) if len(scores) > 1 else 0.0
        failed_courses = grades.count('F')
        pass_rate      = (len(grades) - failed_courses) / len(grades) * 100
        current_gpa    = gpas[-1] if gpas else 0.0
        half           = max(len(scores) // 2, 1)
        score_trend    = float(np.mean(scores[-half:])) - float(np.mean(scores[:half]))
        prev_avg_score = float(np.mean(scores[:half]))

        return pd.DataFrame([{
            'avg_score':            round(avg_score, 4),
            'prev_avg_score':       round(prev_avg_score, 4),
            'score_trend':          round(score_trend, 4),
            'score_std':            round(score_std, 4),
            'failed_courses':       failed_courses,
            'gpa':                  round(current_gpa, 4),
            'pass_rate':            round(pass_rate, 4),
            'attendance_rate':      round(attendance_rate, 4),
            'study_hours_per_week': round(study_hours, 4),
            'num_courses':          len(scores),
        }], columns=FEATURE_COLS)

    def predict_performance(self, student_results, attendance_rate=75.0, study_hours=5.0):
        if not student_results or len(student_results) < 2:
            return 'Insufficient Data'
        if not self._ml_ready:
            return 'Model Not Loaded'
        try:
            X = self._build_feature_vector(student_results, attendance_rate, study_hours)
            return self.encoder.inverse_transform(
                self.model.predict(self.scaler.transform(X)))[0]
        except Exception as e:
            logger.error(f'predict_performance error: {e}')
            return 'Prediction Error'

    def predict_performance_proba(self, student_results, attendance_rate=75.0, study_hours=5.0):
        if not student_results or not self._ml_ready:
            return {}
        try:
            X     = self._build_feature_vector(student_results, attendance_rate, study_hours)
            probs = self.model.predict_proba(self.scaler.transform(X))[0]
            return {cls: round(float(p), 4) for cls, p in zip(self.encoder.classes_, probs)}
        except Exception as e:
            logger.error(f'predict_performance_proba error: {e}')
            return {}

    def analyze_trends(self, student_results):
        if not student_results:
            return {'trend': 'No Data', 'improvement': 0, 'consistency': 0, 'average_score': 0}
        scores = [float(r['score']) for r in student_results]
        gpas   = [float(r.get('gpa', 0)) for r in student_results]
        if len(scores) >= 2:
            recent  = np.mean(scores[-3:]) if len(scores) >= 3 else scores[-1]
            earlier = np.mean(scores[:-3]) if len(scores) > 3  else scores[0]
            imp     = recent - earlier
            trend   = 'Improving' if imp > 5 else ('Declining' if imp < -5 else 'Stable')
        else:
            trend, imp = 'Insufficient Data', 0.0
        consistency = max(0.0, min(100.0, 100.0 - np.std(scores) * 2)) if len(scores) > 1 else 0.0
        return {
            'trend':         trend,
            'improvement':   round(float(imp), 2),
            'consistency':   round(float(consistency), 2),
            'average_score': round(float(np.mean(scores)), 2),
            'current_gpa':   gpas[-1] if gpas else 0,
        }

    def identify_at_risk_students(self, all_students_results):
        return [sid for sid, res in all_students_results.items()
                if res and len(res) >= 2 and self.predict_performance(res) == 'At-Risk']

    def generate_recommendations(self, student_results, current_gpa,
                                  attendance_rate=75.0, study_hours=5.0):
        if not student_results:
            return ['Insufficient data for recommendations.']
        prediction   = self.predict_performance(student_results, attendance_rate, study_hours)
        proba        = self.predict_performance_proba(student_results, attendance_rate, study_hours)
        failed_count = [r.get('grade', '') for r in student_results].count('F')

        advice = {
            'Excellent': [
                'ML Analysis: Excellent performance — keep up the outstanding work!',
                'Consider mentoring peers to reinforce and deepen your knowledge.',
            ],
            'Good': [
                'ML Analysis: Good performance. Focus on maintaining consistency.',
                'Target weak areas to move from Good to Excellent standing.',
            ],
            'Average': [
                'ML Analysis: Average performance. Increase study time and seek help proactively.',
                'Join study groups and utilise office hours for challenging topics.',
            ],
            'At-Risk': [
                'WARNING - ML Analysis: You are academically at risk. Seek immediate academic support.',
                'Meet with your lecturer and academic advisor as soon as possible.',
                'Consider enrolling in the university study-skills and time-management workshop.',
            ],
        }
        recs = list(advice.get(prediction, ['Prediction unavailable.']))
        if proba:
            conf = proba.get(prediction, 0)
            if conf < 0.6:
                recs.append(f'Note: Prediction confidence is {conf*100:.0f}%. '
                            'Submit more results for a more reliable analysis.')
        if failed_count > 0:
            recs.append(f'You have {failed_count} failed course(s). '
                        'Plan retakes and dedicate extra time to those subjects.')
        if current_gpa < 2.0:
            recs.append('Your GPA is below 2.0 — urgent action required to avoid academic probation.')
        elif current_gpa >= 4.5:
            recs.append('First Class standing! Maintain this excellence for graduation honours.')
        return recs

    def calculate_performance_metrics(self, results):
        if not results:
            return {}
        scores = [r['score'] for r in results]
        grades = [r.get('grade', '') for r in results]
        return {
            'total_courses':      len(results),
            'average_score':      round(float(np.mean(scores)), 2),
            'highest_score':      max(scores),
            'lowest_score':       min(scores),
            'score_range':        max(scores) - min(scores),
            'standard_deviation': round(float(np.std(scores)), 2),
            'passed_courses':     sum(1 for g in grades if g != 'F'),
            'failed_courses':     grades.count('F'),
            'ml_prediction':      self.predict_performance(results),
            'ml_confidence':      self.predict_performance_proba(results),
            'grade_distribution': {g: grades.count(g) for g in ['A', 'B', 'C', 'D', 'E', 'F']},
        }


# ══════════════════════════════════════════════════════════════════════════════
# FLASK APP + EXTENSIONS
# template_folder and static_folder point to BUNDLE_DIR so PyInstaller can
# find them whether the app is frozen or running in development.
# The database URI points to BASE_DIR so the DB file lives next to the EXE
# and persists across launches.
# ══════════════════════════════════════════════════════════════════════════════
app = Flask(
    __name__,
    template_folder=os.path.join(BUNDLE_DIR, 'templates'),
    static_folder=os.path.join(BUNDLE_DIR, 'static'),
)
app.config['SECRET_KEY']                  = 'adeleke-ars-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI']     = 'sqlite:///' + os.path.join(BASE_DIR, 'result_management.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

ai_analyzer = PerformanceAnalyzer()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ══════════════════════════════════════════════════════════════════════════════
# AUTO-SEED DATABASE ON FIRST RUN
# ══════════════════════════════════════════════════════════════════════════════

def _seed_defaults():
    """Create all tables and populate with seed data if the DB is brand new."""
    db.create_all()
    if User.query.count() > 0:
        return   # Already seeded — skip

    # ── Users ──────────────────────────────────────────────────────────────
    admin = User(username='admin', email='admin@university.edu',
                 role='admin', full_name='System Administrator')
    admin.set_password('admin123')

    lecturer = User(username='lecturer1', email='lecturer@university.edu',
                    role='lecturer', full_name='Dr. John Lecturer')
    lecturer.set_password('lecturer123')

    db.session.add_all([admin, lecturer])
    db.session.commit()

    # ── Departments ────────────────────────────────────────────────────────
    depts = [
        Department(name='Computer Science',       code='CSC'),
        Department(name='Software Engineering',   code='SEN'),
        Department(name='Information Technology', code='IFT'),
    ]
    db.session.add_all(depts)
    db.session.commit()

    csc = Department.query.filter_by(code='CSC').first()
    lecturer.department_id = csc.id
    db.session.commit()

    # ── Courses ────────────────────────────────────────────────────────────
    courses = [
        Course(course_code='CSC301', course_title='Data Structures',        credit_unit=3, semester='First',  level=300, department_id=csc.id),
        Course(course_code='CSC302', course_title='Algorithm Design',       credit_unit=3, semester='First',  level=300, department_id=csc.id),
        Course(course_code='CSC303', course_title='Database Systems',       credit_unit=4, semester='First',  level=300, department_id=csc.id),
        Course(course_code='CSC304', course_title='Operating Systems',      credit_unit=3, semester='First',  level=300, department_id=csc.id),
        Course(course_code='CSC305', course_title='Web Development',        credit_unit=3, semester='First',  level=300, department_id=csc.id),
        Course(course_code='CSC306', course_title='Software Engineering',   credit_unit=3, semester='Second', level=300, department_id=csc.id),
        Course(course_code='CSC307', course_title='Artificial Intelligence',credit_unit=4, semester='Second', level=300, department_id=csc.id),
    ]
    db.session.add_all(courses)
    db.session.commit()

    # ── Students & Sample Results ──────────────────────────────────────────
    student_data = [
        ('CSC/2021/001', 'John',    'Doe',      'john.doe@student.edu'),
        ('CSC/2021/002', 'Jane',    'Smith',    'jane.smith@student.edu'),
        ('CSC/2021/003', 'Michael', 'Johnson',  'michael.j@student.edu'),
        ('CSC/2021/004', 'Sarah',   'Williams', 'sarah.w@student.edu'),
        ('CSC/2021/005', 'David',   'Brown',    'david.b@student.edu'),
    ]
    students = []
    for matric, fname, lname, email in student_data:
        u = User(username=matric, email=email, role='student',
                 full_name=f'{fname} {lname}')
        u.set_password('password123')
        db.session.add(u)
        db.session.commit()

        s = Student(matric_number=matric, first_name=fname, last_name=lname,
                    email=email, department_id=csc.id, level=300, user_id=u.id)
        db.session.add(s)
        students.append(s)
    db.session.commit()

    sess              = '2023/2024'
    first_sem_courses = courses[:5]

    for student in students:
        for course in first_sem_courses:
            score = max(0, min(100, int(random.gauss(65, 15))))
            rd    = process_result(score, course.credit_unit)
            db.session.add(Result(
                student_id=student.id, course_id=course.id, session=sess,
                score=score, grade=rd['grade'], grade_point=rd['grade_point'],
                remarks=rd['remarks'],
            ))
        db.session.commit()

        all_r        = Result.query.filter_by(student_id=student.id, session=sess).all()
        gpa_data     = [(Course.query.get(r.course_id).credit_unit, r.grade_point) for r in all_r]
        total_units  = sum(cu for cu, _ in gpa_data)
        total_points = sum(cu * gp for cu, gp in gpa_data)
        db.session.add(SessionSummary(
            student_id=student.id, session=sess, semester='First',
            total_units=total_units, total_points=total_points,
            gpa=calculate_gpa(gpa_data), cgpa=calculate_cgpa(gpa_data),
        ))
    db.session.commit()


with app.app_context():
    _seed_defaults()


# ══════════════════════════════════════════════════════════════════════════════
# HELPER: Recalculate GPA/CGPA after a result is entered
# ══════════════════════════════════════════════════════════════════════════════

def update_student_summary(student_id, session, semester):
    results      = db.session.query(Result, Course).join(Course).filter(
        Result.student_id == student_id,
        Result.session    == session,
        Course.semester   == semester,
    ).all()
    gpa_data     = [(c.credit_unit, r.grade_point) for r, c in results]
    total_units  = sum(c.credit_unit for _, c in results)
    total_points = sum(r.grade_point * c.credit_unit for r, c in results)
    gpa          = calculate_gpa(gpa_data)

    all_results  = db.session.query(Result, Course).join(Course).filter(
        Result.student_id == student_id).all()
    cgpa = calculate_cgpa([(c.credit_unit, r.grade_point) for r, c in all_results])

    summary = SessionSummary.query.filter_by(
        student_id=student_id, session=session, semester=semester).first()
    if summary:
        summary.total_units  = total_units
        summary.total_points = total_points
        summary.gpa          = gpa
        summary.cgpa         = cgpa
    else:
        db.session.add(SessionSummary(
            student_id=student_id, session=session, semester=semester,
            total_units=total_units, total_points=total_points, gpa=gpa, cgpa=cgpa,
        ))
    db.session.commit()


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — AUTHENTICATION
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':    return redirect(url_for('admin_dashboard'))
        if current_user.role == 'lecturer': return redirect(url_for('lecturer_dashboard'))
        if current_user.role == 'student':  return redirect(url_for('student_dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user     = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            if user.role == 'admin':    return redirect(url_for('admin_dashboard'))
            if user.role == 'lecturer': return redirect(url_for('lecturer_dashboard'))
            if user.role == 'student':  return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — ADMIN
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    return render_template('admin_dashboard.html',
        total_students    = Student.query.count(),
        total_courses     = Course.query.count(),
        total_departments = Department.query.count(),
        total_results     = Result.query.count(),
        recent_results    = Result.query.order_by(Result.created_at.desc()).limit(10).all(),
    )


@app.route('/admin/students', methods=['GET', 'POST'])
@login_required
def manage_students():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        matric        = request.form.get('matric_number')
        first_name    = request.form.get('first_name')
        last_name     = request.form.get('last_name')
        email         = request.form.get('email')
        department_id = request.form.get('department_id')
        level         = request.form.get('level')

        user = User(username=matric, email=email, role='student',
                    full_name=f'{first_name} {last_name}')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        db.session.add(Student(
            matric_number=matric, first_name=first_name, last_name=last_name,
            email=email, department_id=department_id, level=level, user_id=user.id,
        ))
        db.session.commit()
        flash('Student added successfully', 'success')
        return redirect(url_for('manage_students'))

    return render_template('manage_students.html',
        students    = Student.query.all(),
        departments = Department.query.all(),
    )


@app.route('/admin/courses', methods=['GET', 'POST'])
@login_required
def manage_courses():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        db.session.add(Course(
            course_code   = request.form.get('course_code'),
            course_title  = request.form.get('course_title'),
            credit_unit   = request.form.get('credit_unit'),
            semester      = request.form.get('semester'),
            level         = request.form.get('level'),
            department_id = request.form.get('department_id'),
        ))
        db.session.commit()
        flash('Course added successfully', 'success')
        return redirect(url_for('manage_courses'))

    return render_template('manage_courses.html',
        courses     = Course.query.all(),
        departments = Department.query.all(),
    )


@app.route('/admin/students/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    student = Student.query.get_or_404(student_id)
    name    = f'{student.first_name} {student.last_name}'

    Result.query.filter_by(student_id=student.id).delete()
    SessionSummary.query.filter_by(student_id=student.id).delete()

    user = User.query.get(student.user_id)
    db.session.delete(student)
    if user:
        db.session.delete(user)
    db.session.commit()

    flash(f'Student "{name}" and all their records have been removed.', 'success')
    return redirect(url_for('manage_students'))


@app.route('/admin/students/edit/<int:student_id>', methods=['POST'])
@login_required
def edit_student(student_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    student = Student.query.get_or_404(student_id)
    student.first_name    = request.form.get('first_name', student.first_name)
    student.last_name     = request.form.get('last_name',  student.last_name)
    student.email         = request.form.get('email',      student.email)
    student.department_id = request.form.get('department_id', student.department_id)
    student.level         = request.form.get('level',      student.level)

    user = User.query.get(student.user_id)
    if user:
        user.email     = student.email
        user.full_name = f'{student.first_name} {student.last_name}'

    db.session.commit()
    flash(f'Student "{student.first_name} {student.last_name}" updated successfully.', 'success')
    return redirect(url_for('manage_students'))


@app.route('/admin/courses/edit/<int:course_id>', methods=['POST'])
@login_required
def edit_course(course_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    course = Course.query.get_or_404(course_id)
    course.course_code  = request.form.get('course_code',  course.course_code)
    course.course_title = request.form.get('course_title', course.course_title)
    course.credit_unit  = request.form.get('credit_unit',  course.credit_unit)
    course.semester     = request.form.get('semester',     course.semester)
    course.level        = request.form.get('level',        course.level)
    course.department_id= request.form.get('department_id',course.department_id)

    db.session.commit()
    flash(f'Course "{course.course_title}" updated successfully.', 'success')
    return redirect(url_for('manage_courses'))


@app.route('/admin/results')
@login_required
def manage_results():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    # Support filtering by student or course
    student_id = request.args.get('student_id', type=int)
    course_id  = request.args.get('course_id',  type=int)
    session_f  = request.args.get('session',    '').strip()

    query = db.session.query(Result, Student, Course)\
        .join(Student, Result.student_id == Student.id)\
        .join(Course,  Result.course_id  == Course.id)

    if student_id:
        query = query.filter(Result.student_id == student_id)
    if course_id:
        query = query.filter(Result.course_id == course_id)
    if session_f:
        query = query.filter(Result.session == session_f)

    rows     = query.order_by(Result.created_at.desc()).all()
    students = Student.query.order_by(Student.last_name).all()
    courses  = Course.query.order_by(Course.course_code).all()
    sessions = db.session.query(Result.session).distinct().order_by(Result.session.desc()).all()
    sessions = [s[0] for s in sessions]

    # Build a set of result IDs that already have a pending delete request
    pending_result_ids = {
        n.result_id for n in DeleteNotification.query.filter_by(status='pending').all()
    }

    # Count unresolved notifications for the badge
    pending_notifications_count = DeleteNotification.query.filter_by(status='pending').count()

    return render_template('manage_results.html',
        rows=rows, students=students, courses=courses, sessions=sessions,
        filter_student=student_id, filter_course=course_id, filter_session=session_f,
        pending_result_ids=pending_result_ids,
        pending_notifications_count=pending_notifications_count,
    )


@app.route('/admin/results/request-delete/<int:result_id>', methods=['POST'])
@login_required
def request_delete_result(result_id):
    """Admin initiates a deletion request; if the result has an owner lecturer,
    a notification is created and the deletion is held pending confirmation.
    If there is no owner, the admin may delete directly."""
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    result = Result.query.get_or_404(result_id)
    admin_message = request.form.get('admin_message', '').strip()

    if result.entered_by:
        # Check if a pending notification already exists
        existing_notif = DeleteNotification.query.filter_by(
            result_id=result_id, status='pending').first()
        if existing_notif:
            flash('A deletion request is already pending for this result. '
                  'Please wait for the lecturer to respond.', 'warning')
            return redirect(request.referrer or url_for('manage_results'))

        # Create notification for the owning lecturer
        notif = DeleteNotification(
            result_id=result_id,
            requested_by=current_user.id,
            lecturer_id=result.entered_by,
            status='pending',
            admin_message=admin_message or None,
        )
        db.session.add(notif)
        db.session.commit()

        lecturer_name = result.lecturer.full_name or result.lecturer.username
        flash(f'Deletion request sent to {lecturer_name}. '
              'The result will be deleted once they approve.', 'info')
    else:
        # No lecturer owner — admin can delete directly
        student_id = result.student_id
        course     = Course.query.get(result.course_id)
        session    = result.session
        db.session.delete(result)
        db.session.commit()
        if course:
            update_student_summary(student_id, session, course.semester)
        flash('Result deleted and GPA recalculated successfully.', 'success')

    return redirect(request.referrer or url_for('manage_results'))


# Keep old route name for backward compatibility (direct delete when no owner)
@app.route('/admin/results/delete/<int:result_id>', methods=['POST'])
@login_required
def delete_result(result_id):
    return request_delete_result(result_id)


@app.route('/admin/results/notifications')
@login_required
def admin_delete_notifications():
    """Admin view of all pending/resolved deletion requests."""
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    notifications = DeleteNotification.query\
        .order_by(DeleteNotification.created_at.desc()).all()
    return render_template('admin_delete_notifications.html',
                           notifications=notifications)


# ── LECTURER ROUTES FOR DELETION CONFIRMATION ──────────────────────────────

@app.route('/lecturer/delete-requests')
@login_required
def lecturer_delete_requests():
    """Lecturer sees their pending (and past) deletion requests."""
    if current_user.role != 'lecturer':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    notifications = DeleteNotification.query.filter_by(
        lecturer_id=current_user.id
    ).order_by(DeleteNotification.created_at.desc()).all()
    return render_template('lecturer_delete_requests.html',
                           notifications=notifications)


@app.route('/lecturer/delete-requests/<int:notif_id>/respond', methods=['POST'])
@login_required
def respond_delete_request(notif_id):
    """Lecturer approves or rejects a deletion request."""
    if current_user.role != 'lecturer':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    notif = DeleteNotification.query.get_or_404(notif_id)
    if notif.lecturer_id != current_user.id:
        flash('This request is not assigned to you.', 'error')
        return redirect(url_for('lecturer_delete_requests'))
    if notif.status != 'pending':
        flash('This request has already been responded to.', 'warning')
        return redirect(url_for('lecturer_delete_requests'))

    decision      = request.form.get('decision')          # 'approve' | 'reject'
    lecturer_note = request.form.get('lecturer_note', '').strip()

    notif.responded_at   = datetime.datetime.utcnow()
    notif.lecturer_note  = lecturer_note or None

    if decision == 'approve':
        notif.status = 'approved'
        # Perform the actual deletion now
        result = Result.query.get(notif.result_id)
        if result:
            student_id = result.student_id
            course     = Course.query.get(result.course_id)
            session    = result.session
            db.session.delete(result)
            db.session.commit()
            if course:
                update_student_summary(student_id, session, course.semester)
        db.session.commit()
        flash('You approved the deletion. The result has been removed and GPA recalculated.', 'success')
    else:
        notif.status = 'rejected'
        db.session.commit()
        flash('You rejected the deletion request. The result remains intact.', 'info')

    return redirect(url_for('lecturer_delete_requests'))


@app.route('/admin/courses/delete/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    course = Course.query.get_or_404(course_id)
    title  = course.course_title

    Result.query.filter_by(course_id=course.id).delete()
    db.session.delete(course)
    db.session.commit()

    flash(f'Course "{title}" and all associated results have been removed.', 'success')
    return redirect(url_for('manage_courses'))


@app.route('/admin/departments', methods=['GET', 'POST'])
@login_required
def manage_departments():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip().upper()

        if not name or not code:
            flash('Department name and code are required.', 'error')
            return redirect(url_for('manage_departments'))
        if Department.query.filter_by(code=code).first():
            flash(f'Department code "{code}" already exists.', 'error')
            return redirect(url_for('manage_departments'))
        if Department.query.filter_by(name=name).first():
            flash(f'Department "{name}" already exists.', 'error')
            return redirect(url_for('manage_departments'))

        db.session.add(Department(name=name, code=code))
        db.session.commit()
        flash(f'Department "{name}" ({code}) added successfully.', 'success')
        return redirect(url_for('manage_departments'))

    departments = Department.query.order_by(Department.created_at.desc()).all()
    dept_info = []
    for dept in departments:
        dept_info.append({
            'dept':           dept,
            'student_count':  Student.query.filter_by(department_id=dept.id).count(),
            'course_count':   Course.query.filter_by(department_id=dept.id).count(),
            'lecturer_count': User.query.filter_by(role='lecturer', department_id=dept.id).count(),
        })
    return render_template('manage_departments.html', dept_info=dept_info)


@app.route('/admin/departments/delete/<int:dept_id>', methods=['POST'])
@login_required
def delete_department(dept_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    dept = Department.query.get_or_404(dept_id)
    name = dept.name

    students = Student.query.filter_by(department_id=dept.id).all()
    for student in students:
        Result.query.filter_by(student_id=student.id).delete()
        SessionSummary.query.filter_by(student_id=student.id).delete()
        user = User.query.get(student.user_id)
        db.session.delete(student)
        if user:
            db.session.delete(user)

    courses = Course.query.filter_by(department_id=dept.id).all()
    for course in courses:
        Result.query.filter_by(course_id=course.id).delete()
        db.session.delete(course)

    User.query.filter_by(role='lecturer', department_id=dept.id).update(
        {'department_id': None})

    db.session.delete(dept)
    db.session.commit()
    flash(f'Department "{name}" and all its students, courses, and results have been deleted.', 'success')
    return redirect(url_for('manage_departments'))


@app.route('/admin/lecturers', methods=['GET', 'POST'])
@login_required
def manage_lecturers():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username      = request.form.get('username', '').strip()
        full_name     = request.form.get('full_name', '').strip()
        email         = request.form.get('email', '').strip()
        password      = request.form.get('password', '').strip()
        department_id = request.form.get('department_id')

        if not all([username, full_name, email, password]):
            flash('All fields are required.', 'error')
            return redirect(url_for('manage_lecturers'))
        if User.query.filter_by(username=username).first():
            flash(f'Username "{username}" is already taken.', 'error')
            return redirect(url_for('manage_lecturers'))
        if User.query.filter_by(email=email).first():
            flash(f'Email "{email}" is already registered.', 'error')
            return redirect(url_for('manage_lecturers'))

        user = User(username=username, email=email, role='lecturer',
                    full_name=full_name,
                    department_id=int(department_id) if department_id else None)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f'Lecturer "{full_name}" added. Login: {username} / {password}', 'success')
        return redirect(url_for('manage_lecturers'))

    return render_template('manage_lecturers.html',
        lecturers   = User.query.filter_by(role='lecturer').order_by(User.created_at.desc()).all(),
        departments = Department.query.all(),
    )


@app.route('/admin/lecturers/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_lecturer(user_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    lecturer = User.query.get_or_404(user_id)
    if lecturer.role != 'lecturer':
        flash('That user is not a lecturer.', 'error')
        return redirect(url_for('manage_lecturers'))
    name = lecturer.full_name or lecturer.username
    db.session.delete(lecturer)
    db.session.commit()
    flash(f'Lecturer "{name}" has been removed.', 'success')
    return redirect(url_for('manage_lecturers'))


@app.route('/admin/analytics')
@login_required
def analytics():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    students             = Student.query.all()
    all_students_results = {}
    for student in students:
        results = Result.query.filter_by(student_id=student.id).all()
        if results:
            all_students_results[student.id] = [{
                'score': r.score,
                'grade': r.grade,
                'gpa':   (SessionSummary.query.filter_by(
                              student_id=student.id, session=r.session).first()
                          or type('_', (), {'gpa': 0})()).gpa,
            } for r in results]

    at_risk_ids      = ai_analyzer.identify_at_risk_students(all_students_results)
    at_risk_students = Student.query.filter(Student.id.in_(at_risk_ids)).all()
    return render_template('analytics.html',
        at_risk_students = at_risk_students,
        total_students   = len(students),
        total_at_risk    = len(at_risk_students),
    )


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — LECTURER
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/lecturer/dashboard')
@login_required
def lecturer_dashboard():
    if current_user.role != 'lecturer':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    pending_requests = DeleteNotification.query.filter_by(
        lecturer_id=current_user.id, status='pending').count()
    return render_template('lecturer_dashboard.html',
                           courses=Course.query.all(),
                           pending_requests=pending_requests)


@app.route('/lecturer/enter-results', methods=['GET', 'POST'])
@login_required
def enter_results():
    if current_user.role != 'lecturer':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        course_id  = request.form.get('course_id')
        sess       = request.form.get('session')
        score      = float(request.form.get('score'))

        if not validate_score(score):
            flash('Invalid score. Must be between 0 and 100', 'error')
            return redirect(url_for('enter_results'))

        course      = Course.query.get(course_id)
        result_data = process_result(score, course.credit_unit)

        existing = Result.query.filter_by(
            student_id=student_id, course_id=course_id, session=sess).first()
        if existing:
            existing.score       = score
            existing.grade       = result_data['grade']
            existing.grade_point = result_data['grade_point']
            existing.remarks     = result_data['remarks']
            existing.entered_by  = current_user.id   # update ownership on edit
            existing.updated_at  = datetime.datetime.utcnow()
        else:
            db.session.add(Result(
                student_id=student_id, course_id=course_id, session=sess,
                score=score, grade=result_data['grade'],
                grade_point=result_data['grade_point'], remarks=result_data['remarks'],
                entered_by=current_user.id,            # record ownership
            ))
        db.session.commit()
        update_student_summary(student_id, sess, course.semester)
        flash('Result entered successfully', 'success')
        return redirect(url_for('enter_results'))

    return render_template('enter_results.html',
        students = Student.query.all(),
        courses  = Course.query.all(),
    )


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — STUDENT
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('index'))

    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('Student record not found', 'error')
        return redirect(url_for('index'))

    results     = Result.query.filter_by(student_id=student.id).all()
    result_data = [{
        'score': r.score,
        'grade': r.grade,
        'gpa':   (SessionSummary.query.filter_by(
                      student_id=student.id, session=r.session).first()
                  or type('_', (), {'gpa': 0})()).gpa,
    } for r in results]

    latest_summary = SessionSummary.query.filter_by(
        student_id=student.id).order_by(SessionSummary.created_at.desc()).first()
    cgpa = latest_summary.cgpa if latest_summary else 0.0

    return render_template('student_dashboard.html',
        student         = student,
        results         = results,
        cgpa            = cgpa,
        prediction      = ai_analyzer.predict_performance(result_data),
        trends          = ai_analyzer.analyze_trends(result_data),
        recommendations = ai_analyzer.generate_recommendations(result_data, cgpa),
        metrics         = ai_analyzer.calculate_performance_metrics(result_data),
    )


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — API
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/api/student-performance/<int:student_id>')
@login_required
def api_student_performance(student_id):
    student     = Student.query.get_or_404(student_id)
    results     = Result.query.filter_by(student_id=student_id).all()
    result_data = [{'score': r.score, 'grade': r.grade,
                    'course': r.course.course_code, 'session': r.session}
                   for r in results]
    return jsonify({
        'student': {'name': f'{student.first_name} {student.last_name}',
                    'matric': student.matric_number},
        'metrics': ai_analyzer.calculate_performance_metrics(result_data),
        'results': result_data,
    })


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — ML CONTROL PANEL (Admin only)
# New data and retrained models are saved to ML_DIR_WRITABLE (next to the EXE)
# so the frozen bundle is never written to.
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/admin/ml/status')
@login_required
def ml_status():
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403

    csv_path     = os.path.join(ML_DIR_WRITABLE, 'student_training_data.csv')
    model_exists = os.path.exists(MODEL_PATH)
    csv_exists   = os.path.exists(csv_path)
    model_mtime  = None
    csv_rows     = None

    if model_exists:
        model_mtime = datetime.datetime.fromtimestamp(
            os.path.getmtime(MODEL_PATH)).strftime('%Y-%m-%d %H:%M')
    if csv_exists:
        try:
            csv_rows = len(pd.read_csv(csv_path))
        except Exception:
            csv_rows = '?'

    return jsonify({
        'model_exists':  model_exists,
        'csv_exists':    csv_exists,
        'model_trained': model_mtime,
        'csv_rows':      csv_rows,
    })


@app.route('/admin/ml/generate', methods=['POST'])
@login_required
def ml_generate_data():
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403

    try:
        n_samples = max(200, min(5000, int(request.form.get('n_samples', 1000))))
        np.random.seed(42)

        def _g(s):
            if s>=70: return 'A'
            elif s>=60: return 'B'
            elif s>=50: return 'C'
            elif s>=45: return 'D'
            elif s>=40: return 'E'
            else: return 'F'

        def _gp(g): return {'A':5,'B':4,'C':3,'D':2,'E':1,'F':0}.get(g, 0)

        def _calc_gpa(sc, cu):
            t = sum(cu)
            return round(sum(_gp(_g(s))*c for s,c in zip(sc,cu))/t, 2) if t else 0.0

        def _label(avg, fails, gpa, trend):
            if   avg>=68 and fails==0 and gpa>=3.5: return 'Excellent'
            elif avg>=55 and fails<=1 and gpa>=2.5 and trend>=-3: return 'Good'
            elif avg>=45 and fails<=2 and gpa>=1.5: return 'Average'
            else: return 'At-Risk'

        archetypes = [(78,6,.15),(68,7,.25),(57,8,.30),(47,9,.20),(35,10,.10)]
        records    = []
        for i in range(n_samples):
            idx     = np.random.choice(len(archetypes), p=[a[2] for a in archetypes])
            ms, ss, _ = archetypes[idx]
            nc      = np.random.randint(4, 8)
            cu      = np.random.choice([2,3,4], size=nc)
            sc      = np.clip(np.random.normal(ms, ss, nc), 0, 100).astype(int).tolist()
            att     = float(np.clip(np.random.normal(75+(ms-55)*.3, 10), 20, 100))
            sh      = float(np.clip(np.random.normal(2+(ms-40)*.08, 1.5), 0, 12))
            avg     = round(float(np.mean(sc)), 2)
            fails   = sum(1 for s in sc if s < 40)
            gpa     = _calc_gpa(sc, cu.tolist())
            prev    = round(float(np.clip(avg + np.random.normal(0,5), 0, 100)), 2)
            trend   = avg - prev
            records.append({
                'student_id':           f'STU{1001+i}',
                'department':           np.random.choice(['Computer Science','Engineering','Business','Medicine','Law','Arts']),
                'level':                np.random.choice([100,200,300,400]),
                'semester':             np.random.choice(['First','Second']),
                'num_courses':          nc,
                'avg_score':            avg,
                'prev_avg_score':       prev,
                'score_trend':          round(trend, 2),
                'score_std':            round(float(np.std(sc)), 2),
                'failed_courses':       fails,
                'gpa':                  gpa,
                'pass_rate':            round((nc-fails)/nc*100, 2),
                'attendance_rate':      round(att, 2),
                'study_hours_per_week': round(sh, 2),
                'performance_label':    _label(avg, fails, gpa, trend),
            })

        df = pd.DataFrame(records)
        os.makedirs(ML_DIR_WRITABLE, exist_ok=True)
        csv_out = os.path.join(ML_DIR_WRITABLE, 'student_training_data.csv')
        df.to_csv(csv_out, index=False)

        return jsonify({
            'success':      True,
            'message':      f'Generated {n_samples} training records successfully.',
            'rows':         n_samples,
            'distribution': df['performance_label'].value_counts().to_dict(),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/ml/train', methods=['POST'])
@login_required
def ml_train_model():
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403

    try:
        csv_path = os.path.join(ML_DIR_WRITABLE, 'student_training_data.csv')
        if not os.path.exists(csv_path):
            return jsonify({'success': False,
                            'error': 'Training data not found. Generate data first.'}), 400

        df    = pd.read_csv(csv_path)
        X     = df[FEATURE_COLS]
        y     = df['performance_label']
        le    = LabelEncoder()
        y_enc = le.fit_transform(y)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_enc, test_size=0.2, random_state=42, stratify=y_enc)

        scaler    = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s  = scaler.transform(X_test)

        n_estimators = max(50, min(500, int(request.form.get('n_estimators', 200))))
        rf = RandomForestClassifier(
            n_estimators=n_estimators, max_depth=12,
            min_samples_split=4, min_samples_leaf=2,
            class_weight='balanced', random_state=42, n_jobs=-1)
        rf.fit(X_train_s, y_train)

        cv_scores = cross_val_score(rf, X_train_s, y_train, cv=5, scoring='accuracy')
        y_pred    = rf.predict(X_test_s)
        test_acc  = float(accuracy_score(y_test, y_pred))
        report    = classification_report(y_test, y_pred,
                                          target_names=le.classes_, output_dict=True)

        # Save retrained models to writable dir (next to the EXE)
        os.makedirs(ML_DIR_WRITABLE, exist_ok=True)
        w_model   = os.path.join(ML_DIR_WRITABLE, 'performance_model.pkl')
        w_scaler  = os.path.join(ML_DIR_WRITABLE, 'scaler.pkl')
        w_encoder = os.path.join(ML_DIR_WRITABLE, 'label_encoder.pkl')
        w_feature = os.path.join(ML_DIR_WRITABLE, 'feature_names.pkl')
        for path, obj in [(w_model, rf), (w_scaler, scaler),
                          (w_encoder, le), (w_feature, FEATURE_COLS)]:
            with open(path, 'wb') as f:
                pickle.dump(obj, f)

        global ai_analyzer
        ai_analyzer = PerformanceAnalyzer()

        importances = dict(sorted(
            {f: round(float(v), 4) for f, v in zip(FEATURE_COLS, rf.feature_importances_)}.items(),
            key=lambda x: x[1], reverse=True))

        return jsonify({
            'success':            True,
            'test_accuracy':      round(test_acc * 100, 2),
            'cv_accuracy':        round(float(cv_scores.mean()) * 100, 2),
            'cv_std':             round(float(cv_scores.std()) * 100, 2),
            'n_estimators':       n_estimators,
            'training_rows':      len(df),
            'per_class':          {cls: {
                                        'precision': round(report[cls]['precision'], 3),
                                        'recall':    round(report[cls]['recall'], 3),
                                        'f1':        round(report[cls]['f1-score'], 3),
                                        'support':   int(report[cls]['support']),
                                   } for cls in le.classes_},
            'feature_importance': importances,
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def find_free_port(start=5000, end=65535):
    """Find the first available TCP port in the given range."""
    import socket
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise RuntimeError('No free port found in range.')


if __name__ == '__main__':
    import time
    import threading

    port = find_free_port()
    url  = f'http://127.0.0.1:{port}'
    print(f'[INFO] Starting server on {url}')

    # ── Try to open a native desktop window via pywebview ──────────────────
    try:
        import webview

        def _run_flask():
            app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)

        flask_thread = threading.Thread(target=_run_flask, daemon=True)
        flask_thread.start()

        # Give Flask a moment to start before pywebview tries to load the URL.
        # This is especially important inside a PyInstaller onefile EXE where
        # startup is slightly slower than in normal development.
        time.sleep(1.5)

        webview.create_window(
            'Student Result Management System — Adeleke University',
            url,
            width=1280,
            height=820,
            resizable=True,
        )
        webview.start()

    except ImportError:
        # pywebview not installed — fall back to regular browser launch
        import webbrowser
        def _open_browser():
            time.sleep(1)
            webbrowser.open(url)
        threading.Thread(target=_open_browser, daemon=True).start()
        app.run(debug=True, host='0.0.0.0', port=port)