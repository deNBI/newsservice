import os
from newsservice.db import db_session, init_db
from flask_bootstrap import Bootstrap

from flask import Flask

DEFAULT_CONFIG = '../config/config.py'


def register_blueprints(app):
    from newsservice import index
    app.register_blueprint(index.bp)

    from newsservice import savenews
    app.register_blueprint(savenews.bp)

    from newsservice import requestnews
    app.register_blueprint(requestnews.bp)

    from newsservice import latestnews
    app.register_blueprint(latestnews.bp)


def config_flask(app, config_path):
    if config_path is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile(DEFAULT_CONFIG, silent=True)
    else:
        app.config.from_pyfile(DEFAULT_CONFIG, silent=True)
        app.config.from_pyfile(config_path)

    secret_key = os.environ.get('SECRET_KEY', 'dev')
    app.config['SECRET_KEY'] = secret_key

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


def create_app(config_path=None):
    """
    This Method initializes the Flask Application and uses the default config file.
    It imports the other Python Methods with Blueprints.
    it was implemented with the help of the official flask tutorial: https://flask.palletsprojects.com/en/1.1.x/tutorial/
    :param config:
    :return: Returns the Flask Application
    """

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    Bootstrap(app)

    init_db()

    config_flask(app, config_path)

    register_blueprints(app)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app
