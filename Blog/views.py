from flask import render_template, redirect, url_for, flash, abort, Blueprint
from flask_login import current_user
from functools import wraps
from datetime import date
from . import db
from .forms import CommentForm, CreatePostForm, ContactForm
from .models import User, BlogPost, Comment
import smtplib

views = Blueprint("views", __name__)


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function


@views.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    users = User.query.all()
    return render_template("index.html", all_posts=posts, all_users=users)


@views.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment!")
            return redirect(url_for("auth.login"))
        new_comment = Comment(
            text=form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
    return render_template("post.html", post=requested_post, form=form, current_user=current_user)


@views.route("/about")
def about():
    return render_template("about.html")


@views.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login("georgepavlej@gmail.com", "Avensis13570530!")
            connection.sendmail(
                from_addr="georgepavlej@gmail.com",
                to_addrs="georgepavlej@gmail.com",
                msg=f"Subject:Question\n\n"
                    f"Name: {form.name.data}\n\n"
                    f"Phone number: {form.phone_number.data}\n\n"
                    f"Message: {form.message.data}"
            )
        return render_template("contact.html", form=form, msg_sent=True)
    return render_template("contact.html", form=form, msg_sent=False)


@views.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("views.get_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user)


@views.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=current_user,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("views.show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


@views.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('views.get_all_posts'))
