from app import app
from models import db, Admin


def buat_admin():
    with app.app_context():

        print("=" * 40)
        print("CREATE ADMIN SEISMIC WAVES")
        print("=" * 40)

        username = input("Username admin: ")
        nama = input("Nama admin: ")
        password = input("Password admin: ")

        admin_lama = Admin.query.filter_by(
            username=username
        ).first()

        if admin_lama:
            print()
            print("Username tersebut sudah digunakan!")
            return

        admin = Admin(
            username=username,
            nama=nama
        )

        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print()
        print("Admin berhasil dibuat!")
        print("Username :", username)


if __name__ == "__main__":
    buat_admin()
    