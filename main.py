import datetime
import logging

from bs4 import BeautifulSoup
import requests

logging.basicConfig(level=logging.INFO)

URL = "https://old.meneame.net/queue"


def main() -> None:
    now = datetime.datetime.now()
    logging.info(now)
    user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    )

    headers = {"User-Agent": user_agent}
    html = requests.get(URL, headers=headers)
    soup = BeautifulSoup(html.text, "html.parser")
    newswrap = soup.find_all(id="newswrap")
    assert len(newswrap) == 1

    news_summary = newswrap[0].find_all(class_="news-summary")
    assert len(news_summary) == 50

    first_news_title = news_summary[0].find("h2").text
    logging.info(first_news_title)


if __name__ == "__main__":
    main()
