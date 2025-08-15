from sqlalchemy import create_engine, Engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
import time
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

# Base class for all models
Base = declarative_base()

def get_connection_url() -> str:
    """
    Build database connection URL from environment variables or default values.
    """
    db_user = os.getenv("DB_USER", "carsales_user")
    db_password = os.getenv("DB_PASSWORD", "Mudar123!")
    db_host = os.getenv("DB_HOST", "db-carsales")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "carsales")
    
    # Build MySQL connection URL
    connection_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    logger.info(f"Database connection URL: mysql+pymysql://{db_user}:***@{db_host}:{db_port}/{db_name}")
    return connection_url

def get_engine() -> Engine:
    """
    Create and return a SQLAlchemy engine instance with retry logic.
    """
    connection_url = get_connection_url()
    
    # Retry connection logic for containerized environments
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting database connection (attempt {attempt + 1}/{max_retries})")
            
            engine = create_engine(
                connection_url,
                echo=os.getenv("SQL_ECHO", "False").lower() == "true",
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_timeout=30,
                pool_size=5,
                max_overflow=10,
                connect_args={
                    "connect_timeout": 60,
                    "read_timeout": 60,
                    "write_timeout": 60,
                }
            )
            
            # Test the connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1")).fetchone()
            
            logger.info("Database connection established successfully")
            return engine
            
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("All database connection attempts failed")
                raise e

# Create a lazy-initialized session factory
_session_factory = None

def get_session_factory():
    """Get or create the session factory."""
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _session_factory

@contextmanager
def get_db_session():
    """
    Context manager for database sessions.
    Usage:
        with get_db_session() as session:
            # use session for database operations
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_db():
    """
    Generator function for FastAPI dependency injection.
    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            # use db for database operations
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()