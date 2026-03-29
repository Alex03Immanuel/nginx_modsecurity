from app import app, db, User

print("----------")
print("Creating user...")
username = input("Enter username: ")
password = input("Enter password: ")

def create_user(username, password):

    with app.app_context():
        if User.query.filter_by(username=username).first():
            print("User already exists")
            return
        
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        print("User created successfully")

create_user(username, password)