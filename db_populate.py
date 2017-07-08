from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

from db_setup import Base, User, Category, Place

engine = create_engine('sqlite:///neighborhood.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

with open('db_populate.json') as data_file:
    neighborhood_json = json.load(data_file)

# Create dummy users
for user in neighborhood_json['users']:
    user_entry = User(
        name=str(user['name']),
        email=str(user['email'])
    )
    session.add(user_entry)
    session.commit()

# Create initial categories
for category in neighborhood_json['categories']:
    cat_entry = Category(
        name=str(category['name']),
        description=str(category['description'])
    )
    session.add(cat_entry)
    session.commit()

# Create initial places
for place in neighborhood_json['places']:
    place_entry = Place(
        name=str(place['name']),
        neighborhood=str(place['neighborhood']),
        description=str(place['description']),
        category_id=int(place['category_id']),
        user_id=int(place['user_id']),
    )
    session.add(place_entry)
    session.commit()

print "added places to neighborhood guide!"
