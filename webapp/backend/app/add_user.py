import getpass
from sqlalchemy.orm import Session
from models import User, SessionLocal, create_db_and_tables
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def main():
    create_db_and_tables()
    db: Session = SessionLocal()
    username = input("Enter new username: ")
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Confirm password: ")
    
    if password != confirm_password:
        print("Passwords do not match. Please try again.")
        db.close()
        return
    
    hashed_password = get_password_hash(password)
    
    if db.query(User).filter(User.username == username).first():
        print(f"User '{username}' already exists.")
        return
    
    user = User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"User '{username}' added successfully.")
    db.close()

if __name__ == "__main__":
    main()
