import re
from typing import (
    Dict,
    List,
)

from scraper.logger import get_logger

log = get_logger()


class CommentsProcessor:
    """Applying all processing steps through chaining"""

    # TODO: minimum positive votes

    def __init__(self, comments: List[Dict]):
        self.comments = comments

    def validation_mnm(self):
        self.comments = [el for el in self.comments if validation_mnm(el)]
        return self

    def filter_controversial(self):
        self.comments = filter_controversial(self.comments)
        return self

    def sort_by_votes(self):
        self.comments = sort_by_votes(self.comments)
        return self

    def get_output(self):
        return self.comments


def filter_controversial(comments: List[Dict]) -> List[Dict]:
    limit_negative_votes = 5
    result = [el for el in comments if el["votes_negative"] < limit_negative_votes]
    filtered = len(comments) - len(result)
    log.debug("Number of controversial comments filtered out: %d" % (filtered))
    return result


def proportion_uppercase(text: str) -> float:
    alphanumeric_chars = list(filter(str.isalpha, text))
    if len(alphanumeric_chars) > 0:
        return sum(map(str.isupper, alphanumeric_chars)) / len(alphanumeric_chars)
    return 0


def sort_by_votes(comments: List[Dict]) -> List[Dict]:
    comments_sorted = sorted(
        comments, key=lambda x: x["votes_positive"] - x["votes_negative"], reverse=True
    )
    return comments_sorted


def validation_mnm(comment: dict) -> bool:
    text = comment["comment_text"]
    if any(
        [
            len(text) < 5,
            not bool(re.search(r"[a-zA-Z:-]", text)),
            proportion_uppercase(text) > 0.3,
        ]
    ):
        # Check there are at least a valid char
        log.debug("Comment filtered out in validation: %s" % (comment))
        return False
    return True
