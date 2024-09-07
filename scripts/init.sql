CREATE TABLE IF NOT EXISTS dim_author (
    author_id VARCHAR(255) PRIMARY KEY,
    author_name TEXT
    );

CREATE TABLE dim_subreddit (
    subreddit_id VARCHAR(255) PRIMARY KEY,
    subreddit_name TEXT
    );

CREATE TABLE IF NOT EXISTS fact_post (
    post_id VARCHAR(255) PRIMARY KEY,
    title TEXT,
    author_id VARCHAR(255),
    subreddit_id VARCHAR(255),
    score INT,
    num_comments INT,
    created_at TIMESTAMP,
    url TEXT,
    selftext TEXT,
    category TEXT,
    subcategory TEXT
    );

CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,
    day INT,
    month INT,
    year INT,
    weekday INT
    );






