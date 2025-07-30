import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def get_default_courses():
    """Return the pre-loaded course list"""
    return [
        {"code": "BSD 1323", "name": "Storytelling & Data Visualization", "carry_weight": 60, "exam_weight": 40},
        {"code": "BSD 2143", "name": "Operational Research", "carry_weight": 60, "exam_weight": 40},
        {"code": "BUM 2413", "name": "Applied Statistics", "carry_weight": 60, "exam_weight": 40},
        {"code": "BUM 2123", "name": "Applied Calculus", "carry_weight": 60, "exam_weight": 40},
        {"code": "BCU 1023", "name": "Programming Technique", "carry_weight": 60, "exam_weight": 40},
        {"code": "ULS 1312", "name": "Spanish A1", "carry_weight": 60, "exam_weight": 40},
        {"code": "UHE 3032", "name": "Introduction to Human Behaviour", "carry_weight": 60, "exam_weight": 40}
    ]

def initialize_session_state():
    """Initialize session state variables"""
    if 'courses' not in st.session_state:
        st.session_state.courses = get_default_courses()
    
    if 'carry_marks' not in st.session_state:
        st.session_state.carry_marks = []
    
    if 'final_exams' not in st.session_state:
        st.session_state.final_exams = []
    
    if 'assignments' not in st.session_state:
        st.session_state.assignments = []
    
    if 'theme_color' not in st.session_state:
        st.session_state.theme_color = "#1f77b4"

def get_courses_df():
    """Get courses as DataFrame"""
    return pd.DataFrame(st.session_state.courses)

def get_carry_marks_df():
    """Get carry marks as DataFrame"""
    if st.session_state.carry_marks:
        return pd.DataFrame(st.session_state.carry_marks)
    return pd.DataFrame(columns=['course_code', 'element_type', 'element_name', 'earned', 'max_possible', 'weight_percentage', 'final_contribution', 'date_added'])

def get_assignments_df():
    """Get assignments as DataFrame"""
    if st.session_state.assignments:
        return pd.DataFrame(st.session_state.assignments)
    return pd.DataFrame(columns=['title', 'course_code', 'type', 'due_date', 'status', 'description'])

def add_course(course_data):
    """Add a new course"""
    st.session_state.courses.append(course_data)

def update_course(index, course_data):
    """Update an existing course"""
    if 0 <= index < len(st.session_state.courses):
        st.session_state.courses[index] = course_data

def delete_course(index):
    """Delete a course"""
    if 0 <= index < len(st.session_state.courses):
        course_code = st.session_state.courses[index]['code']
        # Remove associated carry marks and assignments
        st.session_state.carry_marks = [cm for cm in st.session_state.carry_marks if cm.get('course_code') != course_code]
        st.session_state.assignments = [a for a in st.session_state.assignments if a.get('course_code') != course_code]
        st.session_state.final_exams = [fe for fe in st.session_state.final_exams if fe.get('course_code') != course_code]
        del st.session_state.courses[index]

def add_carry_mark(carry_data):
    """Add a new carry mark entry"""
    carry_data['date_added'] = datetime.now().strftime("%Y-%m-%d")
    st.session_state.carry_marks.append(carry_data)

def add_assignment(assignment_data):
    """Add a new assignment"""
    st.session_state.assignments.append(assignment_data)

def update_assignment_status(index, new_status):
    """Update assignment status"""
    if 0 <= index < len(st.session_state.assignments):
        st.session_state.assignments[index]['status'] = new_status

def delete_assignment(index):
    """Delete an assignment"""
    if 0 <= index < len(st.session_state.assignments):
        del st.session_state.assignments[index]
