# ruff: noqa: T201
import asyncio
from datetime import date
import os

import asyncpraw

from scraper.config import config


async def initiate_scraping():
    """Start scraping, sleep for an hour, and repeat."""
    # Do this in the Dockerfile
    if not os.path.exists("dataset"):
        os.mkdir("dataset")
    else:
        print("Dataset folder already exists.")
    reddit = asyncpraw.Reddit(
        client_id=config.CLIENT_ID,
        client_secret=config.CLIENT_SECRET,
        user_agent=config.USER_AGENT,
        ratelimit_seconds=config.RATELIMIT_SECONDS
    )
    # This should be saved in a local file as well
    accepted_submissions = []
    rejected_submissions = []
    while True:
        saved_submissions = []
        emotions_to_check = config.INITIAL_EMOTIONS
        for spanish_subreddit in config.ES_SUBREDDITS:
            subreddit = await reddit.subreddit(spanish_subreddit)
            async for submission in subreddit.new(limit=config.HOURLY_LIMIT):
                hashed_submission = hash(submission.selftext)
                if contains_emotion(submission, emotions_to_check):
                    saved_submissions.append(submission.selftext)
                    accepted_submissions.append(hashed_submission)
                else:
                    rejected_submissions.append(hashed_submission)
            print(f"Scraped {len(accepted_submissions)} new posts")
        with open(f"dataset/{date.today()}.txt", "a+") as f:
            for submission in saved_submissions:
                f.write(str(submission))
        print("Done scraping. Sleeping for an hour.")
        await asyncio.sleep(3600)

def contains_emotion(submission, emotions_to_check):
    """Analyze submission for pattern, return updated emotions."""
    return True
