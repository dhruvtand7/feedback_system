# utils/helpers.py

from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user, logout_user

from flask import session

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print(f"Session Role: {session.get('role')}, Current User Role: {current_user.role}, Allowed Roles: {roles}")
            
            if not current_user.is_authenticated or current_user.role not in roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            # Extra check: Ensure session role matches current user role
            if session.get('role') != current_user.role:
                print("Role mismatch detected. Logging out.")
                session.clear()
                logout_user()  # Log out the user if roles mismatch
                flash('Session expired or role mismatch. Please log in again.', 'error')
                return redirect(url_for('auth.login'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def calculate_average_ratings(feedback_list, feedback_type):
    if not feedback_list:
        return None
        
    if feedback_type == 'teacher':
        total = {
            'knowledge': 0,
            'presentation': 0,
            'interaction': 0,
            'punctuality': 0
        }
    else:  # student
        total = {
            'participation': 0,
            'teamwork': 0,
            'timeliness': 0,
            'behaviour': 0
        }
    
    for feedback in feedback_list:
        for key in total.keys():
            total[key] += feedback[f'feedback_{key}_rating']
    
    for key in total.keys():
        total[key] = round(total[key] / len(feedback_list), 2)
    
    return total

def is_review_cycle_open(mysql, university_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT * FROM review 
        WHERE university_id = %s 
        AND status = 'open' 
        AND start_date <= NOW() 
        AND end_date >= NOW()
    """, (university_id,))
    review = cur.fetchone()
    cur.close()
    return bool(review)