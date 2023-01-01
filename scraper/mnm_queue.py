import datetime
import json
import logging

from bs4 import BeautifulSoup
import requests

from scraper import db
from scraper.news_summary import NewsSummary
from scraper.extract_comments import DOMAIN_TO_SCRIPT


logging.basicConfig(level=logging.INFO)

URL = "https://old.meneame.net/queue"
# https://www.useragents.me/


def refresh() -> list[NewsSummary]:
    """Scrape the last version of the Meneame queue"""
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

    summaries = []
    for news_summary in news_summaries:
        summary = NewsSummary(news_summary)
        summaries.append(summary)
        news_data = summary.info()
        current_time = datetime.datetime.now()
        news_data["updated_at"] = current_time.isoformat()
        news_data["is_commented"] = False
        news_data["is_discarded"] = False
        news_data["are_comments_extracted"] = False
        history = json.dumps([])
        news_data["comment_extraction_history"] = history
        logging.info(f'Stored article: {news_data["url_full"]}')

        db.upsert_news(news_data)

    return summaries


def update_status(news_id: int, exit_code: int) -> None:
    """Update comments extraction status and history"""
    max_attemps = 5
    current_time = datetime.datetime.now()

    current_status = db.read_news(news_id)
    history = current_status["comment_extraction_history"]
    history.append({"exit_code": exit_code, "datetime": current_time.isoformat()})

    if exit_code == 0:
        are_comments_extracted = True
    else:
        are_comments_extracted = False

    if len(history) > max_attemps:
        is_discarded = True
    else:
        is_discarded = False

    db.update_news_status(
        news_id=news_id,
        updated_at=current_time.isoformat(),
        is_commented=current_status["is_commented"],
        is_discarded=is_discarded,
        are_comments_extracted=are_comments_extracted,
        comment_extraction_history=json.dumps(history),
    )


def filter_news(news: list[NewsSummary]) -> list[NewsSummary]:
    # Filter by managed domains
    managed_domains = DOMAIN_TO_SCRIPT.keys()
    filtered_domain = [el for el in news if el.get_url_domain() in managed_domains]

    # Filter by news status
    manageable_news = []
    for element in filtered_domain:
        news_data = db.read_news(element.get_news_id())
        flags = [
            news_data["is_commented"],
            news_data["is_discarded"],
            news_data["are_comments_extracted"],
        ]
        if any(flags):
            continue
        manageable_news.append(element)

    return manageable_news
