# routes/dean.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from utils.helpers import role_required, calculate_average_ratings
from app import mysql

dean_bp = Blueprint('dean', __name__)

@dean_bp.route('/dashboard')
@login_required
@role_required(['dean'])
def dashboard():
    cur = mysql.connection.cursor()
    
    # Get university info if exists
    cur.execute("SELECT * FROM university WHERE university_id = %s", (current_user.university_id,))
    university = cur.fetchone()
    
    # Get teachers if university exists
    teachers = []
    if university:
        cur.execute("SELECT * FROM teacher WHERE university_id = %s", (university['university_id'],))
        teachers = cur.fetchall()
    
    cur.close()
    return render_template('dashboard/dean_dashboard.html', 
                         university=university, 
                         teachers=teachers)

@dean_bp.route('/create_university', methods=['POST'])
@login_required
@role_required(['dean'])
def create_university():
    if current_user.university_id:
        flash('You already have a university', 'error')
        return redirect(url_for('dean.dashboard'))
    
    name = request.form['university_name']
    cur = mysql.connection.cursor()
    
    try:
        cur.execute("INSERT INTO university (university_name) VALUES (%s)", (name,))
        university_id = cur.lastrowid
        cur.execute("UPDATE dean SET university_id = %s WHERE dean_id = %s", 
                   (university_id, current_user.id))
        mysql.connection.commit()
        flash('University created successfully', 'success')
    except Exception as e:
        flash('Failed to create university', 'error')
    finally:
        cur.close()
    
    return redirect(url_for('dean.dashboard'))