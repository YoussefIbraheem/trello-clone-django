from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base

class Board(Base):
    
    __tablename__="boards"
    
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,nullable=False,index=True)
    description = Column(Text,nullable=True)
    columns = Column(JSON,nullable=True,default=lambda: {"columns": ["ToDO", "InProgress", "Done"]})
    
    project_id = Column(Integer,ForeignKey("projects.id"),index=True,nullable=False)
    
    
    created_at = Column(DateTime(timezone=True),server_default=func.now())
    updated_at = Column(DateTime(timezone=True),server_default=func.now())
    
    project = relationship("Project",back_populates="boards")
    tasks = relationship("Task", back_populates="board", cascade="all, delete-orphan")