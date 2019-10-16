from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app import app, db
from app.forms import DenyQuoteForm
from app.models import User, Speaker, Quote

@app.route('/admin/')
@login_required
def admin_home():
    if current_user.role < 3:
        return render_template('forbidden.html'), 403
    users = User.query.order_by(User.id)
    quotes = Quote.query.order_by(Quote.id)
    speakers = Speaker.query.order_by(Speaker.id)
    return render_template('admin/dash.html', users=users, quotes=quotes, speakers=speakers)

###                                 ###
# User Promotion/Demotion/Destruction #
###                                 ###

@app.route('/promote/<username>/')
@login_required
def promote(username):
    if current_user.role < 4:
        return render_template('forbidden.html'), 403
    user = User.query.filter_by(username=username).first_or_404()
    if user.role < 3:
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
    if current_user.role < 4:
        return render_template('forbidden.html'), 403
    user = User.query.filter_by(username=username).first_or_404()
    if user.role == 1:
        flash('cannot demote below serf level. yes, even freshmen.')
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
    return redirect(url_for('index'))

###                   ###
# Quote Approval/Denial #
###                   ###

@app.route('/approve/q/<id>/')
@login_required
def approve_quote(id):
    id = int(id)
    if current_user.role < 3:
        return render_template('forbidden.html'), 403
    quote = Quote.query.filter_by(id=id).first_or_404()
    quote.published = True
    quote.moderated = True
    db.session.add(quote)
    db.session.commit()
    flash('Quote #' + str(id) + ' has been approved.')
    return redirect(request.args.get('target', url_for('index'), type=str))

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
        quote.score = 0
        db.session.add(quote)
        db.session.commit()
        flash('Quote #' + str(id) + ' has been denied. Reason: ' + form.reason.data)
        # Put submitter email notification here.
        return redirect(url_for('index'))
    return render_template('forms/denyquote.html', form=form)

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
