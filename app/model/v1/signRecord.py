"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from lin.interface import InfoCrud as Base
from sqlalchemy import Column, Integer, String

class signRecord(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    mail = Column(String(50), default="xxx@xgd.com")
    name = Column(String(50))
    dev_model = Column(String(10))
    sign_type = Column(String(10))
    summary = Column(String(1000))
    date_str = Column(String(14))
