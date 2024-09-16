# reddit_bootcamp
To run the application you need [docker](https://www.docker.com/).
Install docker on your machine. This should also install `docker compose`.

## Run the application
Run the code by running `docker compose up -d` in the terminal.

## How to use the Reddit API
The script that fetches data from given subreddits can be found under `scripts/extract_data.py`.    
It uses the `praw` library to interact with the Reddit API.    
Here's how to create the needed credentials:
1. Go to: `https://www.reddit.com/prefs/apps/`.
2. Click the `create app` button.
3. Give the app with the following settings, change if needed: ![reddit_image](assets/reddit_apps_section.png)
4. Copy the client id and client secret into the `.env` file, it's in the same folder as the `extract_data.py` script.
![reddit_client_id_and_secret](assets/reddit_client_id_and_secret.png)