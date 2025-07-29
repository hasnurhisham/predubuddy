import pandas as pd
from datetime import datetime

def calculate_carry_percentage(course_code, carry_marks_df):
    """Calculate carry percentage for a specific course"""
    if carry_marks_df.empty:
        return 0
    
    course_marks = carry_marks_df[carry_marks_df['course_code'] == course_code]
    if course_marks.empty:
        return 0
    
    total_earned = course_marks['earned'].sum()
    total_max = course_marks['max_possible'].sum()
    
    if total_max == 0:
        return 0
    
    return (total_earned / total_max) * 100

def calculate_final_exam_requirement(target_grade, carry_percentage, carry_weight, exam_weight):
    """Calculate minimum final exam mark needed to achieve target grade"""
    if exam_weight == 0:
        return 0
    
    carry_contribution = (carry_percentage / 100) * (carry_weight / 100) * 100
    required_exam_contribution = target_grade - carry_contribution
    required_exam_percentage = (required_exam_contribution / exam_weight) * 100
    
    return max(0, required_exam_percentage)

def calculate_current_grade(course_code, carry_marks_df, courses_df):
    """Calculate current grade based on carry marks"""
    course_info = courses_df[courses_df['code'] == course_code]
    if course_info.empty:
        return 0
    
    course_marks = carry_marks_df[carry_marks_df['course_code'] == course_code]
    if course_marks.empty:
        return 0
    
    # If we have weighted contributions, use those
    if 'final_contribution' in course_marks.columns:
        return course_marks['final_contribution'].sum()
    
    # Fallback to old calculation
    carry_weight = course_info.iloc[0]['carry_weight']
    carry_percentage = calculate_carry_percentage(course_code, carry_marks_df)
    
    return (carry_percentage / 100) * carry_weight

def get_grade_letter(percentage):
    """Convert percentage to letter grade"""
    if percentage >= 90:
        return "A+"
    elif percentage >= 85:
        return "A"
    elif percentage >= 80:
        return "A-"
    elif percentage >= 75:
        return "B+"
    elif percentage >= 70:
        return "B"
    elif percentage >= 65:
        return "B-"
    elif percentage >= 60:
        return "C+"
    elif percentage >= 55:
        return "C"
    elif percentage >= 50:
        return "C-"
    else:
        return "F"

def calculate_days_until_due(due_date_str):
    """Calculate days until due date"""
    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        today = datetime.now()
        delta = due_date - today
        return delta.days
    except:
        return 0

def get_weekly_workload(assignments_df):
    """Calculate weekly workload summary"""
    if assignments_df.empty:
        return pd.DataFrame()
    
    assignments_df['due_date'] = pd.to_datetime(assignments_df['due_date'])
    assignments_df['week'] = assignments_df['due_date'].dt.to_period('W')
    
    weekly_summary = assignments_df.groupby('week').agg({
        'title': 'count',
        'status': lambda x: (x == 'pending').sum()
    }).rename(columns={'title': 'total_assignments', 'status': 'pending_assignments'})
    
    return weekly_summary.reset_index()

def calculate_completion_rate(assignments_df):
    """Calculate assignment completion rate"""
    if assignments_df.empty:
        return 0
    
    completed = len(assignments_df[assignments_df['status'] == 'completed'])
    total = len(assignments_df)
    
    return (completed / total) * 100 if total > 0 else 0

Move calculations to utils
