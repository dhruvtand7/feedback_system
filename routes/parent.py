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
    
    # Get linked students
    cur.execute("""
        SELECT s.* FROM parenting p 
        JOIN student s ON p.student_id = s.student_id 
        WHERE p.parent_id = %s
    """, (current_user.id,))
    students = cur.fetchall()
    
    cur.close()
    return render_template('dashboard/parent_dashboard.html', students=students)

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