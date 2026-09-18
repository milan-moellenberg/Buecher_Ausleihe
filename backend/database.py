import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env file
load_dotenv()

# Get database connection parameters
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")  # Default to localhost if not set
DB_PORT = os.getenv("DB_PORT", "5432")  # Default to 5432 if not set
DB_NAME = os.getenv("DB_NAME", "ausleihe_db")  # Default to ausleihe_db if not set

# Create SQLAlchemy engine and a session factory for database interactions
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=True)  # Set echo=True for SQL query logging in terminal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for all Database models to inherit from
Base = declarative_base()

# assist function for FastAPI dependency injection to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()