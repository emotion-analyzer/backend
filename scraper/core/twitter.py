# ruff: noqa:  D101, D102, D103, D105, E501
import csv
from dataclasses import dataclass

from dateutil import parser
from scraper.config import config
from scraper.core.schemas import FetchRequest, Post
from Scweet.scweet import Scweet


@dataclass
class TwitterScraper:

    def __init__(self):
        self.scweet = Scweet(proxy=None, cookies=None, user_agent=None,
                             disable_images=True, env_path='test.env',
                             n_splits=-1, concurrency=config.TWITTER.CONCURRENT_BROWSERS,
                             headless=False, scroll_ratio=config.TWITTER.SCROLL_RATIO)

    def query(self, fetch_request: FetchRequest) -> list[Post]:
        submission_list = []
        # Verify if the query has already been executed recently before doing this
        self.scweet.scrape(since="2020-10-01", words=[fetch_request.query],
                           limit=fetch_request.limit,
                           lang="es",
                           custom_csv_name=f'tweets_{fetch_request.query}.csv')
        with open(f'outputs/tweets_{fetch_request.query}.csv') as file:
            reader = csv.DictReader(file)
            for row in reader:
                tweet_info = {
                    "id": row['tweetId'],
                    "text": row['Text'],
                    "timestamp": parser.parse(row['Timestamp'])
                }
                submission_list.append(tweet_info)
        return submission_list
