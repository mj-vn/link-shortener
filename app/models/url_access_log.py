from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.mixins import TimestampMixin


class URLAccessLog(TimestampMixin, Base):
    __tablename__ = "url_access_logs"
    id = Column(Integer, primary_key=True, index=True)

    url_id = Column(BigInteger, ForeignKey("urls.short_code"), index=True)

    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    url = relationship("URLItem", back_populates="logs")

