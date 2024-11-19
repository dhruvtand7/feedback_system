# routes/teacher.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from utils.helpers import role_required, calculate_average_ratings, is_review_cycle_open
from app import mysql

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/dashboard')
@login_required
@role_required(['teacher'])
def dashboard():
    cur = mysql.connection.cursor()
    
    # Get teacher's classes
    cur.execute("""
        SELECT c.*, 
            (SELECT COUNT(*) FROM enrollment e WHERE e.class_id = c.class_id) as student_count 
        FROM class c 
        WHERE c.teacher_id = %s
    """, (current_user.id,))
    classes = cur.fetchall()
    
    # Get overall ratings if any
    cur.execute("""
        SELECT * FROM student_feedback 
        WHERE teacher_id = %s
    """, (current_user.id,))
    feedback = cur.fetchall()
    average_ratings = calculate_average_ratings(feedback, 'teacher') if feedback else None
    
    cur.close()
    return render_template('dashboard/teacher_dashboard.html', 
                         classes=classes,
                         average_ratings=average_ratings,
                         university_id=current_user.university_id)

@teacher_bp.route('/join_university', methods=['POST'])
@login_required
@role_required(['teacher'])
def join_university():
    if current_user.university_id:
        flash('Already part of a university', 'error')
        return redirect(url_for('teacher.dashboard'))
    
    university_code = request.form['university_code']
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT university_id FROM university WHERE university_code = %s", (university_code,))
    university = cur.fetchone()
    
    if university:
        cur.execute("UPDATE teacher SET university_id = %s WHERE teacher_id = %s",
                   (university['university_id'], current_user.id))
        mysql.connection.commit()
        flash('Successfully joined university', 'success')
    else:
        flash('Invalid university code', 'error')
    
    cur.close()
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/create_class', methods=['POST'])
@login_required
@role_required(['teacher'])
def create_class():
    if not current_user.university_id:
        flash('Must join a university first', 'error')
        return redirect(url_for('teacher.dashboard'))
    
    class_name = request.form['class_name']
    cur = mysql.connection.cursor()
    
    try:
        cur.execute("INSERT INTO class (teacher_id, class_name) VALUES (%s, %s)",
                   (current_user.id, class_name))
        mysql.connection.commit()
        flash('Class created successfully', 'success')
    except Exception as e:
        flash('Failed to create class', 'error')
    finally:
        cur.close()
    
    return redirect(url_for('teacher.dashboard'))