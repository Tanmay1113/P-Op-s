
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for
from flask.cli import with_appcontext
import click

from config import Config
from .extensions import db, migrate, login_manager, csrf, limiter


def create_app(test_config=None):
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)
    else:
        Config.validate()
        app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    from .auth import bp as auth_bp
    from .dashboard import bp as dashboard_bp
    from .admin import bp as admin_bp
    from .projects import bp as projects_bp
    from .tasks import bp as tasks_bp
    from .operations import bp as operations_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(operations_bp)

    @app.cli.command("seed-admin")
    @with_appcontext
    def seed_admin():
        from .models import User

        email = "admin@company.com"
        username = "admin"
        password = "admin@company"

        existing = User.query.filter(
            db.or_(
                User.email == email,
                User.username == username,
            )
        ).first()

        if existing:
            if existing.email == email and existing.role == "Admin":
                click.echo("Admin account already exists. No changes made.")
            else:
                click.echo(
                    "An account already uses the target email or username. "
                    "No changes made; inspect the conflict before proceeding."
                )
            return

        admin = User(
            username=username,
            email=email,
            role="Admin",
            is_active_account=True,
        )
        admin.set_password(password)

        try:
            db.session.add(admin)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        click.echo("Default admin account created successfully.")
        click.echo(f"Email: {email}")
        click.echo(f"Username: {username}")
        click.echo("Password: admin@company")

    @app.get("/")
    def home():
        from flask_login import current_user

        if current_user.is_authenticated:
            return redirect(url_for("dashboard.index"))

        return render_template("index.html")

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app
