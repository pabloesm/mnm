import json
from pathlib import Path
from typing import (
    Iterable,
    Dict,
)

import pytest

from scraper.ranking_comments import (
    CommentsProcessor,
    sort_by_votes,
    validation_mnm,
)

resources_folder = Path("tests/resources")
comments_sample_filename = "comments_from_article.json"


@pytest.fixture
def comments_sample() -> Iterable[Dict]:
    filepath = resources_folder / comments_sample_filename
    with open(filepath, "r", encoding="utf-8") as comments_file:
        comments = json.load(comments_file)

    yield comments


def test_sort_by_votes(comments_sample):
    # Arrange
    comments = list(comments_sample)

    # Act
    comments_sorted = sort_by_votes(comments)

    # Assert
    net_votes = [x["votes_positive"] - x["votes_negative"] for x in comments_sorted]
    assert all(x >= y for x, y in zip(net_votes, net_votes[1:]))


def test_validation_mnm():
    # Test with a comment that has less than 5 characters
    # Arrange
    comment = {"comment_text": "abc"}

    # Act + Assert
    assert validation_mnm(comment) == False

    # Test with a comment that has only special characters
    # Arrange
    comment = {"comment_text": "!@#$%^&*()"}

    # Act + Assert
    assert validation_mnm(comment) == False

    # Test with a comment that has at least one alphabetical character
    # Arrange
    comment = {"comment_text": "abc123"}
    # Act + Assert
    assert validation_mnm(comment) == True

    # Test with a comment that has at least one alphanumeric character
    # Arrange
    comment = {"comment_text": "abc123:-)"}
    # Act + Assert
    assert validation_mnm(comment) == True

    # Test with a comment that has too many uppercase letters
    # Arrange
    comment = {"comment_text": "ABCd"}
    # Act + Assert
    assert validation_mnm(comment) == False


def test_CommentsProcessor(comments_sample):
    # Arrange
    expected_result_ids = [
        "440844391cc02dbcba5ee1f01d7e3913",
        "44b4886011935d7b091867d10ca51a49",
        "9a6a3b7e355d72bfef50b90b449a5a94",
        "99a4d14d476287de52b495c92b2b2bd0",
        "3e4a4d970e7fd36c55d385fe539dba20",
        "57ad45ba36e9796f1e018cbca66667eb",
        "1c1659582b03ae96ab8a519cafbdd4a3",
        "4641d5958650606acaec39ef6e518a65",
    ]

    comments = list(comments_sample)
    processor = CommentsProcessor(comments)

    # Act
    result = (
        processor.validation_mnm().filter_controversial().sort_by_votes().get_output()
    )

    # Assert
    result_ids = [el["comment_md5_id"] for el in result]
    assert result_ids == expected_result_ids
