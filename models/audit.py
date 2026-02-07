from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from datetime import datetime

class EnrollmentAudit(Base):
    __tablename__ = "enrollment_audit"
    id = Column(Integer, primary_key=True)
    enrollment_id = Column(Integer)
    action = Column(String) # "ENROLLED" or "DROPPED"
    user_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)