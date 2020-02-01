from newsservice.db import db_session
from newsservice.models import News
from newsservice.auth import auth

from flask import (Blueprint, request, json, jsonify, current_app)
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
        current_app.logger.exception(e)

    if article_json is None:
        try:
            article_json = request.json['news']
        except Exception as e:
            current_app.logger.exception(e)
            return "Something went wrong in reading the request. Returning."

    title = article_json[News.TITLE]
    author = article_json[News.AUTHOR]
    text = article_json[News.TEXT]
    tag = article_json[News.TAG]
    fids = article_json[News.FACILITY_ID]
    motd = article_json[News.MOTD]
    token = article_json[News.TOKEN]
    if title is None or not title.strip():
        return "No Title found in JSON"
    if author is None or not author.strip():
        return "No Author found in JSON"
    if text is None or not text.strip():
        return "No Text found in JSON"
    if tag is None or not tag:
        return "No tags found in JSON"
    if fids is None or not fids:
        return "No facility IDS found in JSON"
    if token is None or not token.strip():
        return "No perun login token found in JSON"

    try:
        article = News(title, author, text, tag, fids, motd)
    except Exception as e:
        current_app.logger.exception(e)
        return "Exception when creating News."

    facility_id_no_list = check_if_all_facilities_true(fids, token)
    if not facility_id_no_list:
        db_session.add(article)
        db_session.commit()
        return "The article: '{0}' was added.".format(title)
    else:
        return 'Not posted. Authentication failed for: {0}'.format(','.join(facility_id_no_list))


@bp.route('/', methods=['DELETE'])
def delete():
    news_id = None
    token = None
    try:
        news_id = json.loads(request.data.decode('utf-8'))[News.ID]
        token = json.loads(request.data.decode('utf-8'))[News.TOKEN]
    except Exception as e:
        current_app.logger.exception(e)

    if news_id is None or token is None:
        try:
            news_id = request.json[News.ID]
            token = request.json[News.TOKEN]
            if news_id is None or token is None:
                return 'No news id or token found in request.'
        except Exception as e:
            current_app.logger.exception(e)
            return "Something went wrong in reading the request. Returning."

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
    motd = None
    tag = None
    fids = None
    token = None
    try:
        news_id = json.loads(request.data.decode('utf-8'))[News.ID]
        title = json.loads(request.data.decode('utf-8'))[News.TITLE]
        text = json.loads(request.data.decode('utf-8'))[News.TEXT]
        motd = json.loads(request.data.decode('utf-8'))[News.MOTD]
        tag = json.loads(request.data.decode('utf-8'))[News.TAG]
        fids = json.loads(request.data.decode('utf-8'))[News.FACILITY_ID]
        token = json.loads(request.data.decode('utf-8'))[News.TOKEN]
    except Exception as e:
        current_app.logger.exception(e)

    if news_id is None or token is None or title is None or text is None or tag is None or fids is None:
        try:
            news_id = request.json[News.ID]
            title = request.json[News.TITLE]
            text = request.json[News.TEXT]
            motd = request.json[News.MOTD]
            tag = request.json[News.TAG]
            fids = request.json[News.FACILITY_ID]
            token = request.json[News.TOKEN]
            if news_id is None or token is None or title is None \
                    or text is None or tag is None or fids is None:
                return 'No news id or token or title or text or tag or facility id found in request.'
        except Exception as e:
            current_app.logger.exception(e)
            return "Something went wrong in reading the request. Returning without patching."

    article = News.query.filter(News.id == news_id).first()
    if article is None:
        return 'No article found with id {0}.'.format(news_id)
    news_facility_ids = check_if_all_facilities_true([facility.facility_id for facility in article.facilityid], token)
    if not news_facility_ids or len(news_facility_ids) == 0:
        if motd is None or not motd.strip():
            motd = None
        article.update(title, text, motd, tag, fids)
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
    return format_latest_article(article, request.content_type)


@bp.route('/<tags>/latest/motd')
def request_latest_news_by_tag_as_motd(tags):
    article = News.query \
        .filter(*News.get_tag_queries(tags)) \
        .order_by(News.id.desc()) \
        .first()
    return format_latest_article_as_motd(article, request.content_type)


@bp.route('/latest', methods=['GET'])
def request_latest_news():
    """
    This Method queries the last item of the database and convert it to a string.
    :return: A String with the last item of the database
    """
    article = News.query.order_by(News.id.desc()).first()
    return format_latest_article(article, request.content_type)


@bp.route('/latest/motd', methods=['GET'])
def request_latest_news_as_motd():
    """
    This Method queries the last item of the database and convert it to a string.
    :return: A String with the last item of the database
    """
    article = News.query.order_by(News.id.desc()).first()
    return format_latest_article_as_motd(article, request.content_type)


@bp.route('/<id>/formatted')
def request_formatted_news_by_id(id):
    article = News.query.filter(News.id == id).first()
    return format_latest_article(article, request.content_type)


@bp.route('/<id>/formatted/motd')
def request_formatted_news_by_id_as_motd(id):
    article = News.query.filter(News.id == id).first()
    return format_latest_article_as_motd(article, request.content_type)


def format_latest_article(article, content_type):
    if content_type == 'application/json':
        if article is None:
            return {}
        else:
            return json.dumps(dict(title=article.title, text=article.text,
                                   author=article.author, time=article.time.strftime('%Y-%m-%d %H:%M:%S')))
    else:
        if article is None:
            return ''
        else:
            return '{0}\n{1}\nBy {2} on {3}\n' \
                .format(article.title, article.text, article.author, article.time.strftime('%Y-%m-%d %H:%M:%S'))


def format_latest_article_as_motd(article, content_type):
    if content_type == 'application/json':
        if article is None:
            return {}
        news_link = 'https://cloud.denbi.de/news/id/{0}'.format(article.id)
        if article.motd is not None and article.motd.strip():
            return json.dumps(dict(title=article.title, text=article.motd,
                                   author=article.author, time=article.time.strftime('%Y-%m-%d %H:%M:%S'),
                                   news_link=news_link))
        else:
            return json.dumps(dict(title=article.title, text=article.text,
                                   author=article.author, time=article.time.strftime('%Y-%m-%d %H:%M:%S'),
                                   news_link=news_link))
    else:
        if article is None:
            return 'Article not found!'
        news_link = 'https://cloud.denbi.de/news/id/{0}'.format(article.id)
        if article.motd is not None and article.motd.strip():
            return '{0}\nSee the full news: {1}\n{2}\n' \
                .format(article.motd, news_link, article.time.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            return '{0}\nSee the full news: {1}\n{2}\n' \
                .format(article.text, news_link, article.time.strftime('%Y-%m-%d %H:%M:%S'))


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
