from datetime import datetime
from dataclasses import dataclass
from database_connection import get_connection

@dataclass
class Comment:
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: datetime


class CommentRepo:

    def create(self, post_id: int, user_id:int, content:str)-> Comment:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO comments (post_id, user_id, content)
            VALUES (%s, %s, %s)
            RETURNING id, post_id, user_id, content, created_at
        """, (post_id, user_id, content))

        row = cur.fetchone()

        # hent username separat
        cur.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        username = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return {
            "id": row[0],
            "post_id": row[1],
            "user_id": row[2],
            "content": row[3],
            "created_at": row[4],
            "username": username
        }

    def get_by_post(self, post_id: int):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT c.id, c.post_id, c.user_id, c.content, c.created_at, u.username
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.post_id = %s
            ORDER BY c.created_at ASC
        """, (post_id,))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [
            {
                "id": r[0],
                "post_id": r[1],
                "user_id": r[2],
                "content": r[3],
                "created_at": r[4],
                "username": r[5]
            }
            for r in rows
        ]
