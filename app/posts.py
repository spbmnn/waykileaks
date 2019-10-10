from flask import render_template, flash, redirect, url_for
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
        db.session.add(quote)
        db.session.commit()
        flash('Thanks for your quote on '+quote.topic+'!')
        return redirect(url_for('index'))
    return render_template('forms/submit.html', form=form)

