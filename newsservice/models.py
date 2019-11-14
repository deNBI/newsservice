from datetime import datetime

from sqlalchemy import Column, Integer, String
from newsservice.db import Base


class News(Base):
    __tablename__ = 'News'
    id = Column('news_id', Integer, primary_key=True)
    title = Column(String(500))
    author = Column(String(300))
    time = Column(String(300))
    text = Column(String(5000))
    tag = Column(String(1000))
    facilityid = Column(String(2000))

    def __init__(self, title, author, text, tag, facility_id):
        self.title = title
        self.author = author
        self.time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.text = text
        self.tag = tag
        self.facilityid = facility_id

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'time': self.time,
            'text': self.text,
            'tag': self.tag,
            'facility_id': self.facilityid
        }
