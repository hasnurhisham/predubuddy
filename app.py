import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_manager import get_courses_df, get_carry_marks_df, get_assignments_df
from utils.calculations import calculate_carry_percentage, calculate_current_grade, get_grade_letter, calculate_completion_rate

def analytics_tab():
    """Analytics and insights dashboard"""
    st.header("📊 Personal Insights & Analytics")
    
    courses_df = get_courses_df()
    carry_marks_df = get_carry_marks_df()
    assignments_df = get_assignments_df()
    
    if courses_df.empty:
        st.warning("Please add courses first to see analytics.")
        return
    
    # Overview metrics
    st.subheader("📈 Academic Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_courses = len(courses_df)
        st.metric("Total Courses", total_courses)
    
    with col2:
        if not carry_marks_df.empty:
            avg_performance = carry_marks_df['percentage'].mean()
            st.metric("Average Performance", f"{avg_performance:.1f}%")
        else:
            st.metric("Average Performance", "No data")
    
    with col3:
        if not assignments_df.empty:
            completion_rate = calculate_completion_rate(assignments_df)
            st.metric("Assignment Completion", f"{completion_rate:.1f}%")
        else:
            st.metric("Assignment Completion", "No data")
    
    with col4:
        if not assignments_df.empty:
            pending_assignments = len(assignments_df[assignments_df['status'] == 'pending'])
            st.metric("Pending Assignments", pending_assignments)
        else:
            st.metric("Pending Assignments", 0)
    
    # Initialize course_stats_df
    course_stats_df = pd.DataFrame()
    
    # Course performance analysis
    if not carry_marks_df.empty:
        st.markdown("---")
        st.subheader("🎯 Course Performance Analysis")
        
        # Calculate comprehensive course statistics
        course_stats = []
        for _, course in courses_df.iterrows():
            course_code = course['code']
            course_name = course['name']
            carry_pct = calculate_carry_percentage(course_code, carry_marks_df)
            current_grade = calculate_current_grade(course_code, carry_marks_df, courses_df)
            
            # For letter grade, we need to project the current carry contribution to full grade
            # Current grade is the weighted contribution (e.g., 45 out of 60% possible)
            # We need to calculate what this would be as a percentage of the total possible carry marks
            course_marks = carry_marks_df[carry_marks_df['course_code'] == course_code] if not carry_marks_df.empty else pd.DataFrame()
            if not course_marks.empty and 'final_contribution' in course_marks.columns and 'weight_percentage' in course_marks.columns:
                # Sum of weights entered so far for this course
                total_weight_entered = course_marks['weight_percentage'].sum()
                if total_weight_entered > 0:
                    # Current performance as percentage of work completed so far
                    projected_percentage = (current_grade / total_weight_entered) * 100
                    letter_grade = get_grade_letter(projected_percentage)
                else:
                    letter_grade = "N/A"
            else:
                # Fallback to using carry percentage
                letter_grade = get_grade_letter(carry_pct)
            
            # Count assignments for this course
            course_assignments = assignments_df[assignments_df['course_code'] == course_code] if not assignments_df.empty else pd.DataFrame()
            total_assignments = len(course_assignments)
            completed_assignments = len(course_assignments[course_assignments['status'] == 'completed']) if not course_assignments.empty else 0
            
            course_stats.append({
                'Course Code': course_code,
                'Course Name': course_name,
                'Carry %': carry_pct,
                'Current Grade': current_grade,
                'Letter Grade': letter_grade,
                'Total Assignments': total_assignments,
                'Completed Assignments': completed_assignments,
                'Carry Weight': course['carry_weight'],
                'Exam Weight': course['exam_weight']
            })
        
        course_stats_df = pd.DataFrame(course_stats)
        
        # Performance dashboard
        col1, col2 = st.columns(2)
        
        with col1:
            # Current grades bar chart
            fig_grades = px.bar(
                course_stats_df,
                x='Course Code',
                y='Current Grade',
                color='Current Grade',
                title="Current Grade by Course",
                color_continuous_scale='RdYlGn',
                range_color=[0, 100]
            )
            fig_grades.update_layout(showlegend=False)
            st.plotly_chart(fig_grades, use_container_width=True)
        
        with col2:
            # Carry percentage vs target
            fig_carry = px.scatter(
                course_stats_df,
                x='Carry %',
                y='Current Grade',
                size='Total Assignments',
                color='Letter Grade',
                hover_data=['Course Name'],
                title="Carry Performance vs Current Grade"
            )
            fig_carry.add_shape(
                type="line",
                x0=0, y0=0, x1=100, y1=100,
                line=dict(color="red", width=2, dash="dash"),
            )
            st.plotly_chart(fig_carry, use_container_width=True)
        
        # Detailed course table
        st.subheader("📋 Detailed Course Statistics")
        display_df = course_stats_df[['Course Code', 'Course Name', 'Carry %', 'Current Grade', 'Letter Grade', 'Total Assignments', 'Completed Assignments']]
        st.dataframe(display_df, use_container_width=True)
        
        # Performance trends
        if len(carry_marks_df) > 1:
            st.markdown("---")
            st.subheader("📈 Performance Trends")
            
            # Performance over time
            carry_marks_df_sorted = carry_marks_df.copy()
            carry_marks_df_sorted['date_added'] = pd.to_datetime(carry_marks_df_sorted['date_added'])
            carry_marks_df_sorted = carry_marks_df_sorted.sort_values('date_added')
            
            fig_trend = px.line(
                carry_marks_df_sorted,
                x='date_added',
                y='percentage',
                color='course_code',
                title="Performance Trends Over Time",
                markers=True
            )
            fig_trend.update_layout(
                xaxis_title="Date",
                yaxis_title="Performance (%)",
                legend_title="Course"
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Performance distribution
            col1, col2 = st.columns(2)
            
            with col1:
                fig_hist = px.histogram(
                    carry_marks_df,
                    x='percentage',
                    nbins=20,
                    title="Performance Distribution",
                    color_discrete_sequence=['lightblue']
                )
                fig_hist.update_layout(showlegend=False)
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                fig_box = px.box(
                    carry_marks_df,
                    x='course_code',
                    y='percentage',
                    title="Performance by Course (Box Plot)"
                )
                fig_box.update_layout(showlegend=False)
                st.plotly_chart(fig_box, use_container_width=True)
    
    # Assignment analytics
    if not assignments_df.empty:
        st.markdown("---")
        st.subheader("📋 Assignment Analytics")
        
        # Assignment timeline and workload
        assignments_df_copy = assignments_df.copy()
        assignments_df_copy['due_date'] = pd.to_datetime(assignments_df_copy['due_date'])
        assignments_df_copy['week'] = assignments_df_copy['due_date'].dt.to_period('W')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Assignment status by course
            status_by_course = assignments_df.groupby(['course_code', 'status']).size().reset_index(name='count')
            fig_status = px.bar(
                status_by_course,
                x='course_code',
                y='count',
                color='status',
                title="Assignment Status by Course",
                barmode='stack'
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Assignment types distribution
            type_counts = assignments_df['type'].value_counts()
            fig_types = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title="Assignment Types Distribution"
            )
            st.plotly_chart(fig_types, use_container_width=True)
        
        # Calendar heatmap simulation (using scatter plot)
        st.subheader("📅 Assignment Calendar Heatmap")
        
        # Create daily assignment counts
        daily_counts = assignments_df_copy.groupby(assignments_df_copy['due_date'].dt.date).size().reset_index(name='assignment_count')
        daily_counts['due_date'] = pd.to_datetime(daily_counts['due_date'])
        daily_counts['day_of_week'] = daily_counts['due_date'].dt.day_name()
        daily_counts['week_of_year'] = daily_counts['due_date'].dt.isocalendar().week
        
        if not daily_counts.empty:
            fig_heatmap = px.scatter(
                daily_counts,
                x='week_of_year',
                y='day_of_week',
                size='assignment_count',
                color='assignment_count',
                title="Assignment Due Dates Heatmap",
                color_continuous_scale='Reds',
                size_max=20
            )
            fig_heatmap.update_layout(
                xaxis_title="Week of Year",
                yaxis_title="Day of Week"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Weekly workload trends
        weekly_workload = assignments_df_copy.groupby('week').agg({
            'title': 'count',
            'status': lambda x: (x == 'completed').sum()
        }).rename(columns={'title': 'total', 'status': 'completed'})
        weekly_workload['completion_rate'] = (weekly_workload['completed'] / weekly_workload['total'] * 100).fillna(0)
        
        if not weekly_workload.empty:
            st.subheader("📊 Weekly Workload and Completion Trends")
            
            fig_workload = go.Figure()
            
            weeks = weekly_workload.index.astype(str)
            fig_workload.add_trace(go.Bar(
                x=weeks,
                y=weekly_workload['total'],
                name='Total Assignments',
                marker_color='lightblue',
                yaxis='y'
            ))
            
            fig_workload.add_trace(go.Scatter(
                x=weeks,
                y=weekly_workload['completion_rate'],
                mode='lines+markers',
                name='Completion Rate (%)',
                line=dict(color='red', width=3),
                yaxis='y2'
            ))
            
            fig_workload.update_layout(
                title="Weekly Assignment Workload and Completion Rate",
                xaxis_title="Week",
                yaxis=dict(title="Number of Assignments", side="left"),
                yaxis2=dict(title="Completion Rate (%)", side="right", overlaying="y"),
                legend=dict(x=0.01, y=0.99)
            )
            
            st.plotly_chart(fig_workload, use_container_width=True)
    
    # Insights and recommendations
    st.markdown("---")
    st.subheader("💡 Insights and Recommendations")
    
    insights = []
    
    # Performance insights
    if not carry_marks_df.empty:
        avg_performance = carry_marks_df['percentage'].mean()
        if avg_performance >= 85:
            insights.append("🎉 **Excellent performance!** You're maintaining high standards across your assessments.")
        elif avg_performance >= 70:
            insights.append("👍 **Good performance overall.** Consider focusing on weaker areas to boost your grades.")
        else:
            insights.append("⚠️ **Performance needs improvement.** Consider seeking help or adjusting study strategies.")
        
        # Identify weakest course
        if len(course_stats_df) > 0:
            weakest_course = course_stats_df.loc[course_stats_df['Current Grade'].idxmin()]
            insights.append(f"📚 **Focus area:** {weakest_course['Course Code']} has your lowest current grade ({weakest_course['Current Grade']:.1f}%).")
    
    # Assignment insights
    if not assignments_df.empty:
        completion_rate = calculate_completion_rate(assignments_df)
        if completion_rate >= 90:
            insights.append("✅ **Great job on assignments!** You're staying on top of your work.")
        elif completion_rate >= 70:
            insights.append("📝 **Good assignment management.** Try to improve completion rates further.")
        else:
            insights.append("⏰ **Assignment management needs attention.** Consider better time management strategies.")
        
        # Check for overdue assignments
        today = datetime.now().date()
        overdue_count = 0
        for _, assignment in assignments_df.iterrows():
            if assignment['status'] == 'pending':
                try:
                    due_date = datetime.strptime(assignment['due_date'], "%Y-%m-%d").date()
                    if due_date < today:
                        overdue_count += 1
                except:
                    pass
        
        if overdue_count > 0:
            insights.append(f"🚨 **Urgent:** You have {overdue_count} overdue assignment(s). Address these immediately.")
    
    # Display insights
    for insight in insights:
        st.markdown(insight)
    
    if not insights:
        st.info("Add some courses, carry marks, and assignments to see personalized insights!")
    
    # Data export section
    st.markdown("---")
    st.subheader("📥 Data Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not carry_marks_df.empty:
            csv_carry = carry_marks_df.to_csv(index=False)
            st.download_button(
                label="📊 Download Carry Marks",
                data=csv_carry,
                file_name=f"carry_marks_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if not assignments_df.empty:
            csv_assignments = assignments_df.to_csv(index=False)
            st.download_button(
                label="📋 Download Assignments",
                data=csv_assignments,
                file_name=f"assignments_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if not carry_marks_df.empty and 'course_stats_df' in locals() and not course_stats_df.empty:
            csv_courses = course_stats_df.to_csv(index=False)
            st.download_button(
                label="📚 Download Course Stats",
                data=csv_courses,
                file_name=f"course_statistics_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
