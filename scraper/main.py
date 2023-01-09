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

from scraper import db
from scraper import mnm_queue
from scraper.extract_comments import extract_comments
from scraper.logger import get_logger

log = get_logger()


def main() -> None:
    log.info("main() starting")

    try:
        news = mnm_queue.refresh()

        manageable_articles = mnm_queue.filter_news(news)
        log.info("\n\n ----------- Comment extraction -----------")
        for article in manageable_articles:
            news_id = article.get_news_id()
            url_full = article.get_url_full()
            url_domain = article.get_url_domain()
            log.info(f"Extracting url {url_full}")
            exit_code = extract_comments(url_full, url_domain, news_id)
            mnm_queue.update_status(news_id, exit_code=exit_code)

        deleted_news = db.delete_news_previous_to(datetime.timedelta(hours=8))
        log.info(f"Deleted {len(deleted_news)} news.")

        mnm_queue.comment_stories(news)

    except Exception as err:
        log.error(err)
        log.info("Scrapper failed.")

    log.info("main() done")


if __name__ == "__main__":
    main()
