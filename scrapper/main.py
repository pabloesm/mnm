import datetime
import logging

import bs4
from bs4 import BeautifulSoup
import requests

from scrapper import db
from scrapper.news_summary import NewsSummary

# from scrapper.db8000 import foo

logging.basicConfig(level=logging.INFO)

URL = "https://old.meneame.net/queue"


def main() -> None:
    # db.foo()
    # db.upsert_news("")
    current_time = datetime.datetime.now()
    logging.info(current_time)
    user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    )

    headers = {"User-Agent": user_agent}
    html = requests.get(URL, headers=headers)
    soup = BeautifulSoup(html.text, "html.parser")
    newswrap = soup.find_all(id="newswrap")
    assert len(newswrap) == 1

    news_summaries = newswrap[0].find_all(class_="news-summary")
    assert len(news_summaries) >= 45

    for news_summary in news_summaries:
        summary = NewsSummary(news_summary)
        news_data = summary.info()
        current_time = datetime.datetime.now()
        news_data["updated_at"] = current_time.isoformat()
        news_data["is_commented"] = False
        print(news_data)

        db.upsert_news(news_data)


if __name__ == "__main__":
    main()
