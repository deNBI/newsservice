from newsservice.db import db_session
from newsservice.models import News
from newsservice.auth import auth

from flask import (Blueprint, request, json)
from newsservice.db import init_db

bp = Blueprint('save', __name__)

TITLE = "title"
AUTHOR = "author"
TEXT = "text"
TAG = "tag"
FIDS = "facility-ids"
TOKEN = "perun-login-token"


@bp.route('/savenews', methods=['GET', 'POST'])
def save():
    """
    This Method receives a News and a Authentication Token via JSON document. If the check with auth() was successful it
    adds the news to the database. If not it tells the user that the news wasn't added.
    :return: a status whether the News was added or not.
    """
    init_db()

    try:
        article_json = json.loads(request.data.decode('utf-8'))['news']
    except:
        article_json = request.json['news']
    facility_ids = facility_id_string_to_list(article_json[FIDS])

    if article_json[TITLE].strip() and article_json[AUTHOR].strip() \
            and article_json[TEXT].strip() and article_json[TAG].strip() \
            and article_json[FIDS].strip() and article_json[TOKEN].strip():
        article = News(article_json[TITLE], article_json[AUTHOR], article_json[TEXT],
                       article_json[TAG], article_json[FIDS])
    else:
        return "No empty fields are allowed in the JSON document."

    facility_id_no_list = check_if_all_facilities_true(facility_ids, article_json[TOKEN])
    if not facility_id_no_list:
        db_session.add(article)
        db_session.commit()
        return "The article: '{0}' was added.".format(article_json[TITLE])
    else:
        return 'The news was not posted, as you dont have the permission to post to these facilities: ' + ','.join(facility_id_no_list)


def facility_id_string_to_list(facility_id_string):
    """
    This method receives a string with the facility id's and converts it to a list with 1 facility id at each index.
    :param facility_id_string: string with all the facility id's
    :return: a list containing the facility id's as strings.
    """
    facility_id_list = facility_id_string.split(",")
    return facility_id_list


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
