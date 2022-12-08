import click
from flasgger import Swagger
from flask import Flask
from flask_migrate import Migrate

from common.app_common import db, jwt, ma
from core import settings as default_config

__all__ = ('create_app',)


def create_app(config=None) -> Flask:
    """Create a Flask app."""
    app = Flask(__name__, instance_relative_config=True)

    migrate = Migrate(app, db)
    config = config or default_config
    configure_blueprints(app)
    configure_db(app, config=config.PostgresSettings())
    configure_jwt(app, config=config.JWTSettings())
    configure_ma(app)
    configure_swagger(app)
    configure_cli(app)

    return app


def configure_db(app, config) -> None:
    app.config.from_object(config)
    db.init_app(app)
    app.app_context().push()
    db.create_all()


def configure_jwt(app, config) -> None:
    app.config.from_object(config)
    jwt.init_app(app)


def configure_ma(app) -> None:
    ma.init_app(app)


def configure_swagger(app) -> None:
    Swagger(app, config=default_config.SWAGGER_CONFIG,
            template_file='definitions.yml')


def configure_blueprints(app) -> None:
    from api.v1.auth import blueprint as auth_blueprint
    from api.v1.roles import blueprint as role_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(role_blueprint)


def configure_cli(app):
    @app.cli.command('recreate-database')
    def initdb():
        db.drop_all()
        db.create_all()

    @app.cli.command('create-superuser')
    @click.argument('name')
    @click.argument('password')
    def create_superuser(name, password):
        from db.db_models import Roles, User, UserRole
        user = User(name=name, password=password, is_superuser=True)
        db.session.add(user)

        admin_role = Roles.query.filter_by(code='admin').first()
        if admin_role:
            user_role = UserRole(user_id=user.id, role_id=admin_role.id)
            db.session.add(user_role)
        db.session.commit()


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
