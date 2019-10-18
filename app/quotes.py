from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import SubmitForm
from app.models import User, Quote, Speaker

@app.route('/submit/', methods=['GET', 'POST'])
@login_required
def submit():
    form = SubmitForm()
    if form.validate_on_submit():
        speaker = Speaker.query.filter_by(name=form.speaker.data).first()
        if speaker is None:
            speaker = Speaker(name=form.speaker.data)
            db.session.add(speaker)
            db.session.commit()
            flash('New speaker ' + speaker.name + ' added.')
        quote = Quote(user_id=current_user.id, speaker_id=speaker.id,
                body=form.body.data, topic=form.topic.data)
        if current_user.role > 1:
            quote.published = True
        db.session.add(quote)
        db.session.commit()
        flash('Thanks for your quote on '+quote.topic+'!')
        quote.upvote(current_user.id)
        return redirect(url_for('index'))
    return render_template('forms/submit.html', form=form)

@app.route('/upvote/<id>/')
@login_required
def upvote(id):
    returnto = request.args.get('returnto', 1, )
    id = int(id)
    quote = Quote.query.filter_by(id=id).first()
    user = current_user
    quote.upvote(user.id)
    if not request.referrer:
        return redirect(url_for('quote_page', id=str(id)))
    else:
        return redirect(request.referrer)

@app.route('/downvote/<id>/')
@login_required
def downvote(id):
    returnto = request.args.get('returnto', 1, )
    id = int(id)
    quote = Quote.query.filter_by(id=id).first()
    user = current_user
    quote.downvote(user.id)
    if not request.referrer:
        return redirect(url_for('quote_page', id=str(id)))
    else:
        return redirect(request.referrer)
