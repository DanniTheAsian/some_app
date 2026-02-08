from .database_connection import get_connection
import bcrypt
class User:
    def get_by_email(self, email: str):
        email = email.strip().lower()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, email, password_hash FROM users WHERE LOWER(TRIM(email))=%s",
                    (email,)
                )
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user
    
    def create_user(self,
                    username,
                    email,
                    first_name,
                    last_name,
                    password):
        email = email.strip().lower()
        conn = get_connection()
        cur = conn.cursor()

        password_hash = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

        try:
            cur.execute(
                """INSERT INTO users (username, email, first_name,last_name, password_hash)
                VALUES (%s,%s,%s,%s,%s)
                RETURNING id, username, email""",
                (username, email, first_name, last_name, password_hash)
            )
            user = cur.fetchone()
            conn.commit()
            return user
        except Exception as e:
            print(f"error {e}")
            conn.rollback()
            return None
        finally:
            cur.close()
            conn.close()
    
    def verify_password(self, email, password_input):
        user = self.get_by_email(email)

        if not user:
            print("User not found")
            return False
        
        stored_hash = user[2]
        print("STORED HASH:", stored_hash)
        print("INPUT PASS:", password_input)
        try:
            return bcrypt.checkpw(password_input.encode(), stored_hash.encode())
        except Exception as e:
            print("BCRYPT ERROR:", e)
            return False
