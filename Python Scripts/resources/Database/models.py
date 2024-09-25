# Resource Folder Import
import os
import sys
sys.path.append(os.environ['autobot_modules'])

from sqlalchemy import Column, Integer, String, ForeignKey
from Database.database import Base
from flask_user import UserMixin

class Rate(Base):
    __tablename__ = 'rates'
    state = Column(String(50), nullable=False, primary_key=True)
    utility = Column(String(50), nullable=False, primary_key=True)
    price = Column(Integer, nullable=False)

    def __repr__(self):
        return f'<Rate(state="{self.state}",utility="{self.utility}",price="{self.price}")>'

if __name__ == "__main__":
    print('working')