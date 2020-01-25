from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app import app, db, email
from app.forms import DenyQuoteForm
from app.models import User, Speaker, Quote
from datetime import datetime

@app.route('/admin/')
@login_required
def admin_home():
    if current_user.role < 3:
        return render_template('forbidden.html'), 403
    users = User.query.order_by(User.id)
    quotes = Quote.query.order_by(Quote.id)
    speakers = Speaker.query.order_by(Speaker.id)
    return render_template('admin/dash.html', users=users, quotes=quotes,
        speakers=speakers, title='Admin Home')

###                                 ###
# User Promotion/Demotion/Destruction #
###                                 ###

@app.route('/promote/<username>/')
@login_required
def promote(username):
    if current_user.role < 3:
        return render_template('forbidden.html'), 403
    user = User.query.filter_by(username=username).first_or_404()
    if user.username == current_user.username:
        flash('you cannot promote yourself!!!!')
        return redirect(url_for('index'))
    elif user.role < 3:
        user.role += 1
    else:
        flash('cannot promote past vassal level')
        return redirect(url_for('index'))
    db.session.add(user)
    db.session.commit()
    flash('promoted ' + username + ' to level ' + str(user.role))
    return redirect(url_for('index'))

@app.route('/demote/<username>/')
@login_required
def demote(username):
    if current_user.role < 3:
        return render_template('forbidden.html'), 403
    user = User.query.filter_by(username=username).first_or_404()
    if user.role == 1:
        flash('cannot demote below serf level. yes, even freshmen.')
        return redirect(url_for('index'))
    elif user.role == 4:
        flash('YOU SHALL NOT DEMOTE ME FEEBLE BEING')
        return redirect(url_for('index'))
    elif user.username == current_user.username:
        flash('you should not demote yourself!!!!')
        return redirect(url_for('index'))
    user.role -= 1
    db.session.add(user)
    db.session.commit()
    flash('demoted ' + username + ' to level ' + str(user.role))
    return redirect(url_for('index'))

@app.route('/ban/<username>/')
@login_required
def ban(username):
    if current_user.role < 3:
        return render_template('forbidden.html'), 302
    user = User.query.filter_by(username=username).first_or_404()
    if user.get_existence():
        if user.role >= current_user.role:
            flash('you cannot ban someone of equal or higher status, foul being.')
            return redirect(url_for('index'))
        user.alive = False
        db.session.add(user)
        db.session.commit()
    else:
        flash('user is already banned.')
        return redirect(url_for('index'))
    flash(username + ' is no more.')
    email.ban_email(user=user)
    return redirect(url_for('index'))

@app.route('/unban/<username>/')
@login_required
def unban(username):
    if current_user.role < 3:
        return render_template('forbidden.html'), 302
    user = User.query.filter_by(username=username).first_or_404()
    if user.get_existence():
        flash('user is not banned.')
        return redirect(url_for('index'))
    else:
        user.alive = True
        db.session.add(user)
        db.session.commit()
    flash(username + ' is more.')
    email.unban_email(user=user)
    return redirect(url_for('index'))

###                   ###
# Quote Approval/Denial #
###                   ###

@app.route('/approve/all/')
@login_required
def approve_all():
    if current_user.role < 3:
        return render_template('forbidden.html'), 403
    quotes = Quote.query.filter_by(moderated=False)
    for q in quotes:
        q.moderated = True
        q.approved = True
        db.session.add(q)
        flash('Quote ' + str(q.id) + ' approved')
    db.session.commit()

@app.route('/approve/q/<id>/')
@login_required
def approve_quote(id):
    id = int(id)
    if current_user.role < 3:
        return render_template('forbidden.html'), 403
    quote = Quote.query.filter_by(id=id).first_or_404()
    quote.published = True
    quote.moderated = True
    quote.created = datetime.utcnow()
    db.session.add(quote)
    db.session.commit()
    flash('Quote #' + str(id) + ' has been approved.')
    try:
        email.quote_approved_email(user=quote.submitter, quote=quote)
    except:
        pass
    if not request.referrer:
        return redirect(url_for('index'))
    else:
        return redirect(request.referrer)

@app.route('/deny/q/<id>/', methods=['GET', 'POST'])
@login_required
def deny_quote(id):
    id = int(id)
    if current_user.role < 3:
        return render_template('forbidden.html'), 403
    quote = Quote.query.filter_by(id=id).first_or_404()
    form = DenyQuoteForm(id=str(id))
    if form.validate_on_submit():
        quote.deny_reason = form.reason.data
        quote.published = False
        quote.moderated = True
        db.session.add(quote)
        db.session.commit()
        flash('Quote #' + str(id) + ' has been denied. Reason: ' + form.reason.data)
        try:
            email.quote_denied_email(user=quote.submitter, quote=quote)
        except:
            pass
        # Remove auto-upvote
        uid = quote.submitter.id
        quote.downvote(uid) # Flip from up to down, if necessary
        quote.upvote(uid) # Flip from down to up
        quote.upvote(uid) # Flip from up to neutral
        if not request.referrer:
            return redirect(url_for('index'))
        else:
            return redirect(request.referrer)
    return render_template('forms/denyquote.html', form=form)

@app.route('/delete/q/<id>/')
@login_required
def delete_quote(id):
    id = int(id)
    if current_user.role < 4:
        return 403
    quote = Quote.query.filter_by(id=id).first_or_404()
    db.session.delete(quote)
    db.session.commit()
    flash('Deleted quote #' + str(id))
    if not request.referrer:
        return redirect(url_for('index'))
    else:
        return redirect(request.referrer)

@app.route('/merge/<id1>/into/<id2>/') #merge
@login_required
def merge_speakers(id1, id2):
    if current_user.role < 4:
        return render_template('forbidden.html'), 403
    id1 = int(id1)
    id2 = int(id2)
    speaker1 = Speaker.query.filter_by(id=id1).first_or_404()
    print("Got speaker1: " + speaker1.name)
    speaker2 = Speaker.query.filter_by(id=id2).first_or_404()
    print("Got speaker2: " + speaker2.name)
    for quote in speaker1.quotes:
        quote.speaker = speaker2
        quote.speaker_id = id2
        db.session.add(quote)
    db.session.commit()
    flash('Merged ' + speaker1.name + ' quotes into ' + speaker2.name)
    return redirect(url_for('index'))

@app.route('/purge/s/')
@login_required
def purge_speakers():
    if current_user.role < 3:
        return render_template('forbidden.html'), 403
    speakers = Speaker.query
    empty_speakers = []
    for speaker in speakers:
        if len(speaker.quotes) == 0:
            flash('Deleted empty speaker ' + speaker.name)
            db.session.delete(speaker)
    db.session.commit()
    return redirect(url_for('index'))
