from sqlalchemy import Column, String, Boolean, DateTime, func, LargeBinary, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "User"

    id = Column(String, primary_key=True, index=True) # @default(cuid()) in Prisma
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    jobEmail = Column(String, nullable=True)
    appPassword = Column(String, nullable=True)
    phoneNumber = Column(String, nullable=True)
    linkedinUrl = Column(String, nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())

    sessions = relationship("Session", back_populates="user")
    resumes = relationship("Resume", back_populates="user")
    jobDescriptions = relationship("JobDescription", back_populates="user")

class Session(Base):
    __tablename__ = "Session"

    id = Column(String, primary_key=True, index=True)
    sessionToken = Column(String, unique=True, index=True)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"))
    expires = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="sessions")

class Resume(Base):
    __tablename__ = "Resume"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String)
    mimeType = Column(String)
    content = Column(LargeBinary)
    resumeData = Column(JSON, nullable=True)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"))
    createdAt = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="resumes")

class JobDescription(Base):
    __tablename__ = "JobDescription"

    id = Column(String, primary_key=True, index=True)
    company = Column(String, nullable=True)
    jobRole = Column(String, nullable=True)
    jobDescription = Column(String, nullable=True)
    location = Column(String, nullable=True)
    vendorName = Column(String, nullable=True)
    vendorContact = Column(String, nullable=True)
    vendorEmail = Column(String, nullable=True)
    careerLink = Column(String, nullable=True)
    submissionDetails = Column(String, nullable=True)
    requirementSource = Column(String, nullable=True)
    progress = Column(String, default="None")
    isActive = Column(Boolean, default=True)
    userId = Column(String, ForeignKey("User.id", ondelete="CASCADE"), nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="jobDescriptions")
