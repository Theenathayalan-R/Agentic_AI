from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class TableMetadata(Base):
    __tablename__ = "table_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, index=True, nullable=False)
    schema_name = Column(String, index=True, nullable=False)
    source = Column(String, nullable=True)
    business_definition = Column(Text, nullable=True)
    data_quality_score = Column(Integer, nullable=True)
    tags = Column(JSON, nullable=True)  # Stores a list of strings as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    columns = relationship("ColumnMetadata", back_populates="table", cascade="all, delete-orphan")
    source_lineage = relationship("LineageMetadata", foreign_keys="LineageMetadata.source_table_id", back_populates="source_table")
    target_lineage = relationship("LineageMetadata", foreign_keys="LineageMetadata.target_table_id", back_populates="target_table")

class ColumnMetadata(Base):
    __tablename__ = "column_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("table_metadata.id"), nullable=False)
    column_name = Column(String, index=True, nullable=False)
    data_type = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
    table = relationship("TableMetadata", back_populates="columns")

class LineageMetadata(Base):
    __tablename__ = "lineage_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    source_table_id = Column(Integer, ForeignKey("table_metadata.id"), nullable=False)
    target_table_id = Column(Integer, ForeignKey("table_metadata.id"), nullable=False)
    transformation_logic = Column(Text, nullable=True)
    
    source_table = relationship("TableMetadata", foreign_keys=[source_table_id], back_populates="source_lineage")
    target_table = relationship("TableMetadata", foreign_keys=[target_table_id], back_populates="target_lineage")

class UserFeedback(Base):
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("table_metadata.id"), nullable=False)
    column_id = Column(Integer, ForeignKey("column_metadata.id"), nullable=True)
    feedback_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
