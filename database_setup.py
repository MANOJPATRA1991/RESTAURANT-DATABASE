import sys

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

# to implement foreign key relationships
from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

# Base maintains classes and tables relative to it
# Classes that we define inherit from the Base class
Base = declarative_base()


class Restaurant(Base):
    # create a table named Restaurant
    __tablename__ = 'restaurant'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)


class MenuItem(Base):
    # create a table named menu_item
    __tablename__ = 'menu_item'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)


# INSERT AT END OF FILE
# creates an engine which provides connectivity to the database server
engine = create_engine('sqlite:///restaurantmenu.db')

# goes into the database and adds the classes that we defined
# as new tables into the database
Base.metadata.create_all(engine)
