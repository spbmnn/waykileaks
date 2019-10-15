''' Account.py

'''

from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, SignupForm#, SubmitForm
from app.models import User, Quote, Speaker

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user.get_existence():
            flash('Sorry, your account has been banned for some reason or another.\n \
            For more info, please send us an email.')
            return redirect(url_for('index'))
        if user is None or not user.check_password(form.password.data):
            flash('invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember.data)
        return redirect(url_for('index'))
    return render_template('forms/login.html', title='Log In', form=form)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    if form.validate_on_submit():
        newuser = User(username=form.username.data, email=form.email.data)
        newuser.set_password(form.password.data)
        db.session.add(newuser)
        db.session.commit()
        flash('Welcome to WaykiLeaks!')
        return redirect(url_for('login'))
    return render_template('forms/signup.html', title='Sign Up', form=form)

