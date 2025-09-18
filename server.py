from flask import Flask, url_for, redirect, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float
from form import LoginForm, RegisterForm, MovieForm, SearchMovie
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from api import MovieApi

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    movies = relationship("Movies", back_populates="user")

class Movies(db.Model):
    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user.id"))
    title: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    year: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String, nullable=True)
    img_url: Mapped[str] = mapped_column(String, nullable=True)
    user = relationship("User", back_populates="movies")

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = request.form.get("email")
        password = request.form.get("password")

        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if not user:
            flash("Email not found. Please register first")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("Incorrect password. Please try again")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html", form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        new_email = request.form.get("email")
        new_password= request.form.get("password")
        new_name = request.form.get("name")

        result = db.session.execute(db.select(User).where(User.email == new_email))
        user = result.scalar()

        if user:
            flash("You already have an account. Please Login")
            return redirect(url_for("login"))
        
        new_user = User(
            email=new_email,
            password=generate_password_hash(new_password, method="pbkdf2:sha256", salt_length=8),
            name=new_name
        )

        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("home"))

@app.route("/search_movies", methods=["GET", "POST"])
def search_movies():
    form = SearchMovie()
    title = request.form.get("search")

    if form.validate_on_submit():
        movie = MovieApi(title)
        movies = movie.data
        return render_template("search.html", form=form, movies=movies)
    return render_template("search.html", form=form)

@app.route("/add")
def add_movies():
    title = request.args.get("title")
    movie = MovieApi(title)
    data = movie.data

    new_movie = Movies(
        user_id=current_user.id,
        title=data[0]["title"],
        year=data[0]["release_date"][:4],
        description=data[0]["overview"],
        rating=None,
        ranking=None,
        review=None,
        img_url=f"https://image.tmdb.org/t/p/w500{data[0]["backdrop_path"]}"
    )
    db.session.add(new_movie)
    db.session.commit()
    msg= "Movie just added to your list"
    return redirect(url_for("edit", id=new_movie.id, msg=msg))

@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = MovieForm()
    id = request.args.get("id")
    message = request.args.get("msg")
    movie = db.get_or_404(Movies, id)

    if request.method == "POST":
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        movie.ranking = int(form.ranking.data)
        db.session.commit()
        return redirect(url_for("my_list"))
    
    if request.method == "GET":
        flash(message)
        form.rating.data = movie.rating
        form.review.data = movie.review
        form.ranking.data = movie.ranking

    return render_template("edit.html", form=form, movie=movie)

@app.route("/my_list")
def my_list():
    movies = current_user.movies
    return render_template("mylist.html", movies=movies)

@app.route('/delete')
def delete():
    id = request.args.get("id")
    moive = db.get_or_404(Movies, id)
    db.session.delete(moive)
    db.session.commit()
    flash("Movie in the list just been deleted")
    return redirect(url_for("my_list"))

if __name__ == "__main__":
    app.run(debug=True)