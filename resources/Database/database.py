from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

prod = False

if prod:
    engine = create_engine('sqlite:///autobot.sqlite')
else:
    engine = create_engine('sqlite:///:memory:', echo=True)

Session = sessionmaker(bind=engine)

Base = declarative_base()
