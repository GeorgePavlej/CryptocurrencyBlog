from flask import render_template, redirect, url_for, flash, Blueprint
from flask_login import login_user, current_user, logout_user
from werkzeug.security import check_password_hash
from . import db
from .forms import RegisterForm, LoginForm
from .models import User

auth = Blueprint("auth", __name__)


@auth.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('auth.login'))
        elif not check_password_hash(user.password, form.password.data):
            flash('Password incorrect, please try again.')
            return redirect(url_for('auth.login'))
        else:
            login_user(user)
            return redirect(url_for('views.get_all_posts'))
    return render_template("login.html", form=form, current_user=current_user)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('views.get_all_posts'))


@auth.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user is None:
            new_user = User(
                email=form.email.data,
                name=form.name.data
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("get_all_posts"))
            # User already exists
        flash("You've already signed up with that email, log in instead!")
        return redirect(url_for("login"))
    return render_template("register.html", form=form, loggen_in=current_user.is_authenticated)
