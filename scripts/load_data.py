import os
import psycopg2
from os.path import join, dirname
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection details
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

def load_data(transformed_data):
    connection = None  
    cursor = None 

    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = connection.cursor()

        # Insert author and subreddit into dimension tables (handling conflicts)
        cursor.execute("""
            INSERT INTO dim_author (author_id, author_name)
            VALUES (%s, %s)
            ON CONFLICT (author_id) DO NOTHING;
        """, (transformed_data["author_name"], transformed_data["author_name"]))

        cursor.execute("""
            INSERT INTO dim_subreddit (subreddit_id, subreddit_name)
            VALUES (%s, %s)
            ON CONFLICT (subreddit_id) DO NOTHING;
        """, (transformed_data["subreddit_name"], transformed_data["subreddit_name"]))

        # Insert the post data into the fact_post table
        cursor.execute("""
            INSERT INTO fact_post (post_id, title, author_id, subreddit_id, score, num_comments, created_at, url, selftext)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (post_id) DO NOTHING;
        """, (
            transformed_data["post_id"],
            transformed_data["title"],
            transformed_data["author_name"],
            transformed_data["subreddit_name"],
            transformed_data["score"],
            transformed_data["num_comments"],
            transformed_data["created_at"],
            transformed_data["url"],
            transformed_data["selftext"]
        ))

        connection.commit()
        print("Data loaded successfully!")

    except Exception as error:
        print(f"Error loading data: {error}")
        if connection:
            connection.rollback()

    finally:
        if cursor:  
            cursor.close()
        if connection: 
            connection.close()