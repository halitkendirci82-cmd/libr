from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Book(Base):
    __tablename__ = "books"

    id        = Column(Integer, primary_key=True, index=True)
    title     = Column(String, nullable=False)
    author    = Column(String, nullable=False)
    isbn      = Column(String, unique=True, nullable=False)
    genre     = Column(String, default="Genel")
    year      = Column(Integer, nullable=True)
    copies    = Column(Integer, default=1)
    available = Column(Integer, default=1)
    added_at  = Column(DateTime, default=datetime.now)

    loans = relationship("Loan", back_populates="book")


class Member(Base):
    __tablename__ = "members"

    id        = Column(Integer, primary_key=True, index=True)
    name      = Column(String, nullable=False)
    email     = Column(String, unique=True, nullable=False)
    phone     = Column(String, default="")
    joined_at = Column(DateTime, default=datetime.now)

    loans = relationship("Loan", back_populates="member")


class Loan(Base):
    __tablename__ = "loans"

    id          = Column(Integer, primary_key=True, index=True)
    book_id     = Column(Integer, ForeignKey("books.id"), nullable=False)
    member_id   = Column(Integer, ForeignKey("members.id"), nullable=False)
    borrowed_at = Column(DateTime, default=datetime.now)
    returned_at = Column(DateTime, nullable=True)

    book   = relationship("Book", back_populates="loans")
    member = relationship("Member", back_populates="loans")
