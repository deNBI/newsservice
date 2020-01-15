import sys
from datetime import datetime

from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from newsservice.db import Base


news_tag = Table('news_tag', Base.metadata,
                 Column('news_id', Integer, ForeignKey('news.id'), primary_key=True),
                 Column('tag_id', Integer, ForeignKey('tag.id'), primary_key=True))

news_facility = Table('news_facility', Base.metadata,
                      Column('news_id', Integer, ForeignKey('news.id'), primary_key=True),
                      Column('facility_id', Integer, ForeignKey('facility.id'), primary_key=True))


class News(Base):
    ID = "id"
    TAG = "tag"
    AUTHOR = "author"
    TITLE = "title"
    TEXT = "text"
    OLDER = "older"
    NEWER = "newer"
    FACILITY_ID = "facilityid"
    TOKEN = "perun-login-token"

    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    author = Column(String(300))
    time = Column(String(300))
    text = Column(String(5000))
    tag = relationship("Tag", secondary="news_tag", backref='news')
    facilityid = relationship("Facility", secondary="news_facility", backref='news')

    def __init__(self, title, author, text, tag, facility_id):
        self.title = title
        self.author = author
        self.time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.text = text
        for new_tag in tag:
            new_tag = new_tag.strip()
            if new_tag == '':
                continue
            try:
                existing_tag = Tag.query.filter_by(name=new_tag).all()
                if len(existing_tag) > 0:
                    self.tag.extend(existing_tag)
                else:
                    self.tag.append(Tag(new_tag))
            except Exception as e:
                print(e)
        for new_facility in facility_id:
            try:
                existing_facility = Facility.query.filter_by(facility_id=new_facility).all()
                if len(existing_facility) > 0:
                    self.facilityid.extend(existing_facility)
                else:
                    self.facilityid.append(Facility(new_facility))
            except Exception as e:
                print(e)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'time': self.time,
            'text': self.text,
            'tag': [tag.name for tag in self.tag],
            'facility_id': [facility.facility_id for facility in self.facilityid]
        }

    @staticmethod
    def get_tag_queries(tags):
        queries = []
        tags = tags.split(',')
        for search_tag in tags:
            queries.append(News.tag.any(name=search_tag))
        return queries

    @staticmethod
    def get_facility_queries(facility_id):
        queries = []
        facility_id = facility_id.split(',')
        for search_facility_id in facility_id:
            try:
                search_facility_id = int(search_facility_id)
            except:
                search_facility_id = -1
            queries.append(News.facilityid.any(facility_id=search_facility_id))
        return queries

    @staticmethod
    def get_all_queries(news_id=None, author='', title='', text='', tags='', facility_id='',
                        older=sys.maxsize, newer=-sys.maxsize):
        queries = [News.author.contains(author),
                   News.title.contains(title),
                   News.text.contains(text),
                   News.time <= older,
                   News.time >= newer]

        if tags != '':
            queries.extend(News.get_tag_queries(tags))
        if facility_id != '':
            queries.extend(News.get_facility_queries(facility_id))
        if news_id is not None:
            queries.append(News.id == news_id)
        return queries

    @staticmethod
    def get_all_queries_by_request(request):
        news_id = request.args.get(News.ID, type=int, default=None)
        tags = request.args.get(News.TAG, type=str, default='')
        author = request.args.get(News.AUTHOR, type=str, default='')
        title = request.args.get(News.TITLE, type=str, default='')
        text = request.args.get(News.TEXT, type=str, default='')
        facility_id = request.args.get(News.FACILITY_ID, type=str, default='')
        older = request.args.get(News.OLDER, type=int, default=sys.maxsize)
        newer = request.args.get(News.NEWER, type=int, default=-sys.maxsize)
        return News.get_all_queries(news_id, author, title, text, tags, facility_id, older, newer)

    def update(self, title, text, tag, facility_id):
        self.title = title
        self.text = text
        self.tag = []
        self.facilityid = []
        for new_tag in tag:
            new_tag = new_tag.strip()
            if new_tag == '':
                continue
            try:
                existing_tag = Tag.query.filter_by(name=new_tag).all()
                if len(existing_tag) > 0:
                    self.tag.extend(existing_tag)
                else:
                    self.tag.append(Tag(new_tag))
            except Exception as e:
                print(e)
        for new_facility in facility_id:
            try:
                existing_facility = Facility.query.filter_by(facility_id=new_facility).all()
                if len(existing_facility) > 0:
                    self.facilityid.extend(existing_facility)
                else:
                    self.facilityid.append(Facility(new_facility))
            except Exception as e:
                print(e)


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String(2000), unique=True)

    def __init__(self, name):
        self.name = name


class Facility(Base):
    __tablename__ = 'facility'
    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, unique=True)

    def __init__(self, facility_id):
        self.facility_id = facility_id
