"""
- Filter out users with comments in the story
- Select user with less comments today
"""
import random
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
        return

    user_and_comment = {
        "username": user_info["username"],
        "password": user_info["pass"],
        "story_id": comment["news_id"],
        "proxy_config": user_info["proxy_info"],
        "comment": comment["comment_text"],
    }

    return user_and_comment


def get_suitable_user(comment: dict) -> Optional[Dict]:
    users = db.read_users_with_no_comment_for_story(comment["news_id"])
    log.info({"users_who_no_commented": len(users), "story_id": comment["news_id"]})
    if len(users) == 0:
        return

    random_user = random.choice(users)
    return random_user
