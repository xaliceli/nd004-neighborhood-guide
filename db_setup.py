from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    places = relationship('Place', cascade='save-update, merge, delete')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Place(Base):
    __tablename__ = 'place'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    neighborhood = Column(String(80))
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship('Category')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User')
    created = Column(TIMESTAMP, server_default=func.now())

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        description = self.description.replace('\r', ' ').replace('\n', ' ')
        return {
            'name': self.name,
            'description': description,
            'id': self.id,
        }


engine = create_engine('sqlite:///neighborhood.db')
Base.metadata.create_all(engine)
