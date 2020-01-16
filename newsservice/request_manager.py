from newsservice.db import db_session
from newsservice.models import News
from newsservice.auth import auth

from flask import (Blueprint, request, json, jsonify)
from newsservice.db import init_db

bp = Blueprint('requests', __name__)


@bp.route('/', methods=['POST'])
def save():
    """
    This Method receives a News and a Authentication Token via JSON document. If the check with auth() was successful it
    adds the news to the database. If not it tells the user that the news wasn't added.
    :return: a status whether the News was added or not.
    """
    init_db()
    article_json = None
    try:
        article_json = json.loads(request.data.decode('utf-8'))['news']
    except Exception as e:
        print(e)

    if article_json is None:
        try:
            article_json = request.json['news']
        except Exception as e:
            print(e)
            return "Something went wrong in reading the request. Returning."

    if article_json[News.TITLE].strip() and article_json[News.AUTHOR].strip() \
            and article_json[News.TEXT].strip() and article_json[News.TAG] \
            and article_json[News.FACILITY_ID] and article_json[News.TOKEN].strip():
        article = News(article_json[News.TITLE], article_json[News.AUTHOR], article_json[News.TEXT],
                       article_json[News.TAG], article_json[News.FACILITY_ID])
    else:
        return "No empty fields are allowed in the JSON document."

    facility_id_no_list = check_if_all_facilities_true(article_json[News.FACILITY_ID], article_json[News.TOKEN])
    if not facility_id_no_list:
        db_session.add(article)
        db_session.commit()
        return "The article: '{0}' was added.".format(article_json[News.TITLE])
    else:
        #return 'The news was not posted, as you dont have the permission to post to these facilities: ' + ','.join(facility_id_no_list)
        return 'Not posted. Authentication failed for: {0}'.format(','.join(facility_id_no_list))


@bp.route('/', methods=['DELETE'])
def delete():
    news_id = None
    token = None
    try:
        news_id = json.loads(request.data.decode('utf-8'))[News.ID]
        token = json.loads(request.data.decode('utf-8'))[News.TOKEN]
    except Exception as e:
        print(e)

    if news_id is None or token is None:
        try:
            news_id = request.json[News.ID]
            token = request.json[News.TOKEN]
            if news_id is None or token is None:
                return 'No news id or token found in request.'
        except Exception as e:
            print(e)
            return "Something went wrong in reading the request. Returning."

    #news_id = request.args.get(News.ID, None)
    #token = request.args.get(News.TOKEN, None)
    article = News.query.filter(News.id == news_id).first()
    if article is None:
        return 'No article found.'
    fids = [facility.facility_id for facility in article.facilityid]
    fids = check_if_all_facilities_true(fids, token)
    if not fids or len(fids) == 0:
        db_session.delete(article)
        db_session.commit()
    else:
        return 'Not deleted. Authentication failed for: {0}'.format(','.join(fids))

    return 'True'


@bp.route('/', methods=['PATCH'])
def patch():
    news_id = None
    title = None
    text = None
    tag = None
    fids = None
    token = None
    try:
        news_id = json.loads(request.data.decode('utf-8'))[News.ID]
        title = json.loads(request.data.decode('utf-8'))[News.TITLE]
        text = json.loads(request.data.decode('utf-8'))[News.TEXT]
        tag = json.loads(request.data.decode('utf-8'))[News.TAG]
        fids = json.loads(request.data.decode('utf-8'))[News.FACILITY_ID]
        token = json.loads(request.data.decode('utf-8'))[News.TOKEN]
    except Exception as e:
        print(e)

    if news_id is None or token is None or title is None or text is None or tag is None or fids is None:
        try:
            news_id = request.json[News.ID]
            title = request.json[News.TITLE]
            text = request.json[News.TEXT]
            tag = request.json[News.TAG]
            fids = request.json[News.FACILITY_ID]
            token = request.json[News.TOKEN]
            if news_id is None or token is None or title is None or text is None or tag is None or fids is None:
                return 'No news id or token or title or text or tag or facility id found in request.'
        except Exception as e:
            print(e)
            return "Something went wrong in reading the request. Returning."

    article = News.query.filter(News.id == news_id).first()
    if article is None:
        return 'No article found.'
    news_facility_ids = check_if_all_facilities_true([facility.facility_id for facility in article.facilityid], token)
    if not news_facility_ids or len(news_facility_ids) == 0:
        article.update(title, text, tag, fids)
        db_session.commit()
        return "The article: '{0}' was patched.".format(article.title)
    else:
        return 'Not patched. Authentication failed for: {0}'.format(','.join(fids))


@bp.route('/request', methods=['GET'])
def request_values_as_json():
    queries = News.get_all_queries_by_request(request)
    articles = News.query \
        .filter(*queries) \
        .order_by(News.id.desc()) \
        .all()
    return jsonify(json_list=[i.serialize for i in articles])


@bp.route('/<tags>/latest')
def request_latest_news_by_tag(tags):
    article = News.query \
        .filter(*News.get_tag_queries(tags)) \
        .order_by(News.id.desc()) \
        .first()
    if request.content_type == 'application/json':
        if article is None:
            return {}
        return json.dumps(dict(title=article.title, text=article.text,
                               author=article.author, time=article.time))
    else:
        if article is None:
            return ''
        return '{0}\n{1}\nBy {2} on {3}\n'.format(article.title, article.text, article.author, article.time)


@bp.route('/latest', methods=['GET'])
def request_latest_news_as_string():
    """
    This Method queries the last item of the database and convert it to a string.
    :return: A String with the last item of the database
    """
    article = News.query.order_by(News.id.desc()).first()
    if request.content_type == 'application/json':
        if article is None:
            return {}
        return json.dumps(dict(title=article.title, text=article.text,
                               author=article.author, time=article.time))
    else:
        if article is None:
            return 'NA'

        return '{0}\n{1}\nBy {2} on {3}\n'.format(article.title, article.text, article.author, article.time)


def check_if_all_facilities_true(facilityids, token):
    """
    This method calls the method auth() for each facility id.
    If the User is not a admin at a facility it returns a list containing the facility id.
    :param facilityids: facility id's which auth() should verify
    :param token: Bearer Authentication Token of the User
    :return: list containing the facility id's, where the user is no admin
    """
    facility_list = []
    for facilityid in facilityids:
        if auth(facilityid, token) != '1':
            facility_list.append(facilityid)
    return facility_list
