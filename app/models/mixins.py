from datetime import datetime

from sqlalchemy import DateTime, Column, event
from sqlalchemy.orm import Mapped


class TimestampMixin:

    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)


class ModifiedMixin(TimestampMixin):
    """The __exclude__ type must be `set` type.

    Example:
        __exclude__ = {'title'}
    """

    __exclude__ = set()

    modified_at: Mapped[datetime] = Column(DateTime, nullable=True)

    @property
    def last_modification_time(self):
        return self.modified_at or self.created_at

    @staticmethod
    def before_update(mapper, connection, target):
        if not target.object.__exclude__.issubset(target.unmodified):
            return

        target.object.modified_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, 'before_update', cls.before_update, raw=True)

