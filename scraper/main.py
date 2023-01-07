"""
- Check news queue (update `queue_news`)
- For manageable URLs (managed domain, not commented and not discarded):
    - Process URL (aka extract comments)
    - Update `comments` and URL status in `queue_news`

- For commentable URLs (not commented, comments extracted)
    - Select suitable user
    - Comment
    - Update `published_comments` and URL status in `queue_news`
"""

import datetime
import logging

from scraper import db
from scraper import mnm_queue
from scraper.comment_story import comment_story
from scraper.extract_comments import extract_comments

logging.basicConfig(level=logging.INFO)


def main() -> None:
    logging.info("main() starting")

    comment_story()
    breakpoint()

    try:
        news = mnm_queue.refresh()
        manageable_articles = mnm_queue.filter_news(news)
        for article in manageable_articles:
            news_id = article.get_news_id()
            url_full = article.get_url_full()
            url_domain = article.get_url_domain()
            exit_code = extract_comments(url_full, url_domain, news_id)
            mnm_queue.update_status(news_id, exit_code=exit_code)

        deleted_news = db.delete_news_previous_to(datetime.timedelta(hours=8))
        logging.info(f"Deleted {len(deleted_news)} news.")

    except Exception as err:
        logging.error(err)
        logging.info("Scrapper failed.")

    logging.info("main() done")


if __name__ == "__main__":
    main()
