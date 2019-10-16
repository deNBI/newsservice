from flask import render_template
import http.client
from newsservice.models import News
from flask import (Blueprint)

bp = Blueprint('index', __name__)


def isonline():
    """
    checks if "openstack.cebitec.uni-bielefeld.de" is accessible
    :return: a string which says either "online" or "offline"
    """
    try:
        conn = http.client.HTTPConnection("openstack.cebitec.uni-bielefeld.de")
        conn.request("HEAD", "/")
        r1 = conn.getresponse()
        if int(r1.status) == 302:
            return "online"
        else:
            return "offline"
    except IOError:
        return "offline"


@bp.route('/')
def render():
    """
    This method renders the HTML webside including the isOnline Status and the last 30 database entries.
    :return:
    """

    online = isonline()
    return render_template("index.html", news=News.query.order_by(News.id.desc()).limit(30), online=online)
