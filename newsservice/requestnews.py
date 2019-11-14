import json
import sys
from newsservice.models import News

from flask import (Blueprint, request, jsonify)

bp = Blueprint('request', __name__)

ID = "id"
TAG = "tag"
AUTHOR = "author"
TITLE = "title"
TEXT = "text"
OLDER = "older"
NEWER = "newer"
FACILITY_ID = "facilityid"


@bp.route('/requestnews/json', methods=['GET'])
def requestdb():
    """
    This Method receives filter values as a JSON and uses these to make queries at the database.
    It creates a List with all entries of the database which match the filters.
    Then it converts the list to a JSON document.
    :return: JSON document containing all database entries which matches the filter values.
    """

    data = []
    articles = News.query.all()

    filter_json = json.loads(request.data.decode('utf-8'))

    for key, value in filter_json.items():
        if value != "":
            if key == ID:
                articles = [article for article in articles if str(article.id) == value]
            if key == TAG:
                articles = [article for article in articles if article.tag == value]
            if key == AUTHOR:
                articles = [article for article in articles if value in article.author]
            if key == TITLE:
                articles = [article for article in articles if value in article.title]
            if key == TEXT:
                articles = [article for article in articles if value in article.text]
            if key == FACILITY_ID:
                articles = [article for article in articles if value in article.facilityid]
            if key == OLDER:
                articles = [article for article in articles if article.time <= value]
            if key == NEWER:
                articles = [article for article in articles if article.time >= value]

    for article in articles:
        data.insert(0, {'id': article.id, 'title': article.title, 'author': article.author, 'time': article.time, 'tag': article.tag,
                        'text': article.text, 'facilityid': article.facilityid})

    return json.dumps(data)


@bp.route('/request', methods=['GET'])
def request_values_json():
    return jsonify(json_list=[i.serialize for i in request_values(request)])


def request_values(_request):
    id = _request.args.get(ID, type=int, default=None)
    tag = _request.args.get(TAG, type=str, default='')
    author = _request.args.get(AUTHOR, type=str, default='')
    title = _request.args.get(TITLE, type=str, default='')
    text = _request.args.get(TEXT, type=str, default='')
    facility_id = _request.args.get(FACILITY_ID, type=str, default='')
    older = _request.args.get(OLDER, type=int, default=sys.maxsize)
    newer = _request.args.get(NEWER, type=int, default=-sys.maxsize)

    queries = [News.tag.contains(tag),
               News.author.contains(author),
               News.title.contains(title),
               News.text.contains(text),
               News.facilityid.contains(facility_id),
               News.time <= older,
               News.time >= newer]

    if id is not None:
        queries.append(News.id == id)

    articles = News.query.filter(*queries).all()

    return articles


def request_facility_news(facility_id):
    articles = News.query.filter(News.facilityid.contains(facility_id)).order_by(News.id.desc()).all()
    return articles
