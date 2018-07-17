"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/register", methods=["GET"])
def register_form():
    """display register form"""

    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_process():
    """process registration and sends you home."""

    email = request.form.get('email')
    password = request.form.get('password')

    verify_email = User.query.filter(User.email == email).one()

    if not verify_email:
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect("/")
    else:
        flash('A user with that email already exists!')
        return redirect("/register")


@app.route("/login", methods=["GET"])
def show_login():
    """Shows user login form"""

    return render_template("login.html")


@app.route("/login", methods=["POST"])
def verify_login():
    """Verifies user email is in database and password matches"""

    email = request.form.get('email')
    password = request.form.get('password')

    verify_email = User.query.filter(User.email == email).all()

    if verify_email and (verify_email[0].password == password):
        session['email'] = email
        flash('You are logged in, prepare to be judged.')
        return redirect("/")

    else:
        flash('That login is invalid')
        return redirect("/login")
    
    


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar

    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
