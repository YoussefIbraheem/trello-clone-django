from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from . import Base
from sqlalchemy.orm import relationship
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String(255),nullable=False,index=True)
    description = Column(Text,nullable=True)
    
    created_at = Column(DateTime(timezone=True),server_default=func.now())
    updated_at = Column(DateTime(timezone=True),server_default=func.now())
    
    owner_id = Column(String(255),nullable=False,index=True)
    
    boards = relationship("Board", back_populates="project", cascade="all, delete-orphan")
    
    