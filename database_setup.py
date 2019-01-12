#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
import datetime
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    provider = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'email': self.email,
            'provider': self.provider,
        }


class Genre(Base):
    __tablename__ = 'genre'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Book(Base):
    __tablename__ = 'book'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    author = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    genre_id = Column(Integer, ForeignKey('genre.id', ondelete='CASCADE'))
    genre = relationship(Genre, backref=backref('book', passive_deletes=True))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'author': self.author,
            'price': self.price,
            'description': self.description,
        }


engine = create_engine('sqlite:///BookGenre.db')

Base.metadata.create_all(engine)
