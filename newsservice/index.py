from flask import render_template
from newsservice.models import News
from flask import (Blueprint)

import requests

bp = Blueprint('index', __name__)


def check_cc_sites_status():
    """
    checks if all compute center sites in config are accessible
    :return: an json array
    """
    try:
        from config import config
        cc_sites = config.CC_SITES
    except:
        return []
    sites = {}
    for location, url in cc_sites.items():
        get_status(location, url, sites)
    return sites


def get_status(location, cc_url, sites):
    try:
        response = requests.head(cc_url, timeout=5)
        #status_code = response.status_code
        #reason = response.reason
        sites.update({location: {
            'url': cc_url,
            'status': 0
        }})
    except requests.exceptions.ConnectionError:
        #status_code = '000'
        #reason = 'ConnectionError'
        sites.update({location: {
            'url': cc_url,
            'status': 1
        }})


@bp.route('/')
def render():
    """
    This method renders the HTML webside including the isOnline Status and the last 30 database entries.
    :return:
    """

    sites = check_cc_sites_status()
    return render_template("index.html", news=News.query.order_by(News.id.desc()).limit(30), cc_sites=sites)
