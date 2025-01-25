import datetime

from sqlalchemy import Column, Integer, String, BigInteger

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class Base(AsyncAttrs, DeclarativeBase):
    pass


class BaseModelMixin:

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()  # type: ignore

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(), onupdate=func.now(), server_default=func.now()
    )


class MediaFile(BaseModelMixin, Base):
    """Модель для представления медиафайлов в базе данных."""

    uid = Column(String, unique=True, index=True)
    filename = Column(String, index=True)
    file_size = Column(Integer)
    file_format = Column(String)
    file_extension = Column(String)
