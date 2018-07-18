"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.orm.exc import NoResultFound

from model import User, Rating, Movie, connect_to_db, db
from pprint import pprint


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


@app.route("/user_info", methods=["GET"])
def show_user():
    """shows individual user info"""

    user_id = request.args.get('user_id')

    user = User.query.filter(User.user_id == user_id).one()
    age = user.age
    zipcode = user.zipcode

    user_ratings = Rating.query.filter(Rating.user_id == user.user_id).all()
    # movie_score = []
    # for rating in user_ratings:
    #     movie_score.append((rating.movie.title, rating.score))

    return render_template("user_info.html",
                           user_id=user_id,
                           age=age,
                           zipcode=zipcode,
                           user_ratings=user_ratings
                           )

# @app.route("/user/<user_id>")
# def show_user(user_id):

@app.route("/movies")
def movie_list():
    """Show list of movies in alphabetical order."""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template("movie_list.html", movies=movies)


@app.route("/movies/<movie_id>")
def show_movie(movie_id):

    movie = Movie.query.filter(Movie.movie_id == movie_id).one()
    ratings = Rating.query.filter(Rating.movie_id == movie_id).all()

    if session['email']:
        user = User.query.filter(User.email == session['email']).one()

    return render_template("movie_details.html",
                           movie=movie,
                           ratings=ratings,
                           user=user)


@app.route("/movies/<movie_id>", methods=["POST"])
def rate_movie(movie_id):
    """Get user info from form and add rating to database"""

    score = request.form.get("score")
    user = User.query.filter(User.email == session['email']).one()

    rating = Rating(score=score, movie_id=movie_id, user_id=user.user_id)
    db.session.add(rating)
    db.session.commit()

    flash('You have judged this movie.')
    return redirect("/user_info?user_id=" + str(user.user_id))


@app.route("/register", methods=["GET"])
def register_form():
    """display register form"""

    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_process():
    """process registration and sends you home."""

    email = request.form.get('email')
    password = request.form.get('password')

    try:

        verify_email = User.query.filter(User.email == email).one()

    # if not verify_email:
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect("/")
    # else:
    except NoResultFound:
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
        return redirect("/user_info?user_id=" + str(verify_email[0].user_id))

    else:
        flash('That login is invalid')
        return redirect("/login")
    
@app.route("/logout")
def logout():
    """logs the current user out"""

    del session['email']

    flash("you are no longer being judged... on this website.")
    return redirect("/")

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
