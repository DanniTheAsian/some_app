from database_connection import get_connection
import bcrypt


class User:
    def __init__(self, id: int, email: str, password: str, username: str | None = None):
        self.id = id
        self.email = email
        self.password = password
        self.username = username

class UserRepository:

    def get_by_email(self, email: str):
        email = email.strip().lower()
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, email, password_hash, username
            FROM users
            WHERE LOWER(TRIM(email))=%s
        """, (email,))


        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return User(id=row[0], email=row[1], password=row[2], username=row[3])

        return None


    def get_by_id(self, user_id: int):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, email, password_hash, username
            FROM users
            WHERE id=%s
        """, (user_id,))


        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return User(id=row[0], email=row[1], password=row[2], username=row[3])

        return None


    def create_user(self, username, email, first_name, last_name, password):
        email = email.strip().lower()
        conn = get_connection()
        cur = conn.cursor()

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        cur.execute("""
            INSERT INTO users (username, email, first_name, last_name, password_hash)
            VALUES (%s,%s,%s,%s,%s)
            RETURNING id
        """, (username, email, first_name, last_name, password_hash))

        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return User(id=user_id, email=email, password=password_hash, username=username)



    def verify_password(self, user: User, password_input: str):
        return bcrypt.checkpw(
            password_input.encode(),
            user.password.encode('utf-8')
        )
