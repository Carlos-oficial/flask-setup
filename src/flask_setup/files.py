DOCKERFILE = r"""
# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /{{$APP_NAME}}

# COPY requirements.txt requirements.txt
# RUN pip3 install -r requirements.txt

RUN pip install flask

COPY . .

CMD [ "python3", "-m" , "flask", "run"]
"""

BASE_HTML = r"""
<!doctype html>
<html lang="en">

<head>
    <title>{% block title %}{% endblock %} {{$APP_NAME}} </title>
    <link rel="stylesheet" href="/static/dist/main.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
    <script defer src="https://unpkg.com/alpinejs@3.10.3/dist/cdn.min.js"></script>

    {% block head %}
    {% endblock %}
</head>


<section class="content">
    {% for message in get_flashed_messages() %}
    <div class="flash text-red-600">{{ message }}</div>
    {% endfor %}
    {% block content %}{% endblock %}
</section>

</html> 
"""

BASE_FORM_HTML = r"""
{% extends 'base.html' %}

{% block content %}
<div>
    <div>
        {%block title%}{% endblock %}</div>
    <form method="post">
        {% block form %}
        {% endblock %}
        <button type="submit">{% block button %} {% endblock %}</button>
    </form>
</div>
{% endblock %}
"""

LOGIN_HTML = r'''
{% extends 'auth/base_form.html' %}
{% block title %}Log In{% endblock %}

{% block form %}
<label for="username">Username</label>
<input name="username" id="username" required>
<label for="password">Password</label>
<input type="password" name="password" id="password" required>
<span class="font-thin block">don't have an account? <a href="../auth/register" class="x"> register here </a> </span>
{% endblock %}

{% block button%}Login{% endblock %}
''' 

REGISTER_HTML = r'''
{% extends 'auth/base_form.html' %}
{% block title %}Register{% endblock %}

{% block form %}
<label for="username">Username</label>
<input name="username" id="username" required>
<label for="password">Password</label>
<input type="password" name="password" id="password" required>
<input type="submit" value="Register">
{% endblock %}'''

def init_py(auth=False):
    auth_str = ""
    if auth:
        auth_str = """
    import auth
    app.register_blueprint(auth.bp)"""

    return f"""
import os

from flask import Flask, render_template


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "APP.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello

    import db.db as db

    with app.app_context():
        db.init_db()
    db.init_app(app)

{auth_str}

    import api

    app.register_blueprint(api.api)

    import routes

    with app.app_context():
        routes.init_routes(app)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)

"""


ROUTES_PY = r"""
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)


def init_routes(app):
    @app.route("/")
    def index():
        return "Hello World!" """

DB_PY = r'''
import sqlite3

import click
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("db/schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app, teardown=False):
    if teardown:
        app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


'''

API_PY = """
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/example", methods=["GET"])
def example(): return {"payload":"here's an example"}"""

AUTH_PY = r"""
import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from db.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
"""

AUTH_TABLE = """
CREATE TABLE IF NOT EXISTS user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);"""
