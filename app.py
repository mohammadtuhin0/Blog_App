from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

# ---------------- APP CONFIG ----------------

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

db = SQLAlchemy(app)

# ---------------- MODELS ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    image = db.Column(db.String(200))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    image = db.Column(db.String(200))
    comments = db.relationship("Comment", backref="post", lazy=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))

# ---------------- CREATE TABLES ----------------

with app.app_context():
    db.create_all()

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    posts = Post.query.all()
    return render_template("home.html", posts=posts)


@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("signup.html")


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            session["user"] = user.username
            return redirect("/")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


@app.route("/add", methods=["GET","POST"])
def add():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        image_file = request.files["image"]
        filename = secure_filename(image_file.filename)
        image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        post = Post(title=title, content=content, image=filename)
        db.session.add(post)
        db.session.commit()
        return redirect("/")

    return render_template("add.html")


@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):
    text = request.form["text"]
    new_comment = Comment(text=text, post_id=post_id)
    db.session.add(new_comment)
    db.session.commit()
    return redirect("/")


@app.route("/profile/<int:user_id>")
def profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("profile.html", user=user)


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)
