from fastapi import FastAPI
from scraper.config import config
import praw
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/random")
async def random():
    reddit = praw.Reddit(
        client_id=config.CLIENT_ID,
        client_secret=config.CLIENT_SECRET,
        user_agent=config.USER_AGENT,
    )
    for submission in reddit.subreddit("test").hot(limit=10):
        print(submission.title)