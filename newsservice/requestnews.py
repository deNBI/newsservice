import json
from newsservice.models import News

from flask import (Blueprint, request)

bp = Blueprint('request', __name__)

ID = "id"
TAG = "tag"
AUTHOR = "author"
TITLE = "title"
TEXT = "text"
OLDER = "older"
NEWER = "newer"
FACILITY_ID = "facilityid"

@bp.route('/requestnews', methods=['GET', 'POST'])
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
