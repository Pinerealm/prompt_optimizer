import logging
import os
import time
from datetime import datetime, timezone

import psycopg2

logger = logging.getLogger(__name__)


def get_db_connection():
    """Create a connection to the PostgreSQL database."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "optimized_prompts"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )


def init_db(max_retries=5, retry_delay=2):
    """Create the optimization_logs table if it doesn't exist."""
    for attempt in range(1, max_retries + 1):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS optimization_logs (
                    id SERIAL PRIMARY KEY,
                    original_prompt TEXT NOT NULL,
                    optimized_prompt TEXT NOT NULL,
                    changes TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            logger.info("Database initialized successfully.")
            return
        except psycopg2.OperationalError as e:
            if attempt < max_retries:
                logger.warning(
                    f"Database not ready (attempt {attempt}/{max_retries}). "
                    f"Retrying in {retry_delay}s..."
                )
                time.sleep(retry_delay)
            else:
                raise


def log_optimization(original_prompt, optimized_prompt, changes):
    """Write an optimization result to the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO optimization_logs
            (original_prompt, optimized_prompt, changes, created_at)
        VALUES (%s, %s, %s, %s);
        """,
        (original_prompt, optimized_prompt, changes, datetime.now(timezone.utc)),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_recent_optimizations(limit=10):
    """Return recent optimization logs ordered by newest first."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, original_prompt, optimized_prompt, changes, created_at
        FROM optimization_logs
        ORDER BY created_at DESC
        LIMIT %s;
        """,
        (limit,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": row[0],
            "original_prompt": row[1],
            "optimized_prompt": row[2],
            "changes": row[3],
            "created_at": row[4],
        }
        for row in rows
    ]
