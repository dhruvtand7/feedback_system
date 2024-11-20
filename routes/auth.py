from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from app import mysql, login_manager

# Define the Blueprint only once
auth_bp = Blueprint('auth', __name__)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    cur = mysql.connection.cursor()

    # Use the role from session to locate the correct user table
    role = session.get('role')
    if not role:
        print("No role found in session; redirecting to login.")
        cur.close()
        return None  # No role in session, force re-login

    print(f"Loading user with user_id={user_id} and role={role}")

    # Check only the table corresponding to the session role
    cur.execute(f"SELECT * FROM {role} WHERE {role}_id = %s", (user_id,))
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
        session['role'] = user.role  # Ensure session role consistency
        return user

    print(f"No user found for user_id={user_id} in role={role}")
    session.clear()  # Clear session if no user is found in the expected table
    return None

# Login route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        print(f"Login attempt: Email={email}, Role={role}")

        # Query the database for the user
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT * FROM {role} WHERE email = %s AND password = %s", (email, password))
        user_data = cur.fetchone()
        cur.close()

        if user_data:
            print(f"Logged in as: {role}, User: {user_data['email']}")
            user = User(
                id=user_data[f'{role}_id'],
                email=user_data['email'],
                name=user_data[f'{role}_name'],
                role=role,
                university_id=user_data.get('university_id'),
                parent_code=user_data.get('parent_code')
            )
            
            # Set session data for role and make it persistent
            session.clear()
            session['role'] = user.role  # Set role in session
            session.permanent = True  # Ensure session persists across requests
            login_user(user)
            
            print(f"Session Role after login: {session['role']}")
            
            return redirect(url_for(f'{role}.dashboard'))

        flash('Invalid credentials. Please try again.', 'error')

    return render_template('login.html')

# Register route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Debugging: Log registration attempt
        print(f"Registration attempt: Name={name}, Email={email}, Role={role}")

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
            # Debugging: Log error details
            print(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')
        finally:
            cur.close()

    return render_template('register.html')

# Logout route
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))
