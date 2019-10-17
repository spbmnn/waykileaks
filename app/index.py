from flask import render_template, redirect, url_for
from flask_login import current_user
from app import app

@app.route('/')
def index():
    if current_user.is_anonymous:
        return redirect(url_for('quote_list'))
    elif current_user.role > 2: # king, vassal
        return redirect(url_for('admin_home'))
    else: # baron, serf
        return redirect(url_for('quote_list')) # i really need to build a normie home page. or just a home page
