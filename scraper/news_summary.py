import datetime
import logging

import bs4

logging.basicConfig(level=logging.INFO)


class NewsSummary:
    def __init__(self, soup: bs4.element.ResultSet) -> None:
        self.soup = soup

    def get_title(self) -> str:
        return self.soup.find("h2").text

    def get_news_id(self) -> int:
        return int(self.soup.select("div.news-body")[0]["data-link-id"])

    def get_meneos(self) -> int:
        news_id = self.get_news_id()
        element_id = f"a-votes-{news_id} ga-event"
        return int(self.soup.find("a", {"id": element_id}).text)

    def get_clicks(self) -> int:
        news_id = self.get_news_id()
        element_id = f"clicks-number-{news_id}"
        try:
            clicks = int(self.soup.find("span", {"id": element_id}).text)
        except AttributeError:
            # Still no clicks
            logging.info("News without clicks found.")
            clicks = 0
        return clicks

    def get_votes_positive(self) -> int:
        return int(self.soup.select("span.positive-vote-number")[0].text)

    def get_votes_negative(self) -> int:
        return int(self.soup.select("span.negative-vote-number")[0].text)

    def get_karma(self) -> int:
        return int(self.soup.select("span.karma-number")[0].text)

    def get_url_full(self) -> str:
        return self.soup.select("span.showmytitle")[0]["title"]

    def get_url_domain(self) -> str:
        return self.soup.select("span.showmytitle")[0].text

    def get_time_send(self) -> str:
        send_timestamp_str = self.soup.select("span.ts")[0]["data-ts"]
        send_timestamp = int(send_timestamp_str)
        send_dt = datetime.datetime.fromtimestamp(send_timestamp)
        return send_dt.isoformat()

    def info(self) -> dict:
        return {
            "news_id": self.get_news_id(),
            "title": self.get_title(),
            "meneos": self.get_meneos(),
            "clicks": self.get_clicks(),
            "votes_positive": self.get_votes_positive(),
            "votes_negative": self.get_votes_negative(),
            "karma": self.get_karma(),
            "url_full": self.get_url_full(),
            "url_domain": self.get_url_domain(),
            "time_send": self.get_time_send(),
        }
