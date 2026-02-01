"""
Grading utility module for automated result computation
Based on Adeleke University grading scale
"""

def get_grade(score):
    """
    Convert numerical score to letter grade
    """
    if score >= 70:
        return 'A'
    elif score >= 60:
        return 'B'
    elif score >= 50:
        return 'C'
    elif score >= 45:
        return 'D'
    elif score >= 40:
        return 'E'
    else:
        return 'F'

def get_grade_point(grade):
    """
    Convert letter grade to grade point
    """
    grade_points = {
        'A': 5.0,
        'B': 4.0,
        'C': 3.0,
        'D': 2.0,
        'E': 1.0,
        'F': 0.0
    }
    return grade_points.get(grade, 0.0)

def get_remarks(grade):
    """
    Get remarks based on grade
    """
    remarks_map = {
        'A': 'Excellent',
        'B': 'Very Good',
        'C': 'Good',
        'D': 'Fair',
        'E': 'Pass',
        'F': 'Fail'
    }
    return remarks_map.get(grade, 'N/A')

def calculate_gpa(results):
    """
    Calculate GPA for a semester
    Args:
        results: List of tuples (credit_unit, grade_point)
    Returns:
        GPA rounded to 2 decimal places
    """
    if not results:
        return 0.0
    
    total_points = sum(credit_unit * grade_point for credit_unit, grade_point in results)
    total_units = sum(credit_unit for credit_unit, _ in results)
    
    if total_units == 0:
        return 0.0
    
    return round(total_points / total_units, 2)

def calculate_cgpa(all_semester_results):
    """
    Calculate CGPA across multiple semesters
    Args:
        all_semester_results: List of tuples (credit_unit, grade_point) from all semesters
    Returns:
        CGPA rounded to 2 decimal places
    """
    return calculate_gpa(all_semester_results)

def process_result(score, credit_unit):
    """
    Process a single result entry
    Returns dict with grade, grade_point, and remarks
    """
    grade = get_grade(score)
    grade_point = get_grade_point(grade)
    remarks = get_remarks(grade)
    
    return {
        'grade': grade,
        'grade_point': grade_point,
        'remarks': remarks,
        'weighted_point': grade_point * credit_unit
    }

def validate_score(score):
    """
    Validate that score is within acceptable range (0-100)
    """
    try:
        score_float = float(score)
        return 0 <= score_float <= 100
    except (ValueError, TypeError):
        return False

def get_class_of_degree(cgpa):
    """
    Determine class of degree based on CGPA
    """
    if cgpa >= 4.50:
        return 'First Class Honours'
    elif cgpa >= 3.50:
        return 'Second Class Honours (Upper Division)'
    elif cgpa >= 2.50:
        return 'Second Class Honours (Lower Division)'
    elif cgpa >= 1.50:
        return 'Third Class Honours'
    elif cgpa >= 1.00:
        return 'Pass'
    else:
        return 'Fail'