from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from .model import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        flash('Wrong email or password.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signupPost():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user_by_email = User.query.filter_by(email=email).first()
    user_by_name = User.query.filter_by(name=name).first()
    if user_by_email or user_by_name:
        flash('Name or email already exists.')
        return redirect(url_for('auth.signup'))

    newUser = User(email=email, name=name)
    newUser.set_password(password)

    db.session.add(newUser)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))