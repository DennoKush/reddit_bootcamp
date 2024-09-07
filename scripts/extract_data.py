import praw
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reddit API credentials
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
user_agent = os.getenv("user_agent")

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id=client_id, client_secret=client_secret, user_agent=user_agent
)


def extract_post_data(post):
    """Extract relevant data from a post."""
    return {
        "id": post.id,
        "title": post.title,
        "author": post.author.name if post.author else "[deleted]",
        "subreddit": post.subreddit.display_name,
        "score": post.score,
        "num_comments": post.num_comments,
        "created_utc": post.created_utc,
        "url": post.url,
        "selftext": post.selftext,
    }


def fetch_subreddit_data(subreddit_name, category="hot", limit=100):
    """Fetch data from a specific subreddit and category."""
    subreddit = reddit.subreddit(subreddit_name)

    if category == "hot":
        posts = subreddit.hot(limit=limit)
    elif category == "top":
        posts = subreddit.top(limit=limit, time_filter="week")
    else:
        raise ValueError("Invalid category. Choose 'hot' or 'top'.")

    return [extract_post_data(post) for post in posts]


def main():
    subreddits = ["news", "worldnews", "technology"]  # Add more subreddits as needed
    categories = ["hot", "top"]

    all_data = {}

    for subreddit in subreddits:
        all_data[subreddit] = {}
        for category in categories:
            print(f"Fetching {category} posts from r/{subreddit}")
            all_data[subreddit][category] = fetch_subreddit_data(subreddit, category)

    # Save data to a JSON file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = "reddit_data.json"

    with open(filename, "w") as f:
        json.dump(all_data, f, indent=4)

    print(f"Data saved to {filename}")


if __name__ == "__main__":
    main()
