from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
import sqlalchemy.orm

Base = sqlalchemy.orm.declarative_base()


class City(Base):
    __tablename__ = "city"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    other_name = Column(String, nullable=True)
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    phone = Column(String, nullable=True)
    birthday = Column(DateTime, nullable=True)
    city = Column(Integer, ForeignKey(City.id, ondelete="CASCADE"))
    additional_info = Column(Text, nullable=True)
    is_admin = Column(Boolean, nullable=False)
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
