# A revisit of the blog post project with added features of an SQL database,
# RESTful functionality: now able to edit and delete a blogpost in addition to
# creating and viewing a post.
import datetime
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField


# Standard Flask app and DB setup w/ addition of CKEditor that will allow us to have an
# edit box with full tools w/buttons that you expect in a word editor.
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ckeditor = CKEditor(app)
Bootstrap(app)
db = SQLAlchemy(app)


# Standard DB/Table creation
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# WTForm creation w/addition of CKEditorField just for editing the body
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])

    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

# Need to create db for first time run
# with app.app_context():
#     db.create_all()


# Standard home route that will show all our posts
@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


# Route to create a new post which will get added into the db. Utilizes WTForm and datetime
# for a formatted date
@app.route('/new-post', methods=["GET", "POST"])
def create_new_post():
    new_form = CreatePostForm()
    if new_form.validate_on_submit():
        # "Full month name" "day number", "full year"
        # i.e. August 14, 2024
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        new_blog_post = BlogPost(
            title=new_form.title.data,
            subtitle=new_form.subtitle.data,
            author=new_form.author.data,
            img_url=new_form.img_url.data,
            date=current_date,
            body=new_form.body.data
        )
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=new_form)


# Route to show a specific post when clicked from home page
@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    return render_template("post.html", post=requested_post)


# Route to edit a specific post when clicked from its show_post page.
# Reuses WTForm from creating a new post w/ fields already filled.
@app.route('/edit-post/<post_id>', methods=["GET", "POST"])
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# Delete route that will remove a specific post from the db
@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)
