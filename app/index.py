from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app import app, db
from app.models import User, Speaker, Quote

@app.route('/')
def index():
    if current_user.is_anonymous(): # user not logged in
        return render_template('base.html')
    elif current_user.role > 2: # king, vassal
        return redirect(url_for('admin_home'))
    else: # baron, serf
        return render_template('base.html') # i really need to build a normie home page. or just a home page
