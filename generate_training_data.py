"""
Training Data Generator
Generates 1000 realistic student result records for ML model training.
Run this script ONCE before training: python generate_training_data.py
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)

def get_grade(score):
    if score >= 70: return 'A'
    elif score >= 60: return 'B'
    elif score >= 50: return 'C'
    elif score >= 45: return 'D'
    elif score >= 40: return 'E'
    else: return 'F'

def get_grade_point(grade):
    return {'A': 5.0, 'B': 4.0, 'C': 3.0, 'D': 2.0, 'E': 1.0, 'F': 0.0}.get(grade, 0.0)

def calculate_gpa(scores, credit_units):
    total_points = sum(get_grade_point(get_grade(s)) * c for s, c in zip(scores, credit_units))
    total_units = sum(credit_units)
    return round(total_points / total_units, 2) if total_units else 0.0

def assign_performance_label(avg_score, failed_count, gpa, trend):
    """Ground truth label based on realistic academic criteria."""
    if avg_score >= 68 and failed_count == 0 and gpa >= 3.5:
        return 'Excellent'
    elif avg_score >= 55 and failed_count <= 1 and gpa >= 2.5 and trend >= -3:
        return 'Good'
    elif avg_score >= 45 and failed_count <= 2 and gpa >= 1.5:
        return 'Average'
    else:
        return 'At-Risk'

records = []
student_id = 1001

# Student archetypes for realistic distribution
archetypes = [
    # (mean_score, std, weight)  — weights sum to 1
    (78, 6,  0.15),   # High achievers
    (68, 7,  0.25),   # Good students
    (57, 8,  0.30),   # Average students
    (47, 9,  0.20),   # Struggling students
    (35, 10, 0.10),   # At-risk students
]

for i in range(1000):
    # Pick archetype
    archetype_idx = np.random.choice(len(archetypes), p=[a[2] for a in archetypes])
    mean_s, std_s, _ = archetypes[archetype_idx]

    num_courses = np.random.randint(4, 8)
    credit_units = np.random.choice([2, 3, 4], size=num_courses)
    scores = np.clip(np.random.normal(mean_s, std_s, num_courses), 0, 100).astype(int).tolist()

    # Attendance influences performance slightly
    attendance_rate = np.clip(np.random.normal(75 + (mean_s - 55) * 0.3, 10), 20, 100)

    # Study hours per week
    study_hours = np.clip(np.random.normal(2 + (mean_s - 40) * 0.08, 1.5), 0, 12)

    avg_score = round(np.mean(scores), 2)
    failed_count = sum(1 for s in scores if s < 40)
    gpa = calculate_gpa(scores, credit_units.tolist())

    # Simulate a previous semester average (with some noise)
    prev_avg_score = round(np.clip(avg_score + np.random.normal(0, 5), 0, 100), 2)
    trend = avg_score - prev_avg_score

    score_std = round(np.std(scores), 2)
    pass_rate = round((num_courses - failed_count) / num_courses * 100, 2)

    label = assign_performance_label(avg_score, failed_count, gpa, trend)

    # Department
    department = np.random.choice(['Computer Science', 'Engineering', 'Business', 'Medicine', 'Law', 'Arts'])
    level = np.random.choice([100, 200, 300, 400])
    semester = np.random.choice(['First', 'Second'])

    records.append({
        'student_id': f'STU{student_id}',
        'department': department,
        'level': level,
        'semester': semester,
        'num_courses': num_courses,
        'avg_score': avg_score,
        'prev_avg_score': prev_avg_score,
        'score_trend': round(trend, 2),
        'score_std': score_std,
        'failed_courses': failed_count,
        'gpa': gpa,
        'pass_rate': pass_rate,
        'attendance_rate': round(attendance_rate, 2),
        'study_hours_per_week': round(study_hours, 2),
        'performance_label': label
    })
    student_id += 1

df = pd.DataFrame(records)

os.makedirs('ml_data', exist_ok=True)
csv_path = 'ml_data/student_training_data.csv'
df.to_csv(csv_path, index=False)

print(f"✅ Generated {len(df)} student records → {csv_path}")
print("\nLabel distribution:")
print(df['performance_label'].value_counts())
print("\nSample:")
print(df.head(3).to_string())
