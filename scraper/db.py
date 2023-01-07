import datetime
import os
from typing import List, Dict

from sqlalchemy import create_engine
from sqlalchemy.sql import text


conn_string = os.environ.get("DB_CONN_STRING")

if conn_string is None:
    raise ValueError("Environment variable DB_CONN_STRING not set.")
else:
    engine = create_engine(conn_string, connect_args={"sslmode": "require"}, echo=False)


def check_db_availability():
    with engine.connect() as con:
        rs = con.execute("SELECT version()")

        for row in rs:
            print(row)


def upsert_news(news: dict):
    statement = text(
        """
        INSERT INTO queue_news(
            news_id,
            title,
            meneos,
            clicks,
            votes_positive,
            votes_negative,
            karma,
            url_full,
            url_domain,
            time_send,
            updated_at,
            story_comments_history,
            is_discarded,
            are_comments_extracted,
            comment_extraction_history
        ) VALUES(
            :news_id,
            :title,
            :meneos,
            :clicks,
            :votes_positive,
            :votes_negative,
            :karma,
            :url_full,
            :url_domain,
            :time_send,
            :updated_at,
            :story_comments_history,
            :is_discarded,
            :are_comments_extracted,
            :comment_extraction_history
        )
        ON CONFLICT (news_id)
        DO
            UPDATE SET
                meneos = :meneos,
                clicks = :clicks,
                votes_positive = :votes_positive,
                votes_negative = :votes_negative,
                karma = :karma,
                updated_at = :updated_at
        """
    )
    with engine.connect() as con:
        con.execute(statement, **news)


def read_news(news_id: int) -> dict:
    statement = text(
        """
        SELECT *
        FROM queue_news
        WHERE news_id = :news_id;
        """
    )
    with engine.connect() as con:
        res = con.execute(statement, news_id=news_id)

    return res.mappings().all()[0]


def update_news_status(
    news_id: int,
    updated_at: str,
    story_comments_history: str,
    is_discarded: bool,
    are_comments_extracted: bool,
    comment_extraction_history: str,
) -> List[Dict]:
    statement = text(
        """
        UPDATE queue_news
        SET updated_at = :updated_at,
            story_comments_history = :story_comments_history,
            is_discarded = :is_discarded,
            are_comments_extracted = :are_comments_extracted,
            comment_extraction_history = :comment_extraction_history
        WHERE news_id = :news_id
        RETURNING *;
        """
    )
    with engine.connect() as con:
        res = con.execute(
            statement,
            news_id=news_id,
            updated_at=updated_at,
            story_comments_history=story_comments_history,
            is_discarded=is_discarded,
            are_comments_extracted=are_comments_extracted,
            comment_extraction_history=comment_extraction_history,
        )

    return res.mappings().all()


def delete_news_previous_to(timedelta: datetime.timedelta) -> List[Dict]:
    """Delete news previous to a given datetime that do not contain comments"""

    current_time = datetime.datetime.now()
    datetime_threshold = current_time - timedelta
    statement = text(
        """
        DELETE FROM queue_news qn
        WHERE qn.news_id IN (
            SELECT qn.news_id
            FROM queue_news qn
            LEFT JOIN "comments" c ON qn.news_id = c.news_id
            WHERE time_send < :datetime_threshold AND c.news_id IS NULL
        )
        RETURNING *;
        """
    )
    with engine.connect() as con:
        res = con.execute(statement, datetime_threshold=datetime_threshold)

    return res.mappings().all()
