import os
import psycopg2
from os.path import join, dirname
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    '.env'
)

load_dotenv(env_path)

# Database connection details
DB_NAME = "airflow_logs"
DB_USER = "airflow_user"
DB_PASSWORD = "6VkQHqvcrg86BZTh"
DB_HOST = "postgres"
DB_PORT = "5432"

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
            INSERT INTO fact_post (post_id, title, author_id, subreddit_id, score, num_comments, created_at, url, selftext, category, subcategory)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            transformed_data["selftext"],
            transformed_data["category"],
            transformed_data["subcategory"]
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