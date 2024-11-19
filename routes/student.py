# routes/student.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from utils.helpers import role_required, calculate_average_ratings, is_review_cycle_open
from app import mysql

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@login_required
@role_required(['student'])
def dashboard():
    cur = mysql.connection.cursor()
    
    # Get enrolled classes
    cur.execute("""
        SELECT c.*, t.teacher_name 
        FROM enrollment e 
        JOIN class c ON e.class_id = c.class_id 
        JOIN teacher t ON c.teacher_id = t.teacher_id 
        WHERE e.student_id = %s
    """, (current_user.id,))
    classes = cur.fetchall()
    
    # Get overall ratings
    cur.execute("""
        SELECT * FROM student_feedback 
        WHERE student_id = %s
    """, (current_user.id,))
    feedback = cur.fetchall()
    average_ratings = calculate_average_ratings(feedback, 'student') if feedback else None
    
    cur.close()
    return render_template('dashboard/student_dashboard.html', 
                         classes=classes,
                         average_ratings=average_ratings,
                         parent_code=current_user.parent_code)

@student_bp.route('/join_class', methods=['POST'])
@login_required
@role_required(['student'])
def join_class():
    class_code = request.form['class_code']
    cur = mysql.connection.cursor()
    
    # Check if class exists
    cur.execute("SELECT * FROM class WHERE class_code = %s", (class_code,))
    class_data = cur.fetchone()
    
    if class_data:
        try:
            cur.execute("INSERT INTO enrollment (student_id, class_id) VALUES (%s, %s)",
                       (current_user.id, class_data['class_id']))
            mysql.connection.commit()
            flash('Successfully joined class', 'success')
        except Exception as e:
            flash('Already enrolled in this class', 'error')
    else:
        flash('Invalid class code', 'error')
    
    cur.close()
    return redirect(url_for('student.dashboard'))