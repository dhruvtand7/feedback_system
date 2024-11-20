# routes/parent.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from utils.helpers import role_required
from app import mysql

parent_bp = Blueprint('parent', __name__)

@parent_bp.route('/dashboard')
@login_required
@role_required(['parent'])
def dashboard():
    cur = mysql.connection.cursor()
    
    # Get linked students and their enrollments
    cur.execute("""
        SELECT s.student_id, s.student_name, s.email, c.class_name
        FROM parenting p 
        JOIN student s ON p.student_id = s.student_id 
        LEFT JOIN enrollment e ON s.student_id = e.student_id
        LEFT JOIN class c ON e.class_id = c.class_id
        WHERE p.parent_id = %s
    """, (current_user.id,))
    
    # Organize data into a dictionary format for template usage
    students = {}
    for row in cur.fetchall():
        student_id = row['student_id']
        if student_id not in students:
            students[student_id] = {
                'student_name': row['student_name'],
                'email': row['email'],
                'enrollments': []
            }
        if row['class_name']:
            students[student_id]['enrollments'].append({'class_name': row['class_name']})
    
    cur.close()
    return render_template('dashboard/parent_dashboard.html', students=students.values())

@parent_bp.route('/add_student', methods=['POST'])
@login_required
@role_required(['parent'])
def add_student():
    parent_code = request.form['parent_code']
    cur = mysql.connection.cursor()
    
    # Check if student exists
    cur.execute("SELECT student_id FROM student WHERE parent_code = %s", (parent_code,))
    student = cur.fetchone()
    
    if student:
        try:
            cur.execute("INSERT INTO parenting (parent_id, student_id) VALUES (%s, %s)",
                       (current_user.id, student['student_id']))
            mysql.connection.commit()
            flash('Successfully linked to student', 'success')
        except Exception as e:
            flash('Already linked to this student', 'error')
    else:
        flash('Invalid parent code', 'error')
    
    cur.close()
    return redirect(url_for('parent.dashboard'))