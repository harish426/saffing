from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# Add pool_pre_ping to prevent using closed connections
# Add pool_recycle to recycle connections regularly
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800  # Recycle connections after 30 minutes
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_latest_resume(db):
    """
    Fetches the latest resume with populated resumeData.
    """
    # Import here to avoid circular dependency with models.py which imports Base from here
    from app.models.models import Resume 
    return db.query(Resume).filter(Resume.resumeData.isnot(None)).order_by(Resume.createdAt.desc()).first()

def get_latest_resume_for_user(db, user_id):
    """
    Fetches the latest resume for a specific user with populated resumeData.
    """
    from app.models.models import Resume
    return db.query(Resume).filter(Resume.userId == user_id, Resume.resumeData.isnot(None)).order_by(Resume.createdAt.desc()).first()

def get_user_details(db, user_id):
    from app.models.models import User
    return db.query(User).filter(User.id == user_id).first()