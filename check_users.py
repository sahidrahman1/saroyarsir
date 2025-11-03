from app import create_app
from models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print(f"Total users: {len(users)}")
    print("Users in database:")
    for user in users[:10]:
        print(f"Phone: {user.phoneNumber}, Role: {user.role.value}, Name: {user.first_name} {user.last_name}")