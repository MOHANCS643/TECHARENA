from app import app
from extensions import db
from models.admin import Admin

with app.app_context():

    db.create_all()

    username = "admin"

    admin = Admin.query.filter_by(username=username).first()

    if admin:
        print("Admin already exists.")
    else:
        admin = Admin(
            username="admin",
            full_name="System Administrator",
            email="admin@techarena.com"
        )

        admin.set_password("admin123")

        db.session.add(admin)
        db.session.commit()

        print("Admin created successfully!")