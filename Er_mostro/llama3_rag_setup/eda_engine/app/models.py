from sqlalchemy import Column, Integer, JSON, ForeignKey, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class RawUpload(Base):
    __tablename__ = "raw_uploads"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(JSON)
    file_hash = Column(JSON)
    user_id = Column(JSON)
    upload_time = Column(DateTime(timezone=True))
    file_content = Column(LargeBinary)

class EDAResult(Base):
    __tablename__ = "eda_results"
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("raw_uploads.id"))
    eda_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

