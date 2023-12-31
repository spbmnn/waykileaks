'''
Profile
-------
Handles individual/communal user, speaker, and quote pages.
'''
# TODO: Give /profiles/ a base.html
# TODO: Consolidate /profiles/user.html, speaker.html, & quote.html
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import app, db
from app.models import User, Quote, Speaker
from sqlalchemy import desc

@app.route('/users/')
@login_required
def user_directory():
    users = User.query.order_by(User.id)
    return render_template('profiles/udir.html', users=users, title="Users")

@app.route('/user/<username>/')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    submitcount = str(len(user.submissions))
    return render_template('profiles/user.html', user=user, showstats=True,
        showquotes=True, title=user.username)

@app.route('/quotes/')
def quote_list():
    quoteresult = Quote.query.filter_by(published=True)
    quotes = []
    for quote in quoteresult: quotes.append(quote)
    sort = request.args.get('sort', 'hot', type=str)
    if sort == 'top':
        quotes.sort(key=lambda x: x.score, reverse=True)
    elif sort == 'new':
        quotes.sort(key=lambda x: x.id, reverse=True)
    else:
        quotes.sort(key=lambda x: x.get_hotness(), reverse=True)
    #quotect = len(quotes)
    return render_template('profiles/qdir.html', quotes=quotes,
        title='Quotes', sort=sort)

@app.route('/quote/<id>/')
def quote_page(id):
    quote = Quote.query.filter_by(id=int(id)).first_or_404()
    return render_template('profiles/quote.html', quote=quote,
        title='On {}'.format(quote.topic))

@app.route('/speaker/<id>/')
def speaker_summary(id):
    id=int(id)
    speaker = Speaker.query.filter_by(id=id).first_or_404()
    quotes = []
    if not current_user.is_anonymous and current_user.role > 2:
        quotes = speaker.quotes
    else:
        for quote in speaker.quotes:
            if quote.published:
                quotes.append(quote)
    return render_template('profiles/speaker.html', speaker=speaker, quotes=quotes,
        title=speaker.name)

@app.route('/myquotes/')
@login_required
def my_quotes():
    quotes = Quote.query.filter_by(submitter=current_user).order_by(desc(Quote.id))
    return render_template('profiles/qdir.html', title="My Quotes", quotes=quotes, showstatus=True)
