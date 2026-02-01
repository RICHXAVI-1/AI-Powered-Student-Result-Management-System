"""
AI-Powered Student Result Management System
Main Application File
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models.database import db, User, Student, Department, Course, Result, SessionSummary
from utils.grading import *
from utils.ai_analyzer import PerformanceAnalyzer
import os
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:your_database_password@localhost/result_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize AI analyzer
ai_analyzer = PerformanceAnalyzer()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'lecturer':
            return redirect(url_for('lecturer_dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('student_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'lecturer':
                return redirect(url_for('lecturer_dashboard'))
            elif user.role == 'student':
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Statistics
    total_students = Student.query.count()
    total_courses = Course.query.count()
    total_departments = Department.query.count()
    total_results = Result.query.count()
    
    # Recent activities
    recent_results = Result.query.order_by(Result.created_at.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html',
                         total_students=total_students,
                         total_courses=total_courses,
                         total_departments=total_departments,
                         total_results=total_results,
                         recent_results=recent_results)

@app.route('/lecturer/dashboard')
@login_required
def lecturer_dashboard():
    """Lecturer dashboard"""
    if current_user.role != 'lecturer':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    courses = Course.query.all()
    return render_template('lecturer_dashboard.html', courses=courses)

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    """Student dashboard"""
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get student record
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if not student:
        flash('Student record not found', 'error')
        return redirect(url_for('index'))
    
    # Get all results
    results = Result.query.filter_by(student_id=student.id).all()
    
    # Calculate current semester GPA and CGPA
    current_session = "2023/2024"  # This should be dynamic
    semester_results = [r for r in results if r.session == current_session]
    
    # Prepare data for AI analysis
    result_data = [{
        'score': r.score,
        'grade': r.grade,
        'gpa': SessionSummary.query.filter_by(
            student_id=student.id,
            session=r.session
        ).first().gpa if SessionSummary.query.filter_by(
            student_id=student.id,
            session=r.session
        ).first() else 0
    } for r in results]
    
    # AI Analysis
    performance_prediction = ai_analyzer.predict_performance(result_data)
    trend_analysis = ai_analyzer.analyze_trends(result_data)
    
    # Get latest CGPA
    latest_summary = SessionSummary.query.filter_by(student_id=student.id).order_by(
        SessionSummary.created_at.desc()
    ).first()
    
    cgpa = latest_summary.cgpa if latest_summary else 0.0
    
    recommendations = ai_analyzer.generate_recommendations(result_data, cgpa)
    metrics = ai_analyzer.calculate_performance_metrics(result_data)
    
    return render_template('student_dashboard.html',
                         student=student,
                         results=results,
                         cgpa=cgpa,
                         prediction=performance_prediction,
                         trends=trend_analysis,
                         recommendations=recommendations,
                         metrics=metrics)

@app.route('/admin/students', methods=['GET', 'POST'])
@login_required
def manage_students():
    """Manage students"""
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Add new student
        matric = request.form.get('matric_number')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        department_id = request.form.get('department_id')
        level = request.form.get('level')
        
        # Create user account
        user = User(
            username=matric,
            email=email,
            role='student'
        )
        user.set_password('password123')  # Default password
        
        db.session.add(user)
        db.session.commit()
        
        # Create student record
        student = Student(
            matric_number=matric,
            first_name=first_name,
            last_name=last_name,
            email=email,
            department_id=department_id,
            level=level,
            user_id=user.id
        )
        
        db.session.add(student)
        db.session.commit()
        
        flash('Student added successfully', 'success')
        return redirect(url_for('manage_students'))
    
    students = Student.query.all()
    departments = Department.query.all()
    return render_template('manage_students.html', students=students, departments=departments)

@app.route('/admin/courses', methods=['GET', 'POST'])
@login_required
def manage_courses():
    """Manage courses"""
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        course = Course(
            course_code=request.form.get('course_code'),
            course_title=request.form.get('course_title'),
            credit_unit=request.form.get('credit_unit'),
            semester=request.form.get('semester'),
            level=request.form.get('level'),
            department_id=request.form.get('department_id')
        )
        
        db.session.add(course)
        db.session.commit()
        
        flash('Course added successfully', 'success')
        return redirect(url_for('manage_courses'))
    
    courses = Course.query.all()
    departments = Department.query.all()
    return render_template('manage_courses.html', courses=courses, departments=departments)

@app.route('/lecturer/enter-results', methods=['GET', 'POST'])
@login_required
def enter_results():
    """Enter student results"""
    if current_user.role != 'lecturer':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        course_id = request.form.get('course_id')
        session = request.form.get('session')
        score = float(request.form.get('score'))
        
        # Validate score
        if not validate_score(score):
            flash('Invalid score. Must be between 0 and 100', 'error')
            return redirect(url_for('enter_results'))
        
        # Get course details
        course = Course.query.get(course_id)
        
        # Process result
        result_data = process_result(score, course.credit_unit)
        
        # Check if result already exists
        existing = Result.query.filter_by(
            student_id=student_id,
            course_id=course_id,
            session=session
        ).first()
        
        if existing:
            # Update existing result
            existing.score = score
            existing.grade = result_data['grade']
            existing.grade_point = result_data['grade_point']
            existing.remarks = result_data['remarks']
            existing.updated_at = datetime.utcnow()
        else:
            # Create new result
            result = Result(
                student_id=student_id,
                course_id=course_id,
                session=session,
                score=score,
                grade=result_data['grade'],
                grade_point=result_data['grade_point'],
                remarks=result_data['remarks']
            )
            db.session.add(result)
        
        db.session.commit()
        
        # Recalculate GPA/CGPA
        update_student_summary(student_id, session, course.semester)
        
        flash('Result entered successfully', 'success')
        return redirect(url_for('enter_results'))
    
    students = Student.query.all()
    courses = Course.query.all()
    return render_template('enter_results.html', students=students, courses=courses)

def update_student_summary(student_id, session, semester):
    """Update student's GPA and CGPA"""
    # Get all results for this session and semester
    results = db.session.query(Result, Course).join(Course).filter(
        Result.student_id == student_id,
        Result.session == session,
        Course.semester == semester
    ).all()
    
    # Calculate GPA
    gpa_data = [(course.credit_unit, result.grade_point) for result, course in results]
    gpa = calculate_gpa(gpa_data)
    
    # Get all previous results for CGPA
    all_results = db.session.query(Result, Course).join(Course).filter(
        Result.student_id == student_id
    ).all()
    
    cgpa_data = [(course.credit_unit, result.grade_point) for result, course in all_results]
    cgpa = calculate_cgpa(cgpa_data)
    
    # Update or create session summary
    summary = SessionSummary.query.filter_by(
        student_id=student_id,
        session=session,
        semester=semester
    ).first()
    
    total_units = sum(course.credit_unit for _, course in results)
    total_points = sum(result.grade_point * course.credit_unit for result, course in results)
    
    if summary:
        summary.total_units = total_units
        summary.total_points = total_points
        summary.gpa = gpa
        summary.cgpa = cgpa
    else:
        summary = SessionSummary(
            student_id=student_id,
            session=session,
            semester=semester,
            total_units=total_units,
            total_points=total_points,
            gpa=gpa,
            cgpa=cgpa
        )
        db.session.add(summary)
    
    db.session.commit()

@app.route('/admin/analytics')
@login_required
def analytics():
    """AI-powered analytics dashboard"""
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get all students with their results
    students = Student.query.all()
    all_students_results = {}
    
    for student in students:
        results = Result.query.filter_by(student_id=student.id).all()
        if results:
            all_students_results[student.id] = [{
                'score': r.score,
                'grade': r.grade,
                'gpa': SessionSummary.query.filter_by(
                    student_id=student.id,
                    session=r.session
                ).first().gpa if SessionSummary.query.filter_by(
                    student_id=student.id,
                    session=r.session
                ).first() else 0
            } for r in results]
    
    # Identify at-risk students
    at_risk_ids = ai_analyzer.identify_at_risk_students(all_students_results)
    at_risk_students = Student.query.filter(Student.id.in_(at_risk_ids)).all()
    
    # Overall performance statistics
    total_students = len(students)
    total_at_risk = len(at_risk_students)
    
    return render_template('analytics.html',
                         at_risk_students=at_risk_students,
                         total_students=total_students,
                         total_at_risk=total_at_risk)

@app.route('/api/student-performance/<int:student_id>')
@login_required
def api_student_performance(student_id):
    """API endpoint for student performance data"""
    student = Student.query.get_or_404(student_id)
    results = Result.query.filter_by(student_id=student_id).all()
    
    result_data = [{
        'score': r.score,
        'grade': r.grade,
        'course': r.course.course_code,
        'session': r.session
    } for r in results]
    
    metrics = ai_analyzer.calculate_performance_metrics(result_data)
    
    return jsonify({
        'student': {
            'name': f"{student.first_name} {student.last_name}",
            'matric': student.matric_number
        },
        'metrics': metrics,
        'results': result_data
    })

@app.route('/init-db')
def init_database():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@university.edu', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create sample department
            dept = Department(name='Computer Science', code='CSC')
            db.session.add(dept)
            
            db.session.commit()
            
        return jsonify({'message': 'Database initialized successfully'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)