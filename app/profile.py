'''
Profile
-------
Handles individual/communal user, speaker, and quote pages.
'''
# TODO: Give /profiles/ a base.html
# TODO: Consolidate /profiles/user.html, speaker.html, & quote.html
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app import app, db
from app.models import User, Quote, Speaker
from sqlalchemy import desc

@app.route('/users/')
@login_required
def user_directory():
    users = User.query.order_by(User.id)
    return render_template('profiles/udir.html', users=users)

@app.route('/user/<username>/')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    submitcount = str(len(user.submissions))
    return render_template('profiles/user.html', user=user, showstats=True,
        showquotes=True)

@app.route('/quotes/')
def quote_list():
    quotes = Quote.query.filter_by(published=True).order_by(desc(Quote.score))
    #quotect = len(quotes)
    return render_template('profiles/qdir.html', quotes=quotes)#, quotect=quotect)

@app.route('/quote/<id>/')
def quote_page(id):
    quote = Quote.query.filter_by(id=int(id)).first_or_404()
    return render_template('profiles/quote.html', quote=quote)

@app.route('/speaker/<id>/')
def speaker_summary(id):
    id=int(id)
    speaker = Speaker.query.filter_by(id=id).first_or_404()
    return render_template('profiles/speaker.html', speaker=speaker)
