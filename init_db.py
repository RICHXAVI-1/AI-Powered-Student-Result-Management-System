"""
Database Setup and Initialization Script
Creates sample data for testing the system
"""

from app import app, db
from models.database import User, Student, Department, Course, Result, SessionSummary
from utils.grading import process_result, calculate_gpa, calculate_cgpa
from werkzeug.security import generate_password_hash
import random

def init_database():
    """Initialize database with sample data"""
    with app.app_context():
        # Drop all tables and recreate
        print("Creating database tables...")
        db.create_all()
        
        # Create Admin User
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@university.edu',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create Lecturer User
        lecturer = User(
            username='lecturer1',
            email='lecturer@university.edu',
            role='lecturer'
        )
        lecturer.set_password('lecturer123')
        db.session.add(lecturer)
        
        db.session.commit()
        
        # Create Departments
        print("Creating departments...")
        departments = [
            Department(name='Computer Science', code='CSC'),
            Department(name='Software Engineering', code='SEN'),
            Department(name='Information Technology', code='IFT'),
        ]
        
        for dept in departments:
            db.session.add(dept)
        db.session.commit()
        
        # Create Courses
        print("Creating courses...")
        csc_dept = Department.query.filter_by(code='CSC').first()
        
        courses = [
            Course(course_code='CSC301', course_title='Data Structures', credit_unit=3, 
                   semester='First', level=300, department_id=csc_dept.id),
            Course(course_code='CSC302', course_title='Algorithm Design', credit_unit=3, 
                   semester='First', level=300, department_id=csc_dept.id),
            Course(course_code='CSC303', course_title='Database Systems', credit_unit=4, 
                   semester='First', level=300, department_id=csc_dept.id),
            Course(course_code='CSC304', course_title='Operating Systems', credit_unit=3, 
                   semester='First', level=300, department_id=csc_dept.id),
            Course(course_code='CSC305', course_title='Web Development', credit_unit=3, 
                   semester='First', level=300, department_id=csc_dept.id),
            Course(course_code='CSC306', course_title='Software Engineering', credit_unit=3, 
                   semester='Second', level=300, department_id=csc_dept.id),
            Course(course_code='CSC307', course_title='Artificial Intelligence', credit_unit=4, 
                   semester='Second', level=300, department_id=csc_dept.id),
        ]
        
        for course in courses:
            db.session.add(course)
        db.session.commit()
        
        # Create Sample Students
        print("Creating sample students...")
        student_data = [
            ('CSC/2021/001', 'John', 'Doe', 'john.doe@student.edu'),
            ('CSC/2021/002', 'Jane', 'Smith', 'jane.smith@student.edu'),
            ('CSC/2021/003', 'Michael', 'Johnson', 'michael.j@student.edu'),
            ('CSC/2021/004', 'Sarah', 'Williams', 'sarah.w@student.edu'),
            ('CSC/2021/005', 'David', 'Brown', 'david.b@student.edu'),
        ]
        
        students = []
        for matric, fname, lname, email in student_data:
            # Create user account
            user = User(
                username=matric,
                email=email,
                role='student'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Create student record
            student = Student(
                matric_number=matric,
                first_name=fname,
                last_name=lname,
                email=email,
                department_id=csc_dept.id,
                level=300,
                user_id=user.id
            )
            db.session.add(student)
            students.append(student)
        
        db.session.commit()
        
        # Generate Sample Results
        print("Generating sample results...")
        session = '2023/2024'
        
        for student in students:
            # Generate results for first semester courses
            for course in courses[:5]:  # First 5 courses (First semester)
                # Generate random score with some variation
                base_score = random.randint(40, 95)
                score = base_score + random.randint(-5, 5)
                score = max(0, min(100, score))  # Keep between 0-100
                
                # Process result
                result_data = process_result(score, course.credit_unit)
                
                result = Result(
                    student_id=student.id,
                    course_id=course.id,
                    session=session,
                    score=score,
                    grade=result_data['grade'],
                    grade_point=result_data['grade_point'],
                    remarks=result_data['remarks']
                )
                db.session.add(result)
            
            db.session.commit()
            
            # Calculate and save GPA for first semester
            results = Result.query.filter_by(
                student_id=student.id,
                session=session
            ).all()
            
            gpa_data = []
            total_units = 0
            total_points = 0
            
            for result in results:
                course = Course.query.get(result.course_id)
                gpa_data.append((course.credit_unit, result.grade_point))
                total_units += course.credit_unit
                total_points += result.grade_point * course.credit_unit
            
            gpa = calculate_gpa(gpa_data)
            cgpa = calculate_cgpa(gpa_data)  # Same as GPA for first semester
            
            summary = SessionSummary(
                student_id=student.id,
                session=session,
                semester='First',
                total_units=total_units,
                total_points=total_points,
                gpa=gpa,
                cgpa=cgpa
            )
            db.session.add(summary)
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("Database initialized successfully!")
        print("="*50)
        print("\nDefault Login Credentials:")
        print("-" * 50)
        print("Admin:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nLecturer:")
        print("  Username: lecturer1")
        print("  Password: lecturer123")
        print("\nStudent (example):")
        print("  Username: CSC/2021/001")
        print("  Password: password123")
        print("="*50)
        print(f"\nTotal Students Created: {len(students)}")
        print(f"Total Courses Created: {len(courses)}")
        print(f"Total Departments Created: {len(departments)}")
        print(f"Total Results Generated: {Result.query.count()}")
        print("="*50)

if __name__ == '__main__':
    init_database()