from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class Award(Base):
    __tablename__     = 'awards'
    id                  = Column(Integer, primary_key=True)
    award_name          = Column(String(500))
    category            = Column(String(500))
    first_place         = Column(String(500))
    second_place        = Column(String(500))
    third_place         = Column(String(500))
    description         = Column(String(10000))
    address             = Column(String(500))
    address_lat         = Column(String(500))
    address_long        = Column(String(500))
    address_formatted   = Column(String(500))
    url                 = Column(String(500))
    phone               = Column(String(500))
    whose_pick          = Column(String(500))
    style_url           = Column(String(500))
    year                = Column(String(500))
           
    def __repr__(self):
        return '<Award: {0} in {1} from {2}>'.format(self.award_name, self.category, self.year)


def setup_db():
    engine = create_engine('sqlite:///style_weekly.db')

    # Create all tables in the engine. This is equivalent to "Create Table"
    # statements in raw SQL.
    Base.metadata.create_all(engine)    

def get_session():

    engine = create_engine('sqlite:///style_weekly.db')
    session = sessionmaker()
    session.configure(bind=engine)
    s = session()
    return s