from sqlalchemy import Column, String, Boolean, DateTime, func, LargeBinary, Integer
from database import Base

class JobDescription(Base):
    __tablename__ = "JobDescription"

    id = Column(String, primary_key=True, index=True) # Prisma uses @default(cuid()) which we might need to handle if creating from python, but strictly for reading/processing, string is fine.
    company = Column(String, nullable=True)
    jobRole = Column(String, nullable=True)
    jobDescription = Column(String, nullable=True)
    location = Column(String, nullable=True)
    vendorName = Column(String, nullable=True)
    vendorContact = Column(String, nullable=True)
    vendorEmail = Column(String, nullable=True)
    careerLink = Column(String, nullable=True)
    isActive = Column(Boolean, default=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())

class Resume(Base):
    __tablename__ = "resume"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    content = Column(LargeBinary)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
