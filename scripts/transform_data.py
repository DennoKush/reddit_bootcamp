import re
from datetime import datetime

# Function to transform Reddit post data
def transform_data(data):
    # Transform the timestamp into a human-readable format
    created_at = datetime.utcfromtimestamp(data["created_utc"]).strftime('%Y-%m-%d %H:%M:%S')

    # Extract category and subcategory from the URL
    url_parts = re.findall(r"https?://(?:www\.)?([^/]+)/([^/]+)/?", data["url"])
    if url_parts:
        category = url_parts[0][0]
        subcategory = url_parts[0][1]
    else:
        category = None
        subcategory = None

    # Create a dictionary with transformed data
    transformed_data = {
        "post_id": data["id"],
        "title": data["title"],
        "author_name": data["author"],
        "subreddit_name": data["subreddit"],
        "score": data["score"],
        "num_comments": data["num_comments"],
        "created_at": created_at,
        "url": data["url"],
        "selftext": data["selftext"]
    }

    return transformed_data
