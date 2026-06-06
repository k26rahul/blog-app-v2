from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

    blogs = relationship("Blog", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    comments = relationship(
        "Comment", back_populates="user", cascade="all, delete-orphan"
    )


class Blog(db.Model):
    __tablename__ = "blogs"
    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String)
    slug = Column(String, unique=True)
    description = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    user_id = Column(Integer, ForeignKey("users.id"))

    author = relationship("User", back_populates="blogs", uselist=False)
    likes = relationship("Like", back_populates="blog", cascade="all, delete-orphan")
    comments = relationship(
        "Comment", back_populates="blog", cascade="all, delete-orphan"
    )


class Like(db.Model):
    __tablename__ = "likes"
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    blog_id = Column(Integer, ForeignKey("blogs.id"))

    user = relationship("User", back_populates="likes", uselist=False)
    blog = relationship("Blog", back_populates="likes", uselist=False)


class Comment(db.Model):
    __tablename__ = "comments"
    id = Column(Integer, autoincrement=True, primary_key=True)
    content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey("users.id"))
    blog_id = Column(Integer, ForeignKey("blogs.id"))

    user = relationship("User", back_populates="comments", uselist=False)
    blog = relationship("Blog", back_populates="comments", uselist=False)
