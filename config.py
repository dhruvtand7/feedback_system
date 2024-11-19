class Config:
    SECRET_KEY = 'your-secret-key-here'  # Change this to a secure secret key
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'  # Change to your MySQL username
    MYSQL_PASSWORD = 'password'  # Change to your MySQL password
    MYSQL_DB = 'feedback_system'
    MYSQL_CURSORCLASS = 'DictCursor'