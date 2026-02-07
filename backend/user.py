from database_connection import get_connection
import psycopg2

class User:
    def get_by_email(self, email: str):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, email, password FROM users WHERE email=%s",
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
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """INSERT INTO users (username, email, first_name,last_name, password)
                VALUE (%s,%s,%s,%s,%s)
                RETURNING id, username, email""",
                (username, email, first_name, last_name, password)
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
