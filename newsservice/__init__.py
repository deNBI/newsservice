import os

from werkzeug.middleware.dispatcher import DispatcherMiddleware

from newsservice.db import db_session, init_db
from flask_bootstrap import Bootstrap

from flask import Flask

DEFAULT_CONFIG = '../config/config.py'


def create_app(config_path=None):
    """
    This Method initializes the Flask Application and uses the default config file.
    It imports the other Python Methods with Blueprints.
    it was implemented with the help of the official flask tutorial: https://flask.palletsprojects.com/en/1.1.x/tutorial/
    :param config_path: Path to config. Will overwrite default config.
    :return: Returns the Flask Application
    """

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    Bootstrap(app)

    init_db()

    config_flask(app, config_path)

    register_blueprints(app)

    # if app.config['CC_SITES']:
    #    register_cc_sites(app)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app


def config_flask(app, config_path):
    if config_path is None:
        # load only the default config
        app.config.from_pyfile(DEFAULT_CONFIG, silent=True)
    else:
        # load default config and overwrite with config from path
        app.config.from_pyfile(DEFAULT_CONFIG, silent=True)
        app.config.from_pyfile(config_path)

    # dispatcher needed so that all urls are accessed under APPLICATION_ROOT when inside wsgi container (e.g. gunicorn)
    # dummy_app could handle 404 errors if implemented
    app.wsgi_app = DispatcherMiddleware(Flask('dummy_app'), {app.config['APPLICATION_ROOT']: app.wsgi_app})

    secret_key = os.environ.get('SECRET_KEY', 'dev')
    app.config['SECRET_KEY'] = secret_key

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


def register_blueprints(app):
    from newsservice import index
    app.register_blueprint(index.bp)

    from newsservice import request_manager
    app.register_blueprint(request_manager.bp)


def register_cc_sites(app):
    from config import config
    config.CC_SITES = app.config['CC_SITES']
