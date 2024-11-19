from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, name, role, university_id=None, parent_code=None):
        self.id = id
        self.email = email
        self.name = name
        self.role = role
        self.university_id = university_id
        self.parent_code = parent_code
    
    def get_id(self):
        return str(self.id)
    
    @staticmethod
    def get_user_by_id(mysql, user_id, role):
        cur = mysql.connection.cursor()
        try:
            cur.execute(f"SELECT * FROM {role} WHERE {role}_id = %s", (user_id,))
            user_data = cur.fetchone()
            if user_data:
                return User(
                    id=user_data[f'{role}_id'],
                    email=user_data['email'],
                    name=user_data[f'{role}_name'],
                    role=role,
                    university_id=user_data.get('university_id'),
                    parent_code=user_data.get('parent_code')
                )
        finally:
            cur.close()
        return None