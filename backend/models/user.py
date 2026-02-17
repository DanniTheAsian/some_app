from database_connection import get_connection
import bcrypt


class User:
    def __init__(
        self,
        id,
        username,
        email,
        first_name,
        last_name,
        password_hash
    ):
        self.id = id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password_hash = password_hash

class UserRepository:

    def get_by_username(self, username: str):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, username, email, first_name, last_name, password_hash
            FROM users
            WHERE username = %s
        """, (username,))

        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return User(*row)

        return None


    def get_by_email(self, email: str):
        email = email.strip().lower()
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, username, email, first_name, last_name, password_hash
            FROM users
            WHERE LOWER(TRIM(email))=%s
        """, (email,))

        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return User(*row)

        return None



    def get_by_id(self, user_id: int):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, username, email, first_name, last_name, password_hash
            FROM users
            WHERE id = %s
        """, (user_id,))

        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return User(*row)

        return None



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

        return User(
            id=user_id,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=password_hash
        )


    def verify_password(self, user: User, password_input: str):
        return bcrypt.checkpw(
            password_input.encode(),
            user.password_hash.encode()
        )
