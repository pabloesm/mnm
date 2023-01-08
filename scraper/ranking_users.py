"""
- Filter out users with comments in the story
- Select user with less comments today 
"""

from typing import (
    Dict,
    Optional,
)

from scraper import db
from scraper.logger import get_logger

log = get_logger()


def comment_writing_data(comment: dict) -> Optional[Dict]:
    user_info = get_suitable_user(comment)
    if not user_info:
        log.info("No data for writing a comment. Wait for next attempt!")
        return

    return {
        "username": user_info["username"],
        "pass": user_info["pass"],
        "story_id": comment["news_id"],
        "proxy_config": user_info["proxy_info"],
        "comment": comment["comment_text"],
    }
    # story_id = comment["news_id"]
    # users = db.read_users_with_no_comment_for_story(story_id)
    # comments_by_user = db.number_comments_by_user_last_week()
    # msg = f'{comments_by_user["username"]}: {comments_by_user["num_comments"]}'


def get_suitable_user(comment: dict) -> Optional[Dict]:
    log.info("Function real logic not implemented yet for multiple users")

    users = db.read_users_with_no_comment_for_story(comment["news_id"])
    if len(users) == 0:
        log.info("All users already commented this story.")
        return

    best_user = users[0]
    return best_user
