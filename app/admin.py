from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app import app, db
from app.models import User, Speaker, Quote

@app.route('/admin/')
@login_required
def admin_home():
    if current_user.role < 3:
        return render_template('forbidden.html'), 403
    return "it's not ready yet!!!!!"

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
    if user.alive:
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
    if user.alive:
        flash('user is not banned.')
        return redirect(url_for('index'))
    else:
        user.alive = True
        db.session.add(user)
        db.session.commit()
    flash(username + ' is more.')
    return redirect(url_for('index'))

###                               ###
# Quote Approval/Denial/Destruction #
###                               ###

@app.route('/approve/q/<id>/')
@login_required
def approve_quote(id):
    id = int(id)
    if current_user.role < 3:
        return render_template('forbidden.html'), 403
    quote = Quote.query.filter_by(id=id).first_or_404()
    quote.published = True
    db.session.add(quote)
    db.session.commit()
    flash('Quote #' + str(id) + ' has been approved.')
    return redirect(request.args.get('target', url_for('index'), type=str))

@app.route('/hide/q/<id>/')
@login_required
def unapprove_quote(id):
    id = int(id)
    if current_user.role < 3:
        return render_template('forbidden.html'), 403
    quote = Quote.query.filter_by(id=id).first_or_404()
    quote.published = False
    db.session.add(quote)
    db.session.commit()
    flash('Quote #' + str(id) + ' has been approved.')
    return redirect(url_for('index'))

@app.route('/delete/q/<id>/') # TODO: make this a form / implement reason for removal 4 emailz
@login_required
def delete_quote(id):
    id = int(id)
    if current_user.role < 4:
        return render_template('forbidden.html'), 403
    quote = Quote.query.filter_by(id=id).first_or_404()
    quote.delete(synchronize_session=True)
    db.session.commit()
    flash('Quote #' + str(id) + ' has been deleted.')
    return redirect(url_for('index'))
