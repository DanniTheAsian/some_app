from database_connection import get_connection

class Post:
    def __init__(self, id: int, user_id: int, title: str, content: str, created_at=None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.content = content
        self.created_at = created_at

    @staticmethod
    def create_post(user_id:int, title:str, content:str ):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""INSERT INTO posts(user_id, title, content)
                    VALUES (%s, %s, %s)
                    RETURNING post_id, created_at
                    """,(user_id, title, content))
        
        post_id, created_at = cur.fetchone()
        conn.commit()

        cur.close()
        conn.close()

        return Post(post_id, user_id, title, content, created_at)
    
    @staticmethod
    def get_by_id(post_id:int):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT post_id, user_id, title, content, created_at
            FROM posts
            WHERE post_id = %s
        """, (post_id,))

        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return Post(*row)
        return None
    
    @staticmethod
    def get_all(current_user_id: int):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                p.post_id,
                p.user_id,
                p.title,
                p.content,
                p.created_at,
                u.username,

                COUNT(pl.user_id) AS likes,

                EXISTS (
                    SELECT 1
                    FROM post_likes
                    WHERE user_id = %s
                    AND post_id = p.post_id
                ) AS liked_by_me

            FROM posts p
            JOIN users u ON u.id = p.user_id
            LEFT JOIN post_likes pl ON pl.post_id = p.post_id

            GROUP BY 
                p.post_id,
                p.user_id,
                p.title,
                p.content,
                p.created_at,
                u.username

            ORDER BY p.created_at DESC
        """, (current_user_id,))

        rows = cur.fetchall()

        cur.close()
        conn.close()

        posts = [
            {
                "id": r[0],
                "user_id": r[1],
                "title": r[2],
                "content": r[3],
                "created_at": r[4],
                "username": r[5],
                "likes": r[6],
                "liked_by_me": r[7]
            }
            for r in rows
        ]

        return posts


        
    @staticmethod
    def delete(post_id: int, user_id: int) -> bool:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM posts
            WHERE post_id = %s AND user_id = %s
        """, (post_id, user_id))

        conn.commit()
        deleted = cur.rowcount

        cur.close()
        conn.close()

        return deleted > 0

    @staticmethod
    def update(post_id: int, user_id: int, title: str, content: str) -> bool:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE posts
            SET title=%s, content=%s
            WHERE post_id=%s AND user_id=%s
        """, (title, content, post_id, user_id))

        conn.commit()
        updated = cur.rowcount

        cur.close()
        conn.close()

        return updated > 0
