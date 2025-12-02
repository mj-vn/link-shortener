from app.models.base_class import mapped_column, Base
from app.models.mixins import ModifiedMixin

from sqlalchemy import Integer, ForeignKey, Sequence, BigInteger
from sqlalchemy.orm import Mapped, relationship


url_id_seq = Sequence("url_id_seq", start=3521614606208)


class URLItem(ModifiedMixin, Base):
    __tablename__ = "urls"

    short_code: Mapped[int] = mapped_column(
        BigInteger,
        url_id_seq,
        primary_key=True,
        server_default=url_id_seq.next_value()
    )
    original_url: Mapped[str]
    clicked_count: Mapped[int] = mapped_column(Integer, default=0)

    logs = relationship("URLAccessLog", back_populates="url")
