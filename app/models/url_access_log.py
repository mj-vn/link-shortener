from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from app.db.session import Base
from app.models.base_class import mapped_column
from app.models.mixins import TimestampMixin


class URLAccessLog(TimestampMixin, Base):
    __tablename__ = "url_access_logs"
    id = Column(Integer, primary_key=True, index=True)

    url_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("urls.short_code"),
                                        index=True)

    ip_address: Mapped[str] = mapped_column(String)
    user_agent: Mapped[str] = mapped_column(String)

    url = relationship("URLItem", back_populates="logs")

