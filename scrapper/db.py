import os

from sqlalchemy import create_engine
from sqlalchemy.sql import text

from scrapper.news_summary import NewsSummary


conn_string = os.environ.get("DB_CONN_STRING")

if conn_string is None:
    ValueError("Environment variable DB_CONN_STRING not set.")
else:
    engine = create_engine(conn_string, connect_args={"sslmode": "require"}, echo=True)


def check_db_availability():
    with engine.connect() as con:
        rs = con.execute("SELECT version()")

        for row in rs:
            print(row)


def upsert_news(news: dict):
    # data = {
    #     "news_id": 0,
    #     "title": "título",
    #     "id": 12,
    #     "meneos": 0,
    #     "clicks": 0,
    #     "votes_positive": 0,
    #     "votes_negative": 0,
    #     "karma": 0,
    #     "url_full": "www.foodisea.com/23",
    #     "url_domain": "www.foodisea.com",
    #     "time_send": "1999-01-08 04:05:06",
    #     "updated_at": "1999-01-11 04:05:06",
    #     "is_commented": True,
    # }
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
            is_commented
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
            :is_commented
        ) 
        ON CONFLICT (news_id) 
        DO
            UPDATE SET 
                title = :title,
                meneos = :meneos,
                clicks = :clicks,
                votes_positive = :votes_positive,
                votes_negative = :votes_negative,
                karma = :karma,
                url_full = :url_full,
                url_domain = :url_domain,
                time_send = :time_send,
                updated_at = :updated_at,
                is_commented = :is_commented
        """
    )
    with engine.connect() as con:
        con.execute(statement, **news)
