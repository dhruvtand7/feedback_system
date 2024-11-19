# app.py
from flask import Flask, redirect, url_for
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
    
    # Try to find user in each role table
    for role in ['dean', 'teacher', 'student', 'parent']:
        cur.execute(f"SELECT * FROM {role} WHERE {role}_id = %s", (user_id,))
        user_data = cur.fetchone()
        if user_data:
            cur.close()
            return User(
                id=user_data[f'{role}_id'],
                email=user_data['email'],
                name=user_data[f'{role}_name'],
                role=role,
                university_id=user_data.get('university_id')
            )
    
    cur.close()
    return None

if __name__ == '__main__':
    app.run(debug=True)