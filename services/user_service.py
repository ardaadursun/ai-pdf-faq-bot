import hashlib
from database_dummy import db

class UserService:
    """Handles user authentication and management"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def create_user(username: str, password: str) -> int:
        """Create a new user"""
        password_hash = UserService.hash_password(password)
        user_id = db.insert_user(username, password_hash)
        return user_id
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> int:
        """Authenticate user and return user_id if valid"""
        password_hash = UserService.hash_password(password)
        user = db.get_user_by_credentials(username, password_hash)
        return user['user_id'] if user else None
    
    @staticmethod
    def user_exists(username: str) -> bool:
        """Check if username already exists"""
        return db.user_exists(username)

