import datetime
import json
from typing import List
import uuid

from bs4 import BeautifulSoup
import requests

from scraper import db
from scraper.comment_story import comment_story
from scraper.extract_comments import DOMAIN_TO_SCRIPT
from scraper.logger import get_logger
from scraper.news_summary import NewsSummary
from scraper.random_user_agent import random_ua
from scraper.ranking_comments import CommentsProcessor
from scraper.ranking_users import comment_writing_data

log = get_logger()


URL = "https://old.meneame.net/queue"


def refresh() -> List[NewsSummary]:
    """Scrape the last version of the queue"""
    current_time = datetime.datetime.now()
    log.info(current_time)
    user_agent = random_ua()[0]
    headers = {"User-Agent": user_agent}
    html = requests.get(URL, headers=headers, timeout=20)
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
        news_data["story_comments_history"] = json.dumps([])
        news_data["is_discarded"] = False
        news_data["are_comments_extracted"] = False
        history = json.dumps([])
        news_data["comment_extraction_history"] = history

        db.upsert_news(news_data)
        log.info("Stored article: %s", {news_data["url_full"]})

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

    log.info(
        {
            "news_id": news_id,
            "updated_at": current_time.isoformat(),
            "story_comments_history": current_status["story_comments_history"],
            "is_discarded": is_discarded,
            "are_comments_extracted": are_comments_extracted,
            "comment_extraction_history": history,
        }
    )

    db.update_news_status(
        news_id=news_id,
        updated_at=current_time.isoformat(),
        story_comments_history=json.dumps(current_status["story_comments_history"]),
        is_discarded=is_discarded,
        are_comments_extracted=are_comments_extracted,
        comment_extraction_history=json.dumps(history),
    )


def filter_news(news: List[NewsSummary]) -> List[NewsSummary]:
    filtering_statistics = {
        "initial_news": len(news),
        "filtered_domain": 0,
        "is_discarded": 0,
        "manageable_news": 0,
    }

    # Filter by managed domains
    managed_domains = DOMAIN_TO_SCRIPT.keys()
    filtered_domain = [el for el in news if el.get_url_domain() in managed_domains]

    # Filter by news status
    manageable_news = []
    for element in filtered_domain:
        news_data = db.read_news(element.get_news_id())

        if news_data["is_discarded"]:
            filtering_statistics["is_discarded"] += 1

        # TODO: ensure this is working
        if news_data["is_discarded"]:
            continue
        manageable_news.append(element)

    filtering_statistics["filtered_domain"] = len(news) - len(filtered_domain)
    filtering_statistics["manageable_news"] = len(manageable_news)
    log.info(filtering_statistics)

    return manageable_news


def comment_stories(stories_summary_in_queue: List[NewsSummary]):
    # For commentable URLs (comments extracted)
    # See and validate comments (votes, upper case, min. length, etc.)
    # Filter already used comments
    log.info("\n\n ----------- Commenting stories -----------")
    stories_id_queue = [el.get_news_id() for el in stories_summary_in_queue]
    all_stories = db.read_stories()

    # Filter out stories that are no longer in queue
    stories_in_queue = [el for el in all_stories if el["news_id"] in stories_id_queue]

    # Filter out stories without comments extracted
    stories_w_comments = [el for el in stories_in_queue if el["are_comments_extracted"]]

    log.info(
        {
            "stories_in_db": len(all_stories),
            "stories_in_queue": len(stories_in_queue),
            "stories_in_queue_w_comments": len(stories_w_comments),
        }
    )

    for story in stories_w_comments:
        unpublished_comments = db.read_unpublished_comments_for_story(story["news_id"])
        processor = CommentsProcessor(unpublished_comments)
        sorted_comments = (
            processor.validation_mnm()
            .filter_controversial()
            .filter_few_positive_votes()
            .sort_by_votes()
            .get_output()
        )
        log.info(
            {
                "story_id": story["news_id"],
                "unpublished_comments": len(unpublished_comments),
                "processed_comments": len(sorted_comments),
            }
        )

        if len(sorted_comments) == 0:
            continue

        best_comment = sorted_comments[0]
        log.info("\n\n~~~~~~~~~~~~~~~~~~~~~~~~ Comment ~~~~~~~~~~~~~~~~~~~~~~~~")
        user_and_comment = comment_writing_data(best_comment)
        log.info(user_and_comment)
        log.info("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")

        if not user_and_comment:
            return

        return_code = comment_story(
            user_and_comment["username"],
            user_and_comment["password"],
            user_and_comment["story_id"],
            json.dumps(user_and_comment["proxy_config"]),
            user_and_comment["comment"],
        )
        log.warning({"publish_comment_returncode": return_code})
        if return_code:
            return

        # Update queue_news.story_comments_history
        update_story_comments_history(
            news_id=best_comment["news_id"],
            username=user_and_comment["username"],
            comment_md5_id=best_comment["comment_md5_id"],
        )

        # Update published_comments
        current_time = datetime.datetime.now()
        published_comment = {
            "username": user_and_comment["username"],
            "news_id": best_comment["news_id"],
            "comment_md5_id": best_comment["comment_md5_id"],
            "published_at": current_time.isoformat(),
        }
        log.info("Insert published comment")
        log.info(str(published_comment["comment_md5_id"]))
        db.insert_published_comments(published_comment)


def update_story_comments_history(
    news_id: int,
    username: str,
    comment_md5_id: uuid.UUID,
) -> None:
    """Update story comments history"""
    current_time = datetime.datetime.now()

    current_status = db.read_news(news_id)
    history = current_status["story_comments_history"]
    history.append(
        {
            "username": username,
            "comment_md5_id": str(comment_md5_id),
            "datetime": current_time.isoformat(),
        }
    )

    db.update_news_status(
        news_id=news_id,
        updated_at=current_time.isoformat(),
        story_comments_history=json.dumps(history),
        is_discarded=current_status["is_discarded"],
        are_comments_extracted=current_status["are_comments_extracted"],
        comment_extraction_history=json.dumps(
            current_status["comment_extraction_history"]
        ),
    )

    log.info(
        {
            "event:": "Updated story comments history",
            "news_id": news_id,
            "updated_at": current_time.isoformat(),
            "story_comments_history": history,
        }
    )
