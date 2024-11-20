# app.py
from flask import Flask, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_login import LoginManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize MySQL
mysql = MySQL(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register blueprints
from routes.auth import auth_bp
from routes.dean import dean_bp
from routes.teacher import teacher_bp
from routes.student import student_bp
from routes.parent import parent_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dean_bp, url_prefix='/dean')
app.register_blueprint(teacher_bp, url_prefix='/teacher')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(parent_bp, url_prefix='/parent')

# Add root route
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

# Load user callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    cur = mysql.connection.cursor()

    # Retrieve the role from the session
    role = session.get('role')
    if not role:
        print("No role found in session; redirecting to login.")
        cur.close()
        return None  # No role in session, so re-login is required

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

if __name__ == '__main__':
    app.run(debug=True)