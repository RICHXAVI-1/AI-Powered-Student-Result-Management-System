"""
AI Module for Performance Analysis and Prediction
Uses machine learning algorithms for intelligent academic insights
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error
import pickle
import os

class PerformanceAnalyzer:
    """
    AI-powered performance analysis and prediction system
    """
    
    def __init__(self):
        self.classifier = None
        self.regressor = None
        self.scaler = StandardScaler()
        
    def prepare_features(self, results_data):
        """
        Prepare features from student results for ML models
        Args:
            results_data: List of dicts containing student performance data
        Returns:
            DataFrame with engineered features
        """
        df = pd.DataFrame(results_data)
        
        # Feature engineering
        features = pd.DataFrame()
        
        if len(df) > 0:
            # Calculate average score
            features['avg_score'] = [df['score'].mean()]
            
            # Calculate GPA trend
            features['gpa_trend'] = [df['gpa'].iloc[-1] - df['gpa'].iloc[0] if len(df) > 1 else 0]
            
            # Count failed courses
            features['failed_courses'] = [(df['grade'] == 'F').sum()]
            
            # Calculate attendance rate (simulated - would come from actual data)
            features['attendance_rate'] = [85.0]  # Placeholder
            
            # Previous semester performance
            features['prev_gpa'] = [df['gpa'].iloc[-2] if len(df) > 1 else df['gpa'].iloc[0]]
            
            # Standard deviation of scores (consistency)
            features['score_std'] = [df['score'].std()]
            
        return features
    
    def predict_performance(self, student_results):
        """
        Predict student's future performance category
        Args:
            student_results: List of result records
        Returns:
            Prediction: 'Excellent', 'Good', 'Average', 'At-Risk'
        """
        if not student_results or len(student_results) < 2:
            return 'Insufficient Data'
        
        # Extract features
        scores = [r['score'] for r in student_results]
        grades = [r['grade'] for r in student_results]
        
        # Calculate metrics
        avg_score = np.mean(scores)
        recent_trend = np.mean(scores[-3:]) - np.mean(scores[:-3]) if len(scores) > 3 else 0
        failed_count = grades.count('F')
        
        # Rule-based prediction (can be enhanced with trained ML model)
        if avg_score >= 70 and failed_count == 0:
            return 'Excellent'
        elif avg_score >= 60 and recent_trend >= 0:
            return 'Good'
        elif avg_score >= 50 and failed_count <= 1:
            return 'Average'
        elif avg_score < 50 or failed_count > 2 or recent_trend < -5:
            return 'At-Risk'
        else:
            return 'Average'
    
    def analyze_trends(self, student_results):
        """
        Analyze performance trends over time
        Args:
            student_results: List of result records with timestamps
        Returns:
            Dict with trend analysis
        """
        if not student_results:
            return {
                'trend': 'No Data',
                'improvement': 0,
                'consistency': 0
            }
        
        scores = [r['score'] for r in student_results]
        gpas = [r.get('gpa', 0) for r in student_results]
        
        # Calculate trend
        if len(scores) >= 2:
            recent_avg = np.mean(scores[-3:]) if len(scores) >= 3 else scores[-1]
            earlier_avg = np.mean(scores[:-3]) if len(scores) > 3 else scores[0]
            improvement = recent_avg - earlier_avg
            
            if improvement > 5:
                trend = 'Improving'
            elif improvement < -5:
                trend = 'Declining'
            else:
                trend = 'Stable'
        else:
            trend = 'Insufficient Data'
            improvement = 0
        
        # Calculate consistency (lower std = more consistent)
        consistency = 100 - (np.std(scores) * 2) if len(scores) > 1 else 0
        consistency = max(0, min(100, consistency))  # Bound between 0-100
        
        return {
            'trend': trend,
            'improvement': round(improvement, 2),
            'consistency': round(consistency, 2),
            'average_score': round(np.mean(scores), 2),
            'current_gpa': gpas[-1] if gpas else 0
        }
    
    def identify_at_risk_students(self, all_students_results):
        """
        Identify students who are at academic risk
        Args:
            all_students_results: Dict mapping student_id to their results
        Returns:
            List of student_ids who are at risk
        """
        at_risk = []
        
        for student_id, results in all_students_results.items():
            if not results or len(results) < 2:
                continue
            
            scores = [r['score'] for r in results]
            grades = [r['grade'] for r in results]
            
            # Risk indicators
            avg_score = np.mean(scores)
            failed_count = grades.count('F')
            recent_performance = np.mean(scores[-3:]) if len(scores) >= 3 else avg_score
            
            # Criteria for at-risk
            if (avg_score < 50 or 
                failed_count >= 2 or 
                recent_performance < 45 or
                (len(scores) >= 3 and scores[-1] < scores[-2] < scores[-3])):
                at_risk.append(student_id)
        
        return at_risk
    
    def generate_recommendations(self, student_results, current_gpa):
        """
        Generate personalized recommendations based on performance
        Args:
            student_results: Student's result history
            current_gpa: Current GPA
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if not student_results:
            return ['Insufficient data for recommendations']
        
        scores = [r['score'] for r in student_results]
        grades = [r['grade'] for r in student_results]
        avg_score = np.mean(scores)
        
        # Performance-based recommendations
        if avg_score >= 70:
            recommendations.append('Excellent performance! Keep up the outstanding work.')
            recommendations.append('Consider mentoring peers to reinforce your knowledge.')
        elif avg_score >= 60:
            recommendations.append('Good performance. Focus on maintaining consistency.')
            recommendations.append('Target specific areas for improvement to achieve excellence.')
        elif avg_score >= 50:
            recommendations.append('Moderate performance. Increase study time and seek help when needed.')
            recommendations.append('Join study groups to enhance understanding of challenging topics.')
        else:
            recommendations.append('Performance needs significant improvement. Seek immediate academic support.')
            recommendations.append('Meet with lecturers during office hours for personalized guidance.')
            recommendations.append('Consider academic counseling and time management workshops.')
        
        # Failed courses recommendations
        failed_count = grades.count('F')
        if failed_count > 0:
            recommendations.append(f'You have {failed_count} failed course(s). Plan for retakes and focus on weak areas.')
        
        # GPA-based recommendations
        if current_gpa < 2.0:
            recommendations.append('Your GPA is below 2.0. Urgent action needed to avoid probation.')
        elif current_gpa >= 4.5:
            recommendations.append('First Class standing! Maintain this excellence for graduation honors.')
        
        # Trend-based recommendations
        if len(scores) >= 3:
            if scores[-1] < scores[-2]:
                recommendations.append('Recent performance declined. Review study habits and seek support.')
        
        return recommendations
    
    def calculate_performance_metrics(self, results):
        """
        Calculate comprehensive performance metrics
        Args:
            results: List of result records
        Returns:
            Dict with various metrics
        """
        if not results:
            return {}
        
        scores = [r['score'] for r in results]
        grades = [r['grade'] for r in results]
        
        metrics = {
            'total_courses': len(results),
            'average_score': round(np.mean(scores), 2),
            'highest_score': max(scores),
            'lowest_score': min(scores),
            'score_range': max(scores) - min(scores),
            'standard_deviation': round(np.std(scores), 2),
            'passed_courses': sum(1 for g in grades if g != 'F'),
            'failed_courses': grades.count('F'),
            'grade_distribution': {
                'A': grades.count('A'),
                'B': grades.count('B'),
                'C': grades.count('C'),
                'D': grades.count('D'),
                'E': grades.count('E'),
                'F': grades.count('F')
            }
        }
        
        return metrics