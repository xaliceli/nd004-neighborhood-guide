from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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


# Create dummy user
firstUser = User(name="Neighborhood Resident", email="name@email.com")
session.add(firstUser)
session.commit()

# Create category of restaurants and add entries to category
category1 = Category(name="Restaurants",
                     description="Places to eat.")

session.add(category1)
session.commit()

restaurant1 = Place(name="Bite Kitchen",
                    neighborhood="Ukrainian Village",
                    description="""
                                Quality New American food with an unpretentious
                                vibe. Delicious brunch at reasonable prices.
                                Next door to The Empty Bottle.
                                """,
                    category_id=1,
                    user_id=1)

restaurant2 = Place(name="Tarboush",
                    neighborhood="Wicker Park",
                    description="""
                                Amazing mediterranean food at low prices.
                                Wraps include tasty pickles. Amazing fries!
                                """,
                    category_id=1,
                    user_id=1)

restaurant3 = Place(name="Rangoli",
                    neighborhood="Humboldt Park",
                    description="""
                                Indian restaurant with spicy curries.
                                Madras Lamb Curry is delicious and hard
                                to find elsewhere in Chicago.
                                """,
                    category_id=1,
                    user_id=1)

restaurant4 = Place(name="Le Bouchon",
                    neighborhood="Bucktown",
                    description="""
                                Bustling French bistro with classic dishes.
                                Choose any three courses on Tuesdays for $29.
                                """,
                    category_id=1,
                    user_id=1)

session.add(restaurant1)
session.add(restaurant2)
session.add(restaurant3)
session.add(restaurant4)
session.commit()

# Create category of stores and add entries to category

category2 = Category(name="Stores",
                     description="Places to buy things.")

session.add(category2)
session.commit()

store1 = Place(name="Reckless Records",
               neighborhood="Wicker Park",
               description="""
                           Storied record shop stocking large selection
                           of music. Supposedly the reference point for
                           John Cusack's record shop in High Fidelity.
                           """,
               category_id=2,
               user_id=1)

store2 = Place(name="Myopic Books",
               neighborhood="Wicker Park",
               description="""
                           Multi-level used bookstore with diverse
                           selection and nice seating area on the second floor.
                           """,
               category_id=2,
               user_id=1)

store3 = Place(name="The Ark",
               neighborhood="Wicker Park",
               description="""
                           Small thrift store with surprising selection of
                           designer items. Frequent sales and daily deals.
                           """,
               category_id=2,
               user_id=1)

session.add(store1)
session.add(store2)
session.add(store3)
session.commit()

# Create category of coffeeshops and add entries to category

category3 = Category(name="Cafes",
                     description="Places to sit and work over coffee or tea.")

session.add(category3)
session.commit()

cafe1 = Place(name="Filter",
              neighborhood="Wicker Park",
              description="""
                          Large coffeeshop serving all-day food.
                          Plenty of couches and tables.
                          """,
              category_id=3,
              user_id=1)

cafe2 = Place(name="Wormhole",
              neighborhood="Wicker Park",
              description="""
                          Always busy cafe for coffee snobs.
                          Has a Delorean.
                          """,
              category_id=3,
              user_id=1)

cafe3 = Place(name="Bru",
              neighborhood="Wicker Park",
              description="""
                          Coffeeshop plus coworking space.
                          Serves crepes and smoothies.
                          """,
              category_id=3,
              user_id=1)

cafe4 = Place(name="Caffe Streets",
              neighborhood="Wicker Park",
              description="""
                          Chic European-style coffeeshop.
                          Sleek interior, no food.
                          """,
              category_id=3,
              user_id=1)

session.add(cafe1)
session.add(cafe2)
session.add(cafe3)
session.add(cafe4)
session.commit()

# Create category of music venues and add entries to category

category4 = Category(name="Music",
                     description="Places to hear live music.")

session.add(category4)
session.commit()

music1 = Place(name="The Empty Bottle",
               neighborhood="Ukrainian Village",
               description="""
                           Boasts "music friendly dancing." Good
                           place to catch local bands as well as
                           Pitchfork's favored band of the day.
                           """,
               category_id=4,
               user_id=1)

music2 = Place(name="The Hideout",
               neighborhood="Goose Island",
               description="""
                           Small venue hidden behind warehouses on Goose
                           Island.
                           """,
               category_id=4,
               user_id=1)

music3 = Place(name="Smart Bar",
               neighborhood="Lakeview",
               description="""
                           Nightclub with long history of supporting Chicago's
                           house scene. Somewhat out of place next to
                           Wrigleyville's sports bars.
                           """,
               category_id=4,
               user_id=1)

session.add(music1)
session.add(music2)
session.add(music3)
session.commit()

# Create category of other interesting places and add entries to category

category5 = Category(name="Other",
                     description="Misc bucket of other interesting places.")

session.add(category5)
session.commit()

other1 = Place(name="The 606",
               neighborhood="Bucktown to Humboldt Park",
               description="""
                           Chicago's own high line, spanning roughly 3 miles.
                           Tons of dog parks along the way!
                           """,
               category_id=5,
               user_id=1)

other2 = Place(name="The Flatiron Building",
               neighborhood="Wicker Park",
               description="""
                           Artist studios open to the public every first
                           Friday. Many have dogs!
                           """,
               category_id=5,
               user_id=1)


session.add(other1)
session.add(other2)
session.commit()


print "added places to neighborhood guide!"
