from flask import Flask

from front_end.front import front_blueprint
from back_end.back import back_blueprint

all_blueprints = list()

all_blueprints.append(front_blueprint)
all_blueprints.append(back_blueprint)


def bind_blueprints(flask_app):
    assert isinstance(flask_app, Flask)

    for blueprint in all_blueprints:
        flask_app.register_blueprint(blueprint)

    return flask_app
