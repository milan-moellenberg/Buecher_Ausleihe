import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables from .env file
load_dotenv()

# Get the access tokens

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Database connection string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print("Connecting to database...")

try:
    # create SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Test the connection
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        db_version = result.fetchone()
        print("\n Database connection successful:")
        print(f"PostgreSQL version: {db_version[0]}")

except Exception as e:  
      print("Error connecting to the database!")
      print(f"Error: {e}")
            