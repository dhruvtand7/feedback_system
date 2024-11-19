# routes/auth.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required
from models.user import User
from app import mysql

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT * FROM {role} WHERE email = %s AND password = %s", (email, password))
        user_data = cur.fetchone()
        cur.close()
        
        if user_data:
            user = User(
                id=user_data[f'{role}_id'],
                email=user_data['email'],
                name=user_data[f'{role}_name'],
                role=role,
                university_id=user_data.get('university_id')
            )
            cur.close()
                
            # Clear session and log in the user
            from flask import session
            session.clear()
            login_user(user)
            return redirect(url_for(f'{role}.dashboard'))
            
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        cur = mysql.connection.cursor()
        try:
            cur.execute(f"""
                INSERT INTO {role} ({role}_name, email, password)
                VALUES (%s, %s, %s)
            """, (name, email, password))
            mysql.connection.commit()
            flash('Registration successful', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('Registration failed', 'error')
        finally:
            cur.close()
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))