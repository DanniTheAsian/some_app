from dataclasses import dataclass
from database_connection import get_connection
from datetime import datetime

@dataclass
class PostLike:
    user_id: int
    post_id: int
    created_at: datetime


class LikesRepo:
    def like_post(self, user_id: int, post_id: int):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO post_likes (user_id, post_id)
            VALUES (%s, %s)
            ON CONFLICT (user_id, post_id)
            DO UPDATE SET created_at = NOW()
            RETURNING user_id, post_id, created_at
            """,
            (user_id, post_id)
        )

        row = cur.fetchone()
        conn.commit()

        cur.close()
        conn.close()

        return PostLike(*row)

    
    def unlike_post(self, user_id, post_id:int):
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute(
            """
            DELETE FROM post_likes
            WHERE user_id = %s AND post_id = %s
            """,
            (user_id, post_id)
        )

        conn.commit()
        cur.close()
        conn.close()

    def count_likes(self, post_id:int) -> int:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT COUNT(*) FROM post_likes Where post_id = %s
            """, (post_id,)
            )
        count = cur.fetchone()[0]
        cur.close()
        conn.close()

        return count