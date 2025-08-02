import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Determine the directory where the SQLite database will be stored.
# This ensures it's created in the project root, not within a service's directory.
db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
db_path = os.path.join(db_dir, 'catalog.db')
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

# Create the SQLAlchemy engine.
# connect_args={"check_same_thread": False} is required for SQLite.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a sessionmaker instance to create new database sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for our models.
Base = declarative_base()

def get_db():
    """
    Dependency for getting a database session.
    It yields a session and ensures it's closed properly.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
